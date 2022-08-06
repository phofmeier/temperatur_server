from flask import Flask, render_template
from flask_socketio import SocketIO
from multiprocessing import Process, Queue
import time
import numpy as np

port = 5000
host = '127.0.0.1'

app = Flask(__name__,)
socketio = SocketIO(app)

q = Queue(maxsize=20)




@app.route('/')
def index():
    return render_template('index.html')

# SocketIO event Listener

@socketio.on("timer")
def timer_callback():
    curr_time = time.time_ns()
    temp_1 = [curr_time, np.random.uniform(10.0,100.0)]
    
    curr_time = time.time_ns()
    temp_2 = [curr_time, np.random.uniform(10.0,100.0)]
    socketio.emit("new_temp_data",[temp_1,temp_2])
#     global output_trajectory, q, learned_trajectories
#     while not q.empty():
#         value = q.get(block=False)
#         output_trajectory = value[0]
#         learned_trajectories.append(value)
#         socketio.emit("new_learned_reward", [value[2], value[1]])


def main():
    socketio.run(app, port=port, host=host, debug=True)


if __name__ == "__main__":
    main()
