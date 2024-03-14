from dataclasses import dataclass
from app.time_calculations import PrepareTimeDataForCurrentState
from app.final_data_maker import FinalDataToReturnForDB
from data_store.data_schemas import CollectiveDataForCurrentState
from app.decision_making_functions import decider
from typing import Optional, Dict, Callable, List
from logger_init import get_logger
import datetime

logger = get_logger(__name__)


@dataclass
class ChargingSessionMonitor:
    time_related_data: PrepareTimeDataForCurrentState
    collective_data_for_current_state: CollectiveDataForCurrentState
    activities: List
    final_data_decider: FinalDataToReturnForDB

    def check_current_charging_status(self):
        results = []
        for activity in self.activities:
            logger.info(f"Performing activity {activity}")
            results.append(activity(self.collective_data_for_current_state, self.time_related_data))
        logger.info(f"Final results after all activities are {results}")
        result = [result for result in results if result is not None][0]
        logger.info(f"Final selected result is {result}. Passing it to prepare final data")
        return self.final_data_decider.map_final_data(result)
