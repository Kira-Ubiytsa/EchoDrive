import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
import mss
import time

GAME_REGIONS = {
    "apex": {"left": 0, "top": 0, "width": 1920, "height": 1080},
    "fortnite": {"left": 0, "top": 0, "width": 1920, "height": 1080},
    "league": {"left": 0, "top": 0, "width": 1920, "height": 1080},
    "overwatch2": {"left": 0, "top": 0, "width": 1920, "height": 1080},
    "rocketleague": {"left": 0, "top": 0, "width": 1920, "height": 1080},
    "madden": {"left": 0, "top": 0, "width": 1920, "height": 1080},
    "nba2k": {"left": 0, "top": 0, "width": 1920, "height": 1080},
    "fragpunk": {"left": 0, "top": 0, "width": 1920, "height": 1080}
}


GAME_KEYWORDS = {
    "apex": {
        "kill": ["killed", "you downed", "knocked down", "eliminated"],
        "victory": ["you are the champion"],
        # ...
    },
    "fortnite": {
        "kill": ["eliminated", "knocked out"],
        "victory": ["victory royale"],
        # ...
    },
    "league": {
        "kill": ["enemy slain", "kill"],
        "victory": ["victory"],
        # ...
    },
    "overwatch2": {
        "kill": ["eliminated"],
        "victory": ["victory"],
        # ...
    },
    "rocketleague": {
        "score": ["goal"],
        "victory": ["winner"],
        # ...
    },
    "madden": {
        "score": ["touchdown", "field goal"],
        # ...
    },
    "nba2k": {
        "score": ["pts", "foul", "timeout"],
        # ...
    },
    "fragpunk": {
        "kill": ["kill", "fragged"],
        # ...
    }
}

def capture_and_ocr(game: str) -> str:
    """
    Captures the screen (or defined region for a specific game) and runs OCR.
    Returns the raw text.
    """
    region = GAME_REGIONS.get(game, GAME_REGIONS["league"])  # fallback if unknown

    with mss.mss() as sct:
        screenshot = sct.grab(region)
        img_bgra = np.array(screenshot)
        img_bgr = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray)
    return text.strip()

def parse_game_events(game: str, text: str) -> dict:
    """
    Parses OCR text for known keywords relevant to the specified game.
    Returns a dictionary indicating what events occurred (kill, victory, etc.).
    """
    events_detected = {
        "kill": False,
        "score": False,
        "victory": False,
        "other": ""  
    }

    txt_lower = text.lower()

    keywords = GAME_KEYWORDS.get(game, {})

    kill_words = keywords.get("kill", [])
    for kw in kill_words:
        if kw in txt_lower:
            events_detected["kill"] = True
            break

    victory_words = keywords.get("victory", [])
    for vw in victory_words:
        if vw in txt_lower:
            events_detected["victory"] = True
            break

    # Check for scoring triggers
    score_words = keywords.get("score", [])
    for sw in score_words:
        if sw in txt_lower:
            events_detected["score"] = True
            break

    events_detected["other"] = text  

    return events_detected

def get_game_state(game: str) -> dict:
    """
    High-level function to capture the screen for a given game,
    run OCR, parse events, and return a dictionary of relevant info.
    """
    text = capture_and_ocr(game)
    if not text:
        return {"kill": False, "score": False, "victory": False, "other": ""}

    events = parse_game_events(game, text)

    return events

if __name__ == "__main__":
    game_name = "league"
    print(f"Starting capture for {game_name}...")

    while True:
        events = get_game_state(game_name)
        if events["kill"]:
            print("Kill detected!")
        if events["victory"]:
            print("Victory event detected!")
        if events["score"]:
            print("Score event detected!")
        if events["other"]:
            print("Raw OCR:", events["other"])

        time.sleep(2)  
