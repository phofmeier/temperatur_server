from time import sleep, time
import numpy as np
import requests
from oven_model import OvenModel
from meat_model import MeatModel
port = 5000
host = '192.168.2.106'
url = 'http://' + host + ":" + str(port) + "/input"
value_2 = 15.1
start_time = round(time() * 1e9)

oven_model = OvenModel()
heating = True
upper_temp = 55.0
lower_temp = 45.0
ambient_constant = 0.00001
heat_constant =0.0004
temp_ambient = 20.0
damping=0.010
oven_state = np.array([45.0, 0.0])

meat_model = MeatModel()
meat_state = np.ones(10) * 15.0 


for i in range(100000):
    oven_state, heating = oven_model.next_temp(oven_state,heating, upper_temp,lower_temp,ambient_constant,heat_constant,temp_ambient,damping,1.0)
last_timestamp_oven = start_time
last_timestamp_meat = start_time
for i in range(1000000):
    curr_time_mu_1 = round(time() * 1e9)
    oven_state, heating = oven_model.next_temp(oven_state,heating, upper_temp,lower_temp,ambient_constant,heat_constant,temp_ambient,damping,(curr_time_mu_1-last_timestamp_oven)*1e-9)

    value_1 = oven_state[0] + np.random.normal()*0.01
    curr_time_mu_2 = round(time() * 1e9)
    next_meat_state = meat_model.next_state(meat_state, value_1,7.2,(curr_time_mu_2 - last_timestamp_meat)* 1e-9)
    value_2 = next_meat_state[-1] + np.random.normal()*0.01
    send_string = f"Measurement,device=TempSens,Sensor=1 value={value_1} {curr_time_mu_1}\nMeasurement,device=TempSens,Sensor=2 value={value_2} {curr_time_mu_2}\n"
    x = requests.post(url, send_string)
    last_timestamp_oven = curr_time_mu_1
    last_timestamp_meat = curr_time_mu_2
    meat_state = next_meat_state

    print(x.text)
    sleep(0.99)
