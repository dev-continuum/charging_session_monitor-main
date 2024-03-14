import requests
from simplejson import JSONDecodeError
from config import Settings
from logger_init import get_logger

logger = get_logger(__name__)
settings = Settings()

def call_api(url, params=None, body=None):
    try:
        response = requests.post(url, params=params, json=body)
        parsed_response = response.json()
    except JSONDecodeError:
        logger.warning("Latest status collection failed")
        return {}
    else:
        logger.info(f"Returning current status {parsed_response}")
        return parsed_response