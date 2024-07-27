import importlib

from custom_logger import logger
from langchain_core.tools import Tool


class ToolFactory:
    @staticmethod
    def load_module(module_name: str) -> object:
        """
        Loads a Python module dynamically based on its name.

        Args:
            module_name (str): The name of the module to load.

        Returns:
            object: The loaded module.
        """
        try:
            return importlib.import_module(module_name)
        except ImportError as e:
            logger.error(f"Could not import module '{module_name}': {str(e)}")
            raise ImportError(f"Could not import module '{module_name}': {str(e)}")

    @staticmethod
    def get_class_instance(module, class_name: str, settings: dict) -> object:
        """
        Retrieves an instance of a class from a module.

        Args:
            module: The module from which to retrieve the class.
            class_name (str): The name of the class to retrieve
            settings (dict): The settings to be used for the class instance.

        Returns:
            class_instance (object): The class instance.
        """
        try:
            class_instance = getattr(module, class_name)(settings=settings)
            logger.debug(f"Class instance '{class_name}' created successfully.")
            return class_instance
        except AttributeError:
            logger.error(f"Class '{class_name}' not found in module '{module.__name__}'.")
            raise ValueError(f"Class '{class_name}' not found in module '{module.__name__}'")

    @staticmethod
    def get_function(class_instance, function_name: str) -> object:
        """
        Retrieves a function from a class instance.

        Args:
            class_instance: The class instance from which to retrieve the function.
            function_name (str): The name of the function to retrieve.

        Returns:
            function (object): Retrieved Function.
        """
        if not hasattr(class_instance, function_name):
            logger.error(f"Function '{function_name}' not found in class '{class_instance.__class__.__name__}'")
            raise ValueError(f"Function '{function_name}' not found in class '{class_instance.__class__.__name__}'")
        function = getattr(class_instance, function_name)
        if not callable(function):
            logger.error(f"Attribute '{function_name}' is not callable.")
            raise TypeError(f"Attribute '{function_name}' is not callable")
        return function

    @staticmethod
    def initialize_tool(tool_config: dict) -> Tool:
        """
        Initializes a tool based on the provided configuration.

        Args:
            tool_config (dict): The configuration for the tool.

        Returns:
            Tool: The initialized tool.
        """
        module = ToolFactory.load_module(tool_config["module"])
        if 'class' in tool_config:
            class_instance = ToolFactory.get_class_instance(module, tool_config['class'], tool_config)
            function = ToolFactory.get_function(class_instance, tool_config['function'])
        else:
            function = getattr(module, tool_config['function'])
            if not callable(function):
                logger.error(f"Function '{tool_config['function']}' is not callable.")
                raise TypeError(f"Function '{tool_config['function']}' is not callable")
        logger.debug(f"Tool '{tool_config['name']}' initialized successfully.")
        return Tool.from_function(func=function, name=tool_config['name'], description=tool_config.get('description'))


def initialize_tools(settings: dict) -> list:
    """
    Initializes a list of tools based on the provided settings.

    Args:
        settings (dict): The settings to be used for tool initialization.

    Returns:
        tool_list (list): A list of initialized tools.
    """
    tools_list = []
    for tool_name, tool_config in settings["Tools"].items():
        try:
            tool = ToolFactory.initialize_tool(tool_config)
            tools_list.append(tool)
            logger.info(f"Tool {tool_name} initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing tool {tool_name}: {str(e)}")
    return tools_list
