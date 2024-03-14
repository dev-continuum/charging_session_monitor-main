import simplejson
from app.status_manager import StatusManager, SocketCommunicator
from data_store.data_structure import ChargingStatus
from exceptions.exception import SocketException
from app import get_socket_client
from logger_init import get_logger

logger = get_logger(__name__)


def lambda_handler(event, context):
    try:
        logger.info(f"Passing this event to status manager {event}")
        status_manager = StatusManager(event)
        result = status_manager.check_current_session_data()
    except Exception:
        logger.exception("Status manager is not able to check current session data")
        return ChargingStatus.TERMINATED
    else:
        try:
            socket_comm = SocketCommunicator(get_socket_client(), status_manager.session_data)
            socket_comm.send_message_to_socket()
        except SocketException:
            logger.exception("Unable to send data on socket but we will continue the state machine")
            return result
        else:
            return result
