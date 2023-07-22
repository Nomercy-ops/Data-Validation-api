import os
import shutil
import tempfile
import time
from datetime import datetime
import asyncio
import dask.dataframe as dd
from fastapi import APIRouter, Request, HTTPException, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import WebSocket

from app.DatabaseHandling import process_database_data
from app.validate import calculate_validation_results

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

validation_results = {}  # Move the declaration outside of any function
progress_sockets = []  # Global list to store active progress sockets

# Temporary directory to store uploaded files
TEMP_DIR_PATH = None


# Progress callback function to send progress updates
async def progress_callback(progress, elapsed_time):
    """
    An asynchronous function that takes in `progress` and `elapsed_time` as parameters.
    It sends a JSON response containing the `progress` and `elapsed_time` to each socket in the `progress_sockets` list.
    If a WebSocket connection is closed, the socket is added to a list of sockets to remove.
    After iterating through all the `progress_sockets`, any disconnected sockets are removed from the `progress_sockets` list.
    """
    response = {"progress": progress, "elapsedTime": elapsed_time}
    # Create a copy of the progress_sockets list to safely iterate
    sockets_to_remove = []
    for progress_socket in progress_sockets:
        try:
            await progress_socket.send_json(response)
        except WebSocketDisconnect:
            # WebSocket connection closed, add to the list of sockets to remove
            sockets_to_remove.append(progress_socket)

    # Remove disconnected sockets after the loop
    for socket in sockets_to_remove:
        progress_sockets.remove(socket)

@router.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    """
    Websocket endpoint for handling progress updates.

    Parameters:
    - websocket: A WebSocket instance representing the client connection.

    Returns:
    - None
    """
    await websocket.accept()
    progress_sockets.append(websocket)  # Add the progress socket to the list

    try:
        while True:
            # Receive and ignore any incoming messages
            await websocket.receive_text()

    except WebSocketDisconnect:
        # WebSocket connection closed, remove the WebSocket from the list
        if websocket in progress_sockets:  # Check if the WebSocket is in the list
            progress_sockets.remove(websocket)

async def close_websockets():
    """
    Close the WebSocket connections.
    """
    for progress_socket in progress_sockets:
        await progress_socket.close()
    progress_sockets.clear()



async def show_results(request: Request, validation_results, total_time):
 # Convert total_time from seconds to minutes
    validation_results["processing_time"] = total_time
    # validation_results_json = json.dumps(validation_results)
    print(validation_results)

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "results": validation_results,
        },
    )

# Validate CSV data
@router.post("/validate/csv")
async def validate_csv_data(
    request: Request,
    source: str = Form(...),
    target: str = Form(...),
    source_csv: UploadFile = File(...),
    target_csv: UploadFile = File(...),
):
    validation_results = {}

    try:
        if source == "csv" and target == "csv":
            global TEMP_DIR_PATH
            if not TEMP_DIR_PATH:
                # Create the temporary directory if it doesn't exist
                TEMP_DIR_PATH = tempfile.mkdtemp(dir=os.getcwd())

            start_time = time.time()
            source_file_path = os.path.join(TEMP_DIR_PATH, source_csv.filename)
            target_file_path = os.path.join(TEMP_DIR_PATH, target_csv.filename)

            # Save the uploaded files to the temporary directory
            with open(source_file_path, "wb") as source_file, open(target_file_path, "wb") as target_file:
                source_file.write(await source_csv.read())
                target_file.write(await target_csv.read())

            # Load the data from the temporary files using Dask
            source_data = dd.read_csv(source_file_path, assume_missing=True)
            target_data = dd.read_csv(target_file_path, assume_missing=True)

            mismatched_columns = set(source_data.columns).symmetric_difference(set(target_data.columns))
            if mismatched_columns:
                error_message = f"The following columns are missing or mismatched between the source and target CSV files: {', '.join(mismatched_columns)}"
                validation_results["error"] = error_message

            if "error" in validation_results:
                error_message = validation_results["error"]
                confirm_message = "Validation failed due to the following error: " + error_message
                await close_websockets()
                return templates.TemplateResponse(
                    "confirm.html",
                    {
                        "request": request,
                        "error_message": error_message,
                        "confirm_message": confirm_message,
                        "source_csv": source_csv,
                        "target_csv": target_csv,
                    },
                )

            validation_results =  calculate_validation_results(source_data, target_data)

            # Simulate validation and progress updates
            for progress in range(0, 101, 10):
                elapsed_time = time.time() - start_time
                await progress_callback(progress, elapsed_time)
                await asyncio.sleep(0.1)  # Add a small delay to allow other tasks to run

            total_time = time.time() - start_time

            await cleanup_temp_dir()

            return await show_results(request, validation_results, total_time)

    except Exception as e:
        await cleanup_temp_dir()
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Validate database data
@router.post("/validate/database")
async def validate_database_data(
    request: Request,
    source: str = Form(...),
    target: str = Form(...),
    data: str = Form(...),
):
    try:
        if source == "database" and target == "database":
            start_time = time.time()
            # Process the received data
            res = process_database_data(data)
            # Simulate validation and progress updates
            for progress in range(0, 101, 10):  
                elapsed_time = time.time() - start_time
                await progress_callback(progress, elapsed_time)
                await asyncio.sleep(0.1)  # Add a small delay to allow other tasks to run

            total_time = time.time() - start_time

            return await show_results(request, res, total_time)

    except Exception as e:
        error_message = f"Error occurred during database validation: {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)

