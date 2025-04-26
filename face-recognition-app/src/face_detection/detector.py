import cv2 as cv

class FaceDetector:
    def __init__(self):
        """Initialize the face detector with a pre-trained Haar cascade model."""
        self.face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if self.face_cascade.empty():
            raise IOError("Failed to load Haar cascade model.")

    def detect_faces(self, image):
        """Detect faces in the given image."""
        # Check if the image is already grayscale
        if len(image.shape) == 3:  # If the image has 3 channels (BGR)
            gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        else:
            gray_image = image  # Image is already grayscale
        faces = self.face_cascade.detectMultiScale(
            gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        return faces

    def draw_faces(self, image, faces):
        """Draw bounding boxes around detected faces."""
        for (x, y, w, h) in faces:
            cv.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return image