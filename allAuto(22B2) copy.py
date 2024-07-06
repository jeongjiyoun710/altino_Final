import speech_recognition as sr
from ast import Global
from AltinoLite import *
import pygame













# 음성인식 
def inputAudio():
    # 음성 인식기 인스턴스 생성
    recognizer = sr.Recognizer()

    # 마이크를 음성 소스로 사용
    with sr.Microphone() as source:
        print("말씀해 주세요...")
    
        # 잡음 수준을 자동으로 조정
        recognizer.adjust_for_ambient_noise(source)
    
        # 음성을 들음
        audio_data = recognizer.listen(source)
    
        try:
            # 음성을 텍스트로 변환 (한글 인식)
            text = recognizer.recognize_google(audio_data, language='ko-KR')
            print(f"인식된 텍스트: {text}")
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다.")
        except sr.RequestError as e:
            print(f"구글 음성 인식 서비스에 문제가 있습니다: {e}")

    return text





f1Sum = 0
f2Sum = 0
f3Sum = 0
r4Sum = 0
l5Sum = 0
b6Sum = 0


f1Avr = 0
f2Avr = 0
f3Avr = 0
r4Avr = 0
l5Avr = 0
b6Avr = 0

cnt = 1  #평균 카운트



# 바퀴 돌리는 각도 변수
turnDeg = 0 



# 센서 평균 구하기
def Gear():
    global f1Sum
    global f2Sum
    global f3Sum
    global r4Sum
    global l5Sum
    global b6Sum

    global f1Avr
    global f2Avr
    global f3Avr
    global r4Avr
    global l5Avr
    global b6Avr

    global cnt

    f1Sum += sensor.IR[1]
    f2Sum += sensor.IR[2]
    f3Sum += sensor.IR[3]
    r4Sum += sensor.IR[4]
    l5Sum += sensor.IR[5]
    b6Sum += sensor.IR[6]


    f1Avr = f1Sum // cnt
    f2Avr = f2Sum // cnt
    f3Avr = f3Sum // cnt
    r4Avr = r4Sum // cnt
    l5Avr = l5Sum // cnt
    b6Avr = b6Sum // cnt


    cnt+=1

    if cnt>3:
        cnt=1
        f1Sum = 0
        f2Sum = 0
        f3Sum = 0
        r4Sum = 0
        l5Sum = 0
        b6Sum = 0

    print(str(f1Avr) + " | " + str(f2Avr) + " | " + str(f3Avr) + " | " + str(r4Avr) + " | " + str(l5Avr) + " | " + str(b6Avr))


# 벽에 너무 붙었을 경우 회전
def Turn():
    Gear()

    global turnDeg

    # 우측으로 붙는 경우 왼쪽으로
    if(r4Avr > 100):
        turnDeg = (-r4Avr)+100
        if(turnDeg > 127 or turnDeg < -127):
            # print("127 넘음")
            Steering(-127)
        else:
            Steering(turnDeg)

    # 아무것도 아닌경우 다시 직진
    elif(r4Avr < 100 and l5Avr < 100):
        Steering(0)

    # 좌측으로 붙는 경우 오른쪽으로 => 센서 문제로 값 변경
    elif(l5Avr > 180):
        # Steering(l5Avr-600)
        turnDeg = l5Avr-150
        if(turnDeg > 127 or turnDeg < -127):
            # print("127 넘음")
            Steering(127)
        else:
            Steering(turnDeg)


# 이동하면서 벽에 부딪히지 않도록 회전
def go_turn():
    Gear()
    global turnDeg
    # 멈춤
    if(f1Avr > 40 and f2Avr > 100 and f3Avr > 40):
        Go(0, 0)

    # 아무 상황도 아닐 경우
    else:
        Steering(0)


    # 다음부터는 직진상태에서 커브
    # 오른쪽으로
    if(f1Avr > 5 and f2Avr > 5 ):
        turnDeg = f1Avr-5
        Steering(turnDeg)
        delay(300)
    elif(f1Avr > 5 and l5Avr > 20):
        turnDeg = (f1Avr-5)+(l5Avr-20)

        # 최대치 확인
        if(turnDeg > 127 or turnDeg < -127):
            Steering(127)
            delay(300)
        else:
            Steering(turnDeg)
            delay(300)

    # 왼쪽으로
    elif(f2Avr > 5 and f3Avr > 5):
        turnDeg = (-f3Avr)+5
        Steering(turnDeg)
        delay(300)
    elif(f3Avr > 5 and r4Avr > 20):
        turnDeg = (-f3Avr+5)+(-r4Avr+20)

        # 최대치 확인
        if(turnDeg > 127 or turnDeg < -127):
            Steering(-127)
            delay(300)
        else:
            Steering(turnDeg)
            delay(300)




# -------- 다음부터는 코너 회전 명령 ------------

# 완곡한 코너를 만났을 때, 빈 칸으로 꺾어야한다. 즉, 벽이 있다가 없어지는 구간을 찾아서 회전해야하는 것이다

# chap.1 : 길가다 빈공간 찾기
# chap.2 : 빈공간으로 꺾기
# chap.3 : 만약 부딪힐 것 같으면 다시 뒤로

# 회전해야하는지 확인
turnCheck = False

# 빈 방향 확인 변수
leftConer = False
rightConer = False

forwardClose = False  # 앞이 막혔나 확인

# 앞&양쪽 거리
f2 = 0
l5 = 0
r4 = 0



