"""
Agent definitions matching Section 5 ("Reference Implementation Pattern") of
the benchmark report:

    AssistantAgent (generalist)  -> MMLU / GPQA breadth
    GroupChatManager             -> speaker selection / delegation
    Coder agent                  -> HumanEval / SWE-bench Verified strength
    Executor agent                -> runs code, returns stdout/stderr
    Critic agent                 -> TruthfulQA-aware review before final output
    UserProxyAgent (human-in-the-loop) -> optional approval checkpoint

Each agent is bound to LLM_CONFIG from config.py. In a real deployment you
could point different agents at different models (e.g. a high-GPQA model
for the Critic, a high-HumanEval model for the Coder) by importing a
different config per agent — the report's core recommendation in Section 4.
"""

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from config import LLM_CONFIG

# Code executor config: runs generated code in a local Docker-free sandbox
# directory. Swap for a DockerCommandLineCodeExecutor in production.
CODE_EXECUTION_CONFIG = {
    "work_dir": "coding",
    "use_docker": False,  # set True if Docker is available, for safer sandboxing
}


def build_agents():
    # Generalist assistant: interprets the request, drafts an initial plan.
    assistant = AssistantAgent(
        name="Assistant",
        system_message=(
            "You are a generalist assistant. Interpret the user's request, "
            "break it into a short plan, and hand off coding tasks to the Coder."
        ),
        llm_config=LLM_CONFIG,
    )

    # Coder: writes code in response to the plan.
    coder = AssistantAgent(
        name="Coder",
        system_message=(
            "You write correct, well-documented Python code to satisfy the "
            "plan. Always wrap code in a single ```python block so the "
            "Executor can run it."
        ),
        llm_config=LLM_CONFIG,
    )

    # Critic: reviews Coder/Assistant output before it is finalised.
    critic = AssistantAgent(
        name="Critic",
        system_message=(
            "You are a skeptical reviewer. Check the Executor's run results "
            "and the Coder's code for correctness and unsupported claims. "
            "If the code ran successfully and looks correct, reply with your "
            "review followed by the single word TERMINATE on its own line. "
            "If something is wrong, explain exactly what must change (do not "
            "write TERMINATE in that case)."
        ),
        llm_config=LLM_CONFIG,
    )

    # Executor: a UserProxyAgent configured to auto-run code and report
    # results back into the conversation (no human needed at this step).
    executor = UserProxyAgent(
        name="Executor",
        human_input_mode="NEVER",
        code_execution_config=CODE_EXECUTION_CONFIG,
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )

    # Human-in-the-loop checkpoint: pauses for human approval before the
    # conversation's final output is accepted. Set human_input_mode to
    # "ALWAYS" to require a human reply at every turn, or "TERMINATE" to
    # only ask when the conversation is about to end.
    user_proxy = UserProxyAgent(
        name="Human",
        human_input_mode="TERMINATE",
        code_execution_config=False,  # this agent only approves/rejects, never runs code
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )

    return assistant, coder, critic, executor, user_proxy


def build_group_chat(agents, max_round=12):
    assistant, coder, critic, executor, user_proxy = agents

    # Force a strict hand-off order instead of letting an LLM guess who
    # speaks next (the report, Section 7, flags "auto" speaker selection as
    # unreliable — small local models make this worse). This guarantees the
    # Executor actually runs the Coder's code every single round, closing
    # the execute-and-observe loop from Section 4.3.
    allowed_transitions = {
        user_proxy: [assistant],
        assistant: [coder],
        coder: [executor],
        executor: [critic],
        critic: [coder, user_proxy],  # loop back to Coder on rejection, else finish
    }

    group_chat = GroupChat(
        agents=[user_proxy, assistant, coder, executor, critic],
        messages=[],
        max_round=max_round,
        allowed_or_disallowed_speaker_transitions=allowed_transitions,
        speaker_transitions_type="allowed",
    )

    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=LLM_CONFIG,
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )
    return manager