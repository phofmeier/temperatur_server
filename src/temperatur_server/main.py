""" Main implementation of the server.
"""
import time
from typing import List

from flask import Flask, render_template, request
from flask_socketio import SocketIO

from database.database import Measurement, MeasurementDB
from input.measurement_parser import parse_string
from models.predictor import PredictionInputData, Predictor

port = 5000
host = "192.168.2.106"  # '127.0.0.1'

app = Flask(
    __name__,
)
socketio = SocketIO(app)

nano_seconds_before_start = 10 * 60 * 1e9
predictor_dt = 10.0
predictor_oven_functions = 10
predictor_meat_elements = 10
oven_ref_temp = 90.0
core_ref_temp = 64.0
start_time = time.time_ns()
last_pushed = start_time

database = MeasurementDB()
predictor = Predictor(predictor_dt, predictor_oven_functions, predictor_meat_elements)


@app.route("/input", methods=["POST"])
def receive_input():
    data = request.get_data(as_text=True)
    new_sensor_data = parse_string(data)
    cb_new_input_data(new_sensor_data)
    return "Measurement Received"


def cb_new_input_data(new_data: List[Measurement]):
    """Callback for new arrived input Measurements.

    Args:
        new_data (List[Measurement]): New Measurements.
    """
    database.append(new_data)
    temp_1 = (0, 0.0)
    temp_2 = (0, 0.0)
    # TODO: accept also messages with one new temp
    for data in new_data:
        if data["name"] == "1":
            temp_1 = (data["ts"], data["value"])
        elif data["name"] == "2":
            temp_2 = (data["ts"], data["value"])
    socketio.emit("new_temp_data", [temp_1, temp_2])
    global last_pushed, predictor
    result = predictor.maybe_get_result()
    if result is not None:
        socketio.emit("new_prediction", [result.to_list()])
    if not predictor.is_running() and (
        (time.time_ns() - last_pushed) * 1e-9 > predictor_dt
    ):
        predictor.run_parallel(
            PredictionInputData(
                *database.getInterpolBetweenTime(predictor_dt, start_time),
                start_time,
                core_ref_temp
            )
        )
        last_pushed = time.time_ns()


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("getTimeSeries")
def getTimeSeries(date):
    return_value = database.getBetweenTime(start_time - nano_seconds_before_start)
    return return_value


@socketio.on("getOvenRefTemp")
def getOvenRefTemp(date):
    return oven_ref_temp


@socketio.on("getCoreRefTemp")
def getCoreRefTemp(date):
    return core_ref_temp


@socketio.on("newOvenRef")
def newOvenRef(data):
    global oven_ref_temp
    oven_ref_temp = data


@socketio.on("newCoreRef")
def newCoreRef(data):
    global core_ref_temp
    core_ref_temp = data


@socketio.on("newStartTime")
def newStarTime(data):
    global start_time
    start_time = int(data)


@socketio.on("getStartTime")
def getStarTime(data):
    global start_time
    return start_time


def main():
    """Main function starting the server."""
    socketio.run(app, port=port, host=host, debug=True)


if __name__ == "__main__":
    main()
