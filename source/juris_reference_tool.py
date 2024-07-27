from custom_logger import logger
from web_search_tool import WebSearchTool
from kb_search import KBSearchTool
from custom_chains import chain_handler


class JurisReferenceTool:
    def __init__(self, settings: dict) -> None:
        """
        Initializes the JurisReferenceTool with the provided settings.

        Args:
            settings (dict): The settings to be used for the JurisReferenceTool.

        Returns:
            None
        """
        self.settings = settings
        self.web_search_tool = WebSearchTool(settings["wb_tool"])
        self.juris_chain = chain_handler.create_chain(prompt_id=self.settings.get("prompt_id"))
        self.kb = KBSearchTool(settings["kb_search_tool"])
        logger.debug("JurisReferenceTool initialized with settings.")

    def juris_tool(self, query: str) -> str:
        """
        Executes the JurisReferenceTool.

        Args:
            query (str): The query to be used for the JurisReferenceTool Search.

        Returns:
            results (str): The results of the JurisReferenceTool.
        """
        logger.info(f"Executing Juris Reference search for query: {query}")
        wb_results = self.web_search_tool.wb_tool(query)
        kb_results = self.kb.kb_tool(query)
        results = self.juris_chain.invoke({"input": query, "documents": (wb_results, kb_results)})
        logger.info("Juris Reference search and chain processing completed.")
        return results
