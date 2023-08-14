try:
    import hid
except ModuleNotFoundError as error:
    print(str(error))
import threading
from time import sleep
from rbrelayconfig import hid16c0

class USBHIDRelay:
        	
    def __init__(self):
        self.active = False
        try:
            self.__open()
        except:
            print('Hid device not found')
            self.active = False
            
    def __del__(self):
        pass
        
    def __open(self, driver=hid16c0, port='', rate=0):
        try:
            self.h = hid.Device(driver['vid'], driver['pid'])
            self.driver = driver
            self.active = True
            
        except:
            self.active = False
            # print('could not open HID device')        
    def __close(self):
        pass
        
    def configure(self, driver=hid16c0, port='', rate=0):
        self.driver = driver
        
    def isOpen(self):
        return self.active
        
    def on(self, ch=0):
        if self.active: self.h.write(self.driver['channel'][ch]['on'])

    def off(self, ch=0):
        if self.active: self.h.write(self.driver['channel'][ch]['off'])
        
    def __tOnOff(self, delay, ch, count=1):
        self.__open()
        print('count ', count)
        for _ in range(count):  
            print('start hoot')          
            if self.active: self.h.write(self.driver['channel'][ch]['on'])
            sleep(delay)
            if self.active: self.h.write(self.driver['channel'][ch]['off'])
            print('finish hoot')
        self.__close()

    def onoff(self, delay=0.5, ch=0):
        t = threading.Thread(target=self.__tOnOff, args=(delay, ch))
        t.start()
    
    def onoffmulti(self, count=1, delay=0.5, ch=0):
        t = threading.Thread(target=self.__tOnOff, args=(delay, ch, count))
        t.start()
