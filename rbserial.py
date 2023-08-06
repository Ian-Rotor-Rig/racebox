###https://github.com/jaketeater/Very-Simple-USB-Relay
#
###https://gist.github.com/RJ/7acba5b06a03c9b521601e08d0327d56
#
###https://www.instructables.com/USB-Relay-With-Python-How-to-Guide/
#
###https://github.com/patrickjahns/simpleusbrelay
#
###https://stackoverflow.com/questions/44056846/how-to-read-and-write-from-a-com-port-using-pyserial
#
#
### on Windows you need to do 
### pip install pyserial
### to get the module installed
### and then the port would be 'COM0' or 'COM1' etc
#
### on Ubuntu you need to remove the brltty package like this:
### sudo apt remove brltty
### as this conflicts with the HID CH340 module
### then install the pyserial module
### pip3 install pyserial
### (you should not use sudo for this)
### you can check if it is installed like this
### python3 -m pip show pyserial
### the port on linux is usually /dev/tty/ttyUSB0
### or it could be (eg) /dev/tty/ttyUSB1 if some other serial
### device is plugged in (unlikely)
### check devices like this
### ls /dev | grep USB
#
### python docs
### https://pyserial.readthedocs.io/en/latest/shortintro.html#opening-serial-ports
#
### Ubuntu permission errors
### sudo usermod -a -G dialout ian
#

try:
    import serial
except ModuleNotFoundError as error:
    print(str(error))

from time import sleep
import threading
from rbrelayconfig import ch340
from rbconfig import defaultOn2Off, serialRelayPort


#serial port functionality
class USBSerialRelay:
        	
    def __init__(self):
        try:
            self.connection = serial.Serial()
            self.__open()
        except:
            print('could not get connection to serial device')
            self.active = False
        
    def __del__(self):
        try:
            self.connection.close()
        except:
            print('no active connection')
        
    def __open(self, driver=ch340, port=serialRelayPort, rate=9600):
        self.active = True
        try:
            if self.connection.is_open: self.connection.close()
            self.connection.baudrate = rate
            self.connection.port = port
            self.driver = driver
            self.connection.open()
        except:
            self.active = False
            print('could not open serial device')
        
    def __close(self):
        if not self.active: return
        self.connection.close()
        
    def configurePort(self, driver=ch340, port='/dev/ttyUSB0', rate=9600):
        self.__open(self, driver, port, rate)
        
    def isOpen(self):
        if not self.active: return False
        return self.connection.is_open
        
    def on(self, ch=0):
        if not self.active: return
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['on'])

    def off(self, ch=0):
        if not self.active: return
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['off'])
        
    def __tOnOff(self, delay, ch):
        self.__open()
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['on'])
        sleep(delay)
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['off'])
        self.__close()

    def onoff(self, delay=defaultOn2Off, ch=0):
        if not self.active: return
        t = threading.Thread(target=self.__tOnOff, args=(delay, ch))
        t.start()
