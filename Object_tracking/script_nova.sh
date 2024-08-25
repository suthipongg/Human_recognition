#!/bin/bash

export 'PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512'
source ~/nova/venv/bin/activate

pm2 del service-python-object-tracking
pm2 start