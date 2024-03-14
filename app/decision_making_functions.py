from logger_init import get_logger
from data_store.data_structure import ChargingStatus
from app.time_calculations import PrepareTimeDataForCurrentState, CollectiveDataForCurrentState
from config import Settings

logger = get_logger(__name__)
settings = Settings()


def check_booking_timeout(collective_data_for_current_state: CollectiveDataForCurrentState,
                          time_related_data: PrepareTimeDataForCurrentState):
    """This Function will check the BOOKED state. If time is not elapsed it will not change anything in state"""
    current_status = collective_data_for_current_state.session_data["current_status"]
    if current_status == ChargingStatus.BOOKED.value:
        logger.info(f"Current statues is  {ChargingStatus.BOOKED.value} for the booking id "
                    f"{collective_data_for_current_state.booking_id}")
        if time_related_data.current_booking_duration.duration_delta.total_seconds() > settings.INITIAL_TIMEOUT_MINUTES.total_seconds():
            logger.info("Time has elapsed charge not started by user")
            return ChargingStatus.START_FAILED.value
        else:
            logger.info("Session is booked but not started by user")
            return current_status
    elif current_status == ChargingStatus.REBOOKED.value:
        logger.info("User has rebooked canceling this booking")
        return ChargingStatus.REBOOKED.value
    else:
        return None


def check_start_failure(collective_data_for_current_state: CollectiveDataForCurrentState,
                        time_related_data: PrepareTimeDataForCurrentState):
    if collective_data_for_current_state.session_data["current_status"] == ChargingStatus.START_FAILED.value:
        logger.info(f"Start attempted but failed for booking id {collective_data_for_current_state.booking_id}")
        return ChargingStatus.START_FAILED.value
    else:
        return None


def check_successful_start(collective_data_for_current_state: CollectiveDataForCurrentState,
                           time_related_data: PrepareTimeDataForCurrentState):
    if collective_data_for_current_state.session_data["current_status"] == ChargingStatus.STARTED.value:
        logger.info(f"Charging started successfully for booking id {collective_data_for_current_state.booking_id}. "
                    f"Marking the session as IN_PROGRESS")
        return ChargingStatus.IN_PROGRESS.value
    else:
        return None


def check_termination(collective_data_for_current_state: CollectiveDataForCurrentState,
                      time_related_data: PrepareTimeDataForCurrentState):
    current_status = collective_data_for_current_state.session_data["current_status"]
    if current_status == ChargingStatus.TERMINATED.value:
        logger.info(f"Session is terminated for {collective_data_for_current_state.booking_id} "
                    f"Keeping the state. We should got Final state now")
        return current_status
    else:
        return None


def check_unknown_error(collective_data_for_current_state: CollectiveDataForCurrentState,
                        time_related_data: PrepareTimeDataForCurrentState):
    current_status = collective_data_for_current_state.session_data["current_status"]
    if current_status == ChargingStatus.UNKNOWN_ERROR.value or current_status == ChargingStatus.PROGRESS_UPDATE_UNKNOWN.value:
        logger.info(f"Session is in unknown error state for {collective_data_for_current_state.booking_id} "
                    f"Keeping the state. We should got Final state now")
        return current_status
    else:
        return None


def check_user_interruption(collective_data_for_current_state: CollectiveDataForCurrentState,
                            time_related_data: PrepareTimeDataForCurrentState):
    current_status = collective_data_for_current_state.session_data["current_status"]
    user_stopped = collective_data_for_current_state.session_data["user_stopped"]
    if user_stopped and current_status == ChargingStatus.COMPLETED.value:
        logger.info(
            f"User has successfully stopped charging for booking id {collective_data_for_current_state.booking_id}. "
            f"returning completed. Go to final state")
        return ChargingStatus.COMPLETED.value
    elif user_stopped and current_status == ChargingStatus.STOP_FAILED.value:
        logger.info(f"User tried to stop charging for booking id {collective_data_for_current_state.booking_id}. "
                    f"but it failed. Maintaining state. Manage it in final state")
        return current_status
    else:
        return None


def check_time_based_status(collective_data_for_current_state: CollectiveDataForCurrentState,
                            time_related_data: PrepareTimeDataForCurrentState):
    total_seconds_elapsed = time_related_data.current_duration.duration_delta.total_seconds()
    if total_seconds_elapsed >= time_related_data.target_duration_delta.total_seconds():
        logger.info(f"Charging session is completed for booking id {collective_data_for_current_state.booking_id}")
        return ChargingStatus.COMPLETED.value
    elif total_seconds_elapsed < time_related_data.target_duration_delta.total_seconds():
        logger.info(f"Charging session is in progress for booking id {collective_data_for_current_state.booking_id}. "
                    f"Current duration is {total_seconds_elapsed}")
        return ChargingStatus.IN_PROGRESS.value
    else:
        return None


def check_energy_based_status(collective_data_for_current_state: CollectiveDataForCurrentState,
                              time_related_data: PrepareTimeDataForCurrentState):
    current_energy_consumed = int(collective_data_for_current_state.session_data["current_energy_consumed"])
    target_energy_kw = int(collective_data_for_current_state.target_energy_kw)

    if current_energy_consumed >= target_energy_kw:
        logger.info(f"Charging session is completed for booking id {collective_data_for_current_state.booking_id}")
        return ChargingStatus.COMPLETED.value
    elif current_energy_consumed < target_energy_kw:
        logger.info(f"Charging session is in progress for booking id {collective_data_for_current_state.booking_id}. "
                    f"Current energy consumed is {current_energy_consumed}")
        return ChargingStatus.IN_PROGRESS.value
    else:
        return None


def decider(start_time, time_based=None, energy_based=None) -> []:
    if not start_time:
        return [check_booking_timeout, check_start_failure, check_unknown_error]
    elif start_time and time_based:
        return [check_successful_start, check_termination, check_unknown_error, check_user_interruption,
                check_time_based_status]
    elif start_time and energy_based:
        return [check_successful_start, check_termination, check_unknown_error, check_user_interruption,
                check_energy_based_status]
    else:
        logger.info(f"No strategy found input data to factory was {start_time, time_based, energy_based}")
        return None
