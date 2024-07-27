import functools
from typing import Any, Dict

from custom_logger import logger
from langchain_core.messages import HumanMessage

from supervisor import AgentSupervisor


class GraphNodes:
    """
    A class to manage and configure nodes within a state graph based on provided settings.

    Attributes:
    settings (Dict[str, Any]): Configuration settings for different agents.
    agent_state (Type): The type of the agent state expected to be used throughout the nodes.
    """

    def __init__(self, settings: Dict[str, Any], agent_state) -> None:
        """
        Initializes the GraphNodes instance with settings and state type.

        Args:
        settings (Dict[str, Any]): A dictionary containing configurations for agents.
        agent_state (Type): A class or type defining the structure of the state to be used in nodes.
        """
        self.settings = settings
        self.research_agent = self.settings.get("research_agent")
        self.discriminator_agent = self.settings.get("discriminator_agent")
        self.drafter_tool = self.settings.get("drafter_agent")
        self.agent_supervisor = AgentSupervisor(settings=self.settings["Agent_Supervisor"])
        self.AgentState = agent_state
        logger.debug("GraphNodes initialized with settings and agent state.")

    def agent_nodes(self, state, agent, name):
        """
        Invokes an agent's functionality on a given state and wraps the output in a HumanMessage.

        Args:
        state (Any): The current state to pass to the agent.
        agent (Callable): The agent to invoke.
        name (str): The name of the agent being invoked.

        Returns:
        Dict: A dictionary containing a list of HumanMessage objects generated by the agent.
        """
        result = agent.invoke(state)
        return {"messages": [HumanMessage(content=result["output"], name=name)]}

    def build_nodes(self):
        """
        Constructs and returns a dictionary of partial functions configured as nodes for a state graph.

        Returns:
        Dict[str, Callable]: A dictionary mapping agent names to their respective node implementations.
        """
        # Creating partial functions to ensure correct agent and name are used without requiring re-specification
        research_node = functools.partial(self.agent_nodes, agent=self.research_agent, name="research_agent")
        discriminator_node = functools.partial(self.agent_nodes, agent=self.discriminator_agent,
                                               name="discriminator_agent")
        agent_supervisor_node = self.agent_supervisor.supervisor_chain
        drafter_node = functools.partial(self.agent_nodes, agent=self.drafter_tool, name="drafter_agent")

        # Returning a dictionary of agent nodes to be used in a state graph
        return {
            "research_agent": research_node,
            "discriminator_agent": discriminator_node,
            "agent_supervisor": agent_supervisor_node,
            "drafter_agent": drafter_node
        }
