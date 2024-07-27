import os
import re

from custom_logger import logger
from langchain_community.utilities import GoogleSerperAPIWrapper

# Fetching API keys from environment variables
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class SearchTool:
    def __init__(self, settings: dict) -> None:
        """
        Initializes the SearchTool with the provided settings.

        Args:
            settings (dict): The settings to be used for the SearchTool.

        Returns:
            None
        """
        self.settings = settings
        self.search_api = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
        logger.debug("SearchTool initialized with settings.")

    def perform_search(self, query: str) -> tuple[str, list]:
        """
        Performs a search using the configured search API.

        Args:
            query (str): The search query to be used.

        Returns:
            response, url (tuple[str, list]): The search response and the extracted URLs.

        """
        website_url = self.settings.get("website_url", "")
        modified_query = f"{website_url} {query}"
        logger.debug(f"Performing search with query: {modified_query}")
        response = self.search_api.run(query=modified_query)
        results = self.search_api.results(modified_query)
        urls = self._extract_urls(results)
        logger.info(f"Search performed successfully, extracted {len(urls)} URLs.")
        return response, urls

    @staticmethod
    def _extract_urls(results: dict) -> list[str]:
        """
        Extracts URLs from search results.

        Args:
            results: The search results from which to extract URLs.

        Returns:
            list[str]: The extracted URLs.
        """
        url_list = set(result['link'] for result in results.get('organic', []))
        return list(url_list)

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans the text by removing Markdown links and extra whitespaces.

        Args:
            text (str): The text to be cleaned.

        Returns:
            cleaned_text (str): The cleaned text.
        """
        text_without_md_links = re.sub(r"\[.*?\]\(.*?\)", "", text)
        cleaned_text = re.sub(r"\s+", " ", text_without_md_links).strip()
        logger.debug("Text cleaned for processing.")
        return cleaned_text


class WebSearchTool:
    def __init__(self, settings: dict) -> None:
        """
        Initializes the WebSearchTool with the provided settings.

        Args:
            settings (dict): The settings to be used for the WebSearchTool.

        Returns:
            None
        """
        self.settings = settings
        self.search_tool = SearchTool(settings)
        logger.debug("WebSearchTool initialized with settings.")

    def wb_tool(self, query: str) -> tuple[str, list[str]]:
        """
        Executes the web search tool.

        Args:
            query (str): The query to be used for the search.

        Returns:
            cleaned_response (str): The results of the web search.
            urls (list): The extracted URLs from the search results.
        """
        logger.info(f"Executing web search for query: {query}")
        modified_query = self.settings.get("query_prefix", "") + query
        search_response, urls = self.search_tool.perform_search(modified_query)
        cleaned_response = self.search_tool.clean_text(search_response)
        logger.info("Web search and chain processing completed.")
        return cleaned_response, urls
