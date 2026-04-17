import json
from typing import Any

from call_function import execute_tool
from config import Settings
from ollama import Client
from tools.tool_definitions import build_ollama_tools


def _message_to_dict(message: Any) -> dict:
    """Serialize an Ollama SDK message object to the dict form the API expects."""

    if isinstance(message, dict):
        return message

    if hasattr(message, "model_dump"):
        return message.model_dump()

    d = {"role": message.role}
    if getattr(message, "content", None):
        d["content"] = message.content

    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        serialized = []
        for tc in tool_calls:
            if isinstance(tc, dict):
                serialized.append(tc)
                continue

            fn = getattr(tc, "function", None)
            serialized.append(
                {
                    "id": getattr(tc, "id", None),
                    "type": getattr(tc, "type", "function") or "function",
                    "function": {
                        "name": fn.name if fn else None,
                        "arguments": fn.arguments if fn else {},
                    },
                }
            )
        d["tool_calls"] = serialized
    return d


class OllamaProvider:
    def __init__(self, settings: Settings):
        host = settings.OLLAMA_HOST
        self.client = Client(host=host) if host else Client()
        self.settings = settings
        self.tools = build_ollama_tools()

    def new_chat_state(self, system_instruction: str) -> list[dict]:
        return [{"role": "system", "content": system_instruction}]

    def run_chat(
        self,
        state: Any,
        user_text: str,
        system_instruction: str,
        *,
        verbose: bool = False,
        max_turns: int = 20,
    ) -> str:
        messages = state
        if not messages:
            messages.append({"role": "system", "content": system_instruction})
        elif messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": user_text})
        return self._run_tool_loop_until_text(
            messages,
            verbose=verbose,
            max_turns=max_turns,
        )

    def run_agent(
        self,
        user_prompt: str,
        system_instruction: str,
        *,
        verbose: bool = False,
        max_turns: int = 20,
    ) -> None:
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt},
        ]
        self._run_tool_loop_until_text(
            messages,
            verbose=verbose,
            max_turns=max_turns,
        )

    def _run_tool_loop_until_text(
        self,
        messages: list[dict],
        *,
        verbose: bool,
        max_turns: int,
    ) -> str:
        for _ in range(max_turns):
            response = self.client.chat(
                model=self.settings.OLLAMA_MODEL,
                messages=messages,
                tools=self.tools,
                stream=False,
            )
            msg = response.message

            if not getattr(msg, "tool_calls", None):
                text = msg.content or ""
                print("Response:")
                print(text)
                return text

            messages.append(_message_to_dict(msg))

            for tool_call in msg.tool_calls:
                fn = tool_call.function
                raw_args = fn.arguments
                if isinstance(raw_args, str):
                    try:
                        args_dict = json.loads(raw_args) if raw_args else {}
                    except json.JSONDecodeError:
                        args_dict = {}
                else:
                    args_dict = dict(raw_args) if raw_args else {}

                print(f"Calling function: {fn.name}({args_dict})")
                payload = execute_tool(fn.name, args_dict)
                tool_message = {"role": "tool", "content": json.dumps(payload)}
                if getattr(tool_call, "id", None):
                    tool_message["tool_call_id"] = tool_call.id
                if fn.name:
                    tool_message["name"] = fn.name
                messages.append(tool_message)

        print(
            "Error: Maximum iterations reached without a final text response from the model."
        )
        raise SystemExit(1)
