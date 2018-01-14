#!/usr/bin/env bash
git clone https://github.com/kivy/buildozer
cd buildozer
python setup.py build
sudo pip install -e .
