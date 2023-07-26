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

from time import sleep
import serial
import threading

#serial port functionality
class USBRelay:
    #drivers
    ch340 = {
        'name': 'CH340',
        'channel':
            [
                {'on': b'\xA0\x01\x01\xA2', 'off': b'\xA0\x01\x00\xA1'},
                {'on': b'\xA0\x02\x01\xA3', 'off': b'\xA0\x02\x00\xA2'},
                {'on': b'\xA0\x03\x01\xA4', 'off': b'\xA0\x03\x00\xA3'},
                {'on': b'\xA0\x04\x01\xA5', 'off': b'\xA0\x04\x00\xA4'}
            ]
    }
    
    defaultDelay = 0.75 #seconds
        	
    def __init__(self):
        self.connection = serial.Serial()
        
    def __del__(self):
        self.connection.close()
        
    def __open(self, port='/dev/ttyUSB0', rate=9600, driver=ch340):
        if self.connection.is_open: self.connection.close()
        self.connection.baudrate = rate
        self.connection.port = port
        self.driver = driver
        self.connection.open()
        
    def __close(self):
        self.connection.close()
        
    def configurePort(self, port='/dev/ttyUSB0', rate=9600, driver=ch340):
        self.__open(self, port, rate, driver)
        
    def isOpen(self):
        return self.connection.is_open
        
    def on(self, ch=0):
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['on'])

    def off(self, ch=0):
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['off'])
        
    def __tOnOff(self, ch, delay):
        self.__open()
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['on'])
        sleep(delay)
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['off'])
        self.__close()

    def onoff(self, ch=0, delay=defaultDelay):
        t = threading.Thread(target=self.__tOnOff, args=(ch,delay))
        t.start()
