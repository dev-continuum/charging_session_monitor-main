import datetime

from pydantic import BaseModel
from typing import Optional, Dict
from decimal import Decimal


class DataToUpdateInSessionTable(BaseModel):
    update_table: bool
    table_name: str
    primary_key: dict
    sort_key: dict
    data_to_update: dict


class DataForLiveUpdate(BaseModel):
    current_charging_timer: Optional[str] = None
    target_duration_timestamp: Optional[str] = None
    target_energy_kw: Optional[str] = None
    current_status: str
    emission_saved: Optional[str] = None
    battery_status: Optional[str] = None
    current_energy_consumed: Optional[str] = None
    current_range: Optional[str] = None
    max_energy: Optional[str] = None


class DurationCalculatorData(BaseModel):
    duration_delta: Optional[datetime.timedelta] = "00:00:00"
    duration_as_time_stamp_string: Optional[str] = None


class CollectiveDataForCurrentState(BaseModel):
    booking_id: str
    station_id: str
    vendor_id: str
    charger_point_id: str
    connector_point_id: str
    target_duration_timestamp: Optional[str] = None
    target_energy_kw: Optional[int] = None
    start_time: Optional[str] = None
    session_data: Dict
