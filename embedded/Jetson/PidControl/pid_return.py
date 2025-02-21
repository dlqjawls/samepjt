import cv2
import numpy as np
import math
import time
import datetime
import board
import busio
import socket
import json
import Jetson.GPIO as GPIO
from simple_pid import PID
from adafruit_motor import motor
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit

# -------------------------------
# TCP 서버 설정 (원래 라즈베리 파이와 통신하는 부분)
# 테스트를 위해 아래 코드는 주석 처리하거나 제거하고 진행할 수 있습니다.
# HOST = "0.0.0.0"  # 모든 인터페이스에서 수신
# PORT = 5000       # Raspberry Pi 5에서 전송하는 포트

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((HOST, PORT))
# server_socket.listen(1)
# print(f"[TCP 서버] 센서 데이터 수신 대기 중... (IP: {HOST}, PORT: {PORT})")
# client_socket, client_address = server_socket.accept()
# print(f"클라이언트 연결됨: {client_address}")

# def get_sensor_data():
#     """ Raspberry Pi 5에서 센서 데이터를 수신 (JSON 데이터 정리) """
#     try:
#         data = client_socket.recv(1024).decode("utf-8").strip()  # 수신 및 공백 제거
#         if not data:
#             print("센서 데이터 수신 실패 (빈 데이터)")
#             return None
#         for line in data.splitlines():
#             try:
#                 sensor_data = json.loads(line)
#                 return sensor_data
#             except json.JSONDecodeError:
#                 print(f"센서 데이터 수신 오류: JSON 파싱 실패 (잘못된 형식) → {line}")
#     except Exception as e:
#         print(f"센서 데이터 수신 오류: {e}")
#     return None

# -------------------------------
# 테스트 시 TCP 통신 없이 실행하려면 위 부분을 주석 처리하고 get_sensor_data() 대신
# 터미널 입력 등으로 대체할 수 있습니다.
# -------------------------------

# 기존 설정 초기화 (기존 GPIO 모드 해제)
GPIO.cleanup()

# 전자석 설정
PWM_PIN = 33  # BOARD 모드 사용 시 Pin 33
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)  # 1kHz PWM 신호 생성
pwm.start(0)  # 초기 OFF

def electromagnet_on():
    """전자석을 100% 출력으로 켜기"""
    pwm.ChangeDutyCycle(100)
    print("전자석 ON (100% 출력)")

def electromagnet_off():
    """전자석을 완전히 끄기 (잔류 전류 제거)"""
    pwm.ChangeDutyCycle(10)  # 잔류 전류 제거
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)   # 완전 OFF
    print("전자석 OFF (잔류 전류 제거 완료)")

def reverse_until_nfc(module_name="module"):
    """
    NFC 감지 전까지 후진 후, 터미널 입력(Enter 키)으로 NFC 인식을 시뮬레이션하고
    녹화하면서 후진 → 전진 동작을 수행하는 함수.
    녹화 설정은 제공된 코드의 방식(XVID 코덱, fps=20, .avi 확장자, 프레임 크기는 cap에서 읽은 값)을 사용.
    """
    print("NFC 인식 전까지 후진 시작...")
    kit.servo[0].angle = 90
    # electromagnet_on()  # 전자석 켜기
    motor_hat.set_throttle(-0.30)  # 천천히 후진

    # 영상 녹화 설정 (참고 코드 기반)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"{module_name}combie{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # 캡처된 프레임의 크기를 사용 (녹화 시점에 한 프레임 읽기)
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame for video recording.")
        return
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    fps = 20.0  # fps 설정 (참고 코드: 20.0)
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))
    print("녹화 시작 중... (NFC 감지 시 Enter 키를 누르세요)")
    
    # 후진 중 녹화 & 화면 출력
    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("Aruco Marker Tracking (NFC Detection)", frame)
            cv2.waitKey(1)
        # NFC 센서 대신 터미널에서 Enter 키 입력으로 NFC 감지 시뮬레이션
        user_input = input("NFC 태그 감지 시 Enter 키를 누르세요: ")
        if user_input == "":
            print("NFC 감지됨! UID: SIMULATED_UID, 즉시 정지")
            motor_hat.set_throttle(0)  # 후진 중단
            time.sleep(2)  # 2초 유지
            out.release()   # 녹화 종료 및 저장
            print(f"✅ 녹화 저장 완료: {video_filename}")
            break
        time.sleep(0.1)  # 100ms 대기

    # 전진 동작 (5초 동안 전진하며 화면 출력)
    print("전자석 ON 상태에서 전진 시작 (5초)")
    kit.servo[0].angle = 88
    motor_hat.set_throttle(0.3)  # 천천히 전진
    time.sleep(2.0)
    # electromagnet_off()
    time.sleep(4.5)
    motor_hat.set_throttle(0)
    print("전진 완료, 전자석 OFF 후 정지")
    print("모듈 장착 완료, 전자석 작업 종료 및 정지")

