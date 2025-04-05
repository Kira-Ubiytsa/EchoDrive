# main.py

import time
import pyttsx3
import pynput
from pynput.keyboard import Key, Listener
from capture import get_game_state
from rl_agent import RLLearningAgent

# Shared variable for user feedback (+1, 0, or -1)
user_feedback = 0

def on_key_press(key):
    """Keyboard callback for user feedback: 
       Press '+' for like, '-' for dislike."""
    global user_feedback
    try:
        # If the key pressed is a character and is '+' or '-'
        if key.char == '+':
            user_feedback = +1
        elif key.char == '-':
            user_feedback = -1
    except AttributeError:
        # Special keys (e.g., Arrow keys) might cause an AttributeError
        pass

def setup_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    return engine

def main():
    tts_engine = setup_tts()
    agent = RLLearningAgent(alpha=0.1, gamma=0.9, epsilon=0.2)
    
    # Attempt to load existing Q-table
    agent.load_q_table("q_table.json")

    # Start the keyboard listener for user feedback
    listener = Listener(on_press=on_key_press)
    listener.start()

    print("AI Hype Assistant (with RL) is running...")

    iteration_count = 0

    try:
        while True:
            # 1) Get the current game events (kill, score, victory, etc.)
            events = get_game_state("league")

            # 2) If there's no kill, victory, or score, skip hype
            #    This prevents spamming in idle/lobby states.
            if not (events["kill"] or events["victory"] or events["score"]):
                time.sleep(2)
                continue

            # 3) Convert events dict -> RL state (e.g., (kill_bool, score_bool, victory_bool))
            current_state = agent.encode_state(events)

            # 4) Decide an action via the RL agent
            action = agent.act(current_state)

            # 5) Perform the action (TTS or silent)
            if action == "short_hype":
                tts_engine.say("Nice job!")
                tts_engine.runAndWait()
            elif action == "strong_hype":
                tts_engine.say("You're unstoppable!")
                tts_engine.runAndWait()
            # 'silent' => do nothing

            # 6) Wait to see if there's a new event or user feedback
            time.sleep(2)

            # 7) Get the new state (in case user got another kill, etc.)
            new_events = get_game_state("league")
            new_state = agent.encode_state(new_events)

            # 8) Combine user feedback with performance-based reward
            global user_feedback
            reward = user_feedback  # If user pressed '+' or '-'
            user_feedback = 0       # Reset so we don't reuse it next loop

            # Example: +1 if a kill is detected in the new state
            if new_events.get("kill", False):
                reward += 1

            # 9) Update Q-table
            agent.update(current_state, action, reward, new_state)

            # 10) Periodically save Q-table
            iteration_count += 1
            if iteration_count % 50 == 0:
                agent.save_q_table("q_table.json")

    except KeyboardInterrupt:
        # If user hits Ctrl+C, break the loop
        pass

    # Final save and stop listening
    agent.save_q_table("q_table.json")
    listener.stop()

if __name__ == "__main__":
    main()