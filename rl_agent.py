import json
import random

class RLLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        
        # Q-Table: {state -> {action -> q_value}}
        self.Q = {}
        
        # Possible actions
        self.actions = ["short_hype", "strong_hype", "silent"]

    def encode_state(self, events: dict) -> tuple:
        kill = events.get("kill", False)
        score = events.get("score", False)
        victory = events.get("victory", False)
        return (kill, score, victory)

    def init_state_in_Q(self, state):
        if state not in self.Q:
            self.Q[state] = {action: 0.0 for action in self.actions}

    def act(self, state) -> str:
        self.init_state_in_Q(state)
        
        # Epsilon-greedy
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = self.Q[state]
            return max(q_values, key=q_values.get)

    def update(self, old_state, action, reward, new_state):
        self.init_state_in_Q(old_state)
        self.init_state_in_Q(new_state)

        old_value = self.Q[old_state][action]
        future = max(self.Q[new_state].values())

        new_value = old_value + self.alpha * (reward + self.gamma * future - old_value)
        self.Q[old_state][action] = new_value

    def save_q_table(self, filename: str):
        """
        Save the Q-table to a JSON file.
        Note: The keys are currently Python tuples; JSON only supports strings as keys.
        We'll convert them to strings.
        """
        # Convert keys (which might be tuples) to strings
        q_table_str_keys = {str(k): v for k, v in self.Q.items()}
        
        data = {
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "Q": q_table_str_keys
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Q-table saved to {filename}")

    def load_q_table(self, filename: str):
        """
        Load the Q-table from a JSON file.
        We'll need to convert string keys back to tuples if they were stored that way.
        """
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.alpha = data["alpha"]
                self.gamma = data["gamma"]
                self.epsilon = data["epsilon"]

                q_table_str_keys = data["Q"]
                # Convert string keys back to Python tuples
                self.Q = {}
                for k_str, actions_dict in q_table_str_keys.items():
                    # remove parentheses and split by comma if you used str(tuple)
                    # or use an eval approach to parse the tuple from string carefully
                    # e.g.  k_str might look like:  '(False, False, False)'
                    # You can safely use literal_eval if you trust the JSON file.
                    import ast
                    k_tuple = ast.literal_eval(k_str)
                    self.Q[k_tuple] = actions_dict

            print(f"Q-table loaded from {filename}")

        except FileNotFoundError:
            print(f"No Q-table file found at {filename}; starting fresh.")
            # It's okay if there's no file yet—just start with an empty Q.

