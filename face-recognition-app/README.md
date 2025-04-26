# Face Recognition Application

This project is a face recognition application that utilizes computer vision techniques to detect and recognize faces in images. It is built using Python and leverages libraries such as OpenCV and NumPy.

## Project Structure

```
face-recognition-app
├── src
│   ├── main.py
│   ├── face_detection
│   │   ├── detector.py
│   │   └── __init__.py
│   ├── utils
│   │   ├── image_processing.py
│   │   └── __init__.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd face-recognition-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

## Features

- Face detection in images
- Drawing bounding boxes around detected faces
- Image loading and preprocessing utilities

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.