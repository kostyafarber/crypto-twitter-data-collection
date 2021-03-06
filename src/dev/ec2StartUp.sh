#!/bin/bash

# installs pip
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user

# install needed packages
#pip3 install python-binance
pip3 install websocket-client
pip3 install pandas
pip3 install boto3
sudo yum install tmux -y

# make locations
mkdir crypto-data
cd crypto-data