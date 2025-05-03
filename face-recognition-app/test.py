import cv2
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cv2.namedWindow("Webcam Test", cv2.WINDOW_NORMAL)
if not cap.isOpened():
    print("Webcam not working.")
else:
    print("Webcam opened successfully.")
cap.release()
