from typing import Dict, Any

from custom_logger import logger
from langchain_core.messages import HumanMessage

from agent_factory import agent_manager
from graph_assembler import graph_manager
from utils import get_memory, update_memory

# Variable to hold the settings state across function calls
last_settings = None


def update_settings(settings: Dict[str, Any]) -> None:
    """
    Update and initialize the application settings with the provided dictionary.
    This function initializes various agents as per the settings and updates the application graph.

    Args:
    settings (Dict[str, Any]): A dictionary containing configuration settings for various agents and app components.
    """
    logger.debug("Initializing agent and tools with provided settings.")
    try:
        # Initialize agents with settings from the configuration
        research_agent = agent_manager(settings["research_agent"])
        discriminator_agent = agent_manager(settings["discriminator_agent"])
        drafter_agent = agent_manager(settings["drafter_agent"])

        # Update settings dictionary with initialized agents
        settings["research_agent"] = research_agent
        settings["discriminator_agent"] = discriminator_agent
        settings["drafter_agent"] = drafter_agent

        # Initialize graph with these updated settings
        settings["app"] = graph_manager(settings)

    except Exception as e:
        # Log any exceptions encountered during initialization
        logger.error(f"Error initializing agents: {e}", exc_info=True)
        return

    # Store the successfully updated settings globally for later use
    global last_settings
    last_settings = settings


def ast_driver(in_params: Dict[str, Any], settings: Dict[str, Any] = None) -> tuple:
    """
    Main driver function to process incoming parameters using application settings.
    This function handles initialization, message processing, and memory updates.

    Args:
    in_params (Dict[str, Any]): A dictionary containing input parameters like session ID and query.
    settings (Dict[str, Any], optional): A dictionary of settings that may override the last used settings.

    Returns:
    tuple: A tuple containing the result of processing and the status message.
    """
    # Default status for a successful operation
    status = "200 OK"
    global last_settings

    # Determine which settings to use: existing or newly provided
    if not settings:
        if last_settings is None:
            logger.error("No settings provided and no last settings available.")
            return "Initialization failed. No settings available.", "500 Internal Server Error"
        logger.debug("Reusing last settings.")
        settings = last_settings
    else:
        logger.debug("Updating settings.")
        update_settings(settings)

    # Retrieve the application instance from settings
    app = settings.get("app")
    if not app:
        logger.error("Application instance 'app' not found in settings.")
        return "Initialization failed. App not configured.", "500 Internal Server Error"

    try:
        # Retrieve chat history from memory based on session ID
        chat_history = get_memory(in_params["session_id"])
        result = app.invoke(
            {
                "messages": [
                    HumanMessage(content=in_params["query"])
                ],
                "chat_history": chat_history.messages
            }
        )

        # Log the successful execution of the driver function
        logger.info("Driver function executed successfully.")
        # Update the memory with the new message after processing
        update_memory(session_id=in_params["session_id"], new_message=result)

    except Exception as e:
        logger.error(f"Error With Ast Driver: {e}", exc_info=True)
        result = "Please Try Again! If the issue persists, contact support."
        status = "500 Internal Server Error"

    return result, status
