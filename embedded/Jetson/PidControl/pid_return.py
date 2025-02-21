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
#
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((HOST, PORT))
# server_socket.listen(1)
# print(f"[TCP 서버] 센서 데이터 수신 대기 중... (IP: {HOST}, PORT: {PORT})")
# client_socket, client_address = server_socket.accept()
# print(f"클라이언트 연결됨: {client_address}")
#
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
    모듈 이름은 입력받는 대신, 목표 마커의 매핑된 이름을 사용합니다.
    """
    print("NFC 인식 전까지 후진 시작...")
    kit.servo[0].angle = 90
    motor_hat.set_throttle(-0.40)  # 천천히 후진

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"{module_name}_return_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    ret, frame = cap.read()  # 녹화 시점에 한 프레임 읽어서 프레임 크기 결정
    if not ret:
        print("Error: Could not read frame for video recording.")
        return
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    fps = 20.0  # fps 설정
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))
    print("녹화 시작 중... (NFC 감지 시 'n' 키를 누르세요)")
    
    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("Aruco Marker Tracking (NFC Detection)", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('n'):
            print("NFC 감지됨! UID: SIMULATED_UID, 즉시 정지")
            motor_hat.set_throttle(0)
            time.sleep(2)
            out.release()
            print(f"✅ 녹화 저장 완료: {video_filename}")
            break
        time.sleep(0.1)
    
    print("전자석 ON 상태에서 전진 시작 (5초)")
    kit.servo[0].angle = 88
    motor_hat.set_throttle(0.4)
    time.sleep(2.0)
    # electromagnet_off()
    time.sleep(8.0)
    motor_hat.set_throttle(0)
    print("전진 완료, 전자석 OFF 후 정지")
    print("모듈 장착 완료, 전자석 작업 종료 및 정지")

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
        """PWM 신호를 조정하여 모터 속도 제어 (값 범위 제한 추가)"""
        pulse = min(0xFFFF, max(0, int(0xFFFF * abs(throttle))))
        if throttle < 0:
            self.pwm.channels[5].duty_cycle = pulse
            self.pwm.channels[4].duty_cycle = 0
            self.pwm.channels[3].duty_cycle = 0xFFFF
        elif throttle > 0:
            self.pwm.channels[5].duty_cycle = pulse                    
            self.pwm.channels[4].duty_cycle = 0xFFFF
            self.pwm.channels[3].duty_cycle = 0
        else:
            self.pwm.channels[5].duty_cycle = 0
            self.pwm.channels[4].duty_cycle = 0
            self.pwm.channels[3].duty_cycle = 0

motor_hat = PWMThrottleHat(pca)
kit = ServoKit(channels=16, i2c=i2c, address=0x60)
kit.servo[0].angle = 88  # 초기 조향값 설정

# =============================================================================
# [사용자 입력: 목표 마커 크기, 속도, 루프 주기]
# =============================================================================
# -------------------------------
# [장착할 마커의 ID에 따른 모듈 이름 매핑]
# -------------------------------
# 여기서는 정렬할 마커 ID를 입력받고, id 11은 "return place"로 매핑합니다.
target_marker_id = int(input("정렬할 마커의 ID를 입력하세요 (예: 11): "))

module_name_mapping = {
    11: "return place"
}

target_size = 8000
max_speed = 0.30
min_speed = 0.20
loop_time = 0.2

# =============================================================================
# [PID 제어기 설정]
# =============================================================================
pid_x = PID(0.06, 0.013, 0.004, setpoint=0)
pid_rotation = PID(0.055, 0.011, 0.0035, setpoint=0)
pid_speed = PID(0.022, 0.007, 0.0018, setpoint=target_size)


lost_object_time = None
lost_target_time = None
stop_movement = False

alignment_start_time = None  # 타겟 마커의 정렬 시작 시각

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
        % (sensor_id, capture_width, capture_height, framerate, flip_method, display_width, display_height)
    )

cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("Error: Could not open CSI camera.")
    exit()

def calculate_x_rotation(corner):
    """ X축 회전각 계산 (기울기 보정) """
    top_left, top_right, bottom_right, bottom_left = corner[0]
    height_left = bottom_left[1] - top_left[1]
    height_right = bottom_right[1] - top_right[1]
    if height_left > 0 and height_right > 0:
        rotate_angle = int(round(math.degrees(math.atan((height_right - height_left) / (top_right[0] - top_left[0]))))) * 2
        rotate_angle = max(min(rotate_angle, 90), -90)
    else:
        rotate_angle = 0
    return rotate_angle

# =============================================================================
# [메인 루프]
# =============================================================================
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

        target_found = False  # 목표 마커가 검출되었는지 여부

        if ids is not None:
            lost_object_time = None
            # 검출된 마커 중 목표 마커만 처리 (target_marker_id에 해당하는 마커만 표시)
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id != target_marker_id:
                    continue

                # 목표 마커에 대해 테두리, 모듈 이름, 객체 크기, 평행 및 중앙 정렬 상태 표시
                cv2.polylines(frame, [np.int32(corner)], isClosed=True, color=(0, 255, 0), thickness=2)
                cX = int(np.mean(corner[0][:, 0]))  # 마커 중심 계산
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height  # 마커 면적
                x_rotation = calculate_x_rotation(corner)  # X축 회전각 계산
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x # 중앙 오차 계산

                # 화면에 표시 (순서: 모듈 이름, 사이즈, 평행 정렬, 중앙 정렬)
                module_name = module_name_mapping.get(marker_id, f"ID {marker_id}")
                cv2.putText(frame, f"{module_name}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"size: {int(object_size)}", (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"parallel: {'yes' if abs(x_rotation) < 3 else 'no'}", (50, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0,255,0) if abs(x_rotation) < 3 else (0,0,255), 2)
                cv2.putText(frame, f"center: {'yes' if abs(error_x) < 15 else 'no'}", (50, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0,255,0) if abs(error_x) < 15 else (0,0,255), 2)
                cv2.imshow("Aruco Marker Tracking (PID)", frame)

                target_found = True
                if alignment_start_time is None:
                    alignment_start_time = time.time()  # 정렬 시도 시작 시간 기록

                # 목표 도달 여부 확인 (정렬 완료 조건)
                if abs(error_x) < 10 and abs(x_rotation) < 2 and abs(object_size - target_size) < target_size * 0.1:
                    print("Target marker reached, stopping movement.")
                    motor_hat.set_throttle(0)
                    stop_movement = True  # 정지 상태 유지
                    time.sleep(3)
                    # PID 정렬 완료까지 걸린 시간 계산 및 로그 저장
                    if alignment_start_time is not None:
                        alignment_time = time.time() - alignment_start_time
                        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        with open("pid_return_log.csv", "a") as f:
                            # 로그 형식: timestamp, pid_x:Kp,Ki,Kd, pid_rotation:Kp,Ki,Kd, pid_speed:Kp,Ki,Kd, alignment_time
                            log_line = f"{pid_x.Kp},{pid_x.Ki},{pid_x.Kd},{pid_rotation.Kp},{pid_rotation.Ki},{pid_rotation.Kd},{pid_speed.Kp},{pid_speed.Ki},{pid_speed.Kd},{alignment_time}\n"
                            f.write(log_line)
                        print(f"Alignment time: {alignment_time:.2f} seconds logged.")
                        alignment_start_time = None
                    # NFC 감지 전까지 녹화 및 후진 (파일명은 목표 마커의 매핑된 모듈 이름 사용)
                    reverse_until_nfc(module_name=module_name)
                    target_x = input("목표 X 좌표 (기본값: 100): ")
                    target_y = input("목표 Y 좌표 (기본값: 150): ")
                    continue
                else:
                    # PID 제어 로직 (목표 마커가 정렬되지 않은 경우)
                    if object_size > target_size * 1.1 and (abs(error_x) > 10 or abs(x_rotation) > 2):
                        print("Oversized & misaligned, adjusting position...")
                        
                        # 중앙 정렬 + 평행 정렬 조합
                        # pid_x: 중앙 정렬 오차에 따른 보정값 계산
                        steer_adjust = pid_x(error_x)
                        # pid_rotation: 평행 정렬 오차에 따른 보정값 계산
                        rotation_adjust = pid_rotation(x_rotation)
                        # 두 보정값을 가중치(70%, 30%)로 결합하여 최종 조향 보정값 산출
                        final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)
                        
                        # 가까워질수록 보정 배율을 높이기 위한 게인 스케줄링
                        error_ratio = abs(object_size - target_size) / target_size
                        alpha = 1.0  # 추가 배율 상수 (튜닝 가능)
                        multiplier = 1 + (1 - min(error_ratio, 1)) * alpha
                        final_steering_adjust *= multiplier
                        
                        # **전진 시 조향: 88 기준으로 대칭 적용**
                        # 현재 서보 각도를 88을 기준으로 대칭 보정하고, 값 범위는 68 ~ 108로 제한
                        new_steering = 88 - (kit.servo[0].angle - 88)
                        new_steering = max(68, min(108, new_steering + final_steering_adjust))
                        kit.servo[0].angle = new_steering
                        print(f"Steering Adjust: {steer_adjust:.2f}, Parallel Adjust: {rotation_adjust:.2f}")
                        print(f"Final Steering Adjust: {final_steering_adjust:.2f}, New Steering: {new_steering}")
                        
                        # PID 기반 전후 이동 (목표 크기 정렬)
                        # pid_speed: 목표 객체 크기와 현재 객체 크기 차이에 따른 속도 제어값 계산
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
                        
                        # 가까워질수록 보정 배율을 높이기 위한 게인 스케줄링
                        error_ratio = abs(object_size - target_size) / target_size
                        alpha = 1.0
                        multiplier = 1 + (1 - min(error_ratio, 1)) * alpha
                        final_steering_adjust *= multiplier
                        
                        # 후진 시 조향 (현재 서보 각도에 보정값을 더해 조정, 범위 제한: 68 ~ 108)
                        new_steering = min(108, max(68, kit.servo[0].angle + final_steering_adjust))
                        kit.servo[0].angle = new_steering
                        print(f"Steering Adjust: {steer_adjust:.2f}, Parallel Adjust: {rotation_adjust:.2f}")
                        print(f"Final Steering Adjust: {final_steering_adjust:.2f}, New Steering: {new_steering}")
                        
                        # PID 기반 전후 이동 (목표 크기 정렬)
                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        motor_hat.set_throttle(-speed_adjust)
                        print(f"Moving at speed {-speed_adjust:.2f} (Backward), Object Size: {int(object_size)}")
            # end for

            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time() - lost_target_time > 1.0:
                print("Target marker lost, moving forward to find it...")
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time() - lost_target_time > 1.0:
                print("Target marker lost, moving forward to find it...")
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)
        if target_found:
            lost_target_time = None

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
