#!/bin/bash

export 'PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512'
source ~/nova/venv/bin/activate

python3 initial_system.py

pm2 del service-python-nova
pm2 del service-python-manage-queue
pm2 del service-python-tracking
pm2 start