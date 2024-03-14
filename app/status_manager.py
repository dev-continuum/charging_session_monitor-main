from logger_init import get_logger
from config import Settings
from json.decoder import JSONDecodeError
from dataclasses import dataclass
from app.poller import ChargingSessionMonitor
from typing import Dict
from app.api_caller import call_api
from app.decision_making_functions import decider
from app.time_calculations import PrepareTimeDataForCurrentState
from app.final_data_maker import FinalDataToReturnForDB
from exceptions.exception import DbFetchException, SocketException
from data_store.data_schemas import DataToUpdateInSessionTable, DataForLiveUpdate, CollectiveDataForCurrentState
import requests
import simplejson

logger = get_logger(__name__)
settings = Settings()


class SocketCommunicator:
    def __init__(self, socket_client, data_to_parse):
        self.socket_client = socket_client
        try:
            self.connection_id = data_to_parse["socket_connection_id"]
        except KeyError:
            raise SocketException(code=400, message="There is no connection id in the incoming data")
        self.parsed_data_to_send_on_socket = self.parse_data_for_live_update(data_to_parse)

    @staticmethod
    def parse_data_for_live_update(parsed_data):
        return DataForLiveUpdate.parse_obj(parsed_data).json()

    def send_message_to_socket(self):
        try:
            self.socket_client.post_to_connection(ConnectionId=self.connection_id,
                                                  Data=self.parsed_data_to_send_on_socket.encode("utf-8"))
        except Exception as e:
            raise SocketException(code=500, message="Unable to send data over socket")
        else:
            logger.info(f"Sent Live data on socket for id {self.connection_id}")


class StatusManager:
    def __init__(self, event):
        self.event_data = event
        # Call status api before fetching the current booking session details
        status_updated = call_api(settings.STATUS_URL, params={"booking_id": self.event_data["booking_id"],
                                                               "vendor_id": self.event_data["vendor_id"]},
                                  body={"expanded_vehicle_data": self.event_data["expanded_vehicle_data"]})
        self.session_data = self.get_current_booking_session_data(settings.DB_API, self.event_data["booking_id"],
                                                                  self.event_data["vendor_id"])
        # Taking start time data dynamically because initial data is passed at booking time
        # There will be no start time at that moment
        self.start_time = self.session_data["start_time"]

        self.collective_data_for_current_state = CollectiveDataForCurrentState(
            booking_id=self.event_data["booking_id"],
            station_id=self.event_data["station_id"],
            vendor_id=self.event_data["vendor_id"],
            charger_point_id=self.event_data["charger_point_id"],
            connector_point_id=self.event_data["connector_point_id"],
            target_duration_timestamp=self.event_data["target_duration_timestamp"],
            target_energy_kw=self.event_data["target_energy_kw"],
            start_time=self.start_time,
            session_data=self.session_data)

        self.time_related_data = PrepareTimeDataForCurrentState.parse_obj({"collective_data_for_current_state":
                                                                               self.collective_data_for_current_state})
        self.time_related_data.calculate_time_related_data()

        logger.info(f"Initializing ChargingSessionMonitor")
        self.poller = ChargingSessionMonitor(
            collective_data_for_current_state=self.collective_data_for_current_state,
            time_related_data=self.time_related_data,
            activities=decider(self.collective_data_for_current_state.start_time,
                               self.collective_data_for_current_state.target_duration_timestamp,
                               self.collective_data_for_current_state.target_energy_kw),
            final_data_decider=FinalDataToReturnForDB(self.collective_data_for_current_state, self.time_related_data))

    def get_current_booking_session_data(self, db_api, booking_id, vendor_id):
        try:
            response = requests.post(db_api,
                                     json={"read_table": True,
                                           "table_name": "ChargingSessionRecords",
                                           "primary_key": "booking_id",
                                           "primary_key_value": booking_id,
                                           "sort_key": "vendor_id",
                                           "sort_key_value": vendor_id
                                           })
        except Exception:
            logger.exception("Error while reading data from session table")
            raise DbFetchException(code=500, message="Not able to fetch data from db")
        else:
            try:
                parsed_response = response.json()
            except JSONDecodeError:
                logger.exception(f"Unable to parse fetched data for the booking id: "
                                 f"{booking_id}")
                raise DbFetchException(code=500, message="No data available in response")
            else:
                logger.debug(f"Response from reading table {parsed_response} for booking id "
                             f"{booking_id}")
                return parsed_response

    def check_current_session_data(self):
        data_to_update_db_and_return_status: DataToUpdateInSessionTable = self.poller.check_current_charging_status()
        try:
            self.set_current_booking_session_data(data_to_update_db_and_return_status, settings.DB_API)
        except DbFetchException:
            logger.exception("Unable to write data in session table")
            return data_to_update_db_and_return_status.data_to_update["current_status"]
        else:
            return data_to_update_db_and_return_status.data_to_update["current_status"]

    @staticmethod
    def set_current_booking_session_data(result_to_update: DataToUpdateInSessionTable, db_api):
        # update to session db
        try:
            response = requests.post(db_api,
                                     json=result_to_update.dict())
        except Exception:
            raise DbFetchException(code=500, message="Not able to update data to db")
        else:
            return response
