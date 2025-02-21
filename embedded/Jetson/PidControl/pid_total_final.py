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
import websocket

"""
최종 성공
"""
CLIENT_ID     = "PBVVINNUMBER00001"
###############################################################################
# 전역 설정
###############################################################################
# WS_SERVER_URL = "ws://192.168.100.106:9001/api/socket/ws"
# WS_SERVER_URL = "wss://backend-wandering-river-6835.fly.dev/api/socket/ws"
WS_SERVER_URL = "ws://moducar.duckdns.org:8000/api/socket/ws"


target_size = 8000
max_speed   = 0.40
min_speed   = 0.20

# GPIO / 전자석
GPIO.cleanup()
PWM_PIN = 33
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)  # 1kHz
pwm.start(0)

def flush_nfc_data(timeout=3.0):
    """지정한 시간 동안 get_sensor_data()를 반복 호출해 남은 데이터를 소진."""
    print("[flush_nfc_data] 시작")
    start = time.time()
    while time.time() - start < timeout:
        leftover = get_sensor_data()
        if leftover:
            print("[flush_nfc_data] 버퍼에 남은 데이터 수신:", leftover)
        time.sleep(0.05)
    print("[flush_nfc_data] 종료")


def electromagnet_on():
    pwm.ChangeDutyCycle(100)
    print("[Electromagnet] ON")

def electromagnet_off():
    pwm.ChangeDutyCycle(10)
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)
    print("[Electromagnet] OFF")

# I2C, PCA9685, ServoKit
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 60

class PWMThrottleHat:
    def __init__(self, pwm_obj):
        self.pwm = pwm_obj
        self.pwm.frequency = 60
    def set_throttle(self, throttle):
        pulse = min(0xFFFF, max(0, int(0xFFFF*abs(throttle))))
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
kit.servo[0].angle = 88

# 카메라 세팅
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

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
    print("[Error] CSI 카메라 오픈 실패.")
    # exit()  # 필요시 종료

# TCP 서버 (라즈베리파이 -> NFC UID)
HOST = "0.0.0.0"
PORT = 5000
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen(1)
print(f"[TCP] NFC/센서 데이터 수신 대기... ({HOST}:{PORT})")
client_sock, addr = server_sock.accept()
print(f"[TCP] 연결됨: {addr}")

def get_sensor_data():
    """
    {"NFC_UID": "...", "ULTRASONIC_FRONT": ..., "ULTRASONIC_BACK": ...} 형태를 가정
    """
    try:
        data = client_sock.recv(1024).decode().strip()
        if not data:
            return None
        for line in data.splitlines():
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                print("[TCP] JSON 파싱 실패:", line)
    except:
        pass
    return None

###############################################################################
# NFC 인식하며 후진 → 태그 감지 시 정지 & 영상 저장
# (렌트/리턴 공통으로 사용할 수 있지만, 세부 동작만 조금씩 다름)
###############################################################################
def calculate_rotation(corner):
    top_left, top_right, bottom_right, bottom_left = corner[0]
    h_left = bottom_left[1] - top_left[1]
    h_right = bottom_right[1] - top_right[1]
    if h_left>0 and h_right>0:
        rotate_angle = int(round(math.degrees(
            math.atan((h_right - h_left)/(top_right[0]-top_left[0]))
        ))) * 2
        return max(min(rotate_angle, 90), -90)
    return 0

