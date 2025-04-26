import face_recognition
import pickle
import cv2 as cv

# Path to the reference image
reference_image_path = r"A:\College stuff\DATA AQ\Nour1.jpg"

# Load and encode the reference image
reference_image = face_recognition.load_image_file(reference_image_path)
reference_encodings = face_recognition.face_encodings(reference_image)

if len(reference_encodings) > 0:
    reference_encoding = reference_encodings[0]
    # Save the encoding to a file
    with open("reference_encoding.pkl", "wb") as f:
        pickle.dump(reference_encoding, f)
    print("Reference encoding saved to 'reference_encoding.pkl'.")
else:
    print("No face found in the reference image.")