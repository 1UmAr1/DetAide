from typing import List, Callable

from custom_logger import logger

from utils import setup_es_vector_store


class ElasticsearchIndexManager:
    """
    Manages index-related operations such as checking and updating
    the mapping/schema of an Elasticsearch index.
    """

    def __init__(self, es_store) -> None:
        self.es_store = es_store

    def field_exists_in_index(self, index_name: str, field_name: str) -> bool:
        """
        Checks if a given field exists in the index mapping.
        """
        try:
            current_mapping = self.es_store.get_mapping(index_name=index_name)
            properties = current_mapping.get(index_name, {}).get('mappings', {}).get('properties', {})
            return field_name in properties
        except Exception as e:
            logger.error(f"Error checking field existence in index: {e}", exc_info=True)
            return False

    def update_index_schema(self, index_name: str, field_name: str, field_type: str = "text") -> bool:
        """
        Updates the index schema by adding a new field to the mapping.
        """
        try:
            body = {
                "properties": {
                    field_name: {
                        "type": field_type
                    }
                }
            }
            self.es_store.put_mapping(index_name=index_name, body=body)
            logger.info(f"Schema updated: added field '{field_name}' to '{index_name}'")
            return True
        except Exception as e:
            logger.error(f"Error updating index schema: {e}", exc_info=True)
            return False


class ElasticsearchMemoryActions:
    """
    Performs requested actions (insert, delete, add, append, delete bulk, insert bulk)
    against an Elasticsearch index.
    """

    def __init__(self, es_store) -> None:
        self.es_store = es_store

    def insert(self, index_name: str, field_name: str, items: List[str]) -> str:
        """
        Inserts new items (each as a separate document) into the index.
        """
        try:
            for item in items:
                doc = {field_name: item}
                self.es_store.index_document(index_name=index_name, body=doc)
            return "Insert operation completed."
        except Exception as e:
            logger.error(f"Error inserting items: {e}", exc_info=True)
            return "Error inserting items."

    def delete(self, index_name: str, field_name: str, items: List[str]) -> str:
        """
        Deletes items from the index that match the specified field/value criteria.
        """
        try:
            # Optional optimization: batch multiple items into a single boolean query
            for item in items:
                query = {"query": {"match": {field_name: item}}}
                self.es_store.delete_by_query(index_name=index_name, body=query)
            return "Delete operation completed."
        except Exception as e:
            logger.error(f"Error deleting items: {e}", exc_info=True)
            return "Error deleting items."

    def add(self, index_name: str, field_name: str, items: List[str]) -> str:
        """
        'Add' operation, treated similarly to 'insert' for demonstration.
        """
        return self.insert(index_name, field_name, items)

    def append(self, index_name: str, field_name: str, items: List[str]) -> str:
        """
        'Append' operation, treated similarly to 'insert' for demonstration.
        """
        return self.insert(index_name, field_name, items)

    def insert_bulk(self, index_name: str, field_name: str, items: List[str]) -> str:
        """
        Bulk insert items using a single bulk API call.
        """
        try:
            docs = [
                {
                    "_op_type": "index",
                    "_index": index_name,
                    field_name: item
                }
                for item in items
            ]
            self.es_store.bulk_index(docs)
            return "Bulk insert operation completed."
        except Exception as e:
            logger.error(f"Error performing bulk insert: {e}", exc_info=True)
            return "Error performing bulk insert."

    def delete_bulk(self, index_name: str, field_name: str, items: List[str]) -> str:
        """
        Bulk delete items using delete_by_query for each item or combine into one query.
        """
        try:
            for item in items:
                query = {"query": {"match": {field_name: item}}}
                self.es_store.delete_by_query(index_name=index_name, body=query)
            return "Bulk delete operation completed."
        except Exception as e:
            logger.error(f"Error performing bulk delete: {e}", exc_info=True)
            return "Error performing bulk delete."


class MemoryTool:
    """
    A tool that manages storage and retrieval in Elasticsearch,
    functioning as a 'memory' by handling inserts, deletions, and schema updates.
    """

    def __init__(self, settings: dict) -> None:
        self.settings = settings
        self.prompt_id = self.settings.get("prompt_id")
        self.index_name = self.settings.get("index_name")

        # Create an Elasticsearch store.
        self.es_store = setup_es_vector_store(self.index_name)

        # Manager and action classes to keep responsibilities separated.
        self.index_manager = ElasticsearchIndexManager(self.es_store)
        self.actions = ElasticsearchMemoryActions(self.es_store)

        # Build a dictionary to map action strings to methods, removing large if/else blocks.
        self.action_map = {
            "insert": self.actions.insert,
            "delete": self.actions.delete,
            "add": self.actions.add,
            "append": self.actions.append,
            "delete bulk": self.actions.delete_bulk,
            "insert bulk": self.actions.insert_bulk
        }

        logger.debug("MemoryTool initialized with settings.")

    def memory_tool(self, action: str, items: List[str], location: str) -> str:
        """
        Executes memory operations in Elasticsearch.
        """
        logger.info(f"MemoryTool action='{action}', items='{items}', location='{location}'")

        if not self.index_manager.field_exists_in_index(self.index_name, location):
            logger.warning(
                f"Field '{location}' does not exist in index '{self.index_name}'. "
                "Prompting user to add the field..."
            )
            return "The field is not in Elasticsearch. Would you like me to add it?"

        return self._perform_memory_action(action.lower().strip(), items, location)

    def update_schema(self, location: str, field_type: str = "text") -> str:
        """
        Updates the schema of the index by adding a new field if the user agrees.
        """
        if self.index_manager.update_index_schema(self.index_name, location, field_type):
            logger.info("Schema update completed.")
            return "Task done."
        logger.error("Schema update failed.")
        return "Error updating schema."

    def _perform_memory_action(self, action: str, items: List[str], field_name: str) -> str:
        """
        Dispatches the requested action to the appropriate method in ElasticsearchMemoryActions.
        """
        method: Callable[[str, str, List[str]], str] = self.action_map.get(action)
        if not method:
            logger.error(f"Invalid action '{action}' requested.")
            return f"Error: Invalid action '{action}'."
        return method(self.index_name, field_name, items)
