from AltinoLite import *

Open()

Light(15)

while 1 :
    print("조도 센서 : " + str(sensor.CDS))

Close()