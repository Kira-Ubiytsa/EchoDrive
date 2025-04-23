import time, logging, pyttsx3
from pynput.keyboard import Listener
from capture import get_game_state
from rl_agent import RLLearningAgent
from local_llm import generate_hype_line

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s")

# ----- simple TTS -----
tts = pyttsx3.init()
tts.setProperty('rate', 150)

# ----- user feedback via + / - hotkeys -----
user_feedback = 0
def on_press(key):
    global user_feedback
    try:
        if key.char == '+': user_feedback = +1
        if key.char == '-': user_feedback = -1
    except AttributeError:
        pass
Listener(on_press=on_press, daemon=True).start()

# ----- RL agent -----
agent = RLLearningAgent(alpha=.1, gamma=.9, epsilon=.2)
agent.load_q_table("q_table.json")

kill_streak = 0
loop = 0
print("AI hype assistant running  (Ctrl+C to stop)…")

try:
    while True:
        events = get_game_state("league")

        # skip idle frames
        if not (events["kill"] or events["victory"] or events["score"]):
            time.sleep(1)
            continue

        if events["kill"]:
            kill_streak += 1
        if events["victory"]:
            kill_streak = 0

        action = agent.act(events)

        if action == "short_hype":
            line = generate_hype_line("Single kill happened.")
        elif action == "strong_hype":
            line = generate_hype_line(f"Kill-streak is {kill_streak}. Make it epic.")
        else:
            line = None

        if line:
            tts.say(line); tts.runAndWait()

        # observe outcome
        time.sleep(2)
        next_events = get_game_state("league")

        reward = user_feedback            # ±1 from hotkey
        user_feedback = 0
        if next_events["kill"]:           # another kill soon ➜ bonus
            reward += 1
        if line and not next_events["kill"]:
            reward -= 0.1                 # minor penalty for “useless” hype

        agent.update(events, action, reward, next_events)

        loop += 1
        if loop % 50 == 0:
            agent.save_q_table("q_table.json")

except KeyboardInterrupt:
    pass

agent.save_q_table("q_table.json")
print("\nQ-table saved.  Bye!")
