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

### Windows
Download the installer available on the python.org website\
Add Python/ and Python/Scripts to $PATH

(more info on Windows installs needs to be added here)

python -m pip install pyserial\
python -m pip install hid

### Ubuntu (and many other Linux distros)
Python3 is usually pre-installed. Check by typing in terminal:\
python3 -V

On some distros you may also need to install\
sudo apt install python3-tk\
sudo apt install python3-pip

#### Required software for serial devices
pyserial - to install type:


sudo apt install python3-serial\
OR\
pip3 install pyserial (Ubuntu)\
(you may need to add --break-system-packages as an option at\
the end of the pip3 command - it is a long story)

On Ubuntu the braille display kernel module prevents these serial devices working correctly\
and should be removed. This is caused by a conflict between product ids:

sudo apt remove brltty

#### Required software for HID devices
Read these instructions: [PyPi HID](https://pypi.org/project/hid/)

sudo apt install usbrelay\
(this seems to solve some permissions issues and add the required hidraw package)\

pip3 install hid\
(there is no alternative apt package that provides the correct module)

#### Ubuntu groups
To work on Linux the user must be in the dialout group\
(some docs also suggest plugdev)

sudo usermod -a -G dialout myusername

### HID Relay Miscellaneous Information

The python-hidapi is one way to address HID relays

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