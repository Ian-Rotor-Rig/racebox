# Racebox
Automated race signals for dinghy racing

Working on this for Frensham Pond SC

Provides a connection to USB serial relays in order to control a horn system or lights\
Supports 10-5-Go and 5-4-1-Go start sequences\
A way to record finish times and specify competitors is planned bu not available yet

Currently the common/inexpensive USB serial relays are supported\
that use the instruction set for the CH340 (or CH341)\
These relays quite often have the "Songle" name on the components

![USB relay](https://github.com/Ian-Rotor-Rig/racebox/assets/90469594/fbae9351-5044-4e16-924e-9634cf990999)

The 1, 2 and 4 channel relays should work. It is not too hard to extend the\
code in rbserial.py to support 8 channel relays if you have the instruction set.

WARNING: if the USB relay does not support **serial** communication via CH340 it will not work\
without further configuration. There are some relays that support HID but do not have the serial\
interface. You may be able to make them work by installing a driver. More information on this when I have it.



# Required software for serial devices
pyserial - in Ubuntu - sudo apt install python3-serial
pip3 install pyserial

# Required software for HID devices
hid - in Ubuntu - sudo apt install python3-hid
pip3 install hid

# Ubuntu groups
To work on Linux the user must be in the dialout group\
(some docs suggest plugdev)

# HID Relay Information

The python-hidapi may be one way to address HID relays\
https://trezor.github.io/cython-hidapi/examples.html#finding-devices

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