# ArUco 마커 설정
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

# I2C 및 모터/서보 설정
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 60

class PWMThrottleHat:
    def __init__(self, pwm):
        self.pwm = pwm
        self.pwm.frequency = 60

    def set_throttle(self, throttle):
        """PWM 신호를 조정하여 모터 속도 제어 (값 범위 제한 추가)"""
        pulse = min(0xFFFF, max(0, int(0xFFFF * abs(throttle))))
        if throttle < 0:  # 후진 (목표 접근)
            self.pwm.channels[5].duty_cycle = pulse
            self.pwm.channels[4].duty_cycle = 0
            self.pwm.channels[3].duty_cycle = 0xFFFF
        elif throttle > 0:  # 전진 (목표에서 멀어짐)
            self.pwm.channels[5].duty_cycle = pulse                    
            self.pwm.channels[4].duty_cycle = 0xFFFF
            self.pwm.channels[3].duty_cycle = 0
        else:  # 정지
            self.pwm.channels[5].duty_cycle = 0
            self.pwm.channels[4].duty_cycle = 0
            self.pwm.channels[3].duty_cycle = 0

motor_hat = PWMThrottleHat(pca)
kit = ServoKit(channels=16, i2c=i2c, address=0x60)
kit.servo[0].angle = 88  # 초기 조향값 설정

# 사용자 입력 (목표 마커 크기 및 이동 속도 설정)
target_size = float(input("목표 객체 크기 (5000~75000 추천, 기본값: 11000): ") or 11000)
max_speed = float(input("최대 전진 속도 (0.2~0.5, 기본값: 0.30): ") or 0.30)
min_speed = float(input("최소 전진 속도 (0.05~0.2, 기본값: 0.10): ") or 0.10)
loop_time = float(input("루프 주기(초, 0.1~1.0, 기본값: 0.2): ") or 0.2)

# PID 제어기 설정 (값 조정)
pid_x = PID(0.07, 0.015, 0.005, setpoint=0)         # 중앙 정렬용 PID (조향)
pid_rotation = PID(0.06, 0.012, 0.004, setpoint=0)    # X축 평행 정렬용 PID
pid_speed = PID(0.025, 0.008, 0.002, setpoint=target_size)  # 목표 크기 조정용 PID

# 객체 인식 손실 감지 변수
lost_object_time = None  # 객체를 인식하지 못한 시간 저장

# GStreamer 파이프라인 사용 (CSI 카메라)
def gstreamer_pipeline(sensor_id=1, capture_width=1920, capture_height=1080,
                       display_width=640, display_height=360, framerate=30, flip_method=0):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=%d, height=%d, framerate=%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=%d, height=%d, format=BGRx ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink sync=false"
        % (sensor_id, capture_width, capture_height, framerate, flip_method, display_width, display_height)
    )

cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("Error: Could not open CSI camera.")
    exit()

def calculate_x_rotation(corner):
    """X축 회전각 계산 (기울기 보정)"""
    top_left, top_right, bottom_right, bottom_left = corner[0]
    height_left = bottom_left[1] - top_left[1]
    height_right = bottom_right[1] - top_right[1]
    if height_left > 0 and height_right > 0:
        rotate_angle = int(round(math.degrees(math.atan((height_right - height_left) / (top_right[0] - top_left[0]))))) *2
        rotate_angle = max(min(rotate_angle, 90), -90)
    else:
        rotate_angle = 0
    return rotate_angle

