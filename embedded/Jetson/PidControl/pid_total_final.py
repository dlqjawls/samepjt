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

###############################################################################
# 전역 상수 / 설정
###############################################################################
clientId = "PBVVINNUMBER00001"

module_nfc_tag_map = {
    "A7F189321F22BF": 1,
}

module_name_mapping = {
    1: "camping_module",
    2: "office_module",
    11: "return_place"
}

target_size = 8000
max_speed = 0.40
min_speed = 0.20

# 명령 큐 및 제어 플래그
command_queue = queue.Queue()     # ("rent", payload) or ("return", payload)
current_thread = None            # 현재 실행 중인 동작(장착/반납) 스레드
stop_event = threading.Event()   # 동작 중단 신호

# NFC 이벤트
nfc_detected_event = threading.Event()

# NFC / 센서값 전역
latest_nfc_uid = None
latest_front_distance = None
latest_back_distance = None

# PID 제어용 전역
lost_object_time = None
lost_target_time = None
stop_movement = False
alignment_start_time = None

###############################################################################
# 개선 1) 동영상 변환 & 전송 → 별도 큐 & 스레드 처리
###############################################################################
video_processing_queue = queue.Queue()

def video_processing_worker(ws_send):
    """
    별도 쓰레드에서 동영상 변환(ffmpeg) + base64 인코딩 + 웹소켓 전송을 처리.
    메인 프로세스의 PID 루프가 지연되지 않도록 함.
    """
    while True:
        job = video_processing_queue.get()
        if job is None:
            # None이 들어오면 종료 신호
            break
        
        (video_filename, output_filename, ws_message_dict) = job
        
        try:
            # ffmpeg avi → mp4 변환
            conversion_cmd = f'ffmpeg -y -i "{video_filename}" -vcodec libx264 "{output_filename}"'
            print(f"[VideoWorker] ffmpeg 변환 수행: {conversion_cmd}")
            os.system(conversion_cmd)
            
            # base64 인코딩
            with open(output_filename, "rb") as f:
                data = f.read()
            encoded_data = base64.b64encode(data).decode("utf-8")
            
            # 전송 payload에 비디오 넣고 웹소켓으로 전송
            ws_message_dict["payload"]["video"] = encoded_data
            ws_send(json.dumps(ws_message_dict))
            
            print(f"[VideoWorker] ✅ 변환 및 전송 완료: {output_filename}")
        
        except Exception as e:
            print("[VideoWorker] 에러 발생:", e)


###############################################################################
# 웹소켓 유지 스레드
###############################################################################
ws_app = None

def keep_ws_alive(interval=10):
    """주기적으로 ws_app에 ping을 보내는 스레드 함수"""
    global ws_app
    while True:
        if ws_app:
            try:
                ws_app.send_ping("keepalive")
            except Exception as e:
                print("[WebSocket] Ping failed:", e)
                break
        time.sleep(interval)

def on_message(ws, message):
    """웹소켓 서버에서 메시지를 받으면 호출되는 콜백"""
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
    # 연결 시 "/vehicle/connect" 신호 보냄
    connected_msg = {"type": "service", "path": "/vehicle/connect", "payload": {}}
    ws.send(json.dumps(connected_msg))

def websocket_thread():
    """웹소켓을 유지하는 스레드: 연결 & 메시지 수신 루프"""
    global ws_app
    ws_app = websocket.WebSocketApp(
        f"ws://192.168.219.101:9001/api/socket/ws/{clientId}",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    wst = threading.Thread(target=ws_app.run_forever)
    wst.daemon = True
    wst.start()

    time.sleep(1)
    ping_thr = threading.Thread(target=keep_ws_alive, args=(5,))
    ping_thr.daemon = True
    ping_thr.start()


###############################################################################
# GPIO / 전자석
###############################################################################
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
    pwm.ChangeDutyCycle(10)
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)
    print("전자석 OFF (잔류 전류 제거 완료)")


###############################################################################
# I2C / PCA9685 / ServoKit / Motor
###############################################################################
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 60

