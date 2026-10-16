#!/bin/bash
pkill -f "python3 budgpt_backend.py"
while pgrep -f "python3 budgpt_backend.py" >/dev/null; do
    sleep 0.1
done
nohup python3 budgpt_backend.py > /dev/null 2>&1 &
