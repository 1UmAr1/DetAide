from typing import Any

from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser

from utils import model, fetch_prompt


class ChainHandler:
    def __init__(self) -> None:
        """
        Initializes the ChainHandler.

        Returns:
            None
        """
        pass

    def create_chain(self, prompt_id: str, **kwargs) -> Any:
        """
        Creates a chain using a prompt fetched based on the provided prompt ID.

        Args:
            prompt_id (str): The ID of the prompt used to create the chain.
            **kwargs: Additional arguments to be passed to the chain.

        Returns:
            chain: A chain formed by concatenating the fetched prompt with the model.
        """
        params = kwargs.get("params", {})
        # Fetch prompt based on the provided prompt ID
        prompt = fetch_prompt(prompt_id)

        # Extract the parser and functions from the kwargs
        functions = params.get("functions", {})
        # Concatenate the fetched prompt with the model
        if functions:
            return prompt | model.bind_functions(
                functions=[functions],
                function_call="route"
            ) | JsonOutputFunctionsParser()

        return prompt | model


chain_handler = ChainHandler()
