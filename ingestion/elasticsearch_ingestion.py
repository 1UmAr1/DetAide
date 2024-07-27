import io
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from langchain_community.document_loaders import TextLoader, CSVLoader, PyPDFLoader
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

sys.path.insert(0, "configurations")

from custom_logger import logger

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path)


class DataIngestor:
    def __init__(self):
        """
        Initializes the DataIngestor with Elasticsearch URL and Google Drive credentials from environment variables.
        """
        self.es_url = os.getenv("ES_URL")
        self.google_drive_credentials = os.getenv("GOOGLE_DRIVE_CREDENTIALS")

    def load_data(self, file_path: str, index_name: str, source='local', load_csvs_separately: bool = False,
                  data_type: str = "all"):
        """
        Loads data from the specified file path or Google Drive folder and ingests it into Elasticsearch.

        Args:
            file_path (str): Path to the file or directory to load data from, or ID of the Google Drive folder.
            index_name (str): Name of the Elasticsearch index to ingest data into.
            source (str): Source of the files ('local' or 'google_drive'). Default is 'local'.
            load_csvs_separately (bool): Whether to load CSV files separately. Default is False.
            data_type (str): Type of data to load ('text', 'csv', 'pdf', or 'all'). Default is 'all'.

        Raises:
            ValueError: If an unsupported data type is provided.
        """
        if source == 'google_drive':
            download_path = os.path.join('downloaded_files', index_name)  # Path to save downloaded files
            self.download_files_from_drive(file_path, download_path)
            file_path = download_path  # Update file_path to local download path

        embedding = OpenAIEmbeddings()
        elastic_vector_search = ElasticsearchStore(
            es_url=self.es_url,
            index_name=index_name,
            embedding=embedding
        )
        logger.info("Data loaded successfully.")

        if data_type == "text":
            documents = self._load_text(file_path)
        elif data_type == "csv":
            documents = self._load_csv(file_path)
        elif data_type == "pdf":
            documents = self._load_pdf(file_path)
        elif data_type == "all":
            documents = self._load_all(file_path, load_csvs_separately)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

        self._ingest_to_elasticsearch(elastic_vector_search, documents)

    def _load_text(self, file_path: str) -> list:
        """
        Loads text data from the specified file path and splits it into smaller chunks.

        Args:
            file_path (str): Path to the text file.

        Returns:
            list: List of split document chunks.
        """
        loader = TextLoader(file_path)
        documents = loader.load()
        return self._split_documents(documents)

    def _load_csv(self, file_path: str) -> list:
        """
        Loads CSV data from the specified file path and splits it into smaller chunks.

        Args:
            file_path (str): Path to the CSV file.

        Returns:
            list: List of split document chunks.
        """
        loader = CSVLoader(file_path)
        documents = loader.load()
        return self._split_documents(documents)

    def _load_pdf(self, file_path: str, extract_images: bool = False) -> list:
        """
        Loads PDF data from the specified file path and splits it into pages.

        Args:
            file_path (str): Path to the PDF file.
            extract_images (bool): Whether to extract images from the PDF. Default is False.

        Returns:
            list: List of split pages.
        """
        loader = PyPDFLoader(file_path, extract_images=extract_images)
        pages = loader.load_and_split()
        return pages

    def _load_all(self, directory_path: str, load_csvs_separately: bool) -> list:
        docs = []
        # Ensure the use of Path from pathlib for handling paths
        base_path = Path(directory_path)
        # Recursive glob needs to be correctly used with pathlib or similar
        for file_path in base_path.rglob('*'):  # This correctly uses recursive globbing
            if file_path.is_file():
                if load_csvs_separately and file_path.suffix == '.csv':
                    docs.extend(self._load_csv(str(file_path)))
                elif file_path.suffix == '.pdf':
                    docs.extend(self._load_pdf(str(file_path)))
                else:
                    # Assuming other files are text files
                    docs.extend(self._split_documents([str(file_path)]))
        return docs

    def _split_documents(self, documents: list) -> list:
        """
        Splits documents into smaller chunks using a character-based text splitter.

        Args:
            documents (list): List of documents to split.

        Returns:
            list: List of split document chunks.
        """
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
        return text_splitter.split_documents(documents)

    def _ingest_to_elasticsearch(self, elastic_vector_search: ElasticsearchStore, documents: list) -> None:
        """
        Ingests documents into Elasticsearch.

        Args:
            elastic_vector_search (ElasticsearchStore): Elasticsearch store instance.
            documents (list): List of documents to ingest.
        """
        logger.info("Ingesting documents to Elasticsearch...")
        for doc in documents:
            doc.metadata = {k: v for k, v in doc.metadata.items() if k != "page_content"}
        elastic_vector_search.add_documents(documents)
        logger.info("Documents ingested successfully.")

    def connect_to_google_drive(self):
        """
        Connects to Google Drive using service account credentials.
        """
        logger.info("Connecting to Google Drive...")
        creds = service_account.Credentials.from_service_account_file(
            self.google_drive_credentials,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds)
        return service

    def download_files_from_drive(self, folder_id: str, download_path: str):
        """
        Downloads files from Google Drive folder.

        Args:
            folder_id (str): ID of the Google Drive folder to download files from.
            download_path (str): Local path to save the downloaded files.
        """
        logger.info("Downloading files from Google Drive...")
        service = self.connect_to_google_drive()
        results = service.files().list(q=f"'{folder_id}' in parents", pageSize=1000, fields="files(id, name)").execute()
        items = results.get("files", [])

        if not os.path.exists(download_path):
            os.makedirs(download_path)

        for item in items:
            file_id = item["id"]
            file_name = item["name"]
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(os.path.join(download_path, file_name), 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {file_name}: {int(status.progress() * 100)}%.")
