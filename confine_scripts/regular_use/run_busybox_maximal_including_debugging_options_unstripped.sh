#!/bin/sh
start_time=$(date +%s)

bb="./busybox_maximal_including_debugging_options_unstripped"

while [ $(($(date +%s) - start_time)) -lt 300 ]; do
    $bb
    $bb ls
    $bb touch /tmp/test
    $bb cp /tmp/test /tmp/test2
    $bb rm /tmp/test
    $bb mv /tmp/test2 /tmp/test
    $bb mkdir /tmp/test_dir
    $bb rmdir /tmp/test_dir
    $bb ln -s /tmp/test /tmp/test_link
    $bb cat /tmp/test
    $bb head /tmp/test
    $bb tail /tmp/test
    $bb wc /tmp/test
    $bb df
    $bb du /tmp/test
    $bb echo "abc"
    $bb ps
    $bb ifconfig
    $bb ping -c 1 localhost
    $bb netstat
    $bb echo "abc" | $bb grep "a"
    $bb uname -r
    $bb uptime
    sleep 1
done