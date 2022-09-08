import pandas as pd

class MeasurementDB:
    def __init__(self) -> None:
        self.db_1 = pd.DataFrame(columns=["ts", "name", "value"])
        self.db_2 = pd.DataFrame(columns=["ts", "name", "value"])
    def append(self, meas_data):
        self.db_1 = self.db_1.append(meas_data[0], ignore_index=True,sort=False)
        self.db_2 = self.db_2.append(meas_data[1], ignore_index=True,sort=False)

    def getBetweenTime(self, start, stop=None):
        start_time = pd.to_datetime(start)
        if stop is None:
            stop_time = None
        else:
            stop_time = pd.to_datetime(stop)
        temp_1_db = self.db_1.copy()
        temp_1_db["DateTime"] = pd.to_datetime(temp_1_db["ts"])
        temp_1_db = temp_1_db.set_index("DateTime")
        temp_1_db = temp_1_db[start_time : stop_time]

        temp_2_db = self.db_2.copy()
        temp_2_db["DateTime"] = pd.to_datetime(temp_2_db["ts"])
        temp_2_db = temp_2_db.set_index("DateTime")
        temp_2_db = temp_2_db[start_time:stop_time]
        temp_1_str = temp_1_db[["ts", "value"]].to_json(orient="values")
        temp_2_str = temp_2_db[["ts", "value"]].to_json(orient="values")
        
        return f"[{temp_1_str} , {temp_2_str} ]"