def rent_video_until_nfc(cmd_name="cmd_name"):
    """
    - 후진하며 NFC 감지 대기 & 녹화
    - NFC 감지 → 정지
    - 필요 시 전자석 ON/OFF, 약간 전진 등 후처리
    - 녹화 파일 경로 리턴
    """
    print("[record_video_until_nfc] 후진 시작.")
    # 전자석 On 원하면 
    electromagnet_on()
    kit.servo[0].angle = 90
    motor_hat.set_throttle(-0.40)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    video_filename = f"{rent_id}_{cmd_name}_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    ret, frame = cap.read()
    if not ret:
        print("[Error] 카메라 첫 프레임 실패")
        return None

    h, w = frame.shape[0], frame.shape[1]
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (w, h))
    print("[record_video_until_nfc] 녹화 중, NFC 태그 인식 시 정지")
    

    ultrasonic_triggered = True  # 후방 초음파가 한 번이라도 10 이하가 된 경우 True
    nfc_detected = False
    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("NFC detection", frame)

        sensor_data = get_sensor_data()
        if sensor_data:
            ultrasonic_back = sensor_data.get("ULTRASONIC_BACK")
            # 후방 초음파 값이 10 이하이면 flag를 True로 설정
            if ultrasonic_back is not None and ultrasonic_back <= 10:
                ultrasonic_triggered = True
            nfc_uid = sensor_data.get("NFC_UID")
        else:
            nfc_uid = None

        # 한 번이라도 후방 초음파가 10 이하로 감지되었으면, 그때부터 NFC 값이 있으면 정지
        if ultrasonic_triggered and nfc_uid:
            print(f"[NFC 감지] UID={nfc_uid} (ultrasonic_triggered=True) -> 즉시 정지")
            motor_hat.set_throttle(0)
            nfc_detected = True
            # time.sleep(1.0)
            out.release()
            print(f"녹화 저장 완료: {video_filename}")
            break

        if cv2.waitKey(1)&0xFF == ord('q'):
            print("[User] q -> 중단")
            motor_hat.set_throttle(0)
            out.release()
            return None

        # time.sleep(0.05)


    kit.servo[0].angle = 88
    
    print("[record_video_until_nfc] 전자석 ON 상태로 전진 (예시)")
    motor_hat.set_throttle(0.4)
    time.sleep(1.5)
    electromagnet_off()
    time.sleep(10.0)
    motor_hat.set_throttle(0)

    cv2.destroyWindow("NFC detection")

    return video_filename


def return_video_until_nfc(cmd_name="cmd_name"):
    """
    - 후진하며 NFC 감지 대기 & 녹화
    - NFC 감지 → 정지
    - 필요 시 전자석 ON/OFF, 약간 전진 등 후처리
    - 녹화 파일 경로 리턴
    """
    print("[record_video_until_nfc] 후진 시작.")
    # 전자석 On 원하면 
    # electromagnet_on()
    kit.servo[0].angle = 90
    motor_hat.set_throttle(-0.40)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    video_filename = f"{rent_id}_{cmd_name}_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    ret, frame = cap.read()
    if not ret:
        print("[Error] 카메라 첫 프레임 실패")
        return None
    h, w = frame.shape[0], frame.shape[1]
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (w, h))
    print("[record_video_until_nfc] 녹화 중, NFC 태그 인식 시 정지")

    nfc_detected = False
    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow("NFC detection", frame)

        sensor_data = get_sensor_data()
        nfc_uid = sensor_data.get("NFC_UID") if sensor_data else None

        if nfc_uid:
            print(f"[NFC 감지] UID={nfc_uid}, 즉시 정지")
            motor_hat.set_throttle(0)
            nfc_detected = True
            # time.sleep(1.0)
            out.release()
            print(f"녹화 저장 완료: {video_filename}")
            break

        if cv2.waitKey(1)&0xFF == ord('q'):
            print("[User] q -> 중단")
            motor_hat.set_throttle(0)
            out.release()
            return None
        # time.sleep(0.05)


    print("[record_video_until_nfc] 전자석 ON 상태로 전진 (예시)")
    motor_hat.set_throttle(0.4)
    # time.sleep(1.5)
    # electromagnet_off()
    time.sleep(10.0)
    motor_hat.set_throttle(0)


    return video_filename

