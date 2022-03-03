#!/bin/bash

cd /app

. venv/bin/activate

./maildown.py $@
