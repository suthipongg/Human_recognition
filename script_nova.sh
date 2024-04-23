#!/bin/bash

python3 initial_system.py

python3 app.py &
python3 manage_queue_system.py &
python3 object_tracking_system.py &

wait