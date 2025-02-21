import cv2
import numpy as np
from simple_pid import PID

# ArUco 딕셔너리 및 탐지 파라미터 설정
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

# ID별 표시할 텍스트 정의
marker_texts = {
    1: "Module A",
    11: "Module B",
    21: "Module C",
}

# 목표 면적 및 속도 범위 설정
target_area_center = 8000    # 목표 중심 면적
max_area_diff = 4000         # 최대 면적 차이 (4000일 때와 12000일 때)
min_speed = 0.2              # marker_area가 8000일 때 속도
max_speed = 1.0              # marker_area가 4000 또는 12000일 때 속도
pid_range = max_speed - min_speed  # 0.2

# PID 제어기 설정  
# 입력으로 사용할 값: inverted_error = max_area_diff - abs(marker_area - target_area_center)
# setpoint는 최대값인 max_area_diff (4000)로 설정함.
# 단, PID의 게인은 환경에 맞게 조절하세요.
pid_speed = PID(0.00008, 0.000001, 0, setpoint=max_area_diff)
pid_speed.output_limits = (0, pid_range)  # 출력값은 0 ~ 0.2 사이

# 카메라 열기 (CSI 카메라 또는 USB 카메라)
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

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # 그레이스케일 변환 및 ArUco 마커 검출
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        for i, corner in enumerate(corners):
            marker_id = int(ids[i])
            label = marker_texts.get(marker_id, str(marker_id))

            # 마커의 네 모서리 좌표를 이용하여 면적 계산
            width = np.linalg.norm(corner[0][0] - corner[0][1])
            height = np.linalg.norm(corner[0][1] - corner[0][2])
            marker_area = int(width * height)

            # inverted_error 계산: marker_area가 목표면적(8000)에서 벗어난 정도에 따라 PID 입력 결정
            # marker_area가 8000이면 |marker_area - 8000| = 0 → inverted_error = 4000 (최대)
            # marker_area가 4000 또는 12000이면 |marker_area - 8000| = 4000 → inverted_error = 0
            inverted_error = max(max_area_diff - abs(marker_area - target_area_center), 0)

            # PID 제어기를 사용하여 추가 속도 값을 산출하고, min_speed를 더함
            additional_speed = pid_speed(inverted_error)
            speed_adjust = min_speed + additional_speed

            # if marker_area > target_area_center:
            #     speed_adjust = -speed_adjust

            # 마커 테두리 그리기
            cv2.polylines(frame, [np.int32(corner)], isClosed=True, color=(0, 255, 0), thickness=2)

            # 텍스트 표시 (객체 면적과 계산된 속도)
            display_text = f"Size: {marker_area} | Speed: {speed_adjust:.2f}"
            top_left = corner[0][0]
            text_x, text_y = int(top_left[0]), int(top_left[1]) - 10

            # 텍스트 가독성을 위한 검은색 배경
            cv2.rectangle(frame, (text_x - 5, text_y - 50), (text_x + 300, text_y + 5), (0, 0, 0), -1)
            cv2.putText(frame, display_text, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Target Size : {target_area_center}", (text_x, text_y - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            print(f"Size: {marker_area} | PID Speed: {speed_adjust:.2f}")

    cv2.imshow("ArUco Marker Detection - PID Speed Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Camera closed, program terminated.")
