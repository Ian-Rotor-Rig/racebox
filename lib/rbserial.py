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
import time
try:
    import serial
except ModuleNotFoundError as error:
    print(str(error))

from lib.rbrelayconfig import ch340, pl2303, ft232r

class USBSerialRelay:
        	
    def __init__(self, port='/dev/ttyUSB0', driver='ch340', rate=9600):
        try:
            self.connection = serial.Serial()
            self.configurePort(port, rate)
            self.configure(driver)
            self.__open()
            self.initialiseDevice()
        except:
            self.active = False
        
    def __del__(self):
        try:
            self.connection.close()
        except:
            print('no active connection')
        
    def __open(self):
        self.active = True
        try:
            if self.connection.is_open: self.connection.close()
            self.connection.baudrate = self.rate
            self.connection.port = self.port
            self.driver = self.driver
            self.connection.open()
        except:
            self.active = False
        
    def __close(self):
        if not self.active: return
        self.connection.close()
        
    def configurePort(self, port='/dev/ttyUSB0', rate=9600):
        self.port = port
        self.rate = rate
        
    def configure(self, driverName):
        self.driverName = driverName
        if driverName == 'ch340': self.driver = ch340
        if driverName == 'pl2303': self.driver = pl2303
        if driverName == 'ft232r': self.driver = ft232r
        
    def initialiseDevice(self):
        if 'handshake' in self.driver: 
            self.connection.write(self.driver['handshake'])
            time.sleep(0.25)
        if 'activate' in self.driver: 
            self.connection.write(self.driver['activate'])
        if 'reset' in self.driver: 
            self.connection.write(self.driver['reset'])
            self.connection.write(self.driver['reset'])

    def isOpen(self):
        if not self.active: return False
        return self.connection.is_open
        
    def on(self, ch=0):
        if not self.active: return
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['on'])

    def off(self, ch=0):
        if not self.active: return
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['off'])
           
    def onoff(self, w, delay=0.5, count=1, ch=0, relayOn=False):
        if relayOn: 
            self.off()
            self.__close()
            w.after(int(delay*1500), self.onoff, w, delay, count, ch, False)
            return
        if count < 1: return
        self.__open()
        self.on()
        count -= 1
        w.after(int(delay*1000), self.onoff, w, delay, count, ch, True)
