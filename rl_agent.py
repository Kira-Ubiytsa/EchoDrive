import json, random, ast

class RLLearningAgent:
    def __init__(self, alpha=.1, gamma=.9, epsilon=.2):
        self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon
        self.actions = ["short_hype", "strong_hype", "silent"]
        self.Q = {}

    # ---------- helpers ----------
    def _state_key(self, events):             # encode to tuple
        return (events["kill"], events["score"], events["victory"])

    def _ensure(self, state):
        if state not in self.Q:
            self.Q[state] = {a: 0.0 for a in self.actions}

    # ---------- API ----------
    def act(self, events):
        state = self._state_key(events)
        self._ensure(state)
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        return max(self.Q[state], key=self.Q[state].get)

    def update(self, old_events, action, reward, new_events):
        s, s2 = self._state_key(old_events), self._state_key(new_events)
        self._ensure(s); self._ensure(s2)
        best_future = max(self.Q[s2].values())
        old_q = self.Q[s][action]
        self.Q[s][action] = old_q + self.alpha * (reward + self.gamma*best_future - old_q)

    # ---------- persistence ----------
    def save_q_table(self, path):
        with open(path, "w") as f:
            json.dump({str(k): v for k, v in self.Q.items()}, f, indent=2)

    def load_q_table(self, path):
        try:
            with open(path) as f:
                raw = json.load(f)
            self.Q = {ast.literal_eval(k): v for k, v in raw.items()}
            print("Q-table loaded from", path)
        except FileNotFoundError:
            print("No existing Q-table – starting fresh.")
