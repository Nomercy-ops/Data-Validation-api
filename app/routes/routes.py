# import os
# from fastapi import APIRouter, Request
# from fastapi import UploadFile, File, Form
# import pandas as pd
# from fastapi.templating import Jinja2Templates
# from app.validate import calculate_validation_results
# import tempfile
# from starlette.responses import HTMLResponse


# templates = Jinja2Templates(directory="app/templates")
# router = APIRouter()

# validation_results = {}  # Move the declaration outside of any function

# # Temporary directory to store uploaded files
# temp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())


# @router.get("/results")
# def show_results(request: Request, results: dict):
#     return templates.TemplateResponse("results.html", {"request": request, "results": results})


# @router.post("/validate")
# async def validate_data(
#     request: Request,
#     source: str = Form(...),
#     target: str = Form(...),
#     source_csv: UploadFile = File(...),
#     target_csv: UploadFile = File(...)
# ):
#     global validation_results  # Add this line to access the global variable

#     validation_results = {}

#     if source == "csv" and target == "csv":
#         source_file_path = os.path.join(temp_dir.name, source_csv.filename)
#         target_file_path = os.path.join(temp_dir.name, target_csv.filename)

#         # Save the uploaded files to the temporary directory
#         with open(source_file_path, "wb") as source_file:
#             source_file.write(await source_csv.read())

#         with open(target_file_path, "wb") as target_file:
#             target_file.write(await target_csv.read())

#         # Load the data from the temporary files
#         source_data = pd.read_csv(source_file_path)
#         target_data = pd.read_csv(target_file_path)

#         if not set(source_data.columns).issubset(set(target_data.columns)) or not set(target_data.columns).issubset(set(source_data.columns)):
#             mismatched_columns = set(source_data.columns).symmetric_difference(
#                 set(target_data.columns))
#             error_message = f"The following columns are missing or mismatched between the source and target CSV files: {', '.join(mismatched_columns)}"
#             validation_results["error"] = error_message

#         if "error" in validation_results:
#             error_message = validation_results["error"]
#             confirm_message = "Validation failed due to the following error: " + error_message
#             return templates.TemplateResponse(
#                 "confirm.html",
#                 {
#                     "request": request,
#                     "error_message": error_message,
#                     "confirm_message": confirm_message,
#                     "source_csv": source_csv,  # Add this line to pass the file to the confirm page
#                     "target_csv": target_csv,  # Add this line to pass the file to the confirm page
#                 },
#             )

#         validation_results = calculate_validation_results(
#             source_data, target_data)

#         return show_results(request, validation_results)

#     elif source == "database" and target == "database":
#         pass


# @router.post("/confirm")
# def confirm_data(request: Request, source_csv: str = Form(...), target_csv: str = Form(...), columns_to_remove: str = Form(...)):
#     source_data = pd.read_csv(os.path.join(temp_dir.name, source_csv))
#     target_data = pd.read_csv(os.path.join(temp_dir.name, target_csv))
#     columns_to_remove = columns_to_remove.split(",")

#     # Remove specified columns from either source or target DataFrame if present

#     for column in columns_to_remove:
#         if column in source_data.columns:
#             source_data.drop(column, axis=1, inplace=True)
#         if column in target_data.columns:
#             target_data.drop(column, axis=1, inplace=True)

#     # Get the unique set of columns from both DataFrames
#     all_columns = set(source_data.columns).union(target_data.columns)

#     # Reindex both DataFrames to align their columns
#     source_data = source_data.reindex(columns=all_columns)
#     target_data = target_data.reindex(columns=all_columns)

#     validation_results = calculate_validation_results(source_data, target_data,columns_to_remove)
#     return show_results(request, validation_results)


# @router.get("/error")
# def show_error(request: Request, error_message: str):
#     return templates.TemplateResponse("error.html", {"request": request, "error_message": error_message})

# # Clean up the temporary directory when the server stops


# @router.on_event("shutdown")
# async def cleanup_temp_dir():
#     temp_dir.cleanup()


# @router.get("/contact")
# def show_contact(request: Request):
#     return templates.TemplateResponse("contact.html", {"request": request})


