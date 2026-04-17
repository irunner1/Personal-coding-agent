"""Base Provider."""

from typing import Any, Protocol


class LLMProvider(Protocol):
    def run_agent(
        self,
        user_prompt: str,
        system_instruction: str,
        *,
        verbose: bool = False,
        max_turns: int = 20,
    ) -> None: ...

    def new_chat_state(self, system_instruction: str) -> Any: ...

    def run_chat(
        self,
        state: Any,
        user_text: str,
        system_instruction: str,
        *,
        verbose: bool = False,
        max_turns: int = 20,
    ) -> str: ...