# 코너 만나는 것을 확인하는 함수
def conerCheck():
    global l5
    global r4
    global f2
    global leftConer
    global rightConer
    global forwardClose

    f2 = sensor.IR[2]
    r4 = sensor.IR[4]
    l5 = sensor.IR[5]

    # 초기화 및 설정 (코너 확인)
    if(l5 != 0):
        leftConer = False
    elif(r4 != 0):
        rightConer = False

    if(l5 == 0):
        leftConer = True
        forwardCloseCheck()
    elif(r4 == 0):
        rightConer = True
        forwardCloseCheck()



# 코너 체크가 되었다면, 앞이 막혔는지 확인하는 함수
def forwardCloseCheck():
    global f2

    global forwardClose

    global leftConer
    global rightConer

    global turnCheck

    if(f2 >= 150):
        Go(0, 0)

        turnCheck = True
        
        # 멈춘 후, 빈 방향으로 꺾기 함수 실행
        if(leftConer == True):
            while turnCheck:
                conerTurn("left")
                
        elif(rightConer == True):
            while turnCheck:
                conerTurn("right")



# 이제 코너를 도는 함수이다
# 이 함수에서는 받아온 값이 만약 left라면 왼쪽으로 가는 명령을, right라면 오른쪽으로 가는 명령을 내릴 것이다
# 회전 중, 만약 대각선 센서를 통해 벽과 부딪히는 것을 감지하면 뒤로 다시 빠진다.
# 다만, 뒤로 빠질 경우, 지금 회전하는 반대 방향으로 회전하며 뒤로 간다.
# 뒤 센서가 감지할 경우 다시 앞으로 간다.

def conerTurn(result):
    turnValue = 0
    
    # 오른쪽 or 왼쪽
    if(result == "left"):
        turnValue = -127
    elif(result == "right"):
        turnValue = 127

    print(result)
    # ----------------------------------

    # 회전이동 시작
    # 벽에 부딪히는지 확인
    f1 = 0
    global f2
    f3 = 0
    f1Check = False
    f3Check = False


    b6 = 0 # 뒤 센서

    # 다 돌았을 경우 초기화할 변수들
    global leftConer
    global rightConer
    global forwardClose

    f1 = sensor.IR[1]
    f2 = sensor.IR[2]
    f3 = sensor.IR[3]

    # 지금부터는 뒤로 다시 돌아가는 것 ====================

    # 뒤로 다시 회전 초기 설정
    if(f1 >= 150):
        f1Check = True
    elif(f3 >= 150):
        f3Check = True


    # 회전하며 이동하자 (뒤로)
    # 먼저 뒤에 부딪히는지 확인
    if(b6>=300):
        Go(0, 0)
        f1Check = False
        f3Check = False
    elif(f1Check == True):
        Steering(-30) # 왼쪽으로 핸들
        Go(-270, -270)
        print(f1Check, f3Check)
    elif(f3Check == True):
        Steering(50) # 오른쪽으로 핸들 => 바퀴가 잘 안돌아가서 50으로 변경
        Go(-270, -270)
        print(f1Check, f3Check)

    # 아무것도 해당하지 않을 경우
    else:
        Steering(turnValue)
        Go(270, 270)

    
    # 만약 다 돌았을 경우 => f1,2,3 센서가 아무것도 감지하지 않을 경우
    if(f1 <= 40 and f2 == 0 and f3 <= 40):
        global turnCheck

        turnCheck = False
        print("회전 종료")
        Steering(0)



# 불빛을 만났을경우
# 시작에서 불빛을 만날 경우 오른쪽과 직진을 고를 수 있다.
# 만약 방향을 말했는데 벽이 있을 경우, 명령 취소 후 다시 뭍는다.
def cds_check(text):
    
    right = 1
    left = 1

    if(text == "출발"):
        Go(300, 300)

        return "con"
    elif(text == "오른쪽으로가"):
        while right:
            Go(300, 300)
            if(sensor.IR[3] <= 30):
                Steering(127)
                delay(3500)
                Steering(0)
                right = 0
                
                return "con"
    elif(text == "왼쪽으로가"):
        while right:
            Go(300, 300)
            if(sensor.IR[3] <= 30):
                Steering(-127)
                delay(3500)
                Steering(0)
                right = 0
                
                return "con"
    

            

# ============================================================= 다음부터는 본격적으로 실행



# CDS 센서 작동 변수
cds_ok = False
cds_cnt = 0



Al_sound("go.mp3")


while 1:
    Go(260, 260)

    # 코너 확인
    conerCheck()

    
    Turn()
    go_turn()

    # 만약 sensor.CDS가 커지는 경우
    # 즉, 불빛 감지
    if(sensor.CDS > 830 and cds_ok == False):
        Go(0, 0)
        Al_sound("stopQue.mp3")

        # 음성인식
        text = inputAudio()

        result = cds_check(text)
        if (result == "con"):
            cds_ok = True
            continue
        else:
            break
    cds_cnt+=1

    # 불빛 감지 이후 10번은 불빛 감지 x
    if(cds_cnt == 50):
        cds_ok = False
        cds_cnt = 0
    
    delay(100)

    # print("앞왼쪽 :" + str(sensor.IR[1]) + " | 앞 :" + str(sensor.IR[2]) + " | 앞오른쪽 :" + str(sensor.IR[3]) + " | 오른쪽 :" + str(sensor.IR[4]) + " | 왼쪽 :" + str(sensor.IR[5]) + " | 뒤 :" + str(sensor.IR[6]))

