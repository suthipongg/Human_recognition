# For yolov8 requirement python version 3.8+
## install python3.8 first
1. sudo apt update
2. sudo apt install python3.8
3. sudo apt install python3-dev python3-venv python3-pip libopenblas-base libopenmpi-dev libomp-dev libopenblas-dev -y
4. mkdir Desktop/object_tracking & cd Desktop/object_tracking
5. python3 -m venv venv --system-site-packages
6. source venv/bin/activate
7. wget --quiet --show-progress --progress=bar:force:noscroll --no-check-certificate https://nvidia.box.com/shared/static/lufbgr3xu2uha40cs9ryq1zn4kxsnogl.whl -O torch-1.2.0-cp36-cp36m-linux_aarch64.whl
8. pip install -U pip
9. pip install Cython 'numpy<=1.24' torch-1.2.0-cp36-cp36m-linux_aarch64.whl
10. git clone --branch v0.13.0 https://github.com/pytorch/vision torchvision
11. cd torchvision
12. export BUILD_VERSION=0.13.0
13. python setup.py install --user
14. pip install ultralytics --no-cache-dir option

# install nvidia software through the sdkmanager by not flash

# Best Practices when using NVIDIA Jetson
1. Enable MAX Power Mode
`sudo nvpmodel -m 0`
2. Enable Jetson Clocks
`sudo jetson_clocks`
3. Install Jetson Stats Application
`
sudo apt update
sudo pip install jetson-stats
sudo reboot
jtop
`
4. add
`sudo apt-get install nvidia-jetpack`

### Don't `sudo apt upgrade`


add 
echo 'export PATH="/usr/local/cuda-10.2/bin:$PATH"' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH="/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH"' >> ~/.bashrc



1. sudo apt-get install python-pip python3-venv
3. pip install virtualenv
4. virtualenv --python=python3.6 myvenv
5. source myenv/bin/activate
5.1. pip install -U pip
6. pip install scipy pandas urllib3 numpy==1.19.4 gdown # numpy==1.19.5 will show Illegal instruction (core dumped)
7. sudo apt-get install -y libopenblas-base libopenmpi-dev
8. wget https://nvidia.box.com/shared/static/fjtbno0vpo676a25cgvuqc1wty0fkkg6.whl -O torch-1.10.0-cp36-cp36m-linux_aarch64.whl
9. pip install torch-1.10.0-cp36-cp36m-linux_aarch64.whl
10. sudo apt-get install libjpeg-dev zlib1g-dev libpython3-dev
11. sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
12. gdown https://drive.google.com/uc?id=1C7y6VSIBkmL2RQnVy8xF9cAnrrpJiJ-K
13. pip install torchvision-0.11.0a0+fa347eb-cp36-cp36m-linux_aarch64.whl
14. check torch and gpu `python -c "import torch; print(torch.cuda.is_available())"` if True go to next step
15. git clone https://github.com/amphancm/ultralytics.git
16. cd ultralytics/

python3 setup.py install
if have problem with ModuleNotFoundError: No module named 'skbuild'
pip install scikit-build
pip install opencv-python --verbose
reinstall pandas
reinstall matplotlib && seaborn
pip install urllib3==1.26.18 for solve SyntaxError: future feature annotations is not defined
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/aarch64-linux-gnu/' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:/usr/lib/python3.6/dist-packages/' >> ~/.bashrc
source ~/.bashrc
sudo apt-get update
sudo apt-get install libprotobuf-dev protobuf-compiler
cp -r /usr/lib/python3.6/dist-packages/tensorrt*
pip install onnx==1.9.0
pip install lap
pip install pafy

# install redis
1. sudo apt-get install lsb-release curl gpg
2. curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
3. sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
4. echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
5. sudo apt-get update
6. sudo apt-get install redis
7. test redis `redis-cli`
127.0.0.1:6379> ping
PONG 


# ubuntu 20
1. sudo apt install python3-dev python3-venv python3-pip 
2. mkdir Desktop/object_tracking & cd Desktop/object_tracking
3. python3 -m venv venv --system-site-packages
4. source venv/bin/activate
pip install -U pip
5. pip install ultralytics==8.2.92 onnx==1.16.2 redis
6. pip install numpy==1.23.1 pandas==1.4.4


sudo apt-get install curl -y
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install redis -y