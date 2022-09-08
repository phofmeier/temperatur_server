from time import sleep, time
import requests
port = 5000
host = '127.0.0.1'
url = 'http://' + host + ":" + str(port) + "/input"

for i in range(1000):
    curr_time_mu_1 = round(time() * 1e6)
    value_1 = (i+20.1) % 120
    curr_time_mu_2 = round(time() * 1e6)
    value_2 = (i+15.1) % 130
    send_string = f"Measurement,device=TempSens,Sensor=1 value={value_1} {curr_time_mu_1}\nMeasurement,device=TempSens,Sensor=2 value={value_2} {curr_time_mu_2}\n"
    x = requests.post(url, send_string)

    print(x.text)
    sleep(1)
