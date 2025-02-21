import cv2
import numpy as np
import math

# ArUco 딕셔너리 및 탐지 파라미터 설정
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

# 마커 ID에 따른 텍스트 정의 (옵션)
marker_texts = {
    1: "Module A",
    11: "Module B",
    21: "Module C",
}

# 카메라 열기 (CSI 또는 USB 카메라)
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

    # 프레임을 그레이스케일로 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ArUco 마커 검출
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        for i, corner in enumerate(corners):
            # 마커 경계선 그리기
            cv2.polylines(frame, [np.int32(corner)], isClosed=True, color=(0, 255, 0), thickness=2)

            # 네 개의 코너 추출 (좌상단, 우상단, 우하단, 좌하단)
            top_left = corner[0][0]
            top_right = corner[0][1]
            bottom_right = corner[0][2]
            bottom_left = corner[0][3]

            # 회전 각도 계산
            # a: 왼쪽 변의 높이 (bottom_left - top_left)
            # b: 상단의 길이 (top_right - top_left)
            height_left = bottom_left[1] - top_left[1]
            height_right = bottom_right[1] - top_right[1]
            base_length = top_right[0] - top_left[0]
            
            if base_length != 0:
                # arctan((height_right - height_left) / base_length)를 도(degree)로 변환
                raw_angle = math.degrees(math.atan((height_right - height_left) / base_length))
                # 보정 인자(예: 3)를 곱해 회전 각도 조정, 소수점 1자리까지 유지
                rotate_angle = round(raw_angle * 3, 1)
                # 회전 각도를 ±90°로 제한
                rotate_angle = float(np.clip(rotate_angle, -90, 90))
            else:
                rotate_angle = 0.0

            # 평행 정렬을 위한 조향각은 rotate_angle의 부호를 반전한 값 (소수점 1자리까지)
            steering_angle = round(-rotate_angle, 1)

            # 조향 상태 결정 (세 가지 상태: Parallel, Right Rotation, Left Rotation)
            if steering_angle > 3:
                steering_status = "Left Rotation"
            elif steering_angle < -3:
                steering_status = "Right Rotation"
            else:
                steering_status = "Parallel"

            # 마커 중심 좌표 계산
            cX = int(np.mean(corner[0][:, 0]))
            cY = int(np.mean(corner[0][:, 1]))

            # 마커 ID에 따른 라벨 (옵션)
            marker_id = int(ids[i])
            label = marker_texts.get(marker_id, f"ID: {marker_id}")

            # 표시할 텍스트: "State | SteeringAngle" (조향각은 부호 그대로 소수점 1자리까지 표시)
            display_text = f"{steering_status} | Angle: {steering_angle:.1f}"

            # 텍스트 위치 설정 (마커의 좌상단 기준)
            text_x, text_y = int(top_left[0]), int(top_left[1]) - 10

            # 텍스트 가독성을 위한 검은색 배경 추가
            cv2.rectangle(frame, (text_x - 5, text_y - 20), (text_x + 270, text_y + 5), (0, 0, 0), -1)
            cv2.putText(frame, display_text, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # 마커 중심 표시
            cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)

            print(f"{steering_status} | {steering_angle:.1f}°")

    cv2.imshow("ArUco Marker - Parallel Alignment Steering Angle", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Camera closed, program terminated.")