###############################################################################
# (1) 렌트 프로세스 (target_marker_id=1)
###############################################################################
def rent_process(ws_send, rent_id, target_marker_id):
    # target_marker_id = 1
    pid_x = PID(0.06, 0.013, 0.004, setpoint=0)
    pid_rot = PID(0.055, 0.011, 0.0035, setpoint=0)
    pid_spd = PID(0.022, 0.007, 0.0018, setpoint=target_size)

    lost_target_time = None

    # flush_nfc_data()

    print(f"[rent_process] 시작. target_marker_id={target_marker_id}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Error] 카메라 프레임 읽기 실패")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        found = False
        if ids is not None:
            for i, corner in enumerate(corners):
                mid = int(ids[i][0])
                if mid != target_marker_id:
                    continue
                found = True

                # 추가
                cv2.polylines(frame, [np.int32(corner)], isClosed=True, color=(0, 255, 0), thickness=2)
                
                cX = int(np.mean(corner[0][:,0]))
                width  = np.linalg.norm(corner[0][1]-corner[0][0])
                height = np.linalg.norm(corner[0][2]-corner[0][1])
                obj_size = width*height
                x_rot = calculate_rotation(corner)
                fc_x = frame.shape[1]//2
                err_x = cX - fc_x

                # cv2.putText(frame, f"{module_name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                # cv2.putText(frame, f"size: {int(obj_size)}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                # cv2.putText(frame, f"parallel: {'yes' if abs(x_rot) < 3 else 'no'}",
                #             (50,110), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                #             (0,255,0) if abs(x_rot)<3 else (0,0,255), 2)
                # cv2.putText(frame, f"center: {'yes' if abs(err_x) < 15 else 'no'}",
                #             (50,140), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                #             (0,255,0) if abs(err_x)<15 else (0,0,255), 2)
                # cv2.imshow("Aruco Marker Tracking (PID)", frame)


                # 정렬 완료 조건
                if abs(err_x)<13and abs(x_rot)<3 and abs(obj_size - target_size)<target_size*0.1:
                    print("[rent_process] 정렬 완료 -> NFC 후진")
                    motor_hat.set_throttle(0)
                    time.sleep(1.0)
                    # rent_process 루프를 종료하여 더 이상 cap에서 프레임을 읽지 않게 함
                    cv2.destroyWindow("Rent ArUco")

                    # break
                    # NFC 후진 & 녹화
                    video_file = rent_video_until_nfc("rent")
                    # 완료 후 ffmpeg/전송
                    if video_file:
                        send_video_to_server(ws_send, video_file, "/vehicle/module/mount", rent_id)  
                        # rent_id 예시 (실제로는 payload에서 받은 값 쓰면 됨)
                    return
                else:
                    # PID 제어
                    steer_adj = pid_x(err_x)
                    rot_adj   = pid_rot(x_rot)
                    final_adj = 0.7*steer_adj + 0.3*rot_adj

                    if obj_size>target_size*1.1:
                        new_steer = kit.servo[0].angle

                        new_steer = 88 - (kit.servo[0].angle - 88)
                        new_steer = max(68, min(108, new_steer - final_adj))
                        kit.servo[0].angle = new_steer

                        spd_adj = pid_spd(obj_size)
                        spd_adj = max(min_speed, min(max_speed, spd_adj))
                        motor_hat.set_throttle(spd_adj)
                    elif obj_size<target_size*0.9:
                        new_steer = kit.servo[0].angle
                        new_steer = max(68, min(108, new_steer + final_adj))
                        kit.servo[0].angle = new_steer

                        spd_adj = pid_spd(obj_size)
                        spd_adj = max(min_speed, min(max_speed, spd_adj))
                        motor_hat.set_throttle(-spd_adj)

            if not found:
                if lost_target_time is None:
                    lost_target_time = time.time()
                elif time.time()-lost_target_time>1.0:
                    kit.servo[0].angle = 88
                    motor_hat.set_throttle(0.3)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time()-lost_target_time>1.0:
                kit.servo[0].angle = 88
                motor_hat.set_throttle(0.3)

        cv2.imshow("Rent ArUco", frame)
        if cv2.waitKey(1)&0xFF==ord('q'):
            break
        time.sleep(0.01)

    print("[rent_process] 종료(오류 또는 q)")
    motor_hat.set_throttle(0)

    flush_nfc_data()



