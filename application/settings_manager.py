import json
import os
import shutil

import redis
from custom_logger import logger
from dotenv import load_dotenv

# Path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
# Load environment variables from the .env file
load_dotenv(dotenv_path)

# Connect to Redis using the URL specified in the environment variables
redis_client = redis.Redis.from_url(os.environ.get("REDIS_SETTINGS_URL"), decode_responses=True)

# Local settings directory path
local_settings_dir = os.path.join(os.path.dirname(__file__), "settings")
if os.path.exists(local_settings_dir):
    shutil.rmtree(local_settings_dir)
    logger.info(f"Deleted settings folder at {local_settings_dir}.")


def fetch_settings(app_id: str) -> dict:
    """
    Fetch settings from Redis using the app_id as the key.

    Args:
        app_id (str): The ID of the application whose settings need to be fetched.

    Returns:
        dict: The settings for the specified app_id if found, otherwise an empty dict.
    """
    try:
        settings = redis_client.get(app_id)
        if settings:
            logger.debug(f"Settings retrieved for app_id={app_id}.")
            return json.loads(settings)
        else:
            logger.info(f"No settings found for app_id={app_id}. Returning empty dict.")
            return {}
    except Exception as e:
        logger.error(f"Failed to fetch settings for app_id={app_id}: {str(e)}", exc_info=True)
        return {}


def read_local_settings(app_id: str) -> dict | None:
    """
    Read the local last used settings for the specified app_id.

    Args:
        app_id (str): Application ID to fetch the settings for.

    Returns:
        dict | None: The last used settings if they exist, otherwise None.
    """
    settings_path = os.path.join(local_settings_dir, f"{app_id}", "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r") as file:
            return json.load(file)
    return None


def write_local_settings(app_id: str, settings: dict):
    """
    Write the last used settings locally for the specified app_id.

    Args:
        app_id (str): Application ID to store the settings for.
        settings (dict): Settings to store.
    """
    os.makedirs(os.path.join(local_settings_dir, app_id), exist_ok=True)
    settings_path = os.path.join(local_settings_dir, f"{app_id}", "settings.json")
    with open(settings_path, "w") as file:
        json.dump(settings, file)


def fetch_and_compare(app_id: str) -> dict | None:
    """
    Fetch settings from Redis and compare with the local last used settings.

    Args:
        app_id (str): The ID of the application whose settings need to be fetched and compared.

    Returns:
        dict | None: The settings if they have changed since last fetch, otherwise None.
    """
    try:
        current_settings_json = redis_client.get(app_id)
        if current_settings_json is None:
            logger.info(f"No settings found for app_id={app_id}.")
            return None

        current_settings = json.loads(current_settings_json)
        last_used_settings = read_local_settings(app_id)

        if last_used_settings is None or last_used_settings != current_settings:
            write_local_settings(app_id, current_settings)
            logger.debug(f"Settings changed or first-time fetch for app_id={app_id}. Returning settings.")
            return current_settings

        logger.debug(f"No changes detected for settings of app_id={app_id}.")
        return None
    except Exception as e:
        logger.error(f"Failed to fetch and compare settings for app_id={app_id}: {str(e)}", exc_info=True)
        return None


def upsert_settings(app_id: str, new_settings: dict):
    """
    Update or insert settings in Redis and update local last used settings.

    Args:
        app_id (str): The ID of the application whose settings need to be updated/inserted.
        new_settings (dict): The new settings to be stored.
    """
    try:
        settings_json = json.dumps(new_settings)
        redis_client.set(app_id, settings_json)
        write_local_settings(app_id, new_settings)
        logger.debug(f"Settings for app_id={app_id} updated successfully.")
    except Exception as e:
        logger.error(f"Failed to upsert settings for app_id={app_id}: {str(e)}", exc_info=True)
