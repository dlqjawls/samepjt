import cv2
import numpy as np

# ArUco 딕셔너리 및 탐지 파라미터 설정
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
aruco_params = cv2.aruco.DetectorParameters()

# 카메라 열기 (CSI 카메라 또는 USB 카메라)
def gstreamer_pipeline(sensor_id=0, capture_width=1920, capture_height=1080, display_width=480, display_height=270, framerate=30, flip_method=0):
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

# 실시간 ArUco 마커 인식
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # 그레이스케일 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ArUco 마커 검출
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        for i, corner in enumerate(corners):
            # 마커 윤곽선 그리기
            cv2.polylines(frame, [np.int32(corner)], isClosed=True, color=(0, 255, 0), thickness=2)

            # 마커 중심 좌표 계산
            cX = int(np.mean(corner[0][:, 0]))
            cY = int(np.mean(corner[0][:, 1]))

            # 마커 ID 출력
            marker_id = int(ids[i])
            cv2.putText(frame, f"ID: {marker_id}", (cX - 20, cY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # 중심점 표시
            cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)

            print(f"Detected ArUco Marker ID: {marker_id} at ({cX}, {cY})")

    # 화면 출력
    cv2.imshow("ArUco Marker Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료 처리
cap.release()
cv2.destroyAllWindows()
print("Camera closed, program terminated.")
