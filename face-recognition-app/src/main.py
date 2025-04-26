    import cv2 as cv
    import face_recognition
    import time  # Import time module
    import serial  # Import pyserial for Arduino communication
    from utils.image_processing import load_image

    def main():
        # Initialize serial communication with Arduino
        #arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)  # Replace 'COM3' with your Arduino's port

        # Load Haar Cascade for face detection
        face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            print("Failed to load Haar Cascade model.")
            return

        # Load and preprocess the reference image
        image_path = r"A:\College stuff\DATA AQ\Fares1.jpg"  # Reference image path
        reference_image = load_image(image_path)
        reference_image = cv.cvtColor(reference_image, cv.COLOR_BGR2RGB)  # Convert to RGB for face_recognition

        # Get face encoding for the reference image
        reference_encodings = face_recognition.face_encodings(reference_image)
        if len(reference_encodings) == 0:
            print("No face detected in the reference image. Please use a valid image.")
            return
        reference_encoding = reference_encodings[0]

        # Initialize webcam
        video_capture = cv.VideoCapture(0)  # 0 is the default camera
        video_capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)  # Set resolution
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

            # Convert the frame to grayscale for Haar Cascade
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            # Detect faces using Haar Cascade
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

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
                        break  # Exit the loop if a match is found

            # Display the webcam feed
            cv.imshow("Webcam Feed", frame)

            # Break the loop if 'q' is pressed
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

            # Check if 5 seconds have passed
            elapsed_time = time.time() - start_time
            if elapsed_time > 5 and not match_found:
                print("No match found within 5 seconds. Exiting...")
                # Send "NO_MATCH" signal to Arduino
                #arduino.write(b'NO_MATCH\n')
                break
            elif match_found:
                print("Match found! Exiting...")
                # Send "MATCH" signal to Arduino
                #arduino.write(b'MATCH\n')
                break

        # Release the webcam and close windows
        video_capture.release()
        cv.destroyAllWindows()

    if __name__ == "__main__":
        main()