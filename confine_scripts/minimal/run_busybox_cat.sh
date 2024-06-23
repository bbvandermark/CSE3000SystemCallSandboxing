#!/bin/sh
start_time=$(date +%s)

while [ $(($(date +%s) - start_time)) -lt 300 ]; do
    echo "abc" | ./busybox_cat cat
    sleep 1
done