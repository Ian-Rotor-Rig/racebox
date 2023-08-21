try:
    import hid
except ModuleNotFoundError as error:
    print(str(error))
from rbrelayconfig import hid16c0

class USBHIDRelay:
        	
    def __init__(self, driver=hid16c0):
        self.active = False
        self.driver = driver
        try:
            self.__open()
        except Exception as error:
            print(error)
            self.active = False
            
    def __del__(self):
        pass
        
    def __open(self):
        try:
            self.h = hid.Device(self.driver['vid'], self.driver['pid'])
            self.active = True
        except:
            self.active = False
    def __close(self):
        pass
        
    def configure(self, driver=hid16c0):
        self.driver = driver
        
    def isOpen(self):
        return self.active
        
    def on(self, ch=0):
        if self.active: self.h.write(self.driver['channel'][ch]['on'])

    def off(self, ch=0):
        if self.active: self.h.write(self.driver['channel'][ch]['off'])
    
    def onoff(self, w, delay=0.5, count=1, ch=0, relayOn=False):
        if relayOn: 
            self.off()
            self.__close()
            #print('off')
            w.after(int(delay*1500), self.onoff, w, delay, count, ch, False)
            return
        if count < 1: return
        self.__open()
        #print('on')
        self.on()
        count -= 1
        w.after(int(delay*1000), self.onoff, w, delay, count, ch, True)
