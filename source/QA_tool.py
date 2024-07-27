from typing import List

from custom_logger import logger

from custom_chains import chain_handler
from web_search_tool import WebSearchTool


class QualityAssuranceTool:
    def __init__(self, settings: dict) -> None:
        """
        Initializes the Quality Assurance Tool with the provided settings.

        Args:
            settings (dict): The settings to be used for the Quality Assurance check on final response.

        Returns:
            None
        """
        self.settings = settings
        self.web_search_tool = WebSearchTool(settings["wb_tool"])
        self.qa_chain = chain_handler.create_chain(prompt_id=self.settings.get("prompt_id"))
        logger.debug("Initializing QualityAssuranceTool with settings.")

    def qa_tool(self, query: str, reference_data: List, instructions: List, generated_response: str) -> str:
        """
        Executes the Quality Assurance tool.

        Args:
            query (str): User's input query
            reference_data (List): List of Reference Data
            instructions (list): List of Instructions for Quality Assurance Check.
            generated_response (str): The generated_response on which to perform Quality Assurance Check.


        Returns:
            results (str): Recommendations for improving the data.
        """
        logger.info(f"Executing Quality Assurance check for data: {generated_response}")
        try:
            wb_results = self.web_search_tool.wb_tool(query)
            results = self.qa_chain.invoke(
                {
                    "query": query,
                    "reference_data": (reference_data, wb_results),
                    "instructions": instructions,
                    "data": generated_response

                }
            ).content
            logger.info("Quality Assurance Check and Processing completed.")

        except Exception as e:
            logger.error(f"Error executing Quality Assurance Check: {e}", exc_info=True)
            results = "Error executing Quality Assurance Check"
        return results
