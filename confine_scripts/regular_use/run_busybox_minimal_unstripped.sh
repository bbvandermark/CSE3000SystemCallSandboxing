#!/bin/sh
start_time=$(date +%s)

while [ $(($(date +%s) - start_time)) -lt 300 ]; do
    ./busybox_minimal_unstripped
    sleep 1
done