class PWMThrottleHat:
    def __init__(self, pwm_obj):
        self.pwm = pwm_obj
        self.pwm.frequency = 60

    def set_throttle(self, throttle):
        """ -1.0 ~ +1.0 범위 """
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
kit.servo[0].angle = 88  # 초기화

###############################################################################
# 카메라 (ArUco + PID)
###############################################################################
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

pid_x = PID(0.06, 0.013, 0.004, setpoint=0)
pid_rotation = PID(0.055, 0.011, 0.0035, setpoint=0)
pid_speed = PID(0.022, 0.007, 0.0018, setpoint=target_size)

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
    # exit()

def calculate_x_rotation(corner):
    top_left, top_right, bottom_right, bottom_left = corner[0]
    height_left = bottom_left[1] - top_left[1]
    height_right = bottom_right[1] - top_right[1]
    rotate_angle = 0
    if height_left > 0 and height_right > 0:
        rotate_angle = int(round(
            math.degrees(math.atan((height_right - height_left) / (top_right[0] - top_left[0]))))
        ) * 2
        rotate_angle = max(min(rotate_angle, 90), -90)
    return rotate_angle

###############################################################################
# NFC 서버 스레드
###############################################################################
rent_operating = False
rear_triggered = False

def nfc_server_thread(host="0.0.0.0", port=5000):
    global latest_nfc_uid, latest_front_distance, latest_back_distance
    global rent_operating, rear_triggered

    print(f"[NFC 서버] {host}:{port} 대기중..")
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    print("[NFC 서버] 연결 대기..")

    client_sock, addr = server_sock.accept()
    print(f"[NFC 서버] 연결됨: {addr}")

    while True:
        try:
            data = client_sock.recv(1024).decode().strip()
            if not data:
                continue
            for line in data.splitlines():
                try:
                    sensor_json = json.loads(line)
                    nfc_uid = sensor_json.get("NFC_UID")
                    front_distance = sensor_json.get("ULTRASONIC_FRONT")
                    back_distance = sensor_json.get("ULTRASONIC_BACK")

                    latest_nfc_uid = nfc_uid
                    latest_front_distance = front_distance
                    latest_back_distance = back_distance

                    if back_distance is not None and back_distance <= 10:
                        rear_triggered = True
                        # print("[NFC 서버] 후방 초음파 10 이하 감지")

                    # NFC 태그 수신 시 처리
                    if nfc_uid:
                        if rent_operating:
                            if rear_triggered:
                                print(f"[NFC 서버] 렌트 중 NFC 감지: {nfc_uid} → event.set()")
                                nfc_detected_event.set()
                            else:
                                print(f"[NFC 서버] 렌트 중 NFC 감지 but 후방 미충족 → 무시")
                        else:
                            print(f"[NFC 서버] (반납 or 기타 모드) NFC 감지: {nfc_uid}")
                            nfc_detected_event.set()

                except json.JSONDecodeError:
                    print(f"[NFC 서버] JSON 파싱 실패: {line}")
        except Exception as e:
            print("[NFC 서버] 소켓 오류:", e)
            break

    client_sock.close()
    server_sock.close()

###############################################################################
# (개선 1-1) 동영상 녹화 → "바로" 변환 X, 큐에 저장만
###############################################################################
def enqueue_video_for_processing(video_filename, output_filename, ws_message_dict):
    """동영상 변환/전송 큐에 작업을 넣고 바로 return"""
    video_processing_queue.put((video_filename, output_filename, ws_message_dict))


