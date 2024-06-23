#!/bin/sh

start_time=$(date +%s)

while [ $(($(date +%s) - start_time)) -lt 300 ]; do
    echo "abc" | ./cat
    sleep 1
done