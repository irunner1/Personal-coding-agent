"""Base Provider."""

from typing import Protocol


class LLMProvider(Protocol):
    def run_agent(
        self,
        user_prompt: str,
        system_instruction: str,
        *,
        verbose: bool = False,
        max_turns: int = 20,
    ) -> None: ...
