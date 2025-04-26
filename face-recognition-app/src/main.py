import cv2 as cv
import face_recognition
import time
import os
import serial
import pickle
def main():
    # Check if the DNN model files exist
    proto_path = r"a:\College stuff\DATA AQ\face-recognition-app\src\deploy.prototxt"
    model_path = r"a:\College stuff\DATA AQ\face-recognition-app\src\res10_300x300_ssd_iter_140000.caffemodel"
    if not os.path.exists(proto_path) or not os.path.exists(model_path):
        print("Model files not found. Please check the paths.")
        return
    net = cv.dnn.readNetFromCaffe(proto_path, model_path)

     # Initialize serial communication with Arduino
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)  # Replace 'COM3' with your Arduino's port

    # Load and preprocess the reference image
    reference_image_path = r"A:\College stuff\DATA AQ\Nour1.jpg"  # Reference image path
    reference_image = face_recognition.load_image_file(reference_image_path)
    reference_encodings = face_recognition.face_encodings(reference_image)

    if len(reference_encodings) == 0:
        print("No face detected in the reference image. Please use a valid image.")
        return
    reference_encoding = reference_encodings[0]

    # Initialize webcam
    video_capture = cv.VideoCapture(0)
    video_capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

    print("Looking for a match... Press 'q' to quit.")

    # Record the start time
    start_time = time.time()

    while True:
        # Capture a frame from the webcam
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame from webcam.")
            break

        # Resize frame for faster processing
        small_frame = cv.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # Detect faces using DNN
        blob = cv.dnn.blobFromImage(small_frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        h, w = small_frame.shape[:2]
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Confidence threshold
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (x, y, x1, y1) = box.astype("int")
                faces.append((x * 2, y * 2, (x1 - x) * 2, (y1 - y) * 2))  # Scale back to original size

        match_found = False
        for (x, y, w, h) in faces:
            # Extract the face region
            face_frame = frame[y:y+h, x:x+w]
            if face_frame.size == 0:
                continue

            # Convert the face region to RGB for face_recognition
            face_rgb = cv.cvtColor(face_frame, cv.COLOR_BGR2RGB)

            # Get face encodings for the detected face
            face_encodings = face_recognition.face_encodings(face_rgb)
            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]

                # Compare with the reference encoding
                matches = face_recognition.compare_faces([reference_encoding], face_encoding, tolerance=0.6)
                if True in matches:
                    match_found = True
                    # Draw a green bounding box for a match
                    cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv.putText(frame, "Match", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    time.sleep(1)  # Pause for 1 second to show the match
                    break  # Exit the loop if a match is found
                elif False in matches:
                    # Draw a red bounding box for no match
                    cv.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv.putText(frame, "No Match", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    
            

        # Display the webcam feed
        cv.imshow("Webcam Feed", frame)

        # Break the loop if 'q' is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        # Check if 5 seconds have passed
        elapsed_time = time.time() - start_time
        if elapsed_time > 30 and not match_found:
            print("No match found within 5 seconds. Exiting...")
            # Send "NO_MATCH" signal to Arduino
            arduino.write(b'NO_MATCH\n')
            break
        elif match_found:
            print("Match found! Exiting...")
            # Send "MATCH" signal to Arduino
            arduino.write(b'MATCH\n')
            break

    # Release the webcam and close windows
    video_capture.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()