###############################################################################
# 장착/반납 시 NFC 대기 & 동영상 녹화
###############################################################################
def rent_until_nfc(rentId, module_name, ws_send):
    """
    NFC 인식까지 후진 후 → NFC 감지 → 전진 & 전자석 OFF
    영상을 동영상 처리큐에 넣고, 별도 스레드에서 변환/전송
    """
    nfc_detected_event.clear()

    print("[rent_until_nfc] 후진 시작..")
    kit.servo[0].angle = 90
    electromagnet_on()
    motor_hat.set_throttle(-0.4)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    video_filename = f"{module_name}_rent_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame for video recording.")
        return

    frame_width, frame_height = frame.shape[1], frame.shape[0]
    fps = 20.0
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

    while True:
        if stop_event.is_set():
            print("[rent_until_nfc] 중단 요청 → 종료")
            out.release()
            return

        ret, frame = cap.read()
        if ret:
            out.write(frame)
            # ↓ 필요하다면 주석 해제, 또는 10프레임에 1번만 표시
            # cv2.imshow("Aruco Marker (NFC Detection)", frame)
        if nfc_detected_event.is_set():
            print("[rent_until_nfc] NFC 감지! 정지")
            motor_hat.set_throttle(0)
            out.release()
            ws_send("mount_complete")  # 예시
            break

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            motor_hat.set_throttle(0)
            out.release()
            print("[rent_until_nfc] 사용자가 q → 중단")
            return

        # (pid 루프 방해를 줄이려면 sleep을 최소화하거나 제거)
        time.sleep(0.01)

    print("[rent_until_nfc] 전자석 ON 상태에서 전진 (1.2초) → OFF")
    kit.servo[0].angle = 88
    motor_hat.set_throttle(0.4)
    time.sleep(1.2)
    electromagnet_off()
    time.sleep(1.0)   # 너무 길게 주지 말고 필요 최소
    motor_hat.set_throttle(0)

    print("[rent_until_nfc] 모듈 장착 완료")

    # 곧바로 ffmpeg 변환/전송하지 않고, 큐에 넣고 return
    output_file = f"{rentId}_{module_name}_rent_{timestamp}.mp4"
    msg_dict = {
        "type": "service",
        "path": "/vehicle/module/mount",
        "payload": {
            "rent_id": rentId,
            "video": ""  # 나중에 base64로 채워질 값
        }
    }
    enqueue_video_for_processing(video_filename, output_file, msg_dict)

    # 추가로 arrive_complete 같은 신호도 보낼 수 있음
    ws_send("arrive_complete")


def return_until_nfc(rentId, module_name, ws_send):
    nfc_detected_event.clear()

    print("[return_until_nfc] 후진 시작..")
    kit.servo[0].angle = 90
    motor_hat.set_throttle(-0.4)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    video_filename = f"{module_name}_return_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame for video recording.")
        return

    frame_width, frame_height = frame.shape[1], frame.shape[0]
    fps = 20.0
    out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

    while True:
        if stop_event.is_set():
            print("[return_until_nfc] 중단 요청 → 종료")
            out.release()
            return

        ret, frame = cap.read()
        if ret:
            out.write(frame)
            # ↓ 필요시 주석 해제
            # cv2.imshow("Aruco Marker (NFC Detection)", frame)

        if nfc_detected_event.is_set():
            print("[return_until_nfc] NFC 감지! 정지")
            motor_hat.set_throttle(0)
            out.release()
            ws_send("return_complete")
            break

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            motor_hat.set_throttle(0)
            out.release()
            print("[return_until_nfc] 사용자가 q → 중단")
            return

        time.sleep(0.01)

    print("[return_until_nfc] 전자석 ON 상태에서 전진 (2초)")
    kit.servo[0].angle = 88
    motor_hat.set_throttle(0.4)
    time.sleep(2.0)
    # 필요 시 electromagnet_off()
    time.sleep(1.0)
    motor_hat.set_throttle(0)
    print("[return_until_nfc] 모듈 반납 완료")

    output_file = f"{rentId}_{module_name}_return_{timestamp}.mp4"
    msg_dict = {
        "type": "service",
        "path": "/vehicle/module/return",
        "payload": {
            "rent_id": rentId,
            "video": ""
        }
    }
    enqueue_video_for_processing(video_filename, output_file, msg_dict)

    ws_send("arrive_complete")


