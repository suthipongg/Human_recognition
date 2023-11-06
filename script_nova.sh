#!/bin/bash

python3 /app/webserver_receive_img.py &
python3 /app/scripts/object_tracking_queue.py &

wait