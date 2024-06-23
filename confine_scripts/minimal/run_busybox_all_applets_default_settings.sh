#!/bin/sh
start_time=$(date +%s)

while [ $(($(date +%s) - start_time)) -lt 300 ]; do
    ./busybox_all_applets_default_settings
    sleep 1
done