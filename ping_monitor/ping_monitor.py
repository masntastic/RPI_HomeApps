import os
import time
import subprocess
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

# Set up logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_influxdb():
    """
    Initialize the InfluxDB client.
    Returns the client, write API, and bucket name.
    """
    # Replace these with your InfluxDB configuration
    url = "http://influxdb:8086"
    token = "my-token"
    org = "my-org"
    bucket = "my-bucket"

    # Initialize the InfluxDB client and write API
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    logging.info('Initialized InfluxDB client')
    return client, write_api, bucket

def ping_and_record(write_api, bucket):
    """
    Ping 8.8.8.8, parse results, and send fields/tags to InfluxDB.
    """
    host = os.getenv('HOST', 'raspberry-pi')  # Default to 'raspberry-pi' if not set
    target = '8.8.8.8'
    region = os.getenv('REGION', 'home')  # Optional, for multiple regions

    try:
        response = subprocess.run(['ping', '-c', '1', target], stdout=subprocess.PIPE)
        output = response.stdout.decode()

        if "1 packets transmitted, 1 received" in output:
            # Ping successful: parse latency
            latency = float(output.split('time=')[1].split(' ')[0])
            success = 1
            logging.info(f'Ping successful: latency {latency} ms')
        else:
            # Ping failed
            latency = float('inf')
            success = 0
            logging.warning('Ping failed: packet loss')

        # Create a point with tags and fields
        point = (
            Point("ping")
            .tag("host", host)
            .tag("target", target)
            .tag("region", region)
            .field("latency", latency)
            .field("success", success)
            .time(time.time_ns(), WritePrecision.NS)
        )

        # Write the data point to InfluxDB
        write_api.write(bucket=bucket, record=point)

    except Exception as e:
        logging.error(f"Error during ping: {e}")

def main():
    """
    Main function to initialize InfluxDB and start the ping loop.
    """
    logging.info('Starting the ping monitor script')

    # Initialize InfluxDB
    client, write_api, bucket = init_influxdb()

    # Ping loop: runs indefinitely, pinging every 5 seconds
    while True:
        ping_and_record(write_api, bucket)
        time.sleep(5)

if __name__ == "__main__":
    main()
