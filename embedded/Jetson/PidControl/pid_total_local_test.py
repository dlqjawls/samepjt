import cv2
import numpy as np
import math
import time
import datetime
import board
import busio
import socket
import json
import re
import os
import base64
import Jetson.GPIO as GPIO
from simple_pid import PID
from adafruit_motor import motor
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit
import threading
import queue
import websocket  # pip install websocket-client
import ssl


"""
수정 2
1. 여러 스레드에서 접근 제한
2. 계산, 제어 로그 확인
3. rent에서 target_found 수정
"""

# =============================================================================
# 전역 상수/설정값
# =============================================================================
clientId = "PBVVINNUMBER00001"

module_nfc_tag_map = {
    "A7F189321F22BF": 1,
    # 필요 시 다른 태그와 id 매핑 추가
}

module_name_mapping = {
    1: "camping_module",
    2: "office_module",
    11: "return_place"
}

target_size = 8000
max_speed = 0.30
min_speed = 0.10
loop_time = 0.2

# =============================================================================
# 스레드 안전 제어를 위한 락 (servo, motor 등 공유 자원 보호)
# =============================================================================
control_lock = threading.Lock()

# =============================================================================
# 웹소켓 명령 처리를 위한 큐 및 상태
# =============================================================================
command_queue = queue.Queue()  # ("rent", payload) 또는 ("return", payload) 형태
current_thread = None          # 현재 동작(장착/반납) 스레드
stop_event = threading.Event() # 동작 중단을 위한 이벤트 플래그

# =============================================================================
# 1) 웹소켓 연결 유지 (스레드) 설정
# =============================================================================
ws_app = None  # websocket.WebSocketApp 인스턴스

def keep_ws_alive(interval=10):
    global ws_app
    while True:
        if ws_app:
            try:
                ws_app.send_ping("keepalive")
            except Exception as e:
                print("Ping failed:", e)
                break
        time.sleep(interval)

def on_message(ws, message):
    print("[WebSocket] 수신:", message)
    try:
        command_data = json.loads(message)
        if command_data.get("type") == "service":
            path = command_data.get("path")
            payload = command_data.get("payload", {})
            if path == "/vehicle/rent":
                command_queue.put(("rent", payload))
            elif path == "/vehicle/return":
                command_queue.put(("return", payload))
        else:
            print("[WebSocket] 기타 메시지:", message)
    except Exception as e:
        print("[WebSocket] 명령 파싱 실패:", e)

def on_error(ws, error):
    print("[WebSocket] Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("[WebSocket] Closed:", close_status_code, close_msg)

def on_open(ws):
    print("[WebSocket] Opened")
    connected_msg = {"type": "service", "path": "/vehicle/connect", "payload": {}}
    ws.send(json.dumps(connected_msg))

def websocket_thread():
    """웹소켓을 유지하는 스레드: 연결 & 메시지 수신 루프"""
    global ws_app
    ws_app = websocket.WebSocketApp(
        f"wss://backend-wandering-river-6835.fly.dev/api/socket/ws/{clientId}",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    # SSL 인증 무시 예시 (테스트용)
    wst = threading.Thread(
        target=ws_app.run_forever,
        kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}}
    )
    wst.daemon = True
    wst.start()

    # 연결이 어느 정도 된 후 ping 스레드 시작
    time.sleep(1)
    ping_thr = threading.Thread(target=keep_ws_alive, args=(5,))
    ping_thr.daemon = True
    ping_thr.start()

# =============================================================================
# 2) GPIO / 전자석 관련 초기화
# =============================================================================
GPIO.cleanup()
PWM_PIN = 33  # BOARD 모드 기준 핀번호
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)  # 1kHz
pwm.start(0)

def electromagnet_on():
    pwm.ChangeDutyCycle(100)
    print("전자석 ON (100% 출력)")

def electromagnet_off():
    pwm.ChangeDutyCycle(10)  # 잔류 전류 제거
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)
    print("전자석 OFF (잔류 전류 제거 완료)")

# =============================================================================
# 3) I2C / PCA9685 / ServoKit / MotorHat 준비
# =============================================================================
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 60

class PWMThrottleHat:
    def __init__(self, pwm_obj):
        self.pwm = pwm_obj
        self.pwm.frequency = 60

    def set_throttle(self, throttle):
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
with control_lock:
    kit.servo[0].angle = 88  # 초기 조향값

