#!/bin/sh
start_time=$(date +%s)

while [ $(($(date +%s) - start_time)) -lt 300 ]; do
    ./busybox_default_unstripped
    sleep 1
done