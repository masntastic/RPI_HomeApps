import logging
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time
import subprocess

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def init_influxdb():
    url = "http://influxdb:8086"
    token = "my-token"
    org = "my-org"
    bucket = "my-bucket"

    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    logging.info('Initialized InfluxDB client')
    return client, write_api, bucket

def main():
    logging.info('Starting the ping monitor script')
    client, write_api, bucket = init_influxdb()

    while True:
        try:
            logging.debug('Executing ping command')
            response = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.PIPE)
            output = response.stdout.decode()
            logging.debug(f'Ping output: {output}')
            if "1 packets transmitted, 1 received" in output:
                latency = float(output.split('time=')[1].split(' ')[0])
                point = Point("ping").field("latency", latency).time(time.time_ns(), WritePrecision.NS)
                write_api.write(bucket=bucket, record=point)
                logging.info(f'Ping successful: latency {latency} ms')
            else:
                point = Point("ping").field("latency", float('inf')).time(time.time_ns(), WritePrecision.NS)
                write_api.write(bucket=bucket, record=point)
                logging.warning('Ping failed: packet loss')
        except Exception as e:
            logging.error(f"Error: {e}")

        time.sleep(5)

if __name__ == "__main__":
    main()
