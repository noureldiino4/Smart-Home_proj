import face_recognition
import pickle
import os

# 1) List all of your reference image paths
reference_image_paths = [
    r"A:\College stuff\DATA AQ\Nour1.jpg",
    r"A:\College stuff\DATA AQ\Nour.jpg",
    r"A:\College stuff\DATA AQ\Magd1.jpg",
    r"A:\College stuff\DATA AQ\Abdo1.jpg",
    r"A:\College stuff\DATA AQ\Fares1.jpg"
]

known_encodings = []
known_names     = []

# 2) Loop through each image, load it, find its face encoding, and grab a label
for img_path in reference_image_paths:
    # Derive a simple name from the filename (without extension)
    name = os.path.splitext(os.path.basename(img_path))[0]
    image = face_recognition.load_image_file(img_path)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        print(f"[WARNING] no face found in {img_path!r}")
        continue

    # We’ll just take the first encoding per image
    known_encodings.append(encodings[0])
    known_names.append(name)
    print(f"[OK]   loaded {name!r}")

# 3) Save both lists into one pickle file
data = {
    "encodings": known_encodings,
    "names":     known_names
}
with open("reference_encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print(f"\nSaved {len(known_encodings)} encodings to 'reference_encodings.pkl'.")
