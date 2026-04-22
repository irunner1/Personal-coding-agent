"""Interactive terminal chat loop."""

from config import Settings
from memory_store import load_memory_text
from prompts import build_system_prompt
from providers.base import LLMProvider
from session_store import (
    gemini_state_from_turns,
    load_session,
    save_session,
    session_path,
)


def run_chat(
    provider: LLMProvider,
    runtime_settings: Settings,
    mode: str,
    verbose: bool,
    session_name: str | None,
    resume: bool,
) -> None:
    memory = load_memory_text(runtime_settings)
    system_instruction = build_system_prompt(mode, memory_text=memory)

    gemini_turns = []
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

    print("Chat mode. Commands: /exit, /quit, /clear. EOF to exit.\n")

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
        if line == "/clear":
            state = provider.new_chat_state(system_instruction)
            gemini_turns = []
            print("Cleared conversation in memory.")
            continue

        assistant = provider.run_chat(state, line, system_instruction, verbose=verbose)

        provider_type = runtime_settings.LLM_PROVIDER

        if sess_path:
            if provider_type == "ollama":
                save_session(sess_path, provider="ollama", ollama_messages=state)
            elif provider_type == "gemini":
                gemini_turns.append({"user": line, "assistant": assistant})
                save_session(sess_path, provider="gemini", gemini_turns=gemini_turns)
