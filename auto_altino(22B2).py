import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt

import speech_recognition as sr
from ast import Global
from AltinoLite import *
import pygame

import requests

# 음성 파일 재생
def Al_sound(soundFileName):
    print("사운드 파일 재생 : " + soundFileName)
    pygame.mixer.init()

    # 사운드 소스 위치 설정
    pygame.mixer.music.load("mp3\\" + soundFileName) # 8day 폴더 기준
    # pygame.mixer.music.load("C:\\Users\\buil\Desktop\\altino_class\\sound\\" + soundFileName) #기능부실
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

form_class = uic.loadUiType("altino.ui")[0]

# 센서들 작동
sensorsOk = False

# 자동운전 작동
autoGo = False

# 연결 완료
connectQue = False

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
backFlag = 0 

cds_ok = False
cds_cnt = 0

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
   
say=["",""]

backValue = 0


# 유저 정보
userNameTxt = ''
userPhoneTxt = ''

# 유저 정보를 받았는지 체크
userDataUp = False

# timeSec 를 받았는지 체크
userTimeEnd = False


# 종료 여부
auto_fin = False

# 서버 보내기
def recordUserData( UserName, UserPhone, UserScore ) :
    requests.get('http://desk.sjkim.net:8888/score?NAME=' + str( UserName ) + '&PHONE=' + str( UserPhone ) + '&SCORE=' + str( UserScore ))
    print(str(UserName) + "님의 정보 등록이 완료 되었습니다.")

# 적외선 센서 쓰레드
class Thread1(QThread):
    updateSignal = pyqtSignal(int)
    def run(self):
        while sensorsOk == True:
            # 센서 값 시그널로 메인 클래스에 보내기
            time.sleep(0.05)
            self.updateSignal.emit("test")

