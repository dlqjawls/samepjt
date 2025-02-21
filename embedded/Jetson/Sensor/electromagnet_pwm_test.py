import Jetson.GPIO as GPIO
import time

# 사용할 PWM 핀 (GPIO13 = Pin 33, PWM5)
PWM_PIN = 33  # BOARD 모드 사용 시 Pin 33 (BCM 모드에서는 GPIO 13)

# GPIO 설정
GPIO.setmode(GPIO.BOARD)  # 핀 번호 기반 설정
GPIO.setup(PWM_PIN, GPIO.OUT)  # 출력 모드 설정

# PWM 객체 생성 (1kHz 주파수)
pwm = GPIO.PWM(PWM_PIN, 1000)  # 1kHz PWM 신호 생성
pwm.start(0)  # 초기 상태 OFF (0% 듀티 사이클)

def electromagnet_on():
    """ 전자석을 100% 출력으로 켜기 """
    pwm.ChangeDutyCycle(100)  # 100% 듀티 사이클 (전자석 ON)
    print("전자석 ON (100% 출력)")

def electromagnet_off():
    """ 전자석을 완전히 끄기 (잔류 전류 제거) """
    pwm.ChangeDutyCycle(10)  # 약한 PWM을 짧게 줘서 잔류 전류 제거
    time.sleep(0.1)  # 0.1초 동안 유지
    pwm.ChangeDutyCycle(0)  # PWM 0%로 설정하여 완전히 OFF
    print("전자석 OFF (잔류 전류 제거 완료)")

def set_magnetic_strength(strength):
    """ 자기장 강도를 설정 (0~100%) """
    pwm.ChangeDutyCycle(strength)
    print(f"자기장 강도: {strength}%")

try:
    while True:
        command = input("1: ON (100%), 2: OFF, 3: 강도 설정, 4: 종료\n입력: ")
        if command == "1":
            electromagnet_on()
        elif command == "2":
            electromagnet_off()
        elif command == "3":
            strength = int(input("자기장 강도 (0-100): "))
            if 0 <= strength <= 100:
                set_magnetic_strength(strength)
            else:
                print("잘못된 입력 (0~100 입력)")
        elif command == "4":
            electromagnet_off()
            break
finally:
    pwm.ChangeDutyCycle(0)  # 종료 시 PWM을 0%로 설정
    GPIO.cleanup()
    print("프로그램 종료 및 GPIO 해제")
