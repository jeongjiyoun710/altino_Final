import time  #운영 체제의 시간 관련 모듈 
import serial #블루투스 시리얼 통신을 위한 모듈
from timeit import default_timer as timer #
import threading # 쓰레드 생성하기 위한 모듈  

te=0
tx_d = [2,22,35,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3]

rx_d = [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0]
rx_data = [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0]
rx_dsensor1 = [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0]

speed = 0
connectstate = 0
ser = serial.Serial() 
ser.baudrate = 115200 #Bluetooth serial baudrate
port='com5' # 자기 알티노 포트 번호

ser.timeout = 2000

rxcnt=0
sflag=0

class SensorData :
    IR = [0,0,0,0,0,0,0,0]    
    CDS = 0    
    BAT = 0
    CNT = 0

sensor=SensorData

def startTimer():
    global connectstate    
    
    if connectstate == 1 :
        try :
            timer = threading.Timer(0.08, startTimer)
            timer.start()
            sensor = SensorFun(10)        
        except KeyboardInterrupt :
            Close()

def Open(portName=port) :
    global ser
    global connectstate
    ser.port=portName #Bluetooth serial port
    ser.open()
    connectstate = 1
    delay(1000)
    startTimer()
    print("Bluetooth connect")

def BT(portName=port) :
    Open(portName)

def Bt(portName=port) :
    Open(portName)

def bt(portName=port) :
    Open(portName)

def Close() :
    global ser
    global connectstate
    delay(1000)
    connectstate = 0        
    ser.close()
    print("Bluetooth disconnect")

def close() :
    Close()

def delay(ms):
        time.sleep(ms/1000)
        return

def Delay(ms):
    delay(ms)

def check():
    global ser
    te=0
    tx_d[0]=2
    tx_d[1]=22
    tx_d[3]=1
    tx_d[4]=1
        
    for i in range(3,21):
        te=te+tx_d[i]

    te=te%256

    tx_d[2]=te
    tx_d[21]=3
    ser.write(tx_d)

def IR_Tunning() :
    global ser
    te=0
    tx_d[0]=2
    tx_d[1]=22
    tx_d[3]=1
    tx_d[4]=6
    for i in range(5,21) :
        tx_d[i]=0x00
    for i in range(3,21) :
        te=te+tx_d[i]
    te=te%256
    tx_d[2]=te
    tx_d[21]=3
    ser.write(tx_d)     
    pass

def EEPROM_Flash() :
    global ser
    te=0
    tx_d[0]=2
    tx_d[1]=22
    tx_d[3]=1
    tx_d[4]=7
    for i in range(5,21) :
        tx_d[i]=0x00
    for i in range(3,21) :
        te=te+tx_d[i]
    te=te%256
    tx_d[2]=te
    tx_d[21]=3
    ser.write(tx_d) 
    pass
  
def IRSet() :
    IR_Tunning();delay(1000)
    print('IR_Tunning...')
    EEPROM_Flash();delay(1000)
    print('IR_EEPROM_FLASH...')

def Go(left, right):
    if left>1000:
        left=1000
    if left<-1000:
        left=-1000

    if right>1000:
        right=1000
    if right<-1000:
        right=-1000
    
    if right<0:
        right=(-right)^0xffff
        tx_d[6]=int(right/256)
        tx_d[7]=int(right%256)
    else :
        tx_d[6]=int(right/256)
        tx_d[7]=int(right%256)
    
    if left<0:
        left=(-left)^0xffff
        tx_d[8]=int(left/256)
        tx_d[9]=int(left%256)
    else :
        tx_d[8]=int(left/256)
        tx_d[9]=int(left%256)

def go(left,right) :
    Go(left,right)    

def Steering(st):
    if st < -127 :
        st=-127
    elif st > 127 :
        st = 127
    
    if st>=0 :
        tx_d[5]=st
    else :
        tx_d[5]=(-st)^0xff

