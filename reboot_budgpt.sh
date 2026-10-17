#!/bin/bash
pkill -f "python3 /home/firebot/git/random_bs/budgpt_backend.py"
while pgrep -f "python3 /home/firebot/git/random_bs/budgpt_backend.py" >/dev/null; do
    sleep 0.1
done
nohup python3 /home/firebot/git/random_bs/budgpt_backend.py > /home/firebot/git/random_bs/budgpt.log 2>&1 &
