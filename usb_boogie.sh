#!/bin/bash
# this script calls the boogie sync bluetooth python script,
# that connects to the boogie sync, reads the BT stream
# and generates evdev events to make the device act as a tablet.
# the python script is called with nohup so that it doesn't terminate
# when this caller closes. On exiting the caller, it sends the SIGUSR1
# signal to python, which catches that signal and closes cleanly.
# In this way the caller ensures that when the window is closed,
# the device is disconnected cleanly.

function exit_handler() {
	whoami
	echo "killing process ${PID}"
	kill -SIGUSR1 ${PID}
	rm -f /tmp/boogie.log
}

#set -x
whoami
nohup python3 /home/marc/LinuxSystemFiles/boogie/boogiesync-tablet/usb-driver.py > /tmp/boogie.log 2>&1 &
PID=$!
trap "exit_handler '${PID}'" SIGINT EXIT
sleep 5
# map to the LH monitor only
#IDNUM=$(xinput | grep boogie | cut -d '=' -f 2 | cut -d '	' -f 1)
IDNUM=$(xinput | grep boogie | awk '{ print $4 }' | cut -d '=' -f 2)
#echo "device id is ${IDNUM}"
if [ ! -z ${IDNUM} ]; then
	xinput map-to-output ${IDNUM} DVI-I-3
fi
# leave it running until we close
tail -f /tmp/boogie.log