def steering(value):
    Steering(value)        

def Sound(buzzer) :
    if buzzer < 0 :
        buzzer =0
    if buzzer > 255 :
        buzzer =255
    tx_d[19]=buzzer

def sound(buzzer) :
    Sound(buzzer)

def Display(dot):     
    if type(dot)==int :               
        tx_d[10]=int(dot)
    else :
        tx_d[10]=ord(dot)

    tx_d[11]=0
    tx_d[12]=0
    tx_d[13]=0
    tx_d[14]=0
    tx_d[15]=0
    tx_d[16]=0
    tx_d[17]=0
    tx_d[18]=0

def display(dot):
    Display(dot)                

def DisplayLine(dot1, dot2, dot3, dot4, dot5, dot6, dot7, dot8):
    tx_d[10]=0xff
    tx_d[11]=dot8
    tx_d[12]=dot7
    tx_d[13]=dot6
    tx_d[14]=dot5
    tx_d[15]=dot4
    tx_d[16]=dot3
    tx_d[17]=dot2
    tx_d[18]=dot1

def displayline(dot1, dot2, dot3, dot4, dot5, dot6, dot7, dot8):
    DisplayLine(dot1, dot2, dot3, dot4, dot5, dot6, dot7, dot8)                

def Displayon(x, y) :
    tx_d[10]=0xff
    
    dotx=tx_d[19-x]
    tx_d[19-x]=dotx | pow(2,(y-1))  

def displayon(x,y):
    Displayon(x,y)

def DisplayOn(x,y):
    Displayon(x,y)

def Displayoff(x, y) :
    tx_d[10]=0xff
    
    dotx=tx_d[19-x]
    tx_d[19-x]= dotx & (255-pow(2,(y-1)))  
                
def displayoff(x,y):
    Displayoff(x,y)

def DisplayOff(x,y):
    Displayoff(x,y)

def Light(led) :
    tx_d[20]=led    

def light(led):
    Light(led)

def Led(led):
    Light(led)    

def led(led):
    Light(led)

def Stop() :
    Go(0,0)
    Steering(0)
    Sound(0)
    Display(0)
    Led(0)

def stop():
    Stop()

def SensorFun(command) :
    try :        
        check()    
        
        rx_data=ser.read(22)

        for i in range(0,22):
            for j in range(0,21):
                rx_d[j]=rx_d[j+1]
            rx_d[21]=rx_data[i]
        
            rx_check_sum=0
            if rx_d[0]==2 and rx_d[21] == 3 and rx_d[1] == 22 :

                for cnt in range(3,21) :
                    rx_check_sum = rx_check_sum + rx_d[cnt]
                
                rx_check_sum = rx_check_sum % 256

                if rx_check_sum == rx_d[2]:
                    for cnt in range(5, 21) :
                        rx_dsensor1[cnt]=rx_d[cnt]

                    for k in range(0,22) :
                        rx_d[k]=0
                
        sensordata1 = SensorData

        sensordata1.IR[1]=rx_dsensor1[5] * 256 + rx_dsensor1[6]
        sensordata1.IR[2]=rx_dsensor1[7] * 256 + rx_dsensor1[8]
        sensordata1.IR[3]=rx_dsensor1[9] * 256 + rx_dsensor1[10]
        sensordata1.IR[4]=rx_dsensor1[11] * 256 + rx_dsensor1[12]
        sensordata1.IR[5]=rx_dsensor1[13] * 256 + rx_dsensor1[14]
        sensordata1.IR[6]=rx_dsensor1[15] * 256 + rx_dsensor1[16]

        sensordata1.CDS = rx_dsensor1[17] * 256 + rx_dsensor1[18]
        
        sensordata1.BAT = rx_dsensor1[19] * 256 + rx_dsensor1[20]

        sensordata1.CNT = sensordata1.CNT+1
        
        return sensordata1
    except :
        pass



    
    
