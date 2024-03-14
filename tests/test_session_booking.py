import datetime
from unittest import TestCase
import simplejson
from app.status_manager import StatusManager
from data_store.data_structure import ChargingStatus
from logger_init import get_logger
from config import Settings

settings = Settings()

logger = get_logger(__name__)


class TestChargingSessionBooking(TestCase):
    def setUp(self) -> None:
        with open("./test_data/session_data.json", "r") as fh:
            self.test_data = simplejson.load(fh)

    def mock_get_current_session_data(self, a, b, c):
        return self.test_data

    def mock_set_current_session_data(self, a, b):
        print(a)
        self.assertEqual(a.data_to_update["current_charging_timer"], '00:00:00')

    def test_charging_booked_not_started_under_time_limit(self):
        """
        Test Case 1:
        Scenario:
       Charging session is booked but not started by user
       Its still under timeout limit
       Outcome: Maintain Booked State
        """
        current_time = datetime.datetime.utcnow()

        sample_booking_time = (current_time - datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
        self.test_data["booking_time"] = sample_booking_time
        self.test_data["start_time"] = None
        self.test_data["current_status"] = "BOOKED"

        # Mocking the functions so that we don't actually read or write from db
        StatusManager.get_current_booking_session_data = self.mock_get_current_session_data
        StatusManager.set_current_booking_session_data = self.mock_set_current_session_data
        self.monitor = StatusManager(self.test_data)

        result = self.monitor.check_current_session_data()
        self.assertEqual(result, ChargingStatus.BOOKED.value)

    def test_charging_booked_not_started_time_limit_crossed(self):
        """
        Test Case 1:
        Scenario:
       Charging session is booked but not started by user
       Its still under timeout limit
       Outcome: Maintain Booked State
        """
        current_time = datetime.datetime.utcnow()

        booking_time = (current_time - datetime.timedelta(minutes=6)).strftime('%Y-%m-%d %H:%M:%S')
        self.test_data["booking_time"] = booking_time
        self.test_data["start_time"] = None
        self.test_data["current_status"] = "BOOKED"

        # Mocking the functions so that we don't actually read or write from db
        StatusManager.get_current_booking_session_data = self.mock_get_current_session_data
        StatusManager.set_current_booking_session_data = self.mock_set_current_session_data
        self.monitor = StatusManager(self.test_data)

        result = self.monitor.check_current_session_data()
        self.assertEqual(result, ChargingStatus.TERMINATED.value)


