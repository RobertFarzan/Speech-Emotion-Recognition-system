#!/bin/bash

sudo apt-get update
sudo apt-get install python3.8-dev -y
sudo apt install libpython3.8-dev -y
sudo apt-get install python3.8-venv -y
sudo apt-get install python3-pip -y
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 -y

#pip3 install virtualenv
#virtualenv -p python3 venv
python3.8 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

export PYTHONPATH="$PWD/src"
