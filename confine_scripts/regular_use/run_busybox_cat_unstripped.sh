#!/bin/sh
start_time=$(date +%s)

while [ $(($(date +%s) - start_time)) -lt 300 ]; do
    echo "abc" | ./busybox_cat_unstripped cat
    ./busybox_cat_unstripped cat etc/environment
    sleep 1
done