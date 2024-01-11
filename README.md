# Racebox
Automated race signals and easy finish timing for dinghy racing

* Provides a connection to USB relays in order to control a horn system
* Supports 10-5-Go, 5-4-1-Go and 3-2-1-Go start sequences
* Has a simple way to record finishes on the "Finish Times" tab

Screenshots and more details are over at the [Rotor-Rig.com website](https://www.rotor-rig.com/racebox)

More detailed installation and configuration information is in the [wiki](https://github.com/rotor-rig/racebox/wiki)

Currently the common/inexpensive USB serial relays are supported\
that use the instruction set for the CH340 (or CH341)\
and some USB HID relays are also supported

These relays quite often have the "Songle" name on the components

![USB relay](https://github.com/Ian-Rotor-Rig/racebox/assets/90469594/fbae9351-5044-4e16-924e-9634cf990999)

The 1, 2 and 4 channel relays should work. It is not too hard to extend the\
code in rbrelayconfig.py to support other relays if you have the instruction set.

The PL2303/ICStation and RT232R/KMTronic serial relays are supported

Arduino microcontrollers are supported - see [the Rotor-Rig Arduino repo](https://github.com/rotor-rig/arduino/tree/main/serial/relay-serial.cpp)\
for the sketch that works with the ABCD commands that Racebox uses.

## Configuration File
The configuration file **rbconfig.ini** is created when the program is started.\
This used to adjust defaults and settings

## Running Racebox
Once installed Racebox is run like this:\
**python3 racebox.py**

(on Windows it is python rather than python3)

## Required software
python3.x (latest version) including pip and tcl/tk (often installed by default)

### Windows
The [Digital Ocean](https://www.digitalocean.com/community/tutorials/install-python-windows-10) guide is good\
The required "pip" and "tcl/tk (tkinter)" options are normally installed by default.

### Ubuntu (and many other Linux distros)
Python3 is usually pre-installed. Check by typing in terminal:\
python3 -V

#### Required software for serial devices
There are extra packages required to support various relays.\
These are covered in the relays section of the Wiki
