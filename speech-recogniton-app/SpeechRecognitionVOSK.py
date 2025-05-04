import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import serial

        # Initialize Serial Communication
try:
    serial_port = serial.Serial('COM6', 9600, timeout=1)  # Replace 'COM3' with your Arduino's port
except serial.SerialException:
    print("Error: Could not open serial port.")
    serial_port = None
# Load the model
model = Model(r"C:\VOSK\vosk-model-en-us-0.22")
recognizer = KaldiRecognizer(model, 16000)

# Set up audio queue
q = queue.Queue()

# Audio callback
def callback(indata, frames, time, status):
    if status:
        print("Audio status:", status)
    q.put(bytes(indata))

# Start streaming from mic
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("Listening from built-in mic...")
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            print("You said:", result.get("text", ""))
            if serial_port and result.get("text", "").lower() == "close the gate":
                serial_port.write("CLOSE_MAIN_GATE\n".encode())
                print("Sent 'Close' to Arduino")
            elif serial_port and result.get("text", "").lower() == "open the gate":
                serial_port.write("OPEN_MAIN_GATE\n".encode())
                print("Sent 'Open' to Arduino")
