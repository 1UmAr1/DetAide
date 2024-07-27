from pydantic import BaseModel


class QueryInput(BaseModel):
    """
    Pydantic model representing input parameters for a query.

    Args:
        session_id (str): Session ID for the query.
        query (str): Query string.
    """
    session_id: str  # Type annotation for session ID, string
    query: str  # Type annotation for query, string


class SettingsInput(BaseModel):
    """
    Pydantic model representing input parameters for updating settings.

    Args:
        settings (dict): Dictionary containing settings data.
    """
    settings: dict  # Type annotation for settings, dictionary


class DataIngestionInput(BaseModel):
    """
    Pydantic model representing input parameters for data ingestion.

    Args:
        file_path (str): Path to the file or directory, or ID of the Google Drive folder.
        index_name (str): Name of the Elasticsearch index to ingest data into.
        source (str): Source of the files ('local' or 'google_drive'). Default is 'local'.
        load_csvs_separately (bool): Whether to load CSV files separately. Default is False.
        data_type (str): Type of data to load ('text', 'csv', 'pdf', or 'all'). Default is 'all'.
    """
    file_path: str
    index_name: str
    source: str = 'local'
    load_csvs_separately: bool = False
    data_type: str = 'all'
