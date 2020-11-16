
import serial
import time
import threading
#temperture and humidity
#tNh = serial.Serial('COM5',9600,timeout = 1)
'''
for i in range(30):
    time.sleep(2)
    s = tNh.read_until(terminator=b'\n')
    tNh.write(b'1')
    print(s)
'''
class plantbox(object):
    def __init__(self, tnhPortNumber:str = None, distancePortNumber:str = None):
        self.lock = threading.Lock()
        self._temperture = 0.0
        self._humidity = 0.0
        self._distance = 0
        self._lux = 0.0
        self._tnhPort = None
        self._distancePort = None
        self._status = '正常'
        if tnhPortNumber:
            self.openTnhPort(tnhPortNumber)
        if distancePortNumber:
            self.openDistancePort(distancePortNumber)

        self.tnhThreadQuery = threading.Thread(target=self.tnhQuery, args=())
        self.tnhThreadQuery.setDaemon(True)
        self.tnhThreadQuery.start()

        self.distanceThreadQuery = threading.Thread(target=self.distanceQuery, args=())
        self.distanceThreadQuery.setDaemon(True)
        self.distanceThreadQuery.start()
        
        self._settingTemp = -1
        self._settingHum = -1

    def openTnhPort(self, port):
        if self._tnhPort:
            self._tnhPort.close()
        self._tnhPort = serial.Serial(port,9600,timeout=1)
    def openDistancePort(self, port):
        if self._distancePort:
            self._distancePort.close()
        self._distancePort = serial.Serial(port,230400)        

    def tnhQuery(self):
        while True:
            time.sleep(2)
            if (not self._tnhPort is None) and self._tnhPort.isOpen:
                
                s = self._tnhPort.read_until(terminator=b'\n')
                s = s.rstrip(b'\r\n')
                
                try:
                    s = s.decode('utf-8')
                except UnicodeDecodeError:
                    continue
                
                if len(s) == 0 or s.find('nan') > 0:
                    continue
                s = s.split(',')
                self.lock.acquire()
                
                if s[0] != 'nan':
                    self._humidity = float(s[0])
                    self._temperture = float(s[1])
                
                self.lock.release()
                if self._settingTemp > 0 and self._settingTemp < self._temperture:
                    s = '1'                    
                else:
                    s = '0'
                self._tnhPort.write(s.encode('utf-8'))

                #print(self._humidity)
                #print(self._temperture)
    def status(self):
        
        pass
    def distanceQuery(self):        
        while True:
            time.sleep(0.5)
            if (not self._distancePort is None) and self._distancePort.isOpen():
                #print(self._distancePort.isOpen())
                s = self._distancePort.read_until(terminator=b'\n')
                s = s.rstrip(b'\r\n')
                self._distancePort.flushInput()
                #print(s)
                try:
                    s = s.decode('utf-8')
                    s = s.split(',')
                    self.lock.acquire()
                    if len(s)>1:
                        self._distance = int(s[1])
                    self.lock.release()
                except :
                    pass
                
                #self._distancePort.flush()
                #print(s)
                
                #print(self._distance)
    

    @property
    def tnhIsOpen(self)->bool:        
        return self._tnhPort and self._tnhPort.isOpen()
    @property
    def distanceIsOpen(self)->bool:
        #print('aaaaaa')
        return self._distancePort and self._distancePort.isOpen()
    
    def settingTemp(self, temperture:int):
        self._settingTemp = temperture
    @property
    def tempertureAndHumidity(self):
        self.tnhQuery()
        return [self._temperture,self._humidity]
    @tempertureAndHumidity.setter
    def tempertureAndHumidity(self, temperture:int = 0, humidity:int = 0):
        n = temperture + humidity<< 8 
        
        n = str(n)
        self._tnhPort.write(n.encode("utf-8"))

    @property
    def temperture(self):
        return self._temperture

    @property
    def humidity(self):
        return self._humidity
    @property
    def distance(self):
        return self._distance
   
if __name__ == "__main__":
    p = plantbox(distancePortNumber='COM4')
    #p.openTnhPort('COM3')
    time.sleep(15)
    exit(0)