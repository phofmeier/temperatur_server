"""Database implementation.
"""

import time
from typing import List, Optional, Tuple, TypedDict, Union

import pandas as pd


class Measurement(TypedDict):
    """Typed Dictionary for one measurement."""

    ts: int
    name: str
    value: float


class MeasurementDB:
    """Measurement Database.

    Saving, loading and preprocessing of measurement data.
    The data is saved as csv files.
    """

    def __init__(self) -> None:
        """Initialize the database."""
        self.db_1 = pd.DataFrame(columns=["ts", "name", "value"])
        self.db_2 = pd.DataFrame(columns=["ts", "name", "value"])
        self.last_save_ts = 0.0
        self.db_name = time.strftime("%Y_%m_%d_%H_%M")

    def append(self, meas_data: List[Measurement]) -> None:
        """Append measurements to the database.

        The measurement are added to the database.

        Args:
            meas_data (List[Measurement]): List of measurements to append.
        """
        for data in meas_data:
            if data["name"] == "1":
                self.db_1 = pd.concat(
                    [self.db_1, pd.DataFrame(data, index=[0])], ignore_index=True
                )
            elif data["name"] == "2":
                self.db_2 = pd.concat(
                    [self.db_2, pd.DataFrame(data, index=[0])], ignore_index=True
                )
        if time.time() > self.last_save_ts + 60.0:
            self.last_save_ts = time.time()
            self.db_1.to_csv("./data/" + self.db_name + "_db_1.csv")
            self.db_2.to_csv("./data/" + self.db_name + "_db_2.csv")

    def getBetweenTime(self, start: str, stop: Optional[str] = None) -> str:
        """Get all data between two timepoints.

        Return all data from start time to stop time as a string.
        If stop is none up to the latest data is returned

        Args:
            start (str): start time
            stop (str, optional): stop time. Defaults to None.

        Returns:
            str: containing all data
        """
        self.db_1.sort_values(by="ts", ascending=True, inplace=True)
        self.db_2.sort_values(by="ts", ascending=True, inplace=True)
        start_time = pd.to_datetime(start)
        if stop is None:
            stop_time = None
        else:
            stop_time = pd.to_datetime(stop)
        temp_1_db = self.db_1.copy()
        temp_1_db["DateTime"] = pd.to_datetime(temp_1_db["ts"])
        temp_1_db = temp_1_db.set_index("DateTime")
        temp_1_db = temp_1_db[start_time:stop_time]

        temp_2_db = self.db_2.copy()
        temp_2_db["DateTime"] = pd.to_datetime(temp_2_db["ts"])
        temp_2_db = temp_2_db.set_index("DateTime")
        temp_2_db = temp_2_db[start_time:stop_time]
        temp_1_str = temp_1_db[["ts", "value"]].to_json(orient="values")
        temp_2_str = temp_2_db[["ts", "value"]].to_json(orient="values")

        return f"[{temp_1_str} , {temp_2_str} ]"

    def getInterpolBetweenTime(
        self, dt: float, start: Union[str, int], stop: Optional[str] = None
    ) -> Tuple[List[float], List[float]]:
        """Get data between to timepoints interpolated to a uniform timegrid.

        The data between start and stop is interpolated to a uniform time grid
        with a specific time delta.
        If no stop time is specified up to the latest data is returned.

        Args:
            dt (float): time difference of the uniform grid.
            start (str): start time.
            stop (str, optional): stop time. Defaults to None.

        Returns:
            List[List[float], List[float]]: First and second measurements.
        """
        self.db_1.sort_values(by="ts", ascending=True, inplace=True)
        self.db_2.sort_values(by="ts", ascending=True, inplace=True)
        start_time = pd.to_datetime(start)
        if stop is None:
            stop_time = None
        else:
            stop_time = pd.to_datetime(stop)
        temp_1_db = self.db_1.copy()
        temp_1_db["DateTime"] = pd.to_datetime(temp_1_db["ts"])
        temp_1_db = temp_1_db.set_index("DateTime")
        temp_1_db = temp_1_db[start_time:stop_time]
        temp_1_db = (
            temp_1_db["value"]
            .resample(pd.to_timedelta(dt, unit="s"), origin=start)
            .mean()
        )

        temp_2_db = self.db_2.copy()
        temp_2_db["DateTime"] = pd.to_datetime(temp_2_db["ts"])
        temp_2_db = temp_2_db.set_index("DateTime")
        temp_2_db = temp_2_db[start_time:stop_time]
        temp_2_db = (
            temp_2_db["value"]
            .resample(pd.to_timedelta(dt, unit="s"), origin=start)
            .mean()
        )

        return temp_1_db.to_list(), temp_2_db.to_list()
