import Jetson.GPIO as GPIO
import time

# 사용할 GPIO 핀 (GPIO13 = Pin 33)
CONTROL_PIN = 33  # BOARD 모드 사용 시 Pin 33 (BCM 모드에서는 GPIO 13)

# GPIO 설정
GPIO.setmode(GPIO.BOARD)  # 핀 번호 기반 설정
GPIO.setup(CONTROL_PIN, GPIO.OUT, initial=GPIO.LOW)  # 초기 상태 OFF

def electromagnet_on():
    """ 전자석 ON (HIGH 신호) """
    GPIO.output(CONTROL_PIN, GPIO.HIGH)  # GPIO HIGH로 설정하여 전자석 ON
    print("전자석 ON")

def electromagnet_off():
    """ 전자석 OFF (LOW 신호) """
    GPIO.output(CONTROL_PIN, GPIO.LOW)  # GPIO LOW로 설정하여 전자석 OFF
    print("전자석 OFF")

try:
    while True:
        command = input("1: ON, 2: OFF, 3: 종료\n입력: ")
        if command == "1":
            electromagnet_on()
        elif command == "2":
            electromagnet_off()
        elif command == "3":
            electromagnet_off()
            break
finally:
    GPIO.cleanup()
    print("프로그램 종료 및 GPIO 해제")
