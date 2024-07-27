from custom_logger import logger
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.runnables.history import Runnable

from tools_lib import initialize_tools
from utils import model, fetch_prompt


class AgentManager:
    def __init__(self, settings: dict) -> None:
        """
        Initializes the AgentManager with the given settings.

        Args:
            settings (dict): The settings to be used for agent execution.
        """
        self.settings = settings
        logger.debug("AgentManager initialized with settings.")

    def initialize_agent(self) -> Runnable:
        """
        Initializes and configures the agent for execution.

        Returns:
            agent_runnable (Runnable): The agent setup and configured tools.

        """
        prompt_id = self.settings["parent_settings"]["agent_id"]
        prompt_text = fetch_prompt(prompt_id)
        logger.debug(f"Prompt fetched: {prompt_text}")

        tools = initialize_tools(self.settings)
        logger.debug(f"Tools initialized: {tools}")

        agent_runnable = create_openai_tools_agent(model, tools, prompt_text)
        logger.debug("Agent created and configured with tools and prompt.")
        agent_executor = AgentExecutor(
            agent=agent_runnable,
            tools=tools,
            verbose=True,
            return_intermediate_steps=True,
            early_stopping_method="generate"
        )

        return agent_executor


def agent_manager(settings: dict) -> Runnable:
    """
    Executes the agent using the provided settings.

    Args:
        settings (dict): Settings to be used for agent execution.

    Returns:
        agent_setup (Runnable): The agent setup and configured tools.
    """
    agent_setup = None

    agent_manager_instance = AgentManager(settings=settings)
    logger.info("AgentManager configured with provided settings.")

    try:
        logger.info("Initializing agent and tools.")
        agent_setup = agent_manager_instance.initialize_agent()
        logger.info("Agent and tools initialized successfully.")
    except Exception as e:
        logger.error(f"Error during agent execution: {e}", exc_info=True)

    return agent_setup
