import cv2
import numpy as np
import math
import time
import datetime
import board
import busio
import socket
import json
import os
import base64
import Jetson.GPIO as GPIO
from simple_pid import PID
from adafruit_motor import motor
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit
import threading
import queue
import websocket
import ssl

###############################################################################
# 전역 상수 / 설정
###############################################################################
SERVER_URL = "ws://192.168.219.101:9001/api/socket/ws"
CLIENT_ID  = "PBVVINNUMBER00001"

target_size = 8000
max_speed = 0.30
min_speed = 0.20

# NFC 이벤트
nfc_detected_event = threading.Event()

latest_nfc_uid = None
latest_front_distance = None
latest_back_distance = None

rent_operating = False
rear_triggered = False

###############################################################################
# GPIO / 전자석
###############################################################################
GPIO.cleanup()
PWM_PIN = 33  # BOARD 모드 기준
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)  # 1kHz
pwm.start(0)

def electromagnet_on():
    pwm.ChangeDutyCycle(100)
    print("[Electromagnet] ON")

def electromagnet_off():
    pwm.ChangeDutyCycle(10)
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)
    print("[Electromagnet] OFF")

###############################################################################
# I2C / PCA9685 / Motor / Servo
###############################################################################
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

###############################################################################
# 카메라 / 아루코
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

def calculate_x_rotation(corner):
    top_left, top_right, bottom_right, bottom_left = corner[0]
    height_left = bottom_left[1] - top_left[1]
    height_right = bottom_right[1] - top_right[1]
    rotate_angle = 0
    if height_left > 0 and height_right > 0:
        rotate_angle = int(round(
            math.degrees(math.atan((height_right - height_left) / (top_right[0] - top_left[0]))))
        ) * 2
    return max(min(rotate_angle, 90), -90)

###############################################################################
# (임시) NFC 서버 (초음파/센서값 수신) 스레드
###############################################################################
def nfc_server_thread(host="0.0.0.0", port=5000):
    global latest_nfc_uid, latest_front_distance, latest_back_distance
    global rent_operating, rear_triggered

    print(f"[NFC] 서버 시작 {host}:{port} 대기..")
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    client_sock, addr = server_sock.accept()
    print(f"[NFC] 연결됨: {addr}")

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

                    # 후방 초음파
                    if back_distance is not None and back_distance <= 10:
                        rear_triggered = True

                    # NFC 태그 수신 -> 이벤트 발생
                    if nfc_uid:
                        if rent_operating:
                            if rear_triggered:
                                nfc_detected_event.set()
                                print(f"[NFC] 렌트 중 NFC 감지: {nfc_uid}")
                        else:
                            nfc_detected_event.set()
                            print(f"[NFC] (반납/기타) NFC 감지: {nfc_uid}")

                except json.JSONDecodeError:
                    print("[NFC] JSON 파싱 실패")
        except Exception as e:
            print("[NFC] 소켓 오류:", e)
            break

    client_sock.close()
    server_sock.close()

###############################################################################
# 1) 웹소켓 - 필요할 때만 '한 번' 연결해서 명령을 받기
###############################################################################
def wait_for_command_once():
    """
    - 웹소켓을 임시로 연결하여,
    - /vehicle/rent 또는 /vehicle/return 명령 1회 수신 후
    - 바로 ws.close() 후 반환.
    """
    received_cmd = None
    received_payload = {}

    # 콜백 함수에서 명령 받으면 ws 종료
    def on_message(ws, message):
        nonlocal received_cmd, received_payload
        print("[WebSocket-once] 수신:", message)
        try:
            data = json.loads(message)
            if data.get("type") == "service":
                path = data.get("path", "")
                payload = data.get("payload", {})
                if path == "/vehicle/rent":
                    received_cmd = "rent"
                    received_payload = payload
                elif path == "/vehicle/return":
                    received_cmd = "return"
                    received_payload = payload
            # 명령을 하나라도 받으면 연결 종료
            ws.close()
        except:
            ws.close()

    def on_open(ws):
        print("[WebSocket-once] Opened")
        # 연결 시 '/vehicle/connect' 보낼 수도 있음
        connected_msg = {"type":"service","path":"/vehicle/connect","payload":{}}
        ws.send(json.dumps(connected_msg))

    def on_close(ws, code, msg):
        print("[WebSocket-once] Closed")

    ws_app = websocket.WebSocketApp(
        f"{SERVER_URL}/{CLIENT_ID}",
        on_open=on_open,
        on_message=on_message,
        on_close=on_close
    )

    # run_forever 블로킹 모드: 명령 한 번 받으면 ws.close()로 종료
    ws_app.run_forever()
    return received_cmd, received_payload

