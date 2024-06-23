#!/bin/sh
start_time=$(date +%s)

while [ $(($(date +%s) - start_time)) -lt 300 ]; do
    ./busybox_maximal_including_debugging_options
    sleep 1
done