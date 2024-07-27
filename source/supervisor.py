from custom_logger import logger
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import Runnable

from utils import model


class AgentSupervisor:
    """This tool decides the next step in the process based on the input data."""

    def __init__(self, settings: dict) -> None:
        self.settings = settings.copy()
        members = self.settings.get("members", [])
        options = self.settings.get("options", self.settings.get("members", []))

        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [
                            {"enum": options},
                        ],
                    }
                },
                "required": ["next"],
            },
        }
        system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            " following workers:  {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH. Use your workers frequently. Make sure you"
            " do research and quality assurance check before providing a response"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options), members=", ".join(members))

        self.supervisor_chain = (
                prompt
                | model.bind_functions(functions=[function_def], function_call="route")
                | JsonOutputFunctionsParser()
        )

        logger.debug("Initializing Supervisor Tool with settings.")

    def supervisor_tool(self) -> Runnable:
        """
        Executes the Quality Assurance tool.

        Returns:
            output (dict): Next Steps to take.
        """
        return self.supervisor_chain

