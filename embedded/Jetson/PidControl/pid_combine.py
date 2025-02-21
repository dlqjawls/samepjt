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
- ArUco 마커 추적 및 PID 제어
- 라즈베리 파이에서 넘어오는 NFC UID 체크
- 정렬 완료 시 reverse_until_nfc()에서 후진 → NFC 태그 감지 시 정지
등을 수행하는 예시 코드입니다.
"""

# =============================================================================
# [TCP 서버 설정 - 라즈베리 파이와 통신]
# =============================================================================
HOST = "0.0.0.0"  # Jetson이 모든 인터페이스에서 연결 대기
PORT = 5000       # Raspberry Pi에서 connect((JETSON_IP, PORT))와 동일해야 함

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"[TCP 서버] 센서 데이터 수신 대기 중... (IP: {HOST}, PORT: {PORT})")

client_socket, client_address = server_socket.accept()
print(f"클라이언트 연결됨: {client_address}")

def get_sensor_data():
    """
    라즈베리 파이에서 센서 데이터를 JSON 형태로 송신한다고 가정.
    예: {"NFC_UID": "04 A1 BC ..", "ULTRASONIC_FRONT": 12.3, "ULTRASONIC_BACK": 15.4} 등
    """
    try:
        data = client_socket.recv(1024).decode("utf-8").strip()
        if not data:
            print("[경고] 센서 데이터 수신 실패 (빈 데이터)")
            return None

        # 여러 줄이 한 번에 들어올 수 있으므로, 줄 단위로 split 후 처리
        for line in data.splitlines():
            try:
                sensor_data = json.loads(line)
                return sensor_data
            except json.JSONDecodeError:
                print(f"[에러] JSON 파싱 실패 → {line}")
    except Exception as e:
        print(f"[에러] 센서 데이터 수신 오류: {e}")
    return None


# 기존 설정 초기화 (기존 GPIO 모드 해제)
GPIO.cleanup()

# 전자석 설정
PWM_PIN = 33  # BOARD 모드 사용 시 Pin 33
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)  # 1kHz PWM
pwm.start(0)  # 초기 OFF

def electromagnet_on():
    """전자석 ON (100% Duty)"""
    pwm.ChangeDutyCycle(100)
    print("전자석 ON (100% 출력)")

def electromagnet_off():
    """전자석 OFF (잔류 전류 제거 후 0%)"""
    pwm.ChangeDutyCycle(10)
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)
    print("전자석 OFF (잔류 전류 제거 완료)")

# =============================================================================
# [ArUco 마커 - 완전 정렬된 상태에서 후진 + NFC 감지 로직]
# =============================================================================
def reverse_until_nfc(module_name="module"):
    """
    - 모듈 정렬이 완료된 뒤, NFC 감지 전까지 후진 (녹화)
    - NFC 태그가 감지되는 순간(라즈베리 파이 측 UID가 들어오면) 정지
    - 전자석 켠 상태로 살짝 전진 후 OFF
    """
    print("NFC 인식 전까지 후진 시작...")
    kit.servo[0].angle = 90
    electromagnet_on()
    motor_hat.set_throttle(-0.30)  # 천천히 후진

    # 녹화 설정
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"{module_name}_combine_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    ret, frame = cap.read()
    if not ret:
        print("[에러] 녹화용 첫 프레임 읽기 실패.")
        return
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    fps = 20.0
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

    print("녹화 중... (NFC 카드를 태깅하면 즉시 정지)")

    while True:
        # 1) 라즈베리 파이에서 센서 데이터 수신 (NFC_UID 확인)
        sensor_data = get_sensor_data()
        if sensor_data is not None:
            nfc_uid = sensor_data.get("NFC_UID")  # "04 F3 ..." 등의 문자열 또는 None
        else:
            nfc_uid = None

        # 2) 카메라 프레임 녹화
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("Aruco Marker Tracking (NFC Detection)", frame)

        # 3) NFC 감지되면(UID가 None이 아님) → 즉시 정지
        if nfc_uid:
            print(f"[NFC 감지됨] UID: {nfc_uid}, 즉시 정지")
            motor_hat.set_throttle(0)
            time.sleep(2)
            out.release()
            print(f"✅ 녹화 저장 완료: {video_filename}")
            break

        # 'q' 키로 강제 종료 가능
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[사용자] q 키 입력으로 중단합니다.")
            motor_hat.set_throttle(0)
            out.release()
            return

        time.sleep(0.1)

    # NFC 태그 후 동작: 전자석 ON 상태에서 전진
    print("전자석 ON 상태에서 전진 시작...")
    kit.servo[0].angle = 88
    motor_hat.set_throttle(0.4)
    time.sleep(1.8)
    electromagnet_off()
    time.sleep(10.0)
    motor_hat.set_throttle(0)
    print("전진 완료, 전자석 OFF 후 정지")
    print("모듈 장착 완료, 전자석 작업 종료")

# =============================================================================
# [ArUco 마커 설정 및 I2C/모터/서보 설정]
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
        """PWM 채널들을 사용해 모터 속도 제어 (전진/후진/정지)"""
        pulse = min(0xFFFF, max(0, int(0xFFFF * abs(throttle))))
        if throttle < 0:
            # 후진 방향
            self.pwm.channels[5].duty_cycle = pulse
            self.pwm.channels[4].duty_cycle = 0
            self.pwm.channels[3].duty_cycle = 0xFFFF
        elif throttle > 0:
            # 전진 방향
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
# [사용자 입력: 목표 마커 ID, PID 파라미터]
# =============================================================================
target_marker_id = int(input("장착할 마커의 ID를 입력하세요: "))

module_name_mapping = {
    1: "camping module",
    2: "office module"
}
target_size = 8000
max_speed = 0.40
min_speed = 0.20
loop_time = 0.2

# PID 제어기
pid_x = PID(0.06, 0.013, 0.004, setpoint=0)
pid_rotation = PID(0.055, 0.011, 0.0035, setpoint=0)
pid_speed = PID(0.022, 0.007, 0.0018, setpoint=target_size)

lost_object_time = None
lost_target_time = None
stop_movement = False
alignment_start_time = None

# =============================================================================
# [CSI 카메라 설정: GStreamer 파이프라인]
# =============================================================================
def gstreamer_pipeline(sensor_id=1, capture_width=1920, capture_height=1080,
                       display_width=640, display_height=360, framerate=30, flip_method=0):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=%d, height=%d, framerate=%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=%d, height=%d, format=BGRx ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink sync=false"
        % (sensor_id, capture_width, capture_height,
           framerate, flip_method, display_width, display_height)
    )

cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("[에러] CSI 카메라를 열 수 없습니다.")
    exit()

def calculate_x_rotation(corner):
    """ X축 회전각 계산 (기울기 측정) """
    top_left, top_right, bottom_right, bottom_left = corner[0]
    height_left = bottom_left[1] - top_left[1]
    height_right = bottom_right[1] - top_right[1]
    if height_left > 0 and height_right > 0:
        rotate_angle = int(round(math.degrees(math.atan((height_right - height_left) /
                                                        (top_right[0] - top_left[0]))))) * 2
        rotate_angle = max(min(rotate_angle, 90), -90)
    else:
        rotate_angle = 0
    return rotate_angle

# =============================================================================
# [메인 루프: ArUco 마커 추적 + PID 제어 + 정렬 완료 시 reverse_until_nfc 호출]
# =============================================================================
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[에러] 프레임 읽기 실패.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        target_found = False

        if ids is not None:
            # 검출된 마커 중 목표 마커만 확인
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id != target_marker_id:
                    continue

                target_found = True
                if alignment_start_time is None:
                    alignment_start_time = time.time()

                # 마커 정보 계산
                cv2.polylines(frame, [np.int32(corner)], True, (0, 255, 0), 2)
                cX = int(np.mean(corner[0][:, 0]))
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height
                x_rotation = calculate_x_rotation(corner)
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x

                # 표시용 텍스트
                module_name = module_name_mapping.get(marker_id, f"ID {marker_id}")
                cv2.putText(frame, f"{module_name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"size: {int(object_size)}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"parallel: {'yes' if abs(x_rotation)<3 else 'no'}", (50, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0,255,0) if abs(x_rotation)<3 else (0,0,255), 2)
                cv2.putText(frame, f"center: {'yes' if abs(error_x)<15 else 'no'}", (50, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0,255,0) if abs(error_x)<15 else (0,0,255), 2)

                # 정렬 완료 조건
                if (abs(error_x)<10 and abs(x_rotation)<2 and
                        abs(object_size - target_size) < target_size*0.1):
                    print("[INFO] Target marker reached, stopping movement.")
                    motor_hat.set_throttle(0)
                    stop_movement = True
                    time.sleep(3)

                    # PID 정렬 소요 시간 로그
                    if alignment_start_time is not None:
                        alignment_time = time.time() - alignment_start_time
                        with open("pid_combine_log.csv", "a") as f:
                            log_line = (
                                f"{pid_x.Kp},{pid_x.Ki},{pid_x.Kd},"
                                f"{pid_rotation.Kp},{pid_rotation.Ki},{pid_rotation.Kd},"
                                f"{pid_speed.Kp},{pid_speed.Ki},{pid_speed.Kd},"
                                f"{alignment_time}\n"
                            )
                            f.write(log_line)
                        print(f"[INFO] Alignment time: {alignment_time:.2f} seconds logged.")
                        alignment_start_time = None

                    # 모듈 정렬 완료 후 → NFC 태깅 대기하면서 후진
                    reverse_until_nfc(module_name=module_name)

                    # 이후 원하는 좌표 등 입력
                    target_x = input("목표 X 좌표 (기본값: 100): ")
                    target_y = input("목표 Y 좌표 (기본값: 150): ")
                else:
                    # 아직 정렬 안 됐다면 PID 제어 (전/후진 및 조향)
                    # 예제 코드 그대로
                    if object_size > target_size*1.1 and (abs(error_x)>10 or abs(x_rotation)>2):
                        print("Oversized & misaligned, adjusting position...")
                        steer_adjust = pid_x(error_x)
                        rotation_adjust = pid_rotation(x_rotation)
                        final_steering_adjust = 0.7*steer_adjust + 0.3*rotation_adjust

                        # 전진 시 조향(88 기준)
                        new_steering = 88 - (kit.servo[0].angle - 88)
                        new_steering = max(68, min(108, new_steering + final_steering_adjust))
                        kit.servo[0].angle = new_steering
                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        motor_hat.set_throttle(speed_adjust)
                        print(f"[전진] speed={speed_adjust:.2f}, steering={new_steering:.2f}")

                    elif object_size < target_size*0.9 and (abs(error_x)>10 or abs(x_rotation)>2):
                        print("Small & misaligned, adjusting position...")
                        steer_adjust = pid_x(error_x)
                        rotation_adjust = pid_rotation(x_rotation)
                        final_steering_adjust = 0.7*steer_adjust + 0.3*rotation_adjust

                        # 후진 시 조향(현재 각도 + 조정)
                        new_steering = min(108, max(68, kit.servo[0].angle + final_steering_adjust))
                        kit.servo[0].angle = new_steering
                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        motor_hat.set_throttle(-speed_adjust)
                        print(f"[후진] speed={-speed_adjust:.2f}, steering={new_steering:.2f}")

        # 목표 마커 추적 못 하면 일정 시간 뒤 전진
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time() - lost_target_time > 1.0:
                print("[INFO] Target marker lost, moving forward to find it...")
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)

        if target_found:
            lost_target_time = None

        cv2.imshow("Aruco Marker Tracking (PID)", frame)
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
