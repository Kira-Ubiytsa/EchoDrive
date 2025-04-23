"""
capture.py  –  grab the game window (League default) + OCR ➜ events dict
"""

import cv2, numpy as np, mss, pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# adjust to your resolution / kill-feed area
REGION = {"left": 0, "top": 0, "width": 1920, "height": 1080}

KEYWORDS = {
    "kill":    ["enemy slain", "double kill", "triple kill", "quadra", "penta"],
    "victory": ["victory"],
}

def _ocr(gray: np.ndarray) -> str:
    return pytesseract.image_to_string(gray).lower().strip()

def get_game_state(game: str = "league") -> dict:
    """Return {kill, score, victory, other}"""
    with mss.mss() as sct:
        img = np.array(sct.grab(REGION))
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

    text = _ocr(gray)
    events = {"kill": False, "score": False, "victory": False, "other": text}

    for kw in KEYWORDS["kill"]:
        if kw in text:
            events["kill"] = True
            break
    for kw in KEYWORDS["victory"]:
        if kw in text:
            events["victory"] = True
            break
    # score not used for LoL but placeholder
    return events

