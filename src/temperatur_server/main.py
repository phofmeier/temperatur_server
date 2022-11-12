""" Main implementation of the server.
"""
import time
import traceback
from multiprocessing import Process, Queue

import numpy as np
from flask import Flask, render_template, request
from flask_socketio import SocketIO

from database.database import MeasurementDB
from input.measurement_parser import parse_string
from models.predictor import Predictor

port = 5000
host = "192.168.2.106"  # '127.0.0.1'

app = Flask(
    __name__,
)
socketio = SocketIO(app)

data_queue = Queue(maxsize=1)  # type: ignore
result_queue = Queue(maxsize=1)  # type: ignore
database = MeasurementDB()

oven_ref_temp = 90.0
core_ref_temp = 64.0
start_time = time.time_ns()
got_result = True
last_pushed = start_time


@app.route("/input", methods=["POST"])
def receive_input():
    data = request.get_data(as_text=True)
    new_sensor_data = parse_string(data)
    database.append(new_sensor_data)
    temp_1 = 0
    temp_2 = 0
    for data in new_sensor_data:
        if data["name"] == "1":
            temp_1 = [data["ts"], data["value"]]
        elif data["name"] == "2":
            temp_2 = [data["ts"], data["value"]]
    socketio.emit("new_temp_data", [temp_1, temp_2])
    global data_queue, result_queue, got_result, last_pushed
    if (
        data_queue.empty()
        and got_result
        and ((time.time_ns() - last_pushed) * 1e-9 > 10.0)
    ):

        data_queue.put(
            database.getInterpolBetweenTime(10, start_time)
            + [start_time]
            + [core_ref_temp]
        )
        got_result = False
        last_pushed = time.time_ns()
    if result_queue.full():
        result = result_queue.get()
        socketio.emit("new_prediction", [result])
        got_result = True

    return "Measurement Received"


@app.route("/")
def index():
    return render_template(
        "index.html",
        oven_ref_temp=oven_ref_temp,
        core_ref_temp=core_ref_temp,
        start_time=start_time,
    )


@socketio.on("getTimeSeries")
def getTimeSeries(date):
    return_value = database.getBetweenTime(start_time - (10 * 60 * 1e9))
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


def predictor(data_queue, result_queue):
    dt = 10.0

    while True:
        predictor = Predictor()
        try:

            data = data_queue.get()
            start_time = data[2]
            oven_params, meat_params = predictor.fit(data[0], data[1])
            oven_temp, meat_state, duration_to_end = predictor.predict(data[3])
            t_fit = start_time + np.array(
                range(len(meat_params[1])), dtype=np.int
            ) * int(dt * 1e9)
            t_pred = t_fit[-1] + np.array(range(len(oven_temp)), dtype=np.int) * int(
                dt * 1e9
            )
            t_oven = np.array(range(len(meat_params[1])), dtype=float) * dt
            t_end = start_time + int(duration_to_end * 1e9)
            oven_fit = []
            for i in range(t_oven.shape[0]):
                oven_fit.append(
                    predictor._oven_est._model.func(t_oven[i], *oven_params)
                )

            result = [
                t_fit.tolist(),
                oven_fit,
                meat_params[1].tolist(),
                t_pred.tolist(),
                oven_temp,
                meat_state,
                t_end,
            ]

            result_queue.put(result)

        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            traceback.print_exc()
            time.sleep(10)


def main():
    """Main function starting the server."""
    global data_queue, result_queue

    p = Process(
        target=predictor,
        args=(
            data_queue,
            result_queue,
        ),
        daemon=True,
    )
    p.start()

    socketio.run(app, port=port, host=host, debug=True)


if __name__ == "__main__":
    main()