###############################################################################
# 장착 / 반납 PID 프로세스
###############################################################################
def rent_process(rent_id, ws_send):
    global lost_object_time, lost_target_time, alignment_start_time
    global stop_movement, rent_operating, rear_triggered

    rent_operating = True
    rear_triggered = False

    target_marker_id = 1
    module_name = module_name_mapping.get(target_marker_id, f"ID_{target_marker_id}")
    print(f"[rent_process] rent_id={rent_id}, target_marker_id={target_marker_id}")

    lost_object_time = None
    lost_target_time = None
    alignment_start_time = time.time()
    stop_movement = False

    frame_count = 0  # 프레임 카운트(디버그 출력 주기 제어 용도)

    while True:
        if stop_event.is_set():
            print("[rent_process] 중단 요청 받음 → 종료")
            rent_operating = False
            return

        ret, frame = cap.read()
        if not ret:
            print("[rent_process] 카메라 프레임 읽기 실패")
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

                # ---- 정렬 오차 계산 ----
                cX = int(np.mean(corner[0][:, 0]))
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height
                x_rotation = calculate_x_rotation(corner)
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x

                target_found = True
                if alignment_start_time is None:
                    alignment_start_time = time.time()

                # 정렬 완료 조건
                if (abs(error_x) < 10 and
                    abs(x_rotation) < 2 and
                    abs(object_size - target_size) < target_size * 0.1):
                    motor_hat.set_throttle(0)
                    stop_movement = True
                    time.sleep(0.3)

                    if alignment_start_time is not None:
                        alignment_time = time.time() - alignment_start_time
                        alignment_start_time = None
                        print(f"[rent_process] 정렬 완료 (소요 {alignment_time:.2f}s)")

                    # 모듈 장착
                    rent_until_nfc(rent_id, module_name, ws_send)
                    rent_operating = False
                    return
                else:
                    # PID 제어
                    steer_adjust = pid_x(error_x)
                    rotation_adjust = pid_rotation(x_rotation)
                    final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)

                    if object_size > target_size*1.1:
                        # 너무 가깝고 오차가 있음 → 전진하며 위치 조정
                        new_steering = kit.servo[0].angle
                        new_steering = max(68, min(108, new_steering - final_steering_adjust))
                        kit.servo[0].angle = new_steering

                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        motor_hat.set_throttle(speed_adjust)

                    elif object_size < target_size*0.9:
                        # 너무 멈 → 후진하며 위치 조정
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
                elif time.time()-lost_target_time > 1.0:
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.3)
        else:
            # 마커가 전혀 안보이면
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time()-lost_target_time > 1.0:
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)

        frame_count += 1
        # if frame_count % 30 == 0:
        #     print("[rent_process] PID 동작 중...")  # 필요시 주석 해제

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 메인 PID 루프에서는 sleep을 매우 짧게(또는 아예 X)
        time.sleep(0.01)

    motor_hat.set_throttle(0)
    kit.servo[0].angle = 88
    print("[rent_process] 종료")
    rent_operating = False


