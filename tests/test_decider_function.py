import datetime
from unittest import TestCase
import simplejson
from app.poller import ChargingSessionMonitor
from data_store.data_structure import ChargingStatus
from app.decision_making_functions import *
from logger_init import get_logger

logger = get_logger(__name__)


class TestDecideStrategyBeforeStart(TestCase):
    def setUp(self) -> None:
        self.start_time = None
        self.results = decider(self.start_time)
        self.expected_results = [check_booking_timeout.__name__,
                                 check_unknown_error.__name__,
                                 check_start_failure.__name__]

    def test_the_strategy_before_start_time(self):
        for result in self.results:
            self.assertIn(result.__name__, self.expected_results)


class TestDecideStrategyAfterStart(TestCase):
    def setUp(self) -> None:
        with open("./test_data/session_data.json", "r") as fh:
            self.test_data = simplejson.load(fh)
        self.start_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.expected_time_based_results = [check_successful_start.__name__, check_termination.__name__,
                                            check_unknown_error.__name__, check_user_interruption.__name__,
                                            check_time_based_status.__name__]
        self.expected_energy_based_results = [check_successful_start.__name__, check_termination.__name__,
                                              check_unknown_error.__name__, check_user_interruption.__name__,
                                              check_energy_based_status.__name__]

    def test_the_strategy_after_start_time_without_any_mode(self):
        results = decider(self.start_time)
        self.assertIsNone(results)

    def test_the_strategy_after_start_time_with_time_mode(self):
        results = decider(self.start_time, time_based=self.test_data["target_duration_timestamp"])
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIn(result.__name__, self.expected_time_based_results)

    def test_the_strategy_after_start_time_with_energy_mode(self):
        self.test_data["target_energy_kw"] = 25
        results = decider(self.start_time, energy_based=self.test_data["target_energy_kw"])
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIn(result.__name__, self.expected_energy_based_results)