# 자동운전 쓰레드
class Thread2(QThread):
    updateSignal = pyqtSignal(int)

    def run(self):

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
                    return text        
                except sr.UnknownValueError:
                    print("음성을 인식할 수 없습니다.")
                    return "reload"
                    
                except sr.RequestError as e:
                    print(f"구글 음성 인식 서비스에 문제가 있습니다: {e}")
                    error = ["sayError", str(e)]
                    self.updateSignal.emit(error)

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

            #print(str(f1Avr) + " | " + str(f2Avr) + " | " + str(f3Avr) + " | " + str(r4Avr) + " | " + str(l5Avr) + " | " + str(b6Avr))

        def go_turn():
            Gear()
            global turnDeg
            global f1Avr
            global f2Avr
            global f3Avr
            global r4Avr
            global l5Avr
            global b6Avr

            # 다음부터는 직진상태에서 커브
            # 오른쪽으로
            if(f1Avr > 5):
                turnDeg = f1Avr-2
                Steering(turnDeg)
                delay(300)
            elif(f1Avr > 5 and l5Avr > 10):
                turnDeg = (f1Avr)+(l5Avr-20)

                # 최대치 확인
                if(turnDeg > 127 or turnDeg < -127):
                    Steering(127)
                    delay(300)
                else:
                    Steering(turnDeg)
                    delay(300)

            # 왼쪽으로
            elif(f3Avr > 5):
                turnDeg = (-f3Avr)+2
                Steering(turnDeg)
                delay(300)
            elif(f3Avr > 5 and r4Avr > 10):
                turnDeg = (-f3Avr)+(-r4Avr+20)

                # 최대치 확인
                if(turnDeg > 127 or turnDeg < -127):
                    Steering(-127)
                    delay(300)
                else:
                    Steering(turnDeg)
                    delay(300)
            else:
                if(r4Avr >= 150):
                    turnDeg = (-r4Avr)+150
                    if(turnDeg > 127 or turnDeg < -127):
                        Steering(-127)
                    else:
                        Steering(turnDeg)

                # 좌측으로 붙는 경우 오른쪽으로
                elif(l5Avr >= 150):
                    turnDeg = l5Avr-150
                    if(turnDeg > 127 or turnDeg < -127):
                        Steering(127)
                    else:
                        Steering(turnDeg)

                # 아무것도 아닌경우 다시 직진
                elif(r4Avr < 150 and l5Avr < 150):
                    Steering(0)

        # -------- 다음부터는 코너 회전 명령 ------------

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


            # 버그 수정
            # 만약 빛이 없는 곳에서 코너가 확인되면
            if(sensor.CDS <= 300):
                return

            # 초기화 및 설정 (코너 확인)
            if(l5 != 0):
                leftConer = False
            elif(r4 != 0):
                rightConer = False

            if(l5 == 0):
                leftConer = True
                forwardCloseCheck()
                print("left")
            elif(r4 == 0):
                rightConer = True
                forwardCloseCheck()
                print("right")
            else :
                leftConer = False
                rightConer = False 


        # 코너 체크가 되었다면, 앞이 막혔는지 확인하는 함수
        def forwardCloseCheck():
            global f2

            global forwardClose

            global leftConer
            global rightConer

            global turnCheck

            # 버그 수정
            # 만약 빛이 없는 곳에서 코너가 확인되면
            if(sensor.CDS <= 300):
                return

            if(f2 >= 40):
                Go(0, 0)

                turnCheck = True
                
                # 멈춘 후, 빈 방향으로 꺾기 함수 실행
                if(leftConer == True):
                    while turnCheck:
                        # 버그 수정
                        # 만약 빛이 없는 곳에서 코너가 확인되면
                        if(sensor.CDS <= 300):
                            break
                        conerTurn("left")
                        
                elif(rightConer == True):
                    while turnCheck:
                        # 버그 수정
                        # 만약 빛이 없는 곳에서 코너가 확인되면
                        if(sensor.CDS <= 300):
                            break
                        conerTurn("right")


        # 코너 돌기
        def conerTurn(result):

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
            global backValue

            f1 = sensor.IR[1]
            f2 = sensor.IR[2]
            f3 = sensor.IR[3]

            # 지금부터는 뒤로 다시 돌아가는 것 ====================

            # 뒤로 다시 회전 초기 설정
            if(f1 >= 70):
                f1Check = True
            elif(f3 >= 70):
                f3Check = True


            # 회전하며 이동하자 (뒤로)
            # 먼저 뒤에 부딪히는지 확인
            if(b6>=300):
                f1Check = False
                f3Check = False

                if ( backValue < 0 ) : 
                    Steering(127)
                elif ( backValue > 0 ) : 
                    Steering(-127)
                else :
                    Steering(0)

                Go(280, 280)

            elif(f1Check == True):
                Steering(-30) # 왼쪽으로 핸들
                Go(-280, -280)
                backValue = -50
                #print(f1Check, f3Check)
            elif(f3Check == True):
                Steering(30) # 오른쪽으로 핸들
                Go(-280, -280)
                backValue = 50
                #print(f1Check, f3Check)
            # 아무것도 해당하지 않을 경우
            else:
                #print("TurnValue : " + str(turnValue))
                #Steering(turnValue*-1)
                #Steering(0)
                #backFlag = 0
                if ( backValue < 0 ) : 
                    Steering(127)
                elif ( backValue > 0 ) : 
                    Steering(-127)
                else :
                    Steering(0)

                Go(290, 290)

            # 만약 다 돌았을 경우 => f1,2,3 센서가 아무것도 감지하지 않을 경우
            if(f1 < 20 and f2 < 10 and f3 < 20):
                global turnCheck

                turnCheck = False
                #print("회전 종료")
                if  leftConer ==False :
                    Steering(50)
                elif rightConer==True :
                    Steering(-50)
                else :                    
                    Steering(0)

        # ======================================
        # 다음은 불빛 감지시

        def cds_check(text):
            left = 1
            if(text == "직진"):
                Go(300, 300)

                return "con"
            elif(text == "왼쪽"):
                while left:
                    Go(300, 300)
                    if(sensor.IR[3] <= 30):
                        Steering(-127)
                        delay(4000)
                        Steering(0)
                        left = 0
                        
                        return "con"

        global cds_cnt
        global cds_ok
        global say

        print(autoGo)
        if ( autoGo == True ) :
            Al_sound("go.mp3")
        else :
            return
        
        while autoGo == True:

            Go(300, 300)

            # 코너 확인
            conerCheck()

            delay(200)
            go_turn()

            # 만약 sensor.CDS가 커지는 경우
            # 즉, 불빛 감지
            # 조도 센서 감지
            if(sensor.CDS > 700 and cds_ok == False):

                say = []

                Go(0, 0)

                say = ["robot", "멈췄습니다. 어디로 갈까요?\n(왼쪽, 직진으로 대답해주세요)"]
                self.updateSignal.emit(say)

                Al_sound("stopQue.mp3")
                #self.txtRobotQue.setText("멈췄습니다 어디로 갈까요?")
                #self.updateSignal.emit("멈췄습니다. 어디로갈까요? (오른쪽,왼쪽,직진 으로 대답해주세요)")
                #self.updateSignal.emit()
                #self.txtRobotQueView.setText("예 : 오른쪽, 왼쪽, 직진")
                
                text = ""
                
                answer = False

                while answer == False:
                    # 음성인식
                    text = inputAudio()
                    say = ["person", text]

                    self.updateSignal.emit(say)

                    if(text == "직진" or text == "왼쪽"):
                        answer = True
                    elif(text == "reload"):
                        say = ["robot", "잘 못들었어요. 다시 말해주세요\n(왼쪽, 직진으로 대답해주세요)"]
                        self.updateSignal.emit(say)
                        say = ["person", text]
                        self.updateSignal.emit(say)
                        Al_sound("reload.mp3")
                        continue
                    else:
                        say = ["robot", "예시 답안으로 다시 말해주세요\n(왼쪽, 직진으로 대답해주세요)"]
                        self.updateSignal.emit(say)
                        say = ["person", text]
                        self.updateSignal.emit(say)
                        Al_sound("reAnswer.mp3")
                        continue

                result = cds_check(text)
                if (result == "con"):
                    cds_ok = True
                    continue
                else:
                    break
            cds_cnt+=1

            print("조도 : "+str(sensor.CDS))

            # 불빛 감지 이후 10번은 불빛 감지 x
            if(cds_cnt == 50):
                cds_ok = False
                cds_cnt = 0
            
            # 도착?
            if(sensor.CDS <= 150):
                global auto_fin

                # auto_fin == True
                # while auto_fin == True:
                Go(0,0)
                Al_sound("end.mp3")
                say = ["robot", "도착했습니다!!\n자동운전종료를 눌러주세요."]
                self.updateSignal.emit(say)
                # delay(5000)
            delay(100)
        Go(0, 0) # while 문 빠져나왔을 경우

