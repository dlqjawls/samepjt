import cv2

def gstreamer_pipeline(sensor_id=0, capture_width=1920, capture_height=1080, display_width=480, display_height=270, framerate=30, flip_method=0):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=%d, height=%d, framerate=%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, format=BGRx, width=%d, height=%d ! "
        "videoconvert ! "
        "video/x-raw, format=BGR ! appsink"
        % (sensor_id, capture_width, capture_height, framerate, flip_method, display_width, display_height)
    )

# 두 개의 카메라 설정
cap1 = cv2.VideoCapture(gstreamer_pipeline(sensor_id=0), cv2.CAP_GSTREAMER)
cap2 = cv2.VideoCapture(gstreamer_pipeline(sensor_id=1), cv2.CAP_GSTREAMER)

if not cap1.isOpened() or not cap2.isOpened():
    print("Error: One or both cameras could not be opened.")
    exit()

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if ret1:
        cv2.imshow('Camera 1', frame1)  # 첫 번째 카메라 출력

    if ret2:
        cv2.imshow('Camera 2', frame2)  # 두 번째 카메라 출력

    # 키 입력 대기
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # 'q' 키를 누르면 종료
        break

# 모든 작업이 완료되면 리소스 해제
cap1.release()
cap2.release()
cv2.destroyAllWindows()
