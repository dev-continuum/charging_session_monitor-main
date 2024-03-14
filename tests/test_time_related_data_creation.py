import datetime
from unittest import TestCase
import simplejson
from app.time_calculations import PrepareTimeDataForCurrentState
from data_store.data_schemas import CollectiveDataForCurrentState
from data_store.data_structure import ChargingStatus
from logger_init import get_logger

logger = get_logger(__name__)


class TestTimeDataWithStartTimeNone(TestCase):
    def setUp(self) -> None:
        with open("./test_data/session_data.json", "r") as fh:
            self.test_data = simplejson.load(fh)
        self.collective_data_for_current_state = CollectiveDataForCurrentState.parse_obj({
            "booking_id": self.test_data["booking_id"],
            "station_id": self.test_data["station_id"],
            "vendor_id": self.test_data["vendor_id"],
            "charger_point_id": self.test_data["charger_point_id"],
            "connector_point_id": self.test_data["connector_point_id"],
            "target_duration_timestamp": self.test_data["target_duration_timestamp"],
            "target_energy_kw": self.test_data["target_energy_kw"],
            "start_time": "",
            "session_data": self.test_data
        })

    def test_prepare_time_related_data_without_start_time(self):
        time_related_class = PrepareTimeDataForCurrentState.parse_obj({"collective_data_for_current_state": self.collective_data_for_current_state})
        self.assertIsInstance(time_related_class, PrepareTimeDataForCurrentState)
        self.assertIsNone(time_related_class.iso_formatted_start_time)
        self.assertIsNone(time_related_class.target_duration_delta)
        self.assertIsNone(time_related_class.current_duration)


class TestTimeDataWithStartTimeSet(TestCase):
    def setUp(self) -> None:
        with open("./test_data/session_data.json", "r") as fh:
            self.test_data = simplejson.load(fh)
        current_time = datetime.datetime.utcnow()
        test_start_time = (current_time - datetime.timedelta(minutes=current_time.minute % 5 + 6,
                                                                          seconds=current_time.second,
                                                                          microseconds=current_time.microsecond)).strftime(
            '%Y-%m-%d %H:%M:%S')
        self.test_data["start_time"] = test_start_time
        self.collective_data_for_current_state = CollectiveDataForCurrentState.parse_obj({
            "booking_id": self.test_data["booking_id"],
            "station_id": self.test_data["station_id"],
            "vendor_id": self.test_data["vendor_id"],
            "charger_point_id": self.test_data["charger_point_id"],
            "connector_point_id": self.test_data["connector_point_id"],
            "target_duration_timestamp": self.test_data["target_duration_timestamp"],
            "target_energy_kw": self.test_data["target_energy_kw"],
            "start_time": test_start_time,
            "session_data": self.test_data
        })

    def test_prepare_time_related_data_with_start_time(self):
        time_related_class = PrepareTimeDataForCurrentState.parse_obj({"collective_data_for_current_state": self.collective_data_for_current_state})
        self.assertIsInstance(time_related_class, PrepareTimeDataForCurrentState)
        time_related_class.calculate_time_related_data()
        self.assertIsInstance(time_related_class.iso_formatted_start_time, datetime.datetime)
        self.assertIsInstance(time_related_class.target_duration_delta, datetime.timedelta)
        self.assertIsInstance(time_related_class.current_duration.duration_delta, datetime.timedelta)
        self.assertIsInstance(time_related_class.current_duration.duration_as_time_stamp_string, str)
