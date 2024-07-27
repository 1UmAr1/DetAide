from custom_logger import logger

from custom_chains import chain_handler


class DraftTool:
    def __init__(self, settings: dict) -> None:
        """
        Initializes the Drafting tool.

        Args:
            settings (dict): The settings to be used for drafting the response.

        Returns:
            None
        """
        self.settings = settings.copy()
        self.drafting_chain = chain_handler.create_chain(prompt_id=self.settings.get("prompt_id"))
        logger.debug("Initializing Drafting Tool with settings.")

    def draft_tool(self, information: dict) -> str:
        """
        Executes Drafting Tool for the given query and drafting instructions.

        Args:
            information (dict): The input information for drafting the response.
        Returns:
            results (str): The drafted response for the given query.
        """
        drafting_instructions = self.settings.get("drafting_instructions", "")
        logger.info(f"Executing Drafting Tool with instructions: {drafting_instructions} and reference data.")
        try:
            results = self.drafting_chain.invoke(
                {
                    "information": information
                }
            ).content
            logger.info("Drafting and chain processing completed.")

        except Exception as e:
            logger.error(f"Error executing Drafting Tool: {e}", exc_info=True)
            results = "Error executing Drafting Tool."
        return results
