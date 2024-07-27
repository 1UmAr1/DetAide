import operator
from typing import TypedDict, Annotated, Any, Dict, Sequence

from custom_logger import logger
from langchain_core.messages import BaseMessage
from langchain_core.runnables.history import Runnable
from langgraph.graph import END, StateGraph

from graph_nodes import GraphNodes


class AgentState(TypedDict):
    """
    Typed dictionary for storing agent state within the workflow.

    Attributes:
    next (str): Identifier for the next node in the workflow.
    chat_history (list[BaseMessage]): List of BaseMessage objects representing the communication history.
    messages (Sequence[BaseMessage]): Sequence of messages, annotated with an operator for adding sequences.
    """
    next: str
    chat_history: list[BaseMessage]
    messages: Annotated[Sequence[BaseMessage], operator.add]


def graph_manager(graph_settings: Dict[str, Any]) -> Runnable:
    """
    Initializes and compiles a StateGraph based on provided settings to manage the workflow of agents.

    Args:
    graph_settings (Dict[str, Any]): A dictionary containing the settings required for initializing graph nodes.

    Returns:
    Runnable: A compiled StateGraph that can be executed as part of an application's workflow.
    """
    logger.debug("Initializing GraphNodes with settings.")
    try:
        # Initialize graph nodes with provided settings and AgentState type
        graph_nodes = GraphNodes(settings=graph_settings, agent_state=AgentState)
        nodes = graph_nodes.build_nodes()
        logger.debug("Creating StateGraph with AgentState type.")
        workflow = StateGraph(AgentState)

        logger.debug("Configuring the agent workflow.")
        # Define members involved in the workflow
        members = ["research_agent", "drafter_agent", "discriminator_agent", "agent_supervisor"]

        # Add each member as a node in the workflow
        for member in members:
            workflow.add_node(member, nodes[member])
        logger.debug("Adding edges to create the desired workflow.")
        # Connect nodes to the supervisor, excluding the supervisor itself
        for member in members:
            if member != "agent_supervisor":
                workflow.add_edge(member, "agent_supervisor")

        # Create a conditional map for workflow transitions
        conditional_map = {member: member for member in members if member != "agent_supervisor"}
        conditional_map["FINISH"] = END
        # Add conditional edges based on the 'next' attribute of the state
        workflow.add_conditional_edges("agent_supervisor", lambda x: x["next"], conditional_map)

        logger.debug("Setting the entry point for the workflow.")
        workflow.set_entry_point('agent_supervisor')
        logger.debug("Compiling the workflow.")
        # Compile the workflow into a runnable graph application
        graph_app = workflow.compile()
        logger.info("Workflow compiled successfully.")

    except Exception as e:
        # Log and re-raise exceptions encountered during graph initialization
        logger.error(f"Error: {e}", exc_info=True)
        raise e
    return graph_app
