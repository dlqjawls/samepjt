import cv2
import numpy as np

# ArUco 딕셔너리 로드
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)

# 생성할 마커 ID 및 크기 설정
marker_id = 21
marker_size = 200  # 픽셀 크기

# OpenCV 4.12에서는 drawMarker 대신 generateImageMarker 사용
marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)

# 마커 저장
cv2.imwrite(f"aruco_marker_{marker_id}.png", marker_img)

# 화면에 표시
# cv2.imshow(f"Aruco Marker ID {marker_id}", marker_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
