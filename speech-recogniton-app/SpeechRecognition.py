import speech_recognition as sr
import time

def listen_for_keyword(keyword="hello"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Say '{keyword}' to start capturing speech...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            try:
                # Listen for audio
                audio = recognizer.listen(source)
                # Recognize speech
                text = recognizer.recognize_google(audio).lower()
                print(f"You said: {text}")
                # Check for the keyword
                if keyword in text:
                    print(f"Keyword '{keyword}' detected! Starting speech capture...")
                    return
            except sr.UnknownValueError:
                print("Could not understand the audio. Try again.")
            except sr.RequestError as e:
                print(f"Error with the recognition service: {e}")

def capture_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your speech...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Error with the recognition service: {e}")

if __name__ == "__main__":
    while True:
        listen_for_keyword(keyword="hi assistant")  # Wait for the keyword
        capture_speech()  # Capture speech after the keyword
        print("Going back to listening for the keyword...")
        time.sleep(1)  # Optional: Add a short delay before listening again