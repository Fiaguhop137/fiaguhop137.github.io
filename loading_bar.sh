#!/bin/bash
bar=("⣾" "⣽" "⣻" "⢿" "⡿" "⣟" "⣯" "⣷")
while true; do
    for i in {0..7}; do
        printf "$\r{bar[$i]} Loading..."
        sleep 0.125
    done
done
