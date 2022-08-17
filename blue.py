#!/usr/bin/env python3
from evdev import UInput, AbsInfo, ecodes as e
from bluetooth import *
from time import sleep
import signal  # catch signal from caller to terminate cleanly
import sys

if sys.version < '3':
    input = raw_input

addr = None

if len(sys.argv) < 2:
    print("No device specified.  Searching all nearby bluetooth devices for")
    print("the boogie board sync input")
    print("using default 'A0:E6:F8:A0:FA:95'")
    addr = 'A0:E6:F8:A0:FA:95'
else:
    addr = sys.argv[1]
    print("Searching for boogie board sync on %s" % addr)

# search for the boogie service
uuid = "d6a56f80-88f8-11e3-baa8-0800200c9a66"
service_matches = find_service( uuid = uuid, address = addr )

if len(service_matches) == 0:
    print("couldn't find the boogie board sync")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \"%s\" on %s, port %s" % (name, host, port))

# Create the client socket
sock=BluetoothSocket( RFCOMM )
sock.connect((host, port))
#sock.settimeout(5)

print("connected")
# the following strings are correct but aren't interpreted correctly by python3
#resp = '\xc0\x00\x00\xb8\xf0\xc0'
# instead we need to explicitly convert them to byte array as such:
resp = bytes.fromhex('c00000b8f0c0')
#payload = '\xc0\x00\x53\x05\x05\x00\x04\x10\x71\xc0'
payload = bytes.fromhex('c00053050500041071c0')
print("sending payload")
sock.send(payload)
#payload = '\xc0'
payload = bytes.fromhex('c0')
sock.send(payload)
print("receiving response")
data = sock.recv(1024)
print("received response ",resp)
if resp == data:
    print("good response")
    sock.send(payload)
else:
    print("bad response, exit")
    sys.exit(1)

# Configure UInput device
# Maximum position possible
minxpos = 60
minypos = 135
maxxpos = 19993
maxypos = 13847
minpressure = 0 # 19
#maxpressure = 255    # the device seems to support 1024 levels of pressure,
maxpressure = 1024    # so not sure why this was set to 255 previously.


# Initialise UInput device
cap = {
    e.EV_KEY : (e.BTN_TOUCH, e.BTN_STYLUS2),
    e.EV_ABS : [
        (e.ABS_PRESSURE, AbsInfo(value=minpressure, max=maxpressure, min=0, fuzz=0, flat=0, resolution=0)),
        (e.ABS_X, AbsInfo(value=minxpos, max=maxxpos, min=0, fuzz=0, flat=0, resolution=0)),
        (e.ABS_Y, AbsInfo(value=minypos, max=maxypos, min=0, fuzz=0, flat=0, resolution=0))]
}
ui = UInput(cap, name='boogie-board-sync-pen')

# catch and terminate also on SIGUSR1
def onsig(a,b):
    print("signal caught, ending")
    sock.close()
    sys.exit(1)

signal.signal(signal.SIGUSR1,onsig)

try:
    while True:
        data = list(bytearray(sock.recv(1024)))
        if len(data) != 14 or data[0] != 192 or data[1] != 1 or data[2] != 161:
            continue

        xpos = data[4] | data[5] << 8
        ypos = data[6] | data[7] << 8

        if xpos < minxpos:
            minxpos = xpos
            print('updated minxpos to %d' % minxpos)
        if xpos > maxxpos:
            maxxpos = xpos
            print('updated maxxpos to %d' % maxxpos)
        if ypos < minypos:
            minypos = ypos
            print('updated minypos to %d' % minypos)
        if ypos > maxypos:
            maxypos = ypos
            print('updated maxypos to %d' % maxypos)

        touch = data[10] & 0x01
        stylus = (data[10] & 0x02) >> 1
        pressure = touch * (data[8] | data[9] << 8)
        ui.write(e.EV_ABS, e.ABS_PRESSURE, pressure)
        ui.write(e.EV_ABS, e.ABS_X, xpos)
        ui.write(e.EV_ABS, e.ABS_Y, ypos)
        ui.write(e.EV_KEY,e.BTN_TOUCH,touch)
        ui.write(e.EV_KEY,e.BTN_STYLUS2,stylus)
        ui.syn()
except KeyboardInterrupt:
    pass

sock.close()
