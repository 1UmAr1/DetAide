import sys

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Adding paths to import custom modules
sys.path.insert(1, "source")
sys.path.insert(2, "ingestion")
sys.path.insert(3, "application")
sys.path.insert(4, "configurations")
# Importing input schemas
from schemas import QueryInput, SettingsInput, DataIngestionInput
from custom_logger import logging as logger
# Importing the main function and data ingestor
from driver import ast_driver
from elasticsearch_ingestion import DataIngestor

# Importing functions to fetch and update settings
from settings_manager import fetch_settings, upsert_settings, fetch_and_compare

# Creating a FastAPI instance
app = FastAPI()

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def service_check() -> dict:
    """
    Basic Check

    Returns:
        dict: Return service health
    """

    try:
        return {'status': 'The signals service is up and running smoothly. All systems are green!'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoke/{app_name}")
async def invoke_agent(app_name: str, query_input: QueryInput) -> dict:
    """
    Endpoint to invoke the agent driver function using the app_name and input parameters.

    Args:
        app_name (str): The name of the application.
        query_input (QueryInput): Input parameters including session_id and query.

    Returns:
        dict: Result returned by the agent.
    """
    in_params = {"app_name": app_name, "session_id": query_input.session_id, "query": query_input.query}
    try:
        settings = fetch_and_compare(app_name)
        result, status = ast_driver(in_params, settings)
        return {"result": result, "status": status}
    except Exception as e:
        logger.info(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/settings/{app_name}")
async def get_settings(app_name: str) -> dict:
    """
    Endpoint to retrieve settings for a given app_name.

    Args:
        app_name (str): The name of the application.

    Returns:
        dict: The settings for the given application.
    """
    settings = fetch_settings(app_name)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings


@app.post("/settings/{app_name}")
async def update_settings(app_name: str, settings_input: SettingsInput) -> dict:
    """
    Endpoint to update settings for a given app_name.

    Args:
        app_name (str): The name of the application.
        settings_input (SettingsInput): The updated settings for the application.

    Returns:
        dict: Confirmation message after updating settings.
    """
    try:
        upsert_settings(app_name, settings_input.settings)
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest_data")
async def ingest_data(data_input: DataIngestionInput) -> dict:
    """
    Endpoint to ingest data into Elasticsearch based on provided parameters.

    Args:
        data_input (DataIngestionInput): Input parameters including file path, index name, and other options.

    Returns:
        dict: Status message indicating success or failure of the data ingestion process.
    """

    logger.info(f"Ingesting data into {data_input.index_name} from {data_input.file_path}")
    ingestor = DataIngestor()
    try:
        ingestor.load_data(
            file_path=data_input.file_path,
            index_name=data_input.index_name,
            source=data_input.source,
            load_csvs_separately=data_input.load_csvs_separately,
            data_type=data_input.data_type
        )
        return {"message": "Data ingestion successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Running the FastAPI app using Uvicorn
    uvicorn.run(app=app, host="localhost", port=8080)
