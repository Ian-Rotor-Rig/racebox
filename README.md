# Racebox
Automated race signals for dinghy racing

Working on this for Frensham Pond SC

Provides a connection to USB relays in order to control a horn system or lights\
Supports 10-5-Go and 5-4-1-Go start sequences\
A way to record finish times and specify competitors is planned bu not available yet

Currently the common/inexpensive USB serial relays are supported\
that use the instruction set for the CH340 (or CH341)\
and some USB HID relays are also supported\

These relays quite often have the "Songle" name on the components

![USB relay](https://github.com/Ian-Rotor-Rig/racebox/assets/90469594/fbae9351-5044-4e16-924e-9634cf990999)

The 1, 2 and 4 channel relays should work. It is not too hard to extend the\
code in rbserial.py or rbhid.py to support other relays if you have the instruction set.

## Required software for serial devices
pyserial - in Ubuntu - sudo apt install python3-serial\
pip3 install pyserial

The braille display kernel module prevents these serial devices working correctly\
and should be removed. This is caused by a conflict between product ids

sudo apt remove brltty

## Required software for HID devices
hid - in Ubuntu - sudo apt install python3-hid\
pip3 install hid

## Ubuntu groups
To work on Linux the user must be in the dialout group\
(some docs suggest plugdev)

sudo usermod -a -G dialout myusername

## HID Relay Miscellaneous Information

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