def return_process(rent_id, ws_send):
    global lost_object_time, lost_target_time, alignment_start_time
    global stop_movement

    target_marker_id = 11
    module_name = module_name_mapping.get(target_marker_id, f"ID_{target_marker_id}")
    print(f"[return_process] rent_id={rent_id}, target_marker_id={target_marker_id}")

    lost_object_time = None
    lost_target_time = None
    alignment_start_time = time.time()
    stop_movement = False

    frame_count = 0

    while True:
        if stop_event.is_set():
            print("[return_process] 중단 요청 → 종료")
            return

        ret, frame = cap.read()
        if not ret:
            print("[return_process] 카메라 프레임 읽기 실패")
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

                cX = int(np.mean(corner[0][:, 0]))
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height
                x_rotation = calculate_x_rotation(corner)
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x

                target_found = True
                if alignment_start_time is None:
                    alignment_start_time = time.time()

                if (abs(error_x) < 10 and
                    abs(x_rotation) < 2 and
                    abs(object_size - target_size) < target_size * 0.1):
                    motor_hat.set_throttle(0)
                    stop_movement = True
                    time.sleep(0.3)

                    if alignment_start_time is not None:
                        alignment_time = time.time() - alignment_start_time
                        alignment_start_time = None
                        print(f"[return_process] 정렬 완료 (소요 {alignment_time:.2f}s)")

                    # 반납 루틴
                    return_until_nfc(rent_id, module_name, ws_send)
                    return
                else:
                    # PID 제어
                    steer_adjust = pid_x(error_x)
                    rotation_adjust = pid_rotation(x_rotation)
                    final_steering_adjust = (steer_adjust * 0.7) + (rotation_adjust * 0.3)

                    if object_size > target_size*1.1:
                        new_steering = kit.servo[0].angle
                        new_steering = max(68, min(108, new_steering - final_steering_adjust))
                        kit.servo[0].angle = new_steering

                        speed_adjust = pid_speed(object_size)
                        speed_adjust = max(min_speed, min(max_speed, speed_adjust))
                        motor_hat.set_throttle(speed_adjust)

                    elif object_size < target_size*0.9:
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
                elif time.time()-lost_target_time > 1.0:
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.3)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time()-lost_target_time > 1.0:
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)

        frame_count += 1
        # if frame_count % 30 == 0:
        #     print("[return_process] PID 동작 중...")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.01)

    motor_hat.set_throttle(0)
    kit.servo[0].angle = 88
    print("[return_process] 종료")


###############################################################################
# 메인 루프
###############################################################################
def main_loop():
    global current_thread, stop_event

    while True:
        # 현재 동작이 없거나 종료되었으면 새 명령 확인
        if current_thread is None or not current_thread.is_alive():
            try:
                cmd, payload = command_queue.get(timeout=0.1)
                stop_event.clear()
                if cmd == "rent":
                    rent_id = payload.get("rent_id")
                    print(f"[MainLoop] 'rent' 명령 수신: {rent_id}")
                    current_thread = threading.Thread(
                        target=rent_process,
                        args=(rent_id, ws_app.send)
                    )
                    current_thread.start()
                elif cmd == "return":
                    rent_id = payload.get("rent_id")
                    print(f"[MainLoop] 'return' 명령 수신: {rent_id}")
                    current_thread = threading.Thread(
                        target=return_process,
                        args=(rent_id, ws_app.send)
                    )
                    current_thread.start()
            except queue.Empty:
                # 명령이 없으면 그냥 지나감
                pass

        else:
            # 현재 수행 중인데 새 명령이 있으면 중단 후 재시작
            if not command_queue.empty():
                new_cmd, new_payload = command_queue.get()
                print(f"[MainLoop] 동작 중 새 명령 {new_cmd} → 기존 작업 중단")
                stop_event.set()
                # 짧게 대기 후 새로운 동작
                time.sleep(0.5)
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

        time.sleep(0.1)  # 메인 루프 CPU 점유율 제한

###############################################################################
# 실행부
###############################################################################
if __name__ == "__main__":
    try:
        # 1) NFC 서버
        nfc_thr = threading.Thread(target=nfc_server_thread, daemon=True)
        nfc_thr.start()

        # 2) 웹소켓 스레드
        ws_thr = threading.Thread(target=websocket_thread, daemon=True)
        ws_thr.start()

        # 3) 동영상 처리 스레드
        video_thr = threading.Thread(target=video_processing_worker, args=(lambda msg: ws_app.send(msg),), daemon=True)
        video_thr.start()

        time.sleep(1)

        # 4) 메인 루프 실행
        main_loop()

    except KeyboardInterrupt:
        print("KeyboardInterrupt → 종료")
    except Exception as e:
        print("예외 발생:", e)
    finally:
        print("Exiting... ")
        motor_hat.set_throttle(0)
        kit.servo[0].angle = 88
        pca.deinit()
        GPIO.cleanup()
        cap.release()
        cv2.destroyAllWindows()
        
        # video_processing_thread 정리
        video_processing_queue.put(None)
        
        print("Cleaning up and stopping program.")
