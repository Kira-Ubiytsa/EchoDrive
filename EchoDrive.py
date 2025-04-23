# main.py
import time
import pyttsx3
from pynput.keyboard import Listener, Key
from capture import get_game_state          # your screen-capture / OCR module
from rl_agent import RLLearningAgent        # Q-learning agent
from local_llm import generate_hype_line    # calls text-generation-webui

# ---------- USER-FEEDBACK HOTKEYS ----------
user_feedback = 0                       # +1, 0, or -1

def on_key_press(key):
    global user_feedback
    try:
        if key.char == '+':             # like
            user_feedback = +1
        elif key.char == '-':           # dislike
            user_feedback = -1
    except AttributeError:
        pass                            # ignore non-character keys
# launch listener (runs in its own thread)
Listener(on_press=on_key_press, daemon=True).start()

# ---------- TTS ----------
def setup_tts():
    eng = pyttsx3.init()
    eng.setProperty('rate', 150)
    return eng

# ---------- MAIN LOOP ----------
def main():
    tts = setup_tts()
    agent = RLLearningAgent(alpha=.1, gamma=.9, epsilon=.2)
    agent.load_q_table("q_table.json")          # okay if file doesn’t exist

    print("AI hype assistant is running …   (Ctrl+C to stop)")
    kill_streak = 0
    loop = 0

    try:
        while True:
            # 1. capture current events for League (adjust as needed)
            events = get_game_state("league")   # {"kill":bool,"victory":bool,"score":bool,"other":str}

            # 2. Skip loop if nothing interesting happened
            if not (events["kill"] or events["victory"] or events["score"]):
                time.sleep(1)
                continue

            # 3. Update simple kill-streak counter
            if events["kill"]:
                kill_streak += 1
            if events["victory"]:
                kill_streak = 0                # reset at end of game (example)

            # 4. RL state & action
            state = agent.encode_state(events)  # e.g. (kill,score,victory)
            action = agent.act(state)           # "short_hype" | "strong_hype" | "silent"

            # 5. Perform chosen action
            if action == "short_hype":
                line = generate_hype_line("Single kill just occurred.")
                tts.say(line);  tts.runAndWait()

            elif action == "strong_hype":
                context = f"Kill-streak = {kill_streak} in League."
                line = generate_hype_line(context)
                tts.say(line);  tts.runAndWait()
            # "silent" ⇒ do nothing

            # 6. Wait a bit, observe outcome & build reward
            time.sleep(2)
            new_events = get_game_state("league")
            new_state  = agent.encode_state(new_events)

            reward = 0
            global user_feedback
            reward += user_feedback            # +1 / -1 from hot-key
            user_feedback = 0                  # reset feedback

            if new_events.get("kill"):         # extra reward if another kill followed
                reward += 1
            if action != "silent" and not new_events.get("kill"):
                reward -= 0.1                  # tiny penalty for “useless talk”

            agent.update(state, action, reward, new_state)

            # 7. Autosave Q-table every 50 loops
            loop += 1
            if loop % 50 == 0:
                agent.save_q_table("q_table.json")

    except KeyboardInterrupt:
        print("\nStopping…")

    agent.save_q_table("q_table.json")
    print("Q-table saved. Bye!")

if __name__ == "__main__":
    main()
