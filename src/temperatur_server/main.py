from flask import Flask, render_template, request
from flask_socketio import SocketIO
from multiprocessing import Process, Queue
import time
import numpy as np
from measurement_parser import parse_string
from database import MeasurementDB

port = 5000
host = '127.0.0.1'

app = Flask(__name__,)
socketio = SocketIO(app)

q = Queue(maxsize=20)
database = MeasurementDB()

oven_ref_temp = 90.0
core_ref_temp = 64.0
start_time = time.time_ns()


@app.route("/input", methods=['POST'])
def receive_input():
    data = request.data
    data = request.get_data(as_text=True)
    new_sensor_data = parse_string(data)
    database.append(new_sensor_data)
    
    temp_1 = [new_sensor_data[0]["ts"],new_sensor_data[0]["value"] ]
    temp_2 = [new_sensor_data[1]["ts"],new_sensor_data[1]["value"] ]
    socketio.emit("new_temp_data",[temp_1,temp_2])
    return "Measurement Received"


@app.route('/')
def index():
    return render_template('index.html',oven_ref_temp=oven_ref_temp, core_ref_temp=core_ref_temp,start_time=start_time)

# SocketIO event Listener

@socketio.on("timer")
def timer_callback():
    curr_time = time.time_ns()
    temp_1 = [curr_time, np.random.uniform(10.0,100.0)]
    
    curr_time = time.time_ns()
    temp_2 = [curr_time, np.random.uniform(10.0,100.0)]
    #socketio.emit("new_temp_data",[temp_1,temp_2])
#     global output_trajectory, q, learned_trajectories
#     while not q.empty():
#         value = q.get(block=False)
#         output_trajectory = value[0]
#         learned_trajectories.append(value)
#         socketio.emit("new_learned_reward", [value[2], value[1]])

@socketio.on("getTimeSeries")
def getTimeSeries(date):
    print(start_time)
    return_value =  database.getBetweenTime(start_time-(10*60*1e9))
    return return_value

@socketio.on("newOvenRef")
def newOvenRef(data):
    global oven_ref_temp
    oven_ref_temp=data

@socketio.on("newCoreRef")
def newCoreRef(data):
    global core_ref_temp
    core_ref_temp=data

@socketio.on("newStartTime")
def newStarTime(data):
    global start_time
    start_time=int(data)

def main():
    socketio.run(app, port=port, host=host, debug=True)


if __name__ == "__main__":
    main()