###############################################################################
# (2) 리턴 프로세스 (target_marker_id=11)
###############################################################################
def return_process(ws_send, rent_id):
    target_marker_id = 11
    pid_x = PID(0.06, 0.013, 0.004, setpoint=0)
    pid_rot = PID(0.055, 0.011, 0.0035, setpoint=0)
    pid_spd = PID(0.022, 0.007, 0.0018, setpoint=target_size)

    # flush_nfc_data()

    lost_target_time = None

    print("[return_process] 시작. target_marker_id=11")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Error] 카메라 프레임 읽기 실패")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
        corners, ids, _ = detector.detectMarkers(gray)

        found = False
        if ids is not None:
            for i, corner in enumerate(corners):
                mid = int(ids[i][0])
                if mid != target_marker_id:
                    continue
                found = True

                cX = int(np.mean(corner[0][:,0]))
                width  = np.linalg.norm(corner[0][1]-corner[0][0])
                height = np.linalg.norm(corner[0][2]-corner[0][1])
                obj_size = width*height
                x_rot = calculate_rotation(corner)
                fc_x = frame.shape[1]//2
                err_x = cX - fc_x

                # 정렬 완료
                if abs(err_x)<13 and abs(x_rot)<3 and abs(obj_size - target_size)<target_size*0.1:
                    print("[return_process] 정렬 완료 -> NFC 후진")
                    motor_hat.set_throttle(0)
                    time.sleep(1.0)
                    # NFC 후진 & 녹화
                    video_file = return_video_until_nfc("return")
                    if video_file:
                        send_video_to_server(ws_send, video_file, "/vehicle/module/return", rent_id)
                    return
                else:
                    # PID
                    steer_adj = pid_x(err_x)
                    rot_adj   = pid_rot(x_rot)
                    final_adj = 0.7*steer_adj + 0.3*rot_adj

                    # 가까워질수록 보정 배율을 높이기 위한 게인 스케줄링
                    error_ratio = abs(obj_size - target_size) / target_size
                    alpha = 1.0  # 추가 배율 상수 (튜닝 가능)
                    multiplier = 1 + (1 - min(error_ratio, 1)) * alpha
                    final_adj *= multiplier

                    if obj_size>target_size*1.1:
                        new_steer = kit.servo[0].angle

                        new_steer = 85 - (kit.servo[0].angle - 85)
                        new_steer = max(65, min(105, new_steer - final_adj))
                        kit.servo[0].angle = new_steer

                        spd_adj = pid_spd(obj_size)
                        spd_adj = max(min_speed, min(max_speed, spd_adj))
                        motor_hat.set_throttle(spd_adj)
                    elif obj_size<target_size*0.9:
                        new_steer = kit.servo[0].angle
                        new_steer = max(65, min(105, new_steer + final_adj))
                        kit.servo[0].angle = new_steer

                        spd_adj = pid_spd(obj_size)
                        spd_adj = max(min_speed, min(max_speed, spd_adj))
                        motor_hat.set_throttle(-spd_adj)

            if not found:
                if lost_target_time is None:
                    lost_target_time = time.time()
                elif time.time()-lost_target_time>1.0:
                    kit.servo[0].angle = 85
                    motor_hat.set_throttle(0.3)
        else:
            if lost_target_time is None:
                lost_target_time = time.time()
            elif time.time()-lost_target_time>1.0:
                kit.servo[0].angle = 85
                motor_hat.set_throttle(0.3)

        cv2.imshow("Return ArUco", frame)
        if cv2.waitKey(1)&0xFF==ord('q'):
            break
        time.sleep(0.01)

    print("[return_process] 종료(오류 또는 q)")
    motor_hat.set_throttle(0)

    flush_nfc_data()


