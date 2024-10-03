#!/bin/bash

source venv/bin/activate 

pm2 del nova-camera
pm2 del nova-stream
pm2 del nova-track
pm2 start
pm2 log nova-camera nova-stream nova-track