# =============================================================================
# 4) 카메라 설정 (ArUco + PID 제어)
# =============================================================================
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

pid_x = PID(0.06, 0.013, 0.004, setpoint=0)
pid_rotation = PID(0.055, 0.011, 0.0035, setpoint=0)
pid_speed = PID(0.022, 0.007, 0.0018, setpoint=target_size)

lost_object_time = None
lost_target_time = None
stop_movement = False
alignment_start_time = None

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
    print("Error: Could not open CSI camera.")

def calculate_x_rotation(corner):
    top_left, top_right, bottom_right, bottom_left = corner[0]
    height_left = bottom_left[1] - top_left[1]
    height_right = bottom_right[1] - top_right[1]
    if height_left > 0 and height_right > 0:
        rotate_angle = int(round(
            math.degrees(math.atan((height_right - height_left) / (top_right[0] - top_left[0])))
        )) * 2
        rotate_angle = max(min(rotate_angle, 90), -90)
    else:
        rotate_angle = 0
    return rotate_angle

# =============================================================================
# 5) 장착/반납 동작 + 녹화 함수 (stop_event 체크 포함)
# =============================================================================
def rent_until_nfc(rentId, module_name, ws_send):
    print("NFC 인식 전까지 후진 시작...")
    with control_lock:
        kit.servo[0].angle = 90
    electromagnet_on()
    with control_lock:
        motor_hat.set_throttle(-0.3)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"{module_name}_rent_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame for video recording.")
        return

    frame_width, frame_height = frame.shape[1], frame.shape[0]
    fps = 20.0
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))
    print("녹화 시작 중... (시뮬레이션으로 'n' 키 입력 시 NFC 감지)")

    while True:
        if stop_event.is_set():
            print("[rent_until_nfc] 중단 요청받음 → 즉시 종료")
            out.release()
            return

        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("Aruco Marker Tracking (NFC Detection)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('n'):
            print("NFC 감지됨! 즉시 정지")
            with control_lock:
                motor_hat.set_throttle(0)
            out.release()
            ws_send("mount_complete")
            break

        time.sleep(0.1)

    print("전자석 ON 상태에서 전진 시작 (5초)")
    with control_lock:
        kit.servo[0].angle = 88
        motor_hat.set_throttle(0.4)
    time.sleep(1.2)
    electromagnet_off()
    time.sleep(10.0)
    with control_lock:
        motor_hat.set_throttle(0)
    print("전진 완료, 전자석 OFF 후 정지")
    print("모듈 장착 완료")

    # ffmpeg 변환 및 전송 부분
    temp_file = video_filename
    output_file = f"{rentId}_{module_name}_rent_{timestamp}.mp4"
    conversion_cmd = f'ffmpeg -i "{temp_file}" -vcodec libx264 "{output_file}"'
    print(f"변환 명령 실행: {conversion_cmd}")
    os.system(conversion_cmd)

    try:
        with open(output_file, "rb") as f:
            data = f.read()
            encoded_data = base64.b64encode(data).decode("utf-8")
            message = {
                "type": "service",
                "path": "/vehicle/module/mount",
                "payload": {
                    "rent_id": rentId,
                    "video": encoded_data
                }
            }
        ws_send(json.dumps(message))
        print(f"✅ 녹화 저장 및 전송 완료: {output_file}")
    except Exception as e:
        print("비디오 파일 전송 중 오류:", e)

def return_until_nfc(rentId, module_name, ws_send):
    print("NFC 인식 전까지 후진 시작...")
    with control_lock:
        kit.servo[0].angle = 90
        motor_hat.set_throttle(-0.30)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_filename = f"{module_name}_return_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame for video recording.")
        return

    frame_width, frame_height = frame.shape[1], frame.shape[0]
    fps = 20.0
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))
    print("녹화 시작 중... (시뮬레이션으로 'n' 키 입력 시 NFC 감지)")

    while True:
        if stop_event.is_set():
            print("[return_until_nfc] 중단 요청받음 → 즉시 종료")
            out.release()
            return

        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("Aruco Marker Tracking (NFC Detection)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('n'):
            print("NFC 감지됨! 즉시 정지")
            with control_lock:
                motor_hat.set_throttle(0)
            out.release()
            ws_send("return_complete")
            break

        time.sleep(0.1)

    print("전자석 ON 상태에서 전진 시작 (5초)")
    with control_lock:
        kit.servo[0].angle = 88
        motor_hat.set_throttle(0.4)
    time.sleep(2.0)
    time.sleep(9.0)
    with control_lock:
        motor_hat.set_throttle(0)
    print("전진 완료, 전자석 OFF 후 정지")
    print("모듈 반납 완료")

    temp_file = video_filename
    output_file = f"{rentId}_{module_name}_return_{timestamp}.mp4"
    conversion_cmd = f'ffmpeg -i "{temp_file}" -vcodec libx264 "{output_file}"'
    print(f"변환 명령 실행: {conversion_cmd}")
    os.system(conversion_cmd)

    try:
        with open(output_file, "rb") as f:
            data = f.read()
            encoded_data = base64.b64encode(data).decode("utf-8")
            message = {
                "type": "service",
                "path": "/vehicle/module/return",
                "payload": {
                    "rent_id": rentId,
                    "video": encoded_data
                }
            }
        ws_send(json.dumps(message))
        print(f"✅ 녹화 저장 및 전송 완료: {output_file}")
    except Exception as e:
        print("비디오 파일 전송 중 오류:", e)

# =============================================================================
# 6) 정렬 로직 및 모듈 장착/반납 프로세스 (스레드용)
# =============================================================================
def rent_process(rent_id, ws_send):
    global lost_object_time, lost_target_time, alignment_start_time, stop_movement
    target_marker_id = 1
    module_name = module_name_mapping.get(target_marker_id, f"ID_{target_marker_id}")

    print(f"[장착 프로세스] rent_id={rent_id}, target_marker_id={target_marker_id}")

    lost_object_time = None
    lost_target_time = None
    alignment_start_time = time.time()
    stop_movement = False

    while True:
        if stop_event.is_set():
            print("[rent_process] 중간 중단 요청 받음 → 즉시 종료")
            return

        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        target_found = False

        if ids is not None:
            lost_object_time = None
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id != target_marker_id:
                    continue

                cv2.polylines(frame, [np.int32(corner)], True, (0, 255, 0), 2)
                cX = int(np.mean(corner[0][:, 0]))
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height
                x_rotation = calculate_x_rotation(corner)
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x

                cv2.putText(frame, f"{module_name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"size: {int(object_size)}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"parallel: {'yes' if abs(x_rotation) < 3 else 'no'}",
                            (50,110), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0,255,0) if abs(x_rotation)<3 else (0,0,255), 2)
                cv2.putText(frame, f"center: {'yes' if abs(error_x) < 15 else 'no'}",
                            (50,140), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0,255,0) if abs(error_x)<15 else (0,0,255), 2)
                
                target_found = True
                if alignment_start_time is None:
                    alignment_start_time = time.time()

                if abs(error_x) < 10 and abs(x_rotation) < 2 and abs(object_size - target_size) < target_size * 0.1:
                    print("Target marker reached, stopping movement.")
                    with control_lock:
                        motor_hat.set_throttle(0)
                    stop_movement = True
                    time.sleep(3)
                    if alignment_start_time is not None:
                        alignment_time = time.time() - alignment_start_time
                        alignment_start_time = None
                        print(f"Alignment time: {alignment_time:.2f} seconds")

                    rent_until_nfc(rent_id, module_name, ws_send)
                    return

                else:
                    if object_size > target_size*1.1 and (abs(error_x)>10 or abs(x_rotation)>2):
                        print("Oversized & misaligned, adjusting position...")
                        steer_adjust = pid_x(error_x)
                        rotation_adjust = pid_rotation(x_rotation)
                        final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)
                        
                        with control_lock:
                            # 전진 시 대칭 적용
                            new_steering = 88 - (kit.servo[0].angle - 88)
                            new_steering = max(68, min(108, new_steering + final_steering_adjust))
                            kit.servo[0].angle = new_steering
                        print(f"Steering Adjust: {steer_adjust:.2f}, Parallel Adjust: {rotation_adjust:.2f}")
                        print(f"Final Steering Adjust: {final_steering_adjust:.2f}, New Steering: {new_steering}")
                        
                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        with control_lock:
                            motor_hat.set_throttle(speed_adjust)
                        print(f"Moving at speed {-speed_adjust:.2f} (Backward), Object Size: {int(object_size)}")

                    elif object_size < target_size*0.9 and (abs(error_x)>10 or abs(x_rotation)>2):
                        print("Small & misaligned, adjusting position...")
                        steer_adjust = pid_x(error_x)
                        rotation_adjust = pid_rotation(x_rotation)
                        final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)
                        
                        with control_lock:
                            new_steering = min(108, max(68, kit.servo[0].angle + final_steering_adjust))
                            kit.servo[0].angle = new_steering
                        print(f"Steering Adjust: {steer_adjust:.2f}, Parallel Adjust: {rotation_adjust:.2f}")
                        print(f"Final Steering Adjust: {final_steering_adjust:.2f}, New Steering: {new_steering}")
                        
                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        with control_lock:
                            motor_hat.set_throttle(-speed_adjust)
                        print(f"Moving at speed {-speed_adjust:.2f} (Backward), Object Size: {int(object_size)}")

            
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time() - lost_target_time > 1.0:
                print("Target marker lost, moving forward to find it...")
                with control_lock:
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.2)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time() - lost_target_time > 1.0:
                print("Target marker lost, moving forward to find it...")
                with control_lock:
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.2)

        if target_found:
                lost_target_time = None

        cv2.imshow("Aruco Marker Tracking (PID)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    with control_lock:
        motor_hat.set_throttle(0)
    with control_lock:
        kit.servo[0].angle = 88
    print("[rent_process] 종료")

def return_process(rent_id, ws_send):
    global lost_object_time, lost_target_time, alignment_start_time, stop_movement
    target_marker_id = 11
    module_name = module_name_mapping.get(target_marker_id, f"ID_{target_marker_id}")

    print(f"[반납 프로세스] rent_id={rent_id}, target_marker_id={target_marker_id}")

    lost_object_time = None
    lost_target_time = None
    alignment_start_time = time.time()
    stop_movement = False

    while True:
        if stop_event.is_set():
            print("[return_process] 중간 중단 요청 받음 → 종료")
            return

        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        target_found = False

        if ids is not None:
            lost_object_time = None
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id != target_marker_id:
                    continue

                cv2.polylines(frame, [np.int32(corner)], True, (0, 255, 0), 2)
                cX = int(np.mean(corner[0][:, 0]))
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height
                x_rotation = calculate_x_rotation(corner)
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x

                cv2.putText(frame, f"{module_name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"size: {int(object_size)}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, f"parallel: {'yes' if abs(x_rotation) < 3 else 'no'}",
                            (50,110), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0,255,0) if abs(x_rotation)<3 else (0,0,255), 2)
                cv2.putText(frame, f"center: {'yes' if abs(error_x) < 15 else 'no'}",
                            (50,140), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0,255,0) if abs(error_x)<15 else (0,0,255), 2)
                
                target_found = True
                if alignment_start_time is None:
                    alignment_start_time = time.time()

                if abs(error_x) < 10 and abs(x_rotation) < 2 and abs(object_size - target_size) < target_size * 0.1:
                    print("Target marker reached, stopping movement.")
                    with control_lock:
                        motor_hat.set_throttle(0)
                    stop_movement = True
                    time.sleep(3)
                    if alignment_start_time is not None:
                        alignment_time = time.time() - alignment_start_time
                        alignment_start_time = None
                        print(f"Alignment time: {alignment_time:.2f} seconds")

                    return_until_nfc(rent_id, module_name, ws_send)
                    return
                else:
                    if object_size > target_size*1.1 and (abs(error_x)>10 or abs(x_rotation)>2):
                        print("Oversized & misaligned, adjusting position...")
                        steer_adjust = pid_x(error_x)
                        rotation_adjust = pid_rotation(x_rotation)
                        final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)
                        
                        error_ratio = abs(object_size - target_size) / target_size
                        alpha = 1.0
                        multiplier = 1 + (1 - min(error_ratio, 1)) * alpha
                        final_steering_adjust *= multiplier
                        
                        with control_lock:
                            new_steering = 88 - (kit.servo[0].angle - 88)
                            new_steering = max(68, min(108, new_steering + final_steering_adjust))
                            kit.servo[0].angle = new_steering
                        print(f"Steering Adjust: {steer_adjust:.2f}, Parallel Adjust: {rotation_adjust:.2f}")
                        print(f"Final Steering Adjust: {final_steering_adjust:.2f}, New Steering: {new_steering}")
                        
                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        with control_lock:
                            motor_hat.set_throttle(speed_adjust)
                        print(f"Moving at speed {-speed_adjust:.2f} (Backward), Object Size: {int(object_size)}")

                    elif object_size < target_size*0.9 and (abs(error_x)>10 or abs(x_rotation)>2):
                        print("Small & misaligned, adjusting position...")
                        steer_adjust = pid_x(error_x)
                        rotation_adjust = pid_rotation(x_rotation)
                        final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)
                        
                        error_ratio = abs(object_size - target_size) / target_size
                        alpha = 1.0
                        multiplier = 1 + (1 - min(error_ratio, 1)) * alpha
                        final_steering_adjust *= multiplier
                        
                        with control_lock:
                            new_steering = min(108, max(68, kit.servo[0].angle + final_steering_adjust))
                            kit.servo[0].angle = new_steering
                        print(f"Steering Adjust: {steer_adjust:.2f}, Parallel Adjust: {rotation_adjust:.2f}")
                        print(f"Final Steering Adjust: {final_steering_adjust:.2f}, New Steering: {new_steering}")
                        
                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        with control_lock:
                            motor_hat.set_throttle(-speed_adjust)
                        print(f"Moving at speed {-speed_adjust:.2f} (Backward), Object Size: {int(object_size)}")

            if target_found:
                lost_target_time = None
            else:
                if lost_target_time is None:
                    lost_target_time = time.time()
                elif time.time() - lost_target_time > 1.0:
                    print("Target marker lost, moving forward to find it...")
                    with control_lock:
                        kit.servo[0].angle = 88
                        motor_hat.set_throttle(0.2)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time() - lost_target_time > 1.0:
                print("Target marker lost, moving forward to find it...")
                with control_lock:
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.2)

        cv2.imshow("Aruco Marker Tracking (PID)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    with control_lock:
        motor_hat.set_throttle(0)
    with control_lock:
        kit.servo[0].angle = 88
    print("[return_process] 종료")

# =============================================================================
# 7) 메인 루프: 명령에 따라 rent_process/return_process 실행
# =============================================================================
def main_loop():
    global current_thread, stop_event
    while True:
        if current_thread is None or not current_thread.is_alive():
            try:
                cmd, payload = command_queue.get(timeout=1)
                stop_event.clear()
                if cmd == "rent":
                    rent_id = payload.get("rent_id")
                    print(f"[MainLoop] 'rent' 명령 수신, rent_id={rent_id}")
                    current_thread = threading.Thread(
                        target=rent_process,
                        args=(rent_id, ws_app.send)
                    )
                    current_thread.start()
                elif cmd == "return":
                    rent_id = payload.get("rent_id")
                    print(f"[MainLoop] 'return' 명령 수신, rent_id={rent_id}")
                    current_thread = threading.Thread(
                        target=return_process,
                        args=(rent_id, ws_app.send)
                    )
                    current_thread.start()
            except:
                pass
        else:
            if not command_queue.empty():
                new_cmd, new_payload = command_queue.get()
                print(f"[MainLoop] 동작 중 새 명령 {new_cmd} 수신 → 기존 작업 중단")
                stop_event.set()
                time.sleep(2)
                stop_event.clear()
                if new_cmd == "rent":
                    rent_id = new_payload.get("rent_id")
                    current_thread = threading.Thread(
                        target=rent_process,
                        args=(rent_id, ws_app.send)
                    )
                    current_thread.start()
                elif new_cmd == "return":
                    rent_id = new_payload.get("rent_id")
                    current_thread = threading.Thread(
                        target=return_process,
                        args=(rent_id, ws_app.send)
                    )
                    current_thread.start()
            time.sleep(1)

# =============================================================================
# 8) 실행부
# =============================================================================
if __name__ == "__main__":
    try:
        ws_thr = threading.Thread(target=websocket_thread, daemon=True)
        ws_thr.start()

        time.sleep(1)
        main_loop()

    except KeyboardInterrupt:
        print("KeyboardInterrupt → 종료 처리")
    except Exception as e:
        print("예외 발생:", e)
    finally:
        print("Exiting... ")
        with control_lock:
            motor_hat.set_throttle(0)
        with control_lock:
            kit.servo[0].angle = 88
        pca.deinit()
        GPIO.cleanup()
        cap.release()
        cv2.destroyAllWindows()
        print("Cleaning up pins and stopping program.")
