""" Main implementation of the server.
"""
import time
from typing import List

from flask import Flask, render_template, request
from flask_socketio import SocketIO

from database.database import Measurement, MeasurementDB
from input.measurement_parser import parse_string
from models.predictor import PredictionInputData, Predictor
from temperatur_server.api.api_manager import ApiManager
from temperatur_server.server_state import ServerState

port = 5000
host = "0.0.0.0"

app = Flask(
    __name__,
)
socketio = SocketIO(app, cors_allowed_origins="*")

server_state = ServerState()
database = MeasurementDB()
predictor = Predictor(
    server_state.predictor_dt,
    server_state.predictor_oven_functions,
    server_state.predictor_meat_elements,
)
api_manager = ApiManager(server_state, database, socketio)


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
    api_manager.emit_all("new_temp_data", [temp_1, temp_2])
    result = predictor.maybe_get_result()
    if result is not None:
        api_manager.emit_all("new_prediction", [result.to_list()])
    if not predictor.is_running() and (
        (time.time_ns() - server_state.last_pushed) * 1e-9 > server_state.predictor_dt
    ):
        predictor.run_parallel(
            PredictionInputData(
                *database.getInterpolBetweenTime(
                    server_state.predictor_dt, server_state.start_time
                ),
                server_state.start_time,
                server_state.core_ref_temp,
            )
        )
        server_state.last_pushed = time.time_ns()


@app.route("/")
def index():
    return render_template("index.html")


def main():
    """Main function starting the server."""
    socketio.run(app, port=port, host=host, debug=True)


if __name__ == "__main__":
    main()
