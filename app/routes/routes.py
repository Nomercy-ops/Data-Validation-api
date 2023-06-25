import os
from fastapi import APIRouter, Request
from fastapi import UploadFile, File, Form
import pandas as pd
from fastapi.templating import Jinja2Templates
from app.validate import calculate_validation_results
import tempfile

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

validation_results = {}  # Move the declaration outside of any function

# Temporary directory to store uploaded files
temp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())


@router.get("/results")
def show_results(request: Request, results: dict):
    return templates.TemplateResponse("results.html", {"request": request, "results": results})


@router.post("/validate")
async def validate_data(
    request: Request,
    source: str = Form(...),
    target: str = Form(...),
    source_csv: UploadFile = File(...),
    target_csv: UploadFile = File(...)
):
    global validation_results  # Add this line to access the global variable

    validation_results = {}

    if source == "csv" and target == "csv":
        source_file_path = os.path.join(temp_dir.name, source_csv.filename)
        target_file_path = os.path.join(temp_dir.name, target_csv.filename)

        # Save the uploaded files to the temporary directory
        with open(source_file_path, "wb") as source_file:
            source_file.write(await source_csv.read())

        with open(target_file_path, "wb") as target_file:
            target_file.write(await target_csv.read())

        # Load the data from the temporary files
        source_data = pd.read_csv(source_file_path)
        target_data = pd.read_csv(target_file_path)

        if not set(source_data.columns).issubset(set(target_data.columns)) or not set(target_data.columns).issubset(set(source_data.columns)):
            mismatched_columns = set(source_data.columns).symmetric_difference(
                set(target_data.columns))
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
                    "source_csv": source_csv,  # Add this line to pass the file to the confirm page
                    "target_csv": target_csv,  # Add this line to pass the file to the confirm page
                },
            )

        validation_results = calculate_validation_results(
            source_data, target_data)

    elif source == "database" and target == "database":
        pass

    if "error" in validation_results:
        error_message = validation_results["error"]
        return show_error(request, error_message)

    confirm_message = "Validation successful. Do you want to remove any columns before proceeding?"
    return templates.TemplateResponse(
        "confirm.html",
        {
            "request": request,
            "error_message": "",
            "confirm_message": confirm_message,
            "source_csv": source_csv,  # Add this line to pass the file to the confirm page
            "target_csv": target_csv,  # Add this line to pass the file to the confirm page
        },
    )


@router.post("/confirm")
def confirm_data(request: Request, source_csv: str = Form(...), target_csv: str = Form(...), columns_to_remove: str = Form(...)):
    source_data = pd.read_csv(os.path.join(temp_dir.name, source_csv))
    target_data = pd.read_csv(os.path.join(temp_dir.name, target_csv))
    columns_to_remove = columns_to_remove.split(",")

    # Remove specified columns from either source or target DataFrame if present

    for column in columns_to_remove:
        if column in source_data.columns:
            source_data.drop(column, axis=1, inplace=True)
        if column in target_data.columns:
            target_data.drop(column, axis=1, inplace=True)

    # Get the unique set of columns from both DataFrames
    all_columns = set(source_data.columns).union(target_data.columns)

    # Reindex both DataFrames to align their columns
    source_data = source_data.reindex(columns=all_columns)
    target_data = target_data.reindex(columns=all_columns)

    validation_results = calculate_validation_results(source_data, target_data,columns_to_remove)


    return show_results(request, validation_results)


@router.get("/error")
def show_error(request: Request, error_message: str):
    return templates.TemplateResponse("error.html", {"request": request, "error_message": error_message})

# Clean up the temporary directory when the server stops


@router.on_event("shutdown")
async def cleanup_temp_dir():
    temp_dir.cleanup()
