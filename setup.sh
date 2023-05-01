#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip3 install flask
mkdir instance
cp config.example.py instance/config.py
sed -i s/verysecretkey/`openssl rand -hex 30`/ instance/config.py
export FLASK_APP=competition
flask init-db
flask --debug run