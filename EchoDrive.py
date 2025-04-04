import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
import pyttsx3
import mss
import time

def setup_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Adjust speech speed
    return engine

def main():
    tts_engine = setup_tts()
    print("AI Hype Assistant is running...")

    with mss.mss() as sct:
        # Print the available monitors to see their indexes
        print("Available monitors:")
        for i, mon in enumerate(sct.monitors):
            print(i, mon)

        # Choose the monitor index that corresponds to your game screen
        # (Change this if needed)
        monitor_index = 2
        monitor = sct.monitors[monitor_index]

        while True:
            screenshot = sct.grab(monitor)
            img_bgra = np.array(screenshot)
            img_bgr = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

            cv2.imshow("AI Hype Assistant Preview", img_bgr)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
                break

            # OCR
            text = pytesseract.image_to_string(gray).strip()

            # Print the exact text recognized, to see if we get anything
            if text:
                print(f"Detected raw text: [{text}]")

            # Force lower-case for matching
            text_lower = text.lower()

            # Debug: check if our condition is triggered
            if "kill" in text_lower or "eliminated" in text_lower or "slain" in text_lower or "first blood" in text_lower:
                print("Match found! Triggering TTS...")
                tts_engine.say("Let's go! You're cracked!")
                tts_engine.runAndWait()

            time.sleep(1)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