# 비상등 쓰레드
class Thread3(QThread):
    updateSignal = pyqtSignal(int)

    def run(self):
        global connectQue
        while connectQue == True:
            Light(0x0f)
            delay(1000)
            Light(0x00)
            delay(1000)

timerCheck = False

timeSec = 0 # 타이머 초

# 타이머 쓰레드
class Thread4(QThread):
    updateSignal = pyqtSignal(int)

    def run(self):
        global timerCheck
        global timeSec

        while timerCheck == True:
            self.updateSignal.emit(timeSec)
            delay(10)
            timeSec += 0.01

            # 어두워지면 타이머 종료 및 멈추기
            # if sensor.CDS < 200:
            #     timerCheck = False
            #     Go(0,0)

class Mywindow(QMainWindow, form_class):
    def __init__(self):
        
        super().__init__()
        self.setupUi(self)

        #이미지 초기화 처리를 한다. 
        pixmapLogo   = QPixmap("ui_img\\buil.png")
        pixmapPerson = QPixmap("ui_img\\person.png")
        pixmapRobot = QPixmap("ui_img\\robot.png")
        pixmapAltino = QPixmap("ui_img\\altino_lite_img.png")
        pixmapTalk1 = QPixmap("ui_img\\talkBox1.png")
        pixmapTalk2 = QPixmap("ui_img\\talkBox2.png")
        pixmapConnect = QPixmap("ui_img\\connect_altino.svg")
        pixmapDisconnect = QPixmap("ui_img\\disconnect_altino.svg")
        pixmapHelp = QPixmap("ui_img\\help.svg")
        pixmapStart = QPixmap("ui_img\\start_altino.svg")
        pixmapStop = QPixmap("ui_img\\stop_altino.svg")

        self.label_logo.setPixmap(pixmapLogo)
        self.label_logo.setScaledContents(True) 
        self.person.setPixmap(pixmapPerson)
        self.person.setScaledContents(True) 
        self.robot.setPixmap(pixmapRobot)
        self.robot.setScaledContents(True) 
        self.altino_img.setPixmap(pixmapAltino)
        self.altino_img.setScaledContents(True) 
        self.txtRobot.setPixmap(pixmapTalk1)
        self.txtRobot.setScaledContents(True) 
        self.txtPerson.setPixmap(pixmapTalk2)
        self.txtPerson.setScaledContents(True) 
        self.pixmap_connect.setPixmap(pixmapConnect)
        self.pixmap_connect.setScaledContents(True) 
        self.pixmap_disconnect.setPixmap(pixmapDisconnect)
        self.pixmap_disconnect.setScaledContents(True) 
        self.pixmap_help.setPixmap(pixmapHelp)
        self.pixmap_help.setScaledContents(True) 
        self.pixmap_start.setPixmap(pixmapStart)
        self.pixmap_start.setScaledContents(True) 
        self.pixmap_stop.setPixmap(pixmapStop)
        self.pixmap_stop.setScaledContents(True) 
        

        # 알티노 연결 및 해제
        self.btnConnect.clicked.connect(self.altino_conn)
        self.btnDeconnect.clicked.connect(self.altino_deconn)

        # IR센서 초기화
        self.btnIRSet.clicked.connect(self.IRSetBtn)

        # 쓰레드 실행
        self.thread1 = Thread1() # 적외선 센서
        self.thread2 = Thread2() # 자동 운전
        self.thread3 = Thread3() # 비상등 작동
        self.thread4 = Thread4() # 타이머 작동

        self.thread1.updateSignal.connect(self.updateSensor) # 적외선 센서 작동
        self.thread2.updateSignal.connect(self.sayPrint) # 말하는 것 출력
        self.thread4.updateSignal.connect(self.timerShow) # 타이머 실행

        self.btnAutoStart.clicked.connect(self.autoGoStart) # 자동운전 시작
        self.btnAutoStop.clicked.connect(self.autoGoStop) # 자동운전 종료


    # 키 이벤트
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F8:
            if( autoGo == True ) :
                self.txtLog.appendPlainText(" -- 아직 게임이 끝나지않아 알티노를 뒤로 이동시킬 수 없습니다. -- ")
            else :
                Go(-300, -300)

                # 몇초동안 움질일 것인지
                self.txtLog.appendPlainText(" -- 알티노를 이동시키는 중 입니다. -- ")
                delay(3000)

                Go(0, 0)
                self.txtLog.appendPlainText(" -- 알티노를 뒤로 이동시켰습니다. -- ")

        if e.key() == Qt.Key_F1:
            # 입력한 이름과 전화번호 저장 하기
            global userNameTxt
            global userPhoneTxt
            global userDataUp

            # 값 존재 여부 검사
            if( self.userNametxt.text() == '' or self.userPhonetxt.text() == '' ) :
                self.txtLog.appendPlainText(" -- 유저의 이름또는 유저의 전화번호의 값이 존재 하지 않습니다. -- ")
            # 값이 다 존재한다면 각각의 변수에 저장
            else :
                # 전화번호가 11글자 라면,
                if( len(self.userPhonetxt.text()) == 11 ) :
                    userNameTxt = self.userNametxt.text()
                    userPhoneTxt = self.userPhonetxt.text()
                    self.txtLog.appendPlainText(" -- 유저의 정보를 입력 받았습니다. -- ")
                    userDataUp = True
                    
                    # 전호번호 가리기
                    self.userPhonetxt.setText("010 - XXXX - " + str(userPhoneTxt[7:11]) )
                # 아니라면,
                else :
                    self.txtLog.appendPlainText(" -- 전화번호의 길이가 잘못되었습니다. -- ")

        if e.key() == Qt.Key_F4:
            global userTimeEnd

            # 게임이 끝나있다면,
            if( userTimeEnd == True ) :
                global timeSec

                timeSec = round(timeSec, 2) - 0.01
                print(timeSec)

                # 서버로 get 요청 보내기
                recordUserData( userNameTxt, userPhoneTxt, timeSec )
                self.txtLog.appendPlainText(" -- 유저의 정보를 포함한 최종 결과를 저장하였습니다. -- ")
                self.txtLog.appendPlainText(" -- " + userNameTxt + "님의 정보 등록이 완료 되었습니다. -- ")
                self.txtLog.appendPlainText(" -- 키보드 F8을 눌러 알티노 라이트를 빼내세요 -- ")

                # 사용된 값들 초기화
                userNameTxt = ''
                userPhoneTxt = ''
                timeSec = 0
                userTimeEnd = False

                # 입력란 비우기
                self.userNametxt.setText('')
                self.userPhonetxt.setText('')
            # 아니라면,
            else :
                self.txtLog.appendPlainText(" -- 아직 게임이 끝나지 않았습니다. -- ")

    # 타이머 출력
    def timerShow(self):
        global timeSec

        self.timer.setText(str(round(timeSec, 2)) + "초")
        
    # 음성 출력
    def sayPrint(self):
        global say
        print(say[0] +"/"+ say[1])
        
        if(say[0] == "robot"):
            self.txtRobotQue.setText(say[1])
        elif(say[0] == "person"):
            if say[1] == "reload":
                say[1] = "인식하지 못 하였습니다"
                self.txtPersonAnw.setText(say[1])
            else :
                self.txtPersonAnw.setText(say[1])

    # IR센서 초기화
    def IRSetBtn(self):
        Go(0, 0)
        self.txtLog.appendPlainText("적외선[IR] 센서 초기화 완료..")
        IRSet()

    # 자동운전 멈춤
    def autoGoStop(self):
        global autoGo
        global timeSec
        autoGo = False

        global timerCheck
        timerCheck = False
        self.thread4.start()

        self.txtLog.appendPlainText(" -- 키보드 F4를 눌러 기록을 저장하세요 -- ")

        global userDataUp
        userDataUp = False

        global userTimeEnd
        userTimeEnd = True

        # global auto_fin
        # auto_fin = False

    # 자동운전 실행
    def autoGoStart(self):
        global userDataUp
        
        if ( userDataUp == False ) :
            self.txtLog.appendPlainText(" -- 유저 정보를 입력받지 않은 상태에서 시작하실 수 없습니다. -- ")
            self.txtLog.appendPlainText(" -- 정보를 입력 후, 키보드 F1을 눌러주세요. -- ")
        else :
            Steering(0)
            global autoGo
            autoGo = True
            self.thread2.start()

            global timerCheck
            global timeSec

            timeSec = 0

            timerCheck = True
            self.thread4.start()

    # 적외선 센서 표시
    def updateSensor(self):
        self.lcdF1.display(str(sensor.IR[1]))
        self.lcdF2.display(str(sensor.IR[2]))
        self.lcdF3.display(str(sensor.IR[3]))
        self.lcdR4.display(str(sensor.IR[4]))
        self.lcdL5.display(str(sensor.IR[5]))
        self.lcdB6.display(str(sensor.IR[6]))


    # 알티노 연결
    def altino_conn(self):
        # 시작 음성
        self.txtLog.clear()
        self.txtLog.appendPlainText("알티노 시작")
        self.txtAltinoStatus.setText("연결중..")

        # delay(1000)
        Al_sound("start.mp3")
        try:

            if ( self.txtPort.text() == "") :
                QMessageBox.information(self, "오류", "포트번호를 입력해주세요 ")
                self.txtLog.appendPlainText("Error : 포트번호를 입력해주세요")
                self.txtAltinoStatus.setText("연결오류")
                return

            Open(portName="com"+self.txtPort.text())
            Al_sound("conn.mp3")
            self.txtAltinoStatus.setText("연결완료")
            self.txtLog.appendPlainText("알티노 연결 완료")

            global sensorsOk
            sensorsOk = True
            self.thread1.start()

            # 연결 완료 변수
            global connectQue
            connectQue = True

            # 비상등 작동
            self.thread3.start()
        except Exception as e:
            self.txtLog.appendPlainText(str(e))
            self.txtAltinoStatus.setText("연결오류")
            
    # 알티노 해제
    def altino_deconn(self):
        try:
            global sensorsOk
            sensorsOk = False
            
            global connectQue
            connectQue = False

            Light(0x00)
             
            Go(0, 0)

            Close()
            self.txtLog.appendPlainText("알티노 연결 해제")
            self.txtAltinoStatus.setText("미연결")

            Al_sound("altinoDeconn.mp3")
        except Exception as e:
            self.txtLog.appendPlainText(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Mywindow()
    myWindow.show()
    app.exec_()