###############################################################################
# 2) 웹소켓 - 필요할 때만 연결해서 결과(동영상 등) 전송하기
###############################################################################
def send_video_once(rentId, path, video_filename):
    """
    예: path="/vehicle/module/mount" or "/vehicle/module/return"
    웹소켓 연결 후 동영상 base64 인코딩 → 1회 전송 → close
    """
    # 우선 ffmpeg 변환
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_filename = f"{rentId}_result_{timestamp}.mp4"
    conversion_cmd = f'ffmpeg -y -i "{video_filename}" -vcodec libx264 "{output_filename}"'
    print("[send_video_once] ffmpeg:", conversion_cmd)
    os.system(conversion_cmd)

    # base64 인코딩
    with open(output_filename, "rb") as f:
        data = f.read()
    encoded_data = base64.b64encode(data).decode("utf-8")

    # 최종 전송할 메시지
    final_msg = {
        "type": "service",
        "path": path,  # 예: "/vehicle/module/mount" or "/vehicle/module/return"
        "payload": {
            "rent_id": rentId,
            "video": encoded_data
        }
    }

    def on_open(ws):
        print("[send_video_once] Opened => send data")
        ws.send(json.dumps(final_msg))
        # 전송 후 곧바로 종료
        ws.close()

    def on_close(ws, code, msg):
        print("[send_video_once] Closed")

    ws_app = websocket.WebSocketApp(
        f"{SERVER_URL}/{CLIENT_ID}",
        on_open=on_open,
        on_close=on_close
    )
    ws_app.run_forever()

###############################################################################
# (예) 장착 PID + NFC
###############################################################################
def rent_process(rent_id):
    """
    웹소켓 연결 없이, 오프라인 상태로 PID 정렬 + NFC 대기만 수행
    """
    global rent_operating, rear_triggered
    rent_operating = True
    rear_triggered = False

    target_marker_id = 1  # camping_module
    print(f"[rent_process] start, rent_id={rent_id}, target_marker_id={target_marker_id}")

    lost_target_time = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[rent_process] 카메라 읽기 실패")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            target_found = False
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id != target_marker_id:
                    continue

                target_found = True

                cX = int(np.mean(corner[0][:, 0]))
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height
                x_rotation = calculate_x_rotation(corner)
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x

                # 정렬 체크
                if (abs(error_x) < 10 and abs(x_rotation) < 2
                    and abs(object_size - target_size) < target_size * 0.1):
                    motor_hat.set_throttle(0)
                    time.sleep(0.5)
                    print("[rent_process] 정렬 완료, 후진 + NFC 대기로 이동")
                    # 장착(NFC 루틴) 실행
                    rent_until_nfc(rent_id)
                    rent_operating = False
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

            if not target_found:
                if lost_target_time is None:
                    lost_target_time = time.time()
                elif (time.time() - lost_target_time) > 1.0:
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.3)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif (time.time() - lost_target_time) > 1.0:
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.01)

    motor_hat.set_throttle(0)
    kit.servo[0].angle = 88
    rent_operating = False
    print("[rent_process] 종료")


def rent_until_nfc(rent_id):
    """
    실제 모듈 후진 + NFC 인식 + 전자석 OFF
    동영상 녹화 예시 (동영상은 임시로 동일 스레드에서 처리)
    """
    nfc_detected_event.clear()

    print("[rent_until_nfc] 후진 시작")
    electromagnet_on()
    kit.servo[0].angle = 88
    motor_hat.set_throttle(-0.4)

    # 동영상 녹화
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    video_filename = f"rent_{rent_id}_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    ret, frame = cap.read()
    if not ret:
        print("[rent_until_nfc] 카메라 에러, 녹화 불가")
        return
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (frame_width, frame_height))

    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)

        if nfc_detected_event.is_set():
            print("[rent_until_nfc] NFC 감지 => 정지")
            motor_hat.set_throttle(0)
            out.release()
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            out.release()
            return

        time.sleep(0.01)

    print("[rent_until_nfc] 전자석 OFF 후 전진")
    motor_hat.set_throttle(0.4)
    time.sleep(1.2)
    electromagnet_off()
    time.sleep(1.0)
    motor_hat.set_throttle(0)
    print("[rent_until_nfc] 장착 완료. 녹화파일:", video_filename)

    # rent 프로세스 → 이 녹화본을 서버로 전송(임시 웹소켓)
    # (이 함수 안에서 바로 보내도 되고, rent_process()에서 send_video_once() 호출해도 됨)
    # 여기서는 "나중에 메인에서" 보내도록 일단 return
    return video_filename


###############################################################################
# (예) 반납 PID + NFC (구조 비슷)
###############################################################################
def return_process(rent_id):
    """
    반납. target_marker_id=11 등. (오프라인 정렬 → NFC)
    """
    target_marker_id = 11
    print(f"[return_process] start, rent_id={rent_id}, marker={target_marker_id}")

    lost_target_time = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[return_process] 카메라 읽기 실패")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            target_found = False
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                if marker_id != target_marker_id:
                    continue
                target_found = True

                cX = int(np.mean(corner[0][:, 0]))
                width = np.linalg.norm(corner[0][1] - corner[0][0])
                height = np.linalg.norm(corner[0][2] - corner[0][1])
                object_size = width * height
                x_rotation = calculate_x_rotation(corner)
                frame_center_x = frame.shape[1] // 2
                error_x = cX - frame_center_x

                if (abs(error_x) < 10 and abs(x_rotation) < 2
                    and abs(object_size - target_size) < target_size*0.1):
                    motor_hat.set_throttle(0)
                    time.sleep(0.5)
                    print("[return_process] 정렬 완료 => 후진 + NFC")
                    video_file = return_until_nfc(rent_id)
                    return video_file
                else:
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

            if not target_found:
                if lost_target_time is None:
                    lost_target_time = time.time()
                elif (time.time() - lost_target_time) > 1.0:
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.3)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif (time.time() - lost_target_time) > 1.0:
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.01)

    motor_hat.set_throttle(0)
    kit.servo[0].angle = 88
    print("[return_process] 종료")
    return None

def return_until_nfc(rent_id):
    nfc_detected_event.clear()
    print("[return_until_nfc] 후진 시작")
    kit.servo[0].angle = 88
    motor_hat.set_throttle(-0.4)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    video_filename = f"return_{rent_id}_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    ret, frame = cap.read()
    if not ret:
        print("[return_until_nfc] 카메라 에러")
        return None
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (frame_width, frame_height))

    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)

        if nfc_detected_event.is_set():
            print("[return_until_nfc] NFC 감지 => 정지")
            motor_hat.set_throttle(0)
            out.release()
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            motor_hat.set_throttle(0)
            out.release()
            return None
        time.sleep(0.01)

    print("[return_until_nfc] 전자석 ON상태에서 전진")
    electromagnet_on()
    motor_hat.set_throttle(0.4)
    time.sleep(2.0)
    motor_hat.set_throttle(0)
    electromagnet_off()

    print("[return_until_nfc] 반납 완료, 파일:", video_filename)
    return video_filename

###############################################################################
# 메인 루프: "임시 웹소켓"을 이용해 명령 받고 → 오프라인 처리 → 다시 임시 웹소켓으로 결과 전송
###############################################################################
def main():
    # NFC 스레드 시작
    nfc_thr = threading.Thread(target=nfc_server_thread, daemon=True)
    nfc_thr.start()

    while True:
        print("\n[Main] 웹소켓 연결하여 명령 대기..")
        cmd, payload = wait_for_command_once()

        if not cmd:
            print("[Main] 명령 없음 → 종료")
            break

        if cmd == "rent":
            rent_id = payload.get("rent_id", "UNKNOWN")
            print(f"[Main] 수신 명령: rent, rent_id={rent_id}")
            # 1) 오프라인 PID + NFC
            video_file = None
            rent_process(rent_id)  # 내부에서 rent_until_nfc() 실행
            # rent_until_nfc()가 최종 녹화 파일을 리턴하도록 해도 되지만,
            # 여기선 rent_until_nfc() 내부에서 반환하지 않고, 필요하다면 리턴하도록 변경 가능

            # 2) 완성된 동영상을 서버 전송(재연결)
            #    - rent_until_nfc()에서 만들어진 AVI 파일명을 알 수 있다면 그걸 써서..
            #    - 여기서는 예시로 "rent_{rent_id}_{timestamp}.avi"를 가정
            # 실제로는 rent_until_nfc()에서 return video_filename 받아와야 함.
            # 편의상 timestamp 없이 "rent_{rent_id}.avi"라면 바로:
            # send_video_once(rent_id, "/vehicle/module/mount", video_file)
            # 예시:
            time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            video_filename = f"rent_{rent_id}_{time_str}.avi"
            if os.path.exists(video_filename):
                send_video_once(rent_id, "/vehicle/module/mount", video_filename)
            else:
                print("[Main] rent 동영상 파일을 찾지 못했음:", video_filename)

        elif cmd == "return":
            rent_id = payload.get("rent_id", "UNKNOWN")
            print(f"[Main] 수신 명령: return, rent_id={rent_id}")
            # 1) 오프라인 PID + NFC
            video_file = return_process(rent_id)

            # 2) 웹소켓 재연결 → 결과 전송
            # (마찬가지로 return_process() + return_until_nfc()에서 만든 파일명을 알아야 함)
            time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            video_filename = f"return_{rent_id}_{time_str}.avi"
            if os.path.exists(video_filename):
                send_video_once(rent_id, "/vehicle/module/return", video_filename)
            else:
                print("[Main] return 동영상 파일을 찾지 못했음:", video_filename)

        else:
            print("[Main] 알 수 없는 cmd:", cmd)
            # 필요하면 break로 종료하거나 계속 대기할 수 있음

        # 계속 반복해서 새 명령을 받으려면 while True 유지
        # 한 번만 하고 끝낼 거면 break

###############################################################################
# 실행부
###############################################################################
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except Exception as e:
        print("Error:", e)
    finally:
        motor_hat.set_throttle(0)
        kit.servo[0].angle = 88
        pca.deinit()
        GPIO.cleanup()
        cap.release()
        cv2.destroyAllWindows()
        print("프로그램 종료")
