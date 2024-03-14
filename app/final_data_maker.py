from data_store.data_structure import ChargingStatus
from data_store.data_schemas import CollectiveDataForCurrentState, DataToUpdateInSessionTable, DataForLiveUpdate
from app.time_calculations import PrepareTimeDataForCurrentState
from abc import ABC, abstractmethod
from typing import Optional, Dict
from logger_init import get_logger

logger = get_logger(__name__)


class DataToReturn(ABC):
    """
    Represents an abstract class to implement a class to return final data to write in db
    """
    @abstractmethod
    def map_final_data(self, final_response: ChargingStatus) -> Dict:
        """Returns a dictionary with required data"""


class FinalDataToReturnForDB(DataToReturn):
    def __init__(self, collective_data_for_current_state, time_related_data_for_current_state):
        self.collective_data_for_current_state: CollectiveDataForCurrentState = collective_data_for_current_state
        self.time_related_data_for_current_state: PrepareTimeDataForCurrentState = time_related_data_for_current_state
        self.mapper = {
            ChargingStatus.TERMINATED.value: self.terminated_response,
            ChargingStatus.START_FAILED.value: self.start_failed_response,
            ChargingStatus.UNKNOWN_ERROR.value: self.unknown_error_response,
            ChargingStatus.PROGRESS_UPDATE_UNKNOWN.value: self.progress_update_unknown,
            ChargingStatus.BOOKED.value: self.charging_booked_response,
            ChargingStatus.STARTED.value: self.charging_started_response,
            ChargingStatus.IN_PROGRESS.value: self.charging_in_progress_response,
            ChargingStatus.USER_STOPPED.value: self.charging_stopped_by_user_response,
            ChargingStatus.COMPLETED.value: self.charging_completed_response,
            ChargingStatus.STOP_FAILED.value: self.stop_failed_response,
            ChargingStatus.REBOOKED.value: self.rebooked_response
        }

    def map_final_data(self, final_response):
        return self.mapper[final_response]()

    def _status_mapper(self, current_status):
        return DataToUpdateInSessionTable.parse_obj({
            "update_table": True,
            "table_name": "ChargingSessionRecords",
            "primary_key": {"booking_id": self.collective_data_for_current_state.booking_id},
            "sort_key": {"vendor_id": self.collective_data_for_current_state.vendor_id},
            "data_to_update": {
                "current_status": current_status,
                "current_energy_consumed": self.collective_data_for_current_state.session_data[
                    "current_energy_consumed"],
                "max_energy": self.collective_data_for_current_state.session_data["expanded_vehicle_data"]["power_capacity"],
                "current_charging_timer": self.time_related_data_for_current_state.current_duration.duration_as_time_stamp_string,
                "charging_states": DataForLiveUpdate.parse_obj(
                    self.collective_data_for_current_state.session_data).dict()
            }
        })

    def terminated_response(self):
        return self._status_mapper(current_status=ChargingStatus.TERMINATED.value)

    def start_failed_response(self):
        return self._status_mapper(current_status=ChargingStatus.START_FAILED.value)

    def unknown_error_response(self):
        return self._status_mapper(current_status=ChargingStatus.UNKNOWN_ERROR.value)

    def progress_update_unknown(self):
        return self._status_mapper(current_status=ChargingStatus.PROGRESS_UPDATE_UNKNOWN.value)

    def charging_booked_response(self):
        return self._status_mapper(current_status=ChargingStatus.BOOKED.value)

    def charging_started_response(self):
        return self._status_mapper(current_status=ChargingStatus.STARTED.value)

    def charging_in_progress_response(self):
        return self._status_mapper(current_status=ChargingStatus.IN_PROGRESS.value)

    def charging_stopped_by_user_response(self):
        return self._status_mapper(current_status=ChargingStatus.USER_STOPPED.value)

    def charging_completed_response(self):
        return self._status_mapper(current_status=ChargingStatus.COMPLETED.value)

    def stop_failed_response(self):
        return self._status_mapper(current_status=ChargingStatus.STOP_FAILED.value)

    def rebooked_response(self):
        return self._status_mapper(current_status=ChargingStatus.REBOOKED.value)

