# Racebox
Automated race signals for dinghy racing

* Provides a connection to USB relays in order to control a horn system
* Supports 10-5-Go and 5-4-1-Go start sequences
* Has a simple way to record finishes on the "Finish Times" tab

Currently the common/inexpensive USB serial relays are supported\
that use the instruction set for the CH340 (or CH341)\
and some USB HID relays are also supported

These relays quite often have the "Songle" name on the components

![USB relay](https://github.com/Ian-Rotor-Rig/racebox/assets/90469594/fbae9351-5044-4e16-924e-9634cf990999)

The 1, 2 and 4 channel relays should work. It is not too hard to extend the\
code in rbrelayconfig.py to support other relays if you have the instruction set.

## Required software
python3.x (latest version)\
pip (usually installed with Python)\

### Windows
Download the installer available on the python.org website\
Add Python/ and Python/Scripts to $PATH

### Ubuntu (and many other Linux distros)
Python3 is usually pre-installed. Check by typing in terminal:\
python3 -V

## Required software for serial devices
pyserial\
pip3 install pyserial

(possibly pip rather than pip3 on Windows)

### Ubuntu
sudo apt install python3-serial\
The braille display kernel module prevents these serial devices working correctly\
and should be removed. This is caused by a conflict between product ids:

sudo apt remove brltty

## Required software for HID devices
hid
pip3 install hid

### Ubuntu
sudo apt install python3-hid

### Ubuntu groups
To work on Linux the user must be in the dialout group\
(some docs suggest plugdev)

sudo usermod -a -G dialout myusername

### HID Relay Miscellaneous Information

The python-hidapi is one way to address HID relays\

In Ubuntu, install usbrelay

Then:

sudo usbrelay

this prints:
Device Found
  type: 16c0 05df
  path: /dev/hidraw3
  serial_number: 
  Manufacturer: www.dcttech.com
  Product:      USBRelay2
  Release:      100
  Interface:    0
  Number of Relays = 2
BITFT_1=0
BITFT_2=0

then:

sudo usbrelay BITFT_1=1

turns on the first relay and:

sudo usbrelay BITFT_1=0

turn it off.