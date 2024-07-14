FROM python:3.9

# Install ping utility
RUN apt-get update && apt-get install -y iputils-ping

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "ping_monitor.py"]