try:
    while True:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            lost_object_time = None  # 객체 인식되었으므로 리셋

            for i, corner in enumerate(corners):
                cv2.polylines(frame, [np.int32(corner)], isClosed=True, color=(0, 255, 0), thickness=2)
                cX = int(np.mean(corner[0][:, 0]))  # 마커 중심 계산
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height  # 마커 면적
                x_rotation = calculate_x_rotation(corner)  # X축 회전각 계산
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x  # 중앙 오차 계산

                cv2.putText(frame, f"size: {int(object_size)}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"parallel: {'yes' if abs(x_rotation) < 3 else 'no'}", (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 0) if abs(x_rotation) < 3 else (0, 0, 255), 2)
                cv2.putText(frame, f"center: {'yes' if abs(error_x) < 15 else 'no'}", (50, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 0) if abs(error_x) < 15 else (0, 0, 255), 2)
                cv2.imshow("Aruco Marker Tracking (PID)", frame)

                # 목표 도달 여부 확인
                if abs(error_x) < 10 and abs(x_rotation) < 2 and abs(object_size - target_size) < target_size * 0.1:
                    print("Target reached, stopping movement.")
                    motor_hat.set_throttle(0)
                    stop_movement = True  # 정지 상태 유지
                    time.sleep(3)  # 3초 정지
                    module_name = input("🚀 모듈 이름을 입력하세요 (기본값: module): ") or "module"
                    # NFC 감지 전까지 녹화 및 후진 진행 (터미널 입력으로 NFC 시뮬레이션)
                    reverse_until_nfc(module_name=module_name)
                    target_x = input("목표 X 좌표 (기본값: 100): ")
                    target_y = input("목표 Y 좌표 (기본값: 150): ")
                    continue  # 다음 프레임 처리

                stop_movement = False  # 목표 미달 시 계속 진행

                # PID 기반 보정 로직
                if object_size > target_size * 1.1 and (abs(error_x) > 10 or abs(x_rotation) > 2):
                    print("Oversized & misaligned, adjusting position...")
                    
                    # 중앙 정렬 + 평행 정렬 조합
                    steer_adjust = pid_x(error_x)
                    rotation_adjust = pid_rotation(x_rotation)
                    final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)
                    new_steering = 88 - (kit.servo[0].angle - 88)
                    new_steering = max(68, min(108, new_steering + final_steering_adjust))
                    kit.servo[0].angle = new_steering
                    print(f"Steering Adjust: {steer_adjust:.2f}, Parallel Adjust: {rotation_adjust:.2f}")
                    print(f"Final Steering Adjust: {final_steering_adjust:.2f}, New Steering: {new_steering}")
                    
                    # 속도 조정
                    speed_adjust = pid_speed(object_size)
                    speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                    motor_hat.set_throttle(speed_adjust)
                    print(f"Moving at speed {-speed_adjust:.2f} (Backward), Object Size: {int(object_size)}")
                
                elif object_size < target_size * 0.9 and (abs(error_x) > 10 or abs(x_rotation) > 2):
                    print("Small & misaligned, adjusting position...")
                    
                    # 중앙 정렬 + 평행 정렬 조합
                    steer_adjust = pid_x(error_x)
                    rotation_adjust = pid_rotation(x_rotation)
                    final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)
                    new_steering = min(108, max(68, kit.servo[0].angle + final_steering_adjust))
                    kit.servo[0].angle = new_steering
                    print(f"Steering Adjust: {steer_adjust:.2f}, Parallel Adjust: {rotation_adjust:.2f}")
                    print(f"Final Steering Adjust: {final_steering_adjust:.2f}, New Steering: {new_steering}")
                    
                    # 속도 조정
                    speed_adjust = pid_speed(object_size)
                    speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                    motor_hat.set_throttle(-speed_adjust)
                    print(f"Moving at speed {-speed_adjust:.2f} (Backward), Object Size: {int(object_size)}")

        else:
            # 객체 인식 손실 감지 로직
            if lost_object_time is None:
                lost_object_time = time.time()
            
            # 객체 인식 손실 감지 시 전진 로직
            elif time.time() - lost_object_time > 1.0:
                print("Object lost, moving forward to find it...")
                kit.servo[0].angle = 88
                motor_hat.set_throttle(max_speed)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

finally:
    motor_hat.set_throttle(0)
    kit.servo[0].angle = 88
    pca.deinit()
    cap.release()
    cv2.destroyAllWindows()
    print("Program stopped and motor stopped.")
