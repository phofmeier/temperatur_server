import time

import pandas as pd


class MeasurementDB:
    def __init__(self) -> None:
        self.db_1 = pd.DataFrame(columns=["ts", "name", "value"])
        self.db_2 = pd.DataFrame(columns=["ts", "name", "value"])
        self.last_save_ts = 0.0
        self.db_name = time.strftime("%Y_%m_%d_%H_%M")

    def append(self, meas_data):
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

    def getBetweenTime(self, start, stop=None):
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

    def getInterpolBetweenTime(self, dt, start, stop=None):
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
        temp_1_db = temp_1_db["value"].resample(str(dt) + "s", origin=start).mean()

        temp_2_db = self.db_2.copy()
        temp_2_db["DateTime"] = pd.to_datetime(temp_2_db["ts"])
        temp_2_db = temp_2_db.set_index("DateTime")
        temp_2_db = temp_2_db[start_time:stop_time]
        temp_2_db = temp_2_db["value"].resample(str(dt) + "s", origin=start).mean()

        return [temp_1_db.to_list(), temp_2_db.to_list()]
