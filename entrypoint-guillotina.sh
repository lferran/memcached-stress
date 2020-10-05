#!/bin/bash
set -e

cd /usr/src/app
python3.7 config.py

echo "START GUILLOTINA SERVER"

exec "$@"