@router.post("/confirm")
async def confirm_data(request: Request, source_csv: str = Form(...), target_csv: str = Form(...), columns_to_remove: str = Form(...)):
    try:
        # Define the columns to exclude
        columns_to_remove = columns_to_remove.split(",")
        global TEMP_DIR_PATH
        if not TEMP_DIR_PATH:
            # Create the temporary directory if it doesn't exist
            TEMP_DIR_PATH = tempfile.mkdtemp(dir=os.getcwd())

        start_time = time.time()
        # Read the source and target CSV files into Dask DataFrames, excluding the specified columns
        source_data = dd.read_csv(os.path.join(TEMP_DIR_PATH, source_csv), assume_missing=True,
                                  usecols=lambda col: col not in columns_to_remove)
        target_data = dd.read_csv(os.path.join(TEMP_DIR_PATH, target_csv), assume_missing=True,
                                  usecols=lambda col: col not in columns_to_remove)

        validation_results = calculate_validation_results(
            source_data, target_data, columns_to_remove)

        await cleanup_temp_dir()
        TEMP_DIR_PATH = None
        total_time = time.time() - start_time
        print(total_time)

        return await show_results(request, validation_results,total_time)
    except Exception as e:
        await cleanup_temp_dir()
        TEMP_DIR_PATH = None
        line_number = e.__traceback__.tb_lineno
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"Exception occurred at line {line_number} on {current_time}: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)


@router.get("/error")
def show_error(request: Request, error_message: str):
    """
    Render the error page with the error.html template.

    Args:
        request (Request): FastAPI request object.
        error_message (str): Error message to display.

    Returns:
        TemplateResponse: HTML template response.
    """
    return templates.TemplateResponse("error.html", {"request": request, "error_message": error_message})


@router.get("/contact")
def show_contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@router.on_event("shutdown")
async def cleanup_temp_dir():
    """
    Clean up the temporary directory when the server shuts down.
    """
    global TEMP_DIR_PATH
    try:
        if TEMP_DIR_PATH and os.path.exists(TEMP_DIR_PATH):
            shutil.rmtree(TEMP_DIR_PATH)
            TEMP_DIR_PATH = None
    except Exception as e:
        print(f"Error cleaning up temporary directory: {str(e)}")


@router.on_event("startup")
async def cleanup_temp_dir_startup():
    """
    Perform necessary startup tasks.
    """
    try:
        await cleanup_temp_dir()
    except Exception as e:
        print(f"Error cleaning up temporary directory: {str(e)}")
