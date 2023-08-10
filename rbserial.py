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

try:
    import serial
except ModuleNotFoundError as error:
    print(str(error))

from time import sleep
import threading
from rbrelayconfig import ch340

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
        
    def __open(self, driver=ch340, port='/dev/ttyUSB0', rate=9600):
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

    def onoff(self, delay=0.5, ch=0):
        if not self.active: return
        t = threading.Thread(target=self.__tOnOff, args=(delay, ch))
        t.start()
