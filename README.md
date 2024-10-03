# install ubuntu 20
1. [download image ](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image?tab=readme-ov-file#tip)
2. [Expand the image to larger SD cards](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image?tab=readme-ov-file#tip)  (minimum SDCard storage = 64GB)

ref: https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image?tab=readme-ov-file#tip

# Best Practices when using NVIDIA Jetson
1. Enable MAX Power Mode
`sudo nvpmodel -m 0`
2. Enable Jetson Clocks
`sudo jetson_clocks`

# install nvidia software through the sdkmanager by not flash
1. Install Jetson Stats Application
`
sudo apt update
sudo pip install jetson-stats -y
sudo reboot
jtop
`
2. add
`sudo apt-get install nvidia-jetpack`

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

# Get start
1. sudo apt install python3-dev python3-venv python3-pip 
2. mkdir Desktop/object_tracking & cd Desktop/object_tracking
3. python3 -m venv venv --system-site-packages
4. source venv/bin/activate
5. pip install -U pip
6. git clone https://github.com/suthipongg/Object_tracking.git
7. cd Object_tracking
8. git checkout -b nvidia_jetson
6. pip install -r requirements.txt