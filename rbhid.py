import threading
from time import sleep
import hid
from rbrelayconfig import hid16c0
from rbconfig import defaultOn2Off

class USBHIDRelay:
        	
    def __init__(self, driver=hid16c0):
        try:
            #print('opening HID device')
            #print(hid.enumerate())
            self.h = hid.Device(driver['vid'], driver['pid'])
            #print('Manufacturer: %s' % self.h.manufacturer)
            self.driver = driver
            self.active = True
            
        except:
            self.active = False
            # print('could not open HID device')
            
    def __del__(self):
        pass
        
    def __open(self, driver='', port='', rate=0):
        pass
        
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
        
    def __tOnOff(self, delay, ch):
        self.__open()
        if self.active: self.h.write(self.driver['channel'][ch]['on'])
        sleep(delay)
        if self.active: self.h.write(self.driver['channel'][ch]['off'])
        self.__close()

    def onoff(self, delay=defaultOn2Off, ch=0):
        t = threading.Thread(target=self.__tOnOff, args=(delay, ch))
        t.start()