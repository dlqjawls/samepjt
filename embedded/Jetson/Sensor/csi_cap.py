"""
[누르는 키에 따라 이미지 저장, 영상 녹화]
1 : 이미지 캡쳐
2 : 녹화 시작 / 종료
3 : 프로그램 종료
"""

import cv2
import os
# import ffmpeg

def gstreamer_pipeline(
    sensor_id=1,
    capture_width=1280,  
    capture_height=720,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=%d, height=%d, framerate=%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, format=BGRx, width=%d, height=%d ! "
        "videoconvert ! "
        "video/x-raw, format=BGR ! appsink"
        % (sensor_id, capture_width, capture_height, framerate, flip_method, display_width, display_height)
    )



# CSI 카메라 설정
cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

# CUDA가 가능한지 확인
use_cuda = cv2.cuda.getCudaEnabledDeviceCount() > 0
if use_cuda:
    print("CUDA가 활성화되었습니다.")
else:
    print("CUDA를 사용할 수 없습니다. CPU 모드로 전환합니다.")

# 비디오 코덱 정의 및 VideoWriter 객체 초기화
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None  # 초기에는 비어있음
is_recording = False  # 녹화 상태를 추적
cnt = 0

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        if use_cuda:
            # GPU 메모리로 프레임 올리기
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)
            
            # GPU에서 컬러 변환 (BGR to HSV)
            gpu_hsv = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2HSV)
            # 다시 BGR로 변환하여 출력
            gpu_processed = cv2.cuda.cvtColor(gpu_hsv, cv2.COLOR_HSV2BGR)
            frame = gpu_processed.download()  # 다시 CPU 메모리로 다운로드
        else:
            # CPU에서 처리할 때는 원본 프레임 그대로 사용
            frame = frame

        # 화면에 현재 프레임을 출력
        cv2.imshow('frame', frame)

        # 키 입력 대기
        key = cv2.waitKey(1) & 0xFF

        if key == ord('1'):
            # 1번 누르면 사진 촬영
            cnt += 1
            cv2.imwrite(f'{cnt}.jpg', frame)
            print(f"Image captured and saved as '{cnt}.jpg'")

        elif key == ord('2'):
            # 2번 누르면 녹화 시작/중지
            if is_recording:
                print("Recording stopped.")
                is_recording = False
                out.release()  # 비디오 파일 닫기
                out = None
            else:
                print("Recording started.")
                out = cv2.VideoWriter('output_video.avi', fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                is_recording = True

        elif key == ord('3'):
            # 3번 누르면 종료
            print("Exiting program.")
            break

        if is_recording:
            # 녹화 중이면 현재 프레임을 비디오에 저장
            out.write(frame)

    else:
        break

# 모든 작업이 완료되면 리소스 해제
cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()
