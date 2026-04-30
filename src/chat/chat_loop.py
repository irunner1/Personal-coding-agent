"""Interactive terminal chat loop."""

from config import Settings
from memory_store import load_memory_text
from prompts import VALID_MODES, build_system_prompt
from providers.base import LLMProvider
from session_store import (
    gemini_state_from_turns,
    load_session,
    save_session,
    session_path,
)


def _print_chat_help(current_mode: str) -> None:
    modes = ", ".join(VALID_MODES)
    print("Commands:")
    print(f"  /help              Show this help")
    print(f"  /mode <name>      Switch mode ({modes}); does not clear history")
    print(f"  /clear            Reset conversation (keeps current mode)")
    print(f"  /exit, /quit      Leave chat")
    print(f"Current mode: {current_mode}\n")


def run_chat(
    provider: LLMProvider,
    runtime_settings: Settings,
    mode: str,
    verbose: bool,
    session_name: str | None,
    resume: bool,
    max_turns: int | None = None,
) -> None:
    memory = load_memory_text(runtime_settings)
    current_mode = mode
    system_instruction = build_system_prompt(current_mode, memory_text=memory)
    turns = (
        max_turns
        if max_turns is not None
        else getattr(runtime_settings, "MAX_AGENT_TURNS", 20)
    )

    gemini_turns: list[dict] = []
    state = provider.new_chat_state(system_instruction)

    sess_path = None
    if session_name:
        sess_path = session_path(runtime_settings, session_name)
        if resume and sess_path.is_file():
            data = load_session(sess_path)
            if data:
                prov = data.get("provider", "")
                if prov == "ollama" and isinstance(data.get("ollama_messages"), list):
                    state = data["ollama_messages"]
                    print(f"Resumed Ollama session from {sess_path}")
                elif prov == "gemini" and isinstance(data.get("gemini_turns"), list):
                    from providers.gemini_provider import GeminiProvider

                    if isinstance(provider, GeminiProvider):
                        gemini_turns = [dict(x) for x in data["gemini_turns"]]
                        state = gemini_state_from_turns(gemini_turns)
                        print(
                            f"Resumed Gemini session (text-only history) from {sess_path}"
                        )
                    else:
                        print("Session file is for Gemini; starting fresh with Ollama.")
                else:
                    print("Could not resume session; starting fresh.")
            else:
                print("Could not resume session; starting fresh.")

    if isinstance(state, list) and state and state[0].get("role") == "system":
        state[0]["content"] = system_instruction

    print(
        "Chat mode. Type /help for commands. "
        "EOF to exit.\n"
    )
    print(f"Current mode: {current_mode}\n")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            print()
            break
        if not line:
            continue
        if line in ("/exit", "/quit"):
            break
        if line == "/help":
            _print_chat_help(current_mode)
            continue
        if line == "/clear":
            system_instruction = build_system_prompt(current_mode, memory_text=memory)
            state = provider.new_chat_state(system_instruction)
            gemini_turns = []
            if isinstance(state, list) and state and state[0].get("role") == "system":
                state[0]["content"] = system_instruction
            print("Cleared conversation in memory.")
            continue
        if line.startswith("/mode"):
            parts = line.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                print(
                    f"Usage: /mode <{'|'.join(VALID_MODES)}>  (current: {current_mode})\n"
                )
                continue
            new_mode = parts[1].strip()
            if new_mode not in VALID_MODES:
                print(f"Unknown mode {new_mode!r}. Choose one of: {', '.join(VALID_MODES)}\n")
                continue
            current_mode = new_mode
            system_instruction = build_system_prompt(current_mode, memory_text=memory)
            if isinstance(state, list) and state and state[0].get("role") == "system":
                state[0]["content"] = system_instruction
            print(f"Switched to mode: {current_mode}\n")
            continue

        assistant = provider.run_chat(
            state,
            line,
            system_instruction,
            verbose=verbose,
            max_turns=turns,
        )

        provider_type = runtime_settings.LLM_PROVIDER

        if sess_path:
            if provider_type == "ollama":
                save_session(sess_path, provider="ollama", ollama_messages=state)
            elif provider_type == "gemini":
                gemini_turns.append({"user": line, "assistant": assistant})
                save_session(sess_path, provider="gemini", gemini_turns=gemini_turns)