import os
import tempfile
from fastapi import APIRouter, Request, HTTPException
from fastapi import UploadFile, File, Form, Body
import dask.dataframe as dd
from fastapi.templating import Jinja2Templates
from app.validate import calculate_validation_results
from typing import Dict, Optional
from datetime import datetime
from fastapi.responses import JSONResponse
import json

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

validation_results = {}  # Move the declaration outside of any function

# Temporary directory to store uploaded files
temp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())


@router.get("/results")
def show_results(request: Request, results: dict):
    """
    Render the results page with the results.html template.

    Args:
        request (Request): FastAPI request object.
        results (dict): Validation results.

    Returns:
        TemplateResponse: HTML template response.
    """
    return templates.TemplateResponse("results.html", {"request": request, "results": results})


@router.post("/validate/csv")
async def validate_data(
    request: Request,
    source: str = Form(...),
    target: str = Form(...),
    source_csv: UploadFile = File(None),
    target_csv: UploadFile = File(None),
):
    global validation_results
    validation_results = {}

    try:
        if source == "csv" and target == "csv":
            source_file_path = os.path.join(temp_dir.name, source_csv.filename)
            target_file_path = os.path.join(temp_dir.name, target_csv.filename)

            # Save the uploaded files to the temporary directory
            with open(source_file_path, "wb") as source_file, open(
                target_file_path, "wb"
            ) as target_file:
                source_file.write(await source_csv.read())
                target_file.write(await target_csv.read())

            # Load the data from the temporary files using Dask
            source_data = dd.read_csv(source_file_path, assume_missing=True)
            target_data = dd.read_csv(target_file_path, assume_missing=True)

            mismatched_columns = (
                set(source_data.columns).symmetric_difference(set(target_data.columns))
            )
            if mismatched_columns:
                error_message = f"The following columns are missing or mismatched between the source and target CSV files: {', '.join(mismatched_columns)}"
                validation_results["error"] = error_message

            if "error" in validation_results:
                error_message = validation_results["error"]
                confirm_message = "Validation failed due to the following error: " + error_message
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

            validation_results = calculate_validation_results(source_data, target_data)
            print(validation_results)
            return show_results(request, validation_results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/database")
async def validate_database_data(request: Request,
                                source: str = Form(...),
                                target: str = Form(...),
                                data: str = Form(...)):
    """
    Validate and process database data received from a POST request.

    Args:
        request (Request): The incoming request object.
        source (str): The source of the data.
        target (str): The target of the data.
        source_db (dict): The source database data.
        target_db (dict): The target database data.

    Returns:
        JSONResponse: The response containing a success message if data was received and processed successfully.
    """

    # Process the received data
    print(data)
    print(source)
    

    return JSONResponse(content={'message': 'Data received and processed successfully'})


@router.post("/confirm")
def confirm_data(request: Request, source_csv: str = Form(...), target_csv: str = Form(...), columns_to_remove: str = Form(...)):
    try:
        # Define the columns to exclude
        columns_to_remove = columns_to_remove.split(",")

        # Read the source and target CSV files into Dask DataFrames, excluding the specified columns
        source_data = dd.read_csv(os.path.join(temp_dir.name, source_csv), assume_missing=True,
                                  usecols=lambda col: col not in columns_to_remove)
        target_data = dd.read_csv(os.path.join(temp_dir.name, target_csv), assume_missing=True,
                                  usecols=lambda col: col not in columns_to_remove)

        validation_results = calculate_validation_results(
            source_data, target_data, columns_to_remove)
        return show_results(request, validation_results)
    except Exception as e:
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


@router.on_event("startup")
async def cleanup_temp_dir():
    """
    Clean up the temporary directory when the server starts up.
    """
    temp_files = os.listdir(temp_dir.name)
    for temp_file in temp_files:
        file_path = os.path.join(temp_dir.name, temp_file)
        os.remove(file_path)


@router.on_event("shutdown")
async def cleanup_temp_dir():
    """
    Clean up the temporary directory when the server shuts down.
    """
    try:
        temp_dir.cleanup()
    except Exception as e:
        # Log or handle the exception appropriately
        print(f"Error cleaning up temporary directory: {str(e)}")
