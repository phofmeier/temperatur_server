from time import time


def parse_string(data: str):
    temp_list = str(data).strip().split("\n")
    new_sensor_data = []
    for sensor_data in temp_list:
        sensor_data_splitted = sensor_data.split(" ")
        sensor_name = ""
        sensor_value = 0.0
        if len(sensor_data_splitted) > 2:
            sensor_ts = int(sensor_data_splitted[-1])
        else:
            sensor_ts = round(time() * 1e9)
        for sensor_data_values in sensor_data_splitted:
            if sensor_data_values.startswith("value"):
                sensor_value = float(sensor_data_values.split("value=")[1])
            if sensor_data_values.startswith("Measurement,device=TempSens,Sensor="):
                sensor_name = sensor_data_values.split(
                    "Measurement,device=TempSens,Sensor="
                )[1]
        new_sensor_data.append(
            {"name": sensor_name, "value": sensor_value, "ts": sensor_ts}
        )

    return new_sensor_data
