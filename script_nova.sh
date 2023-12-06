#!/bin/bash

python3 /app/initial_system.py

python3 /app/webserver_receive_img.py &
python3 /app/manage_queue_system.py &
python3 /app/object_tracking_system.py &

wait