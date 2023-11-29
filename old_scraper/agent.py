import random
import os

def get():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    user_agents_path = os.path.join(script_dir, "user_agents.txt")

    user_agents = []
    with open(user_agents_path, "r") as f:
        for line in f:
            user_agents.append(line.replace("\n", ""))

    return random.choice(user_agents)