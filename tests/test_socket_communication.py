import datetime
from unittest import TestCase, skip
import simplejson
from app import get_socket_client
from app.status_manager import SocketCommunicator
from data_store.data_structure import ChargingStatus
from data_store.data_schemas import DataForLiveUpdate
from logger_init import get_logger

logger = get_logger(__name__)


@skip
class TestChargingStart(TestCase):
    def setUp(self) -> None:
        with open("./test_data/session_data.json", "r") as fh:
            self.test_json_data = simplejson.load(fh)
        self.test_json_data["start_time"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.test_json_data["current_status"] = "BOOKED"
        self.test_json_data["current_charging_timer"] = "00:10:00"
        self.socket_client = get_socket_client()
        self.socket_communicator = SocketCommunicator(self.socket_client, self.test_json_data)

    def test_send_data_to_socket(self):
        self.socket_communicator.send_message_to_socket()