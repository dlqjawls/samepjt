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

"""
이 코드는:
- ArUco 마커를 통한 리턴 위치 정렬
- 정렬 완료 후 `return_until_nfc()` 함수를 통해 NFC 태그 인식까지 후진
- NFC가 감지되면 즉시 정지 및 후속 동작 수행
등을 시도하는 예시 코드입니다.
"""

# =============================================================================
# 1) [TCP 서버 설정 - 라즈베리 파이로부터 센서(NFC) 데이터 수신]
#    (렌트 코드에서 사용한 것과 동일 구조)
# =============================================================================
HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"[TCP 서버] 센서 데이터 수신 대기 중... (IP: {HOST}, PORT: {PORT})")

client_socket, client_address = server_socket.accept()
print(f"클라이언트 연결됨: {client_address}")

def get_sensor_data():
    """
    라즈베리 파이에서 JSON 형태로 센서 데이터를 송신한다고 가정.
    예: {"NFC_UID": "04 A1 BC ..", "ULTRASONIC_FRONT": 12.3, "ULTRASONIC_BACK": 15.4}
    """
    try:
        data = client_socket.recv(1024).decode("utf-8").strip()
        if not data:
            # print("[경고] 센서 데이터 수신 실패 (빈 데이터)")
            return None

        # 여러 줄이 한꺼번에 들어올 수도 있으므로 줄 단위로 처리
        for line in data.splitlines():
            try:
                sensor_data = json.loads(line)
                return sensor_data
            except json.JSONDecodeError:
                print(f"[에러] JSON 파싱 실패 → {line}")
    except Exception as e:
        print(f"[에러] 센서 데이터 수신 오류: {e}")
    return None


# =============================================================================
# 2) 전자석 설정 (렌트 코드와 동일)
# =============================================================================
GPIO.cleanup()
PWM_PIN = 33  # BOARD 모드 핀번호
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)  # 1kHz PWM
pwm.start(0)

def electromagnet_on():
    pwm.ChangeDutyCycle(100)
    print("전자석 ON (100%)")

def electromagnet_off():
    pwm.ChangeDutyCycle(10)
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)
    print("전자석 OFF (잔류 전류 제거)")


# =============================================================================
# 3) [반납 시 NFC 인식 - return_until_nfc()]
#    (렌트 코드의 reverse_until_nfc()와 비슷한 구조)
# =============================================================================
def return_until_nfc(module_name="return_module"):
    """
    - “반납할 위치”에 충분히 정렬이 된 뒤,
    - NFC 태그 인식할 때까지 후진
    - NFC 감지 순간 정지
    - 이후 전자석 등 필요 동작
    """
    print("[return_until_nfc] NFC 인식 전까지 후진 시작...")
    kit.servo[0].angle = 90
    # electromagnet_on()   # 반납 상황에서도 전자석이 필요하다면 On, 필요 없다면 Off
    motor_hat.set_throttle(-0.40)

    # 동영상 녹화 예시
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"{module_name}_return_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    ret, frame = cap.read()
    if not ret:
        print("[에러] 녹화용 첫 프레임 읽기 실패. (카메라?)")
        return
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    fps = 20.0
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

    print("[return_until_nfc] 녹화 중... (NFC 태그를 태깅하면 즉시 정지)")
    nfc_detected = False

    while True:
        # 1) 라즈베리 파이 측 센서 데이터 받기
        sensor_data = get_sensor_data()
        nfc_uid = None
        if sensor_data is not None:
            nfc_uid = sensor_data.get("NFC_UID")

        # 2) 카메라 프레임 저장
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("Aruco Marker Tracking (Return NFC)", frame)

        # 3) NFC 감지 시 즉시 정지
        if nfc_uid:
            print(f"[NFC 감지됨] UID: {nfc_uid} -> 즉시 정지")
            motor_hat.set_throttle(0)
            nfc_detected = True
            time.sleep(2)
            out.release()
            print(f"✅ 녹화 저장 완료: {video_filename}")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[사용자] q 키 입력 -> 중단")
            motor_hat.set_throttle(0)
            out.release()
            return

        time.sleep(0.1)

    # NFC 감지 후 추가 동작 (예: 전자석 Off, or 전진 조금 등)
    if nfc_detected:
        print("[return_until_nfc] 전자석 ON 상태에서 전진 (예시)")
        kit.servo[0].angle = 88
        motor_hat.set_throttle(0.4)
        time.sleep(1.8)
        # electromagnet_off()
        time.sleep(10.0)
        motor_hat.set_throttle(0)
        print("[return_until_nfc] 반납 완료!")


# =============================================================================
# 4) [아루코 세팅 + I2C/모터/서보 설정 (렌트 코드와 유사)]
# =============================================================================
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 60

class PWMThrottleHat:
    def __init__(self, pwm):
        self.pwm = pwm
        self.pwm.frequency = 60
    def set_throttle(self, throttle):
        pulse = min(0xFFFF, max(0, int(0xFFFF * abs(throttle))))
        if throttle < 0:
            # 후진
            self.pwm.channels[5].duty_cycle = pulse
            self.pwm.channels[4].duty_cycle = 0
            self.pwm.channels[3].duty_cycle = 0xFFFF
        elif throttle > 0:
            # 전진
            self.pwm.channels[5].duty_cycle = pulse
            self.pwm.channels[4].duty_cycle = 0xFFFF
            self.pwm.channels[3].duty_cycle = 0
        else:
            # 정지
            self.pwm.channels[5].duty_cycle = 0
            self.pwm.channels[4].duty_cycle = 0
            self.pwm.channels[3].duty_cycle = 0

motor_hat = PWMThrottleHat(pca)
kit = ServoKit(channels=16, i2c=i2c, address=0x60)
kit.servo[0].angle = 88

# =============================================================================
# 5) [반납할 마커 ID & PID 설정 + 카메라 & 메인 루프]
# =============================================================================
target_marker_id = int(input("반납할 장소의 마커 ID를 입력하세요 (예: 11): "))

target_size = 8000
max_speed = 0.40
min_speed = 0.20

from simple_pid import PID
pid_x = PID(0.06, 0.013, 0.004, setpoint=0)
pid_rotation = PID(0.055, 0.011, 0.0035, setpoint=0)
pid_speed = PID(0.022, 0.007, 0.0018, setpoint=target_size)

def calculate_x_rotation(corner):
    top_left, top_right, bottom_right, bottom_left = corner[0]
    height_left = bottom_left[1] - top_left[1]
    height_right = bottom_right[1] - top_right[1]
    if height_left>0 and height_right>0:
        rotate_angle = int(round(
            math.degrees(math.atan((height_right - height_left)/(top_right[0]-top_left[0]))))) * 2
        rotate_angle = max(min(rotate_angle, 90), -90)
        return rotate_angle
    return 0

def gstreamer_pipeline(sensor_id=1, capture_width=1920, capture_height=1080,
                       display_width=640, display_height=360, framerate=30, flip_method=0):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=%d, height=%d, framerate=%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=%d, height=%d, format=BGRx ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink sync=false"
        % (sensor_id, capture_width, capture_height, framerate,
           flip_method, display_width, display_height)
    )

cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("[에러] CSI 카메라를 열 수 없음.")
    exit()

alignment_start_time = None
lost_target_time = None

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[에러] 프레임 읽기 실패")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        target_found = False
        if ids is not None:
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id != target_marker_id:
                    continue
                target_found = True

                if alignment_start_time is None:
                    alignment_start_time = time.time()

                # 마커 위치/크기 계산
                cX = int(np.mean(corner[0][:, 0]))
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height
                x_rotation = calculate_x_rotation(corner)
                frame_center_x = frame.shape[1]//2
                error_x = cX - frame_center_x

                # 정렬 완료 조건
                if (abs(error_x) < 10 and abs(x_rotation) < 2
                    and abs(object_size - target_size)< target_size*0.1):
                    print("[INFO] Return marker reached, stop & do NFC logic")
                    motor_hat.set_throttle(0)
                    time.sleep(2)

                    # 곧바로 NFC 인식(후진)
                    return_until_nfc(module_name="return_place")
                    # 이후 필요 시 break
                    break
                else:
                    # PID 제어(전/후진 & 조향)
                    steer_adjust = pid_x(error_x)
                    rotation_adjust = pid_rotation(x_rotation)
                    final_steering_adjust = 0.7*steer_adjust + 0.3*rotation_adjust

                    if object_size>target_size*1.1:
                        # 가까워서 전진
                        new_steering = kit.servo[0].angle
                        new_steering = max(68, min(108, new_steering - final_steering_adjust))
                        kit.servo[0].angle = new_steering

                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        motor_hat.set_throttle(speed_adjust)

                    elif object_size<target_size*0.9:
                        # 멀어서 후진
                        new_steering = kit.servo[0].angle
                        new_steering = max(68, min(108, new_steering + final_steering_adjust))
                        kit.servo[0].angle = new_steering

                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        motor_hat.set_throttle(-speed_adjust)

            if target_found:
                lost_target_time = None
            else:
                if lost_target_time is None:
                    lost_target_time = time.time()
                elif time.time() - lost_target_time > 1.0:
                    print("[INFO] Marker lost, moving forward..")
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.3)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time() - lost_target_time > 1.0:
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)

        cv2.imshow("Return Marker Tracking", frame)
        if cv2.waitKey(1)&0xFF == ord('q'):
            break
        time.sleep(0.01)

except KeyboardInterrupt:
    pass

finally:
    motor_hat.set_throttle(0)
    kit.servo[0].angle = 88
    pca.deinit()
    cap.release()
    cv2.destroyAllWindows()
    print("Return program finished, motor stopped.")
