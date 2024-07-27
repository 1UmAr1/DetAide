import json
import os

from custom_logger import logger
from dotenv import load_dotenv
from langchain import hub
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

# Load environment variables from the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path)


def setup_model() -> object:
    """
    Initialize the large language model.


    Returns:
        llm_model (object): The initialized large language model.
    """
    try:
        model_settings_str = os.environ.get("MODEL_SETTINGS")
        if not model_settings_str:
            logger.error("MODEL_SETTINGS environment variable is not set.")
            raise ValueError("MODEL_SETTINGS environment variable is not set.")

        model_settings = json.loads(model_settings_str)
        llm_model = ChatOpenAI(
            model_name=model_settings.get("model_name"),
            streaming=model_settings.get("streaming"),
            callbacks=[StreamingStdOutCallbackHandler()],
            verbose=True
        )
        logger.info(f"Large language model initialized with model name: {model_settings.get('model_name')}")
        return llm_model
    except Exception as e:
        logger.error(f"Error setting up model: {str(e)}", exc_info=True)
        raise


# Initialize the model
model = setup_model()


def get_memory(session_id: str) -> object:
    """
    Retrieve conversational memory for a given session ID.

    Args:
        session_id (str): The session ID for which to retrieve memory.

    Returns:
        message_history (object): The message history object for the session ID.
    """
    try:
        message_history = RedisChatMessageHistory(
            url=os.environ.get("REDIS_URL"), ttl=600, session_id=session_id
        )
        logger.info(f"Message history setup for session ID: {session_id}")
        return message_history
    except Exception as e:
        logger.error(f"Error retrieving memory for session ID {session_id}: {str(e)}", exc_info=True)
        raise


def update_memory(session_id: str, new_message: BaseMessage) -> None:
    """
    Updates the conversational memory for a given session ID by appending a new message.

    Args:
        session_id (str): The session ID for which to update memory.
        new_message (BaseMessage): The new message object to add to the memory.

    Returns:
        None
    """
    try:
        # Create an instance of RedisChatMessageHistory with session ID
        message_history = RedisChatMessageHistory(
            session_id=session_id,
            url=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
            ttl=600  # Optional: Adjust TTL as required
        )
        # Append the new message to the Redis chat history
        message_history.add_message(new_message)
        logger.info(f"Memory updated for session ID {session_id} with new message.")

    except Exception as e:
        logger.error(f"Error updating memory for session ID {session_id}: {str(e)}", exc_info=True)
        raise


def fetch_prompt(prompt_id: str) -> ChatPromptTemplate:
    """
    Fetch a prompt from the Langchain hub.

    Args:
        prompt_id (str): The ID of the prompt to fetch.

    Returns:
        prompt (ChatPromptTemplate): The fetched prompt.
    """
    try:
        prompt = hub.pull(prompt_id)
        logger.info(f"Prompt fetched with ID: {prompt_id}")
        return prompt
    except Exception as e:
        logger.error(f"Error fetching prompt ID {prompt_id}: {str(e)}", exc_info=True)
        raise


def setup_es_vector_store(index_name: str) -> ElasticsearchStore:
    """
    Initialize the Elasticsearch vector store.

    Args:
        index_name (str): The name of the Elasticsearch index to use for the vector store.

    Returns:
        es_vector_store (object): The initialized Elasticsearch vector store.
    """
    try:
        embedding = OpenAIEmbeddings()
        elastic_vector_search = ElasticsearchStore(
            es_url=os.getenv("ES_URL"),
            index_name=index_name,
            embedding=embedding,
            strategy=ElasticsearchStore.ApproxRetrievalStrategy(hybrid=True, rrf=True)

        )
        return elastic_vector_search
    except Exception as e:
        logger.error(f"Error setting up Elasticsearch vector store: {str(e)}", exc_info=True)
        raise
