from typing import Any

from custom_logger import logger

from custom_chains import chain_handler
from utils import setup_es_vector_store


def fetch_kb_results(query: str, settings: dict) -> list[Any]:
    """
    Fetches Knowledge Base search results based on the provided query and settings.

    Args:
        query (str): The query to be used for the search.
        settings (dict): The settings to be used for the search.

    Returns:
        results (str): The results of the Knowledge Base search.
    """
    logger.info(f"Fetching Knowledge Base search results for query: {query}")

    try:
        es_vs = setup_es_vector_store(settings["index_name"])
        results = es_vs.similarity_search(query=query, k=settings.get("k", 5))
        logger.info("Knowledge Base search results fetched successfully.")
    except Exception as e:
        logger.info(f"Error fetching Knowledge Base search results: {e}")
        results = []
    return results


class KBSearchTool:
    def __init__(self, settings: dict) -> None:
        """
        Initializes the Knowledge Base Search with the provided settings.

        Args:
            settings (dict): The settings to be used for the WebSearchTool.

        Returns:
            None
        """
        self.settings = settings
        self.kb_chain = chain_handler.create_chain(prompt_id=self.settings.get("prompt_id"))
        logger.debug("Initializing with settings.")

    def kb_tool(self, query: str) -> str:
        """
        Executes the web search tool.

        Args:
            query (str): The query to be used for the search.

        Returns:
            results (str): The results of the web search.
        """
        logger.info(f"Executing Knowledge Base search for query: {query}")
        try:
            raw_kb_search = fetch_kb_results(query, self.settings)
            results = self.kb_chain.invoke({"query": query, "documents": raw_kb_search}).content
            logger.info("Knowledge Base Search and chain processing completed.")

        except Exception as e:
            logger.error(f"Error executing Knowledge Base Search: {e}", exc_info=True)
            results = "Error executing Knowledge Base Search."
        return results