###############################################################################
# ffmpeg 변환 & base64 전송
###############################################################################
def send_video_to_server(ws_send, video_filename, path, rent_id="unknown"):
    global module_name
    """
    1) ffmpeg avi → mp4
    2) base64 인코딩
    3) 웹소켓 전송
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if path == "/vehicle/module/mount":
        status = "rent"
        module_name = "camping_module"
    else:
        status = "return"
        module_name = "return place"
    output_mp4 = f"{rent_id}_{status}_{module_name}_{timestamp}.mp4"

    # ffmpeg 변환
    conversion_cmd = f'ffmpeg -y -i "{video_filename}" -vcodec libx264 "{output_mp4}"'
    print("[ffmpeg] 변환중:", conversion_cmd)
    os.system(conversion_cmd)

    # base64
    try:
        with open(output_mp4, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode("utf-8")
        msg = {
            "type": "service",
            "path": path,  # "/vehicle/module/mount" or "/vehicle/module/return"
            "payload": {
                "rent_id": rent_id,
                "video": encoded
            }
        }
        ws_send(json.dumps(msg))
        print("[send_video_to_server] 전송 완료:", output_mp4)
    except Exception as e:
        print("[send_video_to_server] 에러:", e)

###############################################################################
# 웹소켓 콜백
###############################################################################
def on_open(ws):
    print("[WebSocket] 연결됨")
    # 서버에 차량 연결 이벤트 보낼 수도 있음
    init_msg = {"type":"service","path":"/vehicle/connect","payload":{}}
    ws.send(json.dumps(init_msg))

def on_message(ws, message):
    global rent_id
    print("[WebSocket] 수신:", message)
    try:
        data = json.loads(message)
        if data.get("type") == "service":
            path = data.get("path", "")
            payload = data.get("payload", {})
            rent_id = payload.get("rent_id", None)
            # module_nfc_tag 값에 따라 target_marker_id 결정
            module_nfc_tag = payload.get("module_nfc_tag", None)
            if module_nfc_tag == "043F926A6C1D90":
                target_marker_id = 1
            elif module_nfc_tag == "043F8E6A6C1D90":
                target_marker_id = 2

            if path == "/vehicle/rent":
                print("[Main] 렌트 명령 수신 -> rent_process 실행")
                flush_nfc_data()
                # target_marker_id를 인자로 전달하도록 변경
                rent_process(ws.send, rent_id, target_marker_id)
            elif path == "/vehicle/return":
                print("[Main] 리턴 명령 수신 -> return_process 실행")
                flush_nfc_data()
                return_process(ws.send, rent_id)
            else:
                print("[Main] 알 수 없는 명령 path:", path)
        else:
            print("[Main] 기타 메시지:", data)
    except Exception as e:
        print("[WebSocket] JSON 파싱 실패:", e)


def on_error(ws, error):
    print("[WebSocket] 에러:", error)

def on_close(ws, code, msg):
    print("[WebSocket] 연결 종료:", code, msg)

###############################################################################
# 메인 실행부
###############################################################################
if __name__ == "__main__":
    try:
        # 웹소켓 연결(상시 유지)
        ws_app = websocket.WebSocketApp(
            f"{WS_SERVER_URL}/{CLIENT_ID}",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # 웹소켓을 별도 쓰레드에서 실행
        wst = threading.Thread(
            target=ws_app.run_forever,
            kwargs={'ping_interval': 10000, 'ping_timeout': 9999}
        )
        wst.daemon = True
        wst.start()

        print("[Main] 웹소켓 연결 후 명령 대기 중... (rent/return)")

        # 메인 스레드는 종료되지 않고 대기
        while True:
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("[Main] KeyboardInterrupt")
    finally:
        motor_hat.set_throttle(0)
        kit.servo[0].angle = 88
        pca.deinit()
        GPIO.cleanup()
        cap.release()
        cv2.destroyAllWindows()
        print("[Main] 프로그램 종료")
