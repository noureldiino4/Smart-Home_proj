import os
import time
import pickle
import numpy as np
import cv2 as cv
import face_recognition
import serial
import argparse  # Add this import

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
REFERENCE_IMAGE_PATHS = [
    r"A:\College stuff\DATA AQ\Nour1.jpg",
    r"A:\College stuff\DATA AQ\Nour.jpg",
    r"A:\College stuff\DATA AQ\Magd1.jpg",
    r"A:\College stuff\DATA AQ\Abdo1.jpg",
    r"A:\College stuff\DATA AQ\Fares1.jpg",
]
ENCODINGS_FILE = "reference_encodings.pkl"
SERIAL_PORT    = 'COM6'
BAUD_RATE      = 9600
TIMEOUT_SECS   = 30       # seconds before automatic exit
DIST_THRESH    = 0.5      # Euclidean distance threshold
CAMERA_INDICES = [0, 1, 2, 3]   # webcam indices to try
# -----------------------------------------------------------------------------

def load_known_faces(paths, cache_file):
    """
    Builds (or loads) two parallel lists:
      known_encodings, known_names
    Uses cache_file for faster reloads.
    """
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            data = pickle.load(f)
        print(f"[CACHE] Loaded {len(data['encodings'])} encodings from '{cache_file}'")
        return data["encodings"], data["names"]

    encs_list = []
    names_list = []
    for img_path in paths:
        if not os.path.exists(img_path):
            print(f"[WARN] Missing: {img_path}")
            continue
        img = cv.imread(img_path)
        if img is None:
            print(f"[WARN] cv.imread failed: {img_path}")
            continue
        rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        if not encs:
            print(f"[WARN] No face in: {img_path}")
            continue
        encs_list.append(encs[0])
        name = os.path.splitext(os.path.basename(img_path))[0]
        names_list.append(name)
        print(f"[OK] Loaded '{name}'")
    # cache
    with open(cache_file, "wb") as f:
        pickle.dump({"encodings":encs_list, "names":names_list}, f)
    print(f"[SAVE] {len(encs_list)} encodings -> {cache_file}")
    return encs_list, names_list


def main():
    # Load/Cache reference
    known_encodings, known_names = load_known_faces(REFERENCE_IMAGE_PATHS, ENCODINGS_FILE)
    print(f"[INFO] References loaded: {known_names}")

    # Add command line paremeter parsing
    parser=argparse.ArgumentParser(description="Face Recognition door control")
    parser.add_argument('--door', default='main', choices=['main', 'back'], help='Which door to control (main or back)')
    args = parser.parse_args()


    # Serial (optional)
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except Exception:
        print(f"[WARN] Cannot open {SERIAL_PORT}")
        ser = None

    # Open webcam
    cap = None
    for idx in CAMERA_INDICES:
        print(f"[DEBUG] Trying camera index {idx}")
        temp = cv.VideoCapture(idx, cv.CAP_DSHOW)
        time.sleep(1)
        if temp.isOpened():
            cap = temp
            print(f"[INFO] Camera opened on index {idx}")
            break
        temp.release()
    if not cap:
        print("[ERROR] No camera found. Exiting.")
        return

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    cv.namedWindow("Webcam Feed", cv.WINDOW_NORMAL)
    print("[INFO] Camera warm-up...")
    time.sleep(2)

    start_time = time.time()
    match_found = False
    print("[INFO] Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Frame grab failed.")
            break

        # Display frame
        cv.imshow("Webcam Feed", frame)
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[INFO] 'q' pressed, quitting.")
            break

        # Perform recognition
        if known_encodings and not match_found:
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb)
            for (top, right, bottom, left) in locs:
                encs = face_recognition.face_encodings(rgb, [(top, right, bottom, left)])
                if not encs:
                    continue
                dists = face_recognition.face_distance(known_encodings, encs[0])
                idx_min = np.argmin(dists)
                if dists[idx_min] < DIST_THRESH:
                    match_found = True
                    name = known_names[idx_min]
                    print(f"[INFO] Match found: {name}")
                    if ser:
                        # Check which door to control
                        if args.door == 'back':
                            ser.write(b"OPEN_BACK_DOOR\n",)
                            print("[SERIAL] Sent: OPEN_BACK_DOOR")
                            time.sleep(1)  # Wait for the door to open
                        elif args.door == 'main':
                            ser.write(b"MATCH_FOUND\n")
                            print("[SERIAL] Sent: MATCH_FOUND")
                            time.sleep(1)  # Add the same delay for main door
                    # Draw rectangle and label
                    cv.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv.putText(frame, name, (left, top - 5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv.imshow("Webcam Feed", frame)
                    cv.waitKey(500)
                    break

        # Check timeout or match
        elapsed = time.time() - start_time
        if match_found:
            print("[INFO] Exiting after successful match.")
            break
        if elapsed > TIMEOUT_SECS:
            print("[INFO] No match within timeout.")
            if ser:
                ser.write(b"NO_MATCH\n")
            break

    cap.release()
    cv.destroyAllWindows()
    if ser:
        ser.close()

if __name__ == '__main__':
    main()
