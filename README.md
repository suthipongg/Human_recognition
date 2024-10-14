# install ubuntu 20
1. [download image ](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image?tab=readme-ov-file#tip) and flash by use balenaEtcher (username: nano, password: jetson)
2. install gpart with command: `sudo apt-get install gparted -y` and [Expand the image to larger SD cards](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image?tab=readme-ov-file#tip)  (minimum SDCard storage = 64GB)

ref: https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image?tab=readme-ov-file#tip

# Best Practices when using NVIDIA Jetson
1. Enable MAX Power Mode
`sudo nvpmodel -m 0`
2. Enable Jetson Clocks
`sudo jetson_clocks`

### Don't `sudo apt upgrade`

# define cuda apth
``` bash
echo 'export PATH="/usr/local/cuda-10.2/bin:$PATH"' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH="/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH"' >> ~/.bashrc
```

# install redis
1. sudo apt-get install lsb-release curl gpg -y
2. curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
3. sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
4. echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
5. sudo apt-get update
6. sudo apt-get install redis -y
7. test redis command `redis-cli`
    ```
    127.0.0.1:6379> ping
    PONG 
    ```

# install pm2
ref: https://pm2.io/docs/runtime/guide/installation/

# install crontab
ref: https://www.uptimia.com/questions/how-to-install-crontab-in-ubuntu

# Get start
1. sudo apt install python3-dev python3-venv python3-pip -y
2. cd Desktop
3. git clone https://github.com/suthipongg/Object_tracking.git
4. cd Object_tracking
5. git checkout -b nvidia_jetson
6. python3 -m venv venv --system-site-packages
7. source venv/bin/activate
8. pip install -U pip
9. pip install -r requirements.txt

# Model
use yolov8n
1. copy yolov8n.engine & yolov8n.onnx into Object_tracking github location is Object_tracking/weights
2. if don't have yolov8n.engine & yolov8n.onnx file run the command `python3 scripts/convert_pt2rt.py` or `python3 scripts/convert_pt2rt_int8.py` (if want to quantize to int8) and then save yolov8n.engine & yolov8n.onnx

# test tracking
1. cd Object_tracking
2. python3 scripts/demo.py
3. press 'q' to stop record video and wait a minute to compute tracking then result will save in reult folder named as <timestamp>_result.py

# Run
1. cd Object_tracking
2. `bash start_pm2.sh`

# Start/Stop pm2 service period
1. crontab -e
2. set time 9:00 - 13:00
```
0 9 * * * pm2 start yourappname
0 13 * * * pm2 stop yourappname
```