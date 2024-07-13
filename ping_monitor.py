import os
import time
import subprocess
from influxdb import InfluxDBClient

# InfluxDB settings
INFLUXDB_ADDRESS = 'influxdb'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DATABASE = 'ping'

# Ping settings
HOST = "8.8.8.8"
PING_INTERVAL = 5

def init_influxdb():
    client = InfluxDBClient(INFLUXDB_ADDRESS, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
    databases = client.get_list_database()
    if not any(db['name'] == INFLUXDB_DATABASE for db in databases):
        client.create_database(INFLUXDB_DATABASE)
    client.switch_database(INFLUXDB_DATABASE)
    return client

def ping(host):
    response = subprocess.run(['ping', '-c', '1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if response.returncode == 0:
        ping_time = float(response.stdout.decode().split('time=')[1].split(' ms')[0])
        return ping_time, 0
    else:
        return None, 1

def main():
    client = init_influxdb()
    while True:
        ping_time, packet_loss = ping(HOST)
        timestamp = int(time.time() * 1000000000)
        json_body = [
            {
                "measurement": "ping",
                "tags": {
                    "host": HOST
                },
                "time": timestamp,
                "fields": {
                    "response_time": ping_time,
                    "packet_loss": packet_loss
                }
            }
        ]
        client.write_points(json_body)
        time.sleep(PING_INTERVAL)

if __name__ == '__main__':
    main()
