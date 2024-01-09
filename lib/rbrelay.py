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

try:
    import hid
except ModuleNotFoundError as error:
    print(str(error))
    
from lib.rbrelayconfig import ch340, pl2303, ft232r, hid16c0, abcd

class USBRelay():
    def __init__(self):
        pass
    
    def onoff(self, w, delay=0.5, count=1, ch=0, relayOn=False):
        if relayOn: 
            self.off()
            w.after(int(delay*1500), self.onoff, w, delay, count, ch, False) # between multiple signals if count > 1
            return
        if count < 1: return
        count -= 1
        self.on()
        w.after(int(delay*1000), self.onoff, w, delay, count, ch, True)
                        
    def flashon(self, w, ch=0, onfor=0.4, offfor=0.4): #at present onfor and offfor are not in the user config
        self.flashactive = True
        self.__flash(w, onfor, offfor, ch)
        
    def flashoff(self):
        self.flashactive = False #I suppose flashactive could be made channel-specific?
        #maybe an array with a boolean value for each channel?
            
    def __flash(self, w, onfor, offfor, ch):
        if not self.flashactive: return
        self.onoff(w, onfor, 1, ch)
        w.after(int((onfor+offfor)*1000), self.__flash, w, onfor, offfor, ch)

class USBSerialRelay(USBRelay):       	
    def __init__(self, port='/dev/ttyUSB0', driver='ch340', rate=9600):
        try:
            self.connection = serial.Serial()
            self.configurePort(port, rate)
            self.configure(driver)
            self.__open()
            self.initialiseDevice()
            if self.active: print('opened serial port ', port, ' with driver ', driver, ' at rate ', rate)
            else: print('serial port ', port, ' not opened')
        except:
            self.active = False
            
        super().__init__()
        
    def __del__(self):
        self.__close()
        
    def configure(self, driverName):
        self.driverName = driverName
        if driverName == 'ch340': self.driver = ch340
        if driverName == 'pl2303': self.driver = pl2303
        if driverName == 'ft232r': self.driver = ft232r
        if driverName == 'abcd': self.driver = abcd
        
    def __open(self):
        self.active = True
        try:
            if self.connection.is_open: self.connection.close()
            self.connection.baudrate = self.rate
            self.connection.port = self.port
            self.driver = self.driver
            self.connection.open() #the Arduinos take about 2s to initialise
        except:
            self.active = False
        
    def __close(self):
        if not self.active: return
        try:
            self.connection.close()
            self.active = False
        except:
            print('connection could not be closed')
                        
    def configurePort(self, port='/dev/ttyUSB0', rate=9600):
        self.port = port
        self.rate = rate
        
    def initialiseDevice(self):
        if 'handshake' in self.driver: 
            self.connection.write(self.driver['handshake'])
            time.sleep(0.25)
        if 'activate' in self.driver: 
            self.connection.write(self.driver['activate'])
        if 'reset' in self.driver: 
            self.connection.write(self.driver['reset'])
            self.connection.write(self.driver['reset'])
            
    def on(self, ch=0):
        if not self.active: return
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['on'])

    def off(self, ch=0):
        if not self.active: return
        if self.connection.is_open: self.connection.write(self.driver['channel'][ch]['off'])
        
class USBHIDRelay(USBRelay):        	
    def __init__(self, driver=hid16c0):
        self.active = False
        self.driver = driver
        try:
            self.__open()
        except Exception as error:
            print(error)
            self.active = False
        
        super().__init__()
            
    def __del__(self):
        self.__close()

    def configure(self, driverName):
        self.driverName = driverName
        if driverName == 'hid16c0': self.driver = hid16c0
        
    def __open(self):
        try:
            self.h = hid.Device(self.driver['vid'], self.driver['pid'])
            self.active = True
        except:
            self.active = False
    
    def __close(self):
        if self.active: self.h.close()
    
    def on(self, ch=0):
        if self.active: self.h.write(self.driver['channel'][ch]['on'])

    def off(self, ch=0):
        if self.active: self.h.write(self.driver['channel'][ch]['off'])

