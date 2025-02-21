import cv2
import numpy as np

# ArUco 딕셔너리 및 탐지 파라미터 설정
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

# ID별 표시할 텍스트 정의
marker_texts = {
    1: "Module A",
    11: "Module B",
    21: "Module C",
}

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

    # 프레임 중앙 좌표 계산
    frame_center_x = frame.shape[1] // 2
    offset_threshold = 30  # 중앙 허용 오차 (픽셀)

    # 그레이스케일 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ArUco 마커 검출
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        for i, corner in enumerate(corners):
            marker_id = int(ids[i])
            label = marker_texts.get(marker_id, f"ID: {marker_id}")

            # 마커 중심 좌표 계산
            cX = int(np.mean(corner[0][:, 0]))
            cY = int(np.mean(corner[0][:, 1]))

            # 중앙 정렬 여부 판단
            if abs(cX - frame_center_x) <= offset_threshold:
                position_status = "Centered"
            elif cX < frame_center_x:
                position_status = "Left"
            else:
                position_status = "Right"

            # 조향 각도 계산
            # error: 카메라 중앙과 마커 중심의 차이 (픽셀 단위)
            # 양수이면 마커가 왼쪽, 음수이면 오른쪽에 위치
            error = frame_center_x - cX

            # 조향 각도는 error에 비례하도록 계산 (게인 값은 필요에 따라 조절)
            steering_gain = 0.1
            steering_angle = steering_gain * error

            # 최대 ±30°로 제한
            max_steering_angle = 30
            steering_angle = np.clip(steering_angle, -max_steering_angle, max_steering_angle)

            # 마커 테두리 그리기
            cv2.polylines(frame, [np.int32(corner)], isClosed=True, color=(0, 255, 0), thickness=2)

            # 텍스트 표시 (모듈명, 중앙 정렬 상태, 조향 각도)
            display_text = f"{position_status} | Angle: {steering_angle:.1f}"
            top_left = corner[0][0]
            text_x, text_y = int(top_left[0]), int(top_left[1]) - 10

            # 텍스트 가독성을 위한 검은색 배경 추가
            cv2.rectangle(frame, (text_x - 5, text_y - 20), (text_x + 220, text_y + 5), (0, 0, 0), -1)
            cv2.putText(frame, display_text, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # 마커 중심점 표시
            cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)
            print(f"{position_status} | Steering Angle: {steering_angle:.1f}°")

    cv2.imshow("ArUco Marker Detection - Center Alignment with Steering Angle", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Camera closed, program terminated.")
