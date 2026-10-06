"""
Entry point: starts a GroupChat conversation implementing the
Planner/Assistant -> Coder -> Executor -> Critic pattern from the report.

Run with:
    python main.py "Write a function that returns the first repeated
    element in a list, ignoring negatives and zeros."
"""

import sys
from agents import build_agents, build_group_chat


def main():
    task = (
        " ".join(sys.argv[1:])
        or "Write a Python function that checks whether a string is a palindrome, "
           "ignoring spaces and capitalisation. Include a test with at least 3 cases."
    )

    agents = build_agents()
    _, _, _, _, user_proxy = agents
    manager = build_group_chat(agents)

    print(f"\n=== Starting AutoGen GroupChat ===\nTask: {task}\n")

    user_proxy.initiate_chat(
        manager,
        message=task,
    )


if __name__ == "__main__":
    main()
