def load_image(file_path):
    """Load an image from the specified file path."""
    import cv2 as cv
    image = cv.imread(file_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {file_path}")
    return image

def preprocess_image(image, size=(640, 480)):
    """Preprocess the image for face detection."""
    import cv2 as cv
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    resized_image = cv.resize(gray_image, size)
    return resized_image

def display_image(image, window_name='Face Recognition Output'):
    """Display the image in a window."""
    import cv2 as cv
    cv.imshow(window_name, image)
    cv.waitKey(0)
    cv.destroyAllWindows()