# Introduction

This is an implementation of a userspace driver for using the Boogie Board Sync
as a tablet under linux.  There are two apps, one for usb input and one for
bluetooth.  It uses pyusb/pybluez to interface with the device and the UInput
system (via evdev for python) to generate input signals.  It's still early
days, so it may be unstable.

# Requirements

- python
- pyusb (for usb)
- pybluez (for bluetooth)
- evdev

# Usage

For the USB app, plug in the device and run the app. If you get timeout errors see the bugs below.

For bluetooth, it should scan for your device so simply running it should work.  If not, run blue.py with a specific address (e.g., ./blue.py 00:00:00:00:00:00) which you can discover using "hcitool scan".

# Installation

Not sure what of this was required, but:

```
sudo apt-get install \
  libevdev-dev
  libusb1.0-0-dev 
  libbluetooth-dev
  xserver-xorg-input-evdev
  libinput
  libinput-tools
  xinput
  evtest
```

```
sudo pip3 install --user \
  pybluez
  pyusb
  evdev
```

then create `/etc/X11/xorg.conf.d/50-tablet.rules` with content:

```
Section "InputClass"
        Identifier "Boogie Sync BT stylus"
        MatchProduct "boogie-board-sync-pen"
        Driver "evdev"
EndSection
```

and reboot
