import datetime
from unittest import TestCase
import simplejson
from app.status_manager import StatusManager
from data_store.data_structure import ChargingStatus
from logger_init import get_logger

logger = get_logger(__name__)


class TestTimeBasedCharging(TestCase):
    def setUp(self) -> None:
        with open("./test_data/session_data.json", "r") as fh:
            self.test_data = simplejson.load(fh)

    def mock_get_current_session_data(self, a, b, c):
        return self.test_data

    def mock_set_current_session_data(self, a, b):
        self.assertEqual(a.data_to_update["current_charging_timer"], '00:02:00')

    def test_charging_started_first_check(self):
        """
        Test Case 1:
        Scenario:
        Charging has stared 1 minute before
        Current status is set as STARTED
        Monitor should mark it as in progress session with correct duration
        """
        current_time = datetime.datetime.utcnow()

        sample_start_time = (current_time - datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
        self.test_data["booking_time"] = sample_start_time
        self.test_data["start_time"] = sample_start_time
        self.test_data["current_status"] = "STARTED"

        # Mocking the functions so that we don't actually read or write from db
        StatusManager.get_current_booking_session_data = self.mock_get_current_session_data
        StatusManager.set_current_booking_session_data = self.mock_set_current_session_data
        self.monitor = StatusManager(self.test_data)

        result = self.monitor.check_current_session_data()
        self.assertEqual(result, ChargingStatus.IN_PROGRESS.value)

    def test_charging_in_progress(self):
        """
        Test Case 2:
        Scenario:
        Charging is in progress
        Current status is set as IN_PROGRESS
        Duration is under limit
        Monitor should maintain the status is in IN_PROGRESS
        """
        current_time = datetime.datetime.utcnow()

        sample_start_time = (current_time - datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
        self.test_data["booking_time"] = sample_start_time
        self.test_data["start_time"] = sample_start_time
        self.test_data["current_status"] = ChargingStatus.IN_PROGRESS.value
        self.test_data["target_duration_timestamp"] = "00:10:00"

        # Mocking the functions so that we don't actually read or write from db
        StatusManager.get_current_booking_session_data = self.mock_get_current_session_data
        StatusManager.set_current_booking_session_data = self.mock_set_current_session_data
        self.monitor = StatusManager(self.test_data)
        result = self.monitor.check_current_session_data()
        self.assertEqual(result, ChargingStatus.IN_PROGRESS.value)

    def test_charging_time_completed(self):
        """
        Test Case 2:
        Scenario:
        Charging is completed
        Current status is set as COMPLETED
        Duration is crossed
        Monitor should maintain the status is in COMPLETED
        """
        current_time = datetime.datetime.utcnow()

        sample_start_time = (current_time - datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
        self.test_data["booking_time"] = sample_start_time
        self.test_data["start_time"] = sample_start_time
        self.test_data["current_status"] = ChargingStatus.IN_PROGRESS.value
        self.test_data["target_duration_timestamp"] = "00:02:00"

        # Mocking the functions so that we don't actually read or write from db
        StatusManager.get_current_booking_session_data = self.mock_get_current_session_data
        StatusManager.set_current_booking_session_data = self.mock_set_current_session_data
        self.monitor = StatusManager(self.test_data)
        result = self.monitor.check_current_session_data()
        self.assertEqual(result, ChargingStatus.COMPLETED.value)

    def test_charging_in_progress_but_user_stopped_successfully(self):
        """
        Test Case 3:
        Scenario:
        Charging is in progress
        User Stopped Charging in between successfully
        Duration is still under limit
        Monitor should maintain the status is in COMPLETED
        """
        current_time = datetime.datetime.utcnow()

        sample_start_time = (current_time - datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
        self.test_data["booking_time"] = sample_start_time
        self.test_data["start_time"] = sample_start_time
        self.test_data["current_status"] = ChargingStatus.COMPLETED.value
        self.test_data["target_duration_timestamp"] = "00:10:00"
        self.test_data["user_stopped"] = True

        # Mocking the functions so that we don't actually read or write from db
        StatusManager.get_current_booking_session_data = self.mock_get_current_session_data
        StatusManager.set_current_booking_session_data = self.mock_set_current_session_data
        self.monitor = StatusManager(self.test_data)
        result = self.monitor.check_current_session_data()
        self.assertEqual(result, ChargingStatus.COMPLETED.value)

    def test_charging_in_progress_but_user_stopped_but_failed(self):
        """
        Test Case 4:
        Scenario:
        Charging is in progress
        User Stopped Charging in between but failed
        Duration is still under limit
        Monitor should maintain the status is in STOP_FAILED
        """
        current_time = datetime.datetime.utcnow()

        sample_start_time = (current_time - datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
        self.test_data["booking_time"] = sample_start_time
        self.test_data["start_time"] = sample_start_time
        self.test_data["current_status"] = ChargingStatus.STOP_FAILED.value
        self.test_data["target_duration_timestamp"] = "00:10:00"
        self.test_data["user_stopped"] = True

        # Mocking the functions so that we don't actually read or write from db
        StatusManager.get_current_booking_session_data = self.mock_get_current_session_data
        StatusManager.set_current_booking_session_data = self.mock_set_current_session_data
        self.monitor = StatusManager(self.test_data)
        result = self.monitor.check_current_session_data()
        self.assertEqual(result, ChargingStatus.STOP_FAILED.value)
