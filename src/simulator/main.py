from time import sleep, time
import numpy as np
import requests
port = 5000
host = '127.0.0.1'
url = 'http://' + host + ":" + str(port) + "/input"
value_2 = 15.1

for i in range(10000):
    curr_time_mu_1 = round(time() * 1e6)
    value_1 = 10.0*np.sin(0.05*i)+90.1
    curr_time_mu_2 = round(time() * 1e6)
    value_2 = value_2 + 0.001 * (value_1 - value_2)
    send_string = f"Measurement,device=TempSens,Sensor=1 value={value_1} {curr_time_mu_1}\nMeasurement,device=TempSens,Sensor=2 value={value_2} {curr_time_mu_2}\n"
    x = requests.post(url, send_string)

    print(x.text)
    sleep(1)
