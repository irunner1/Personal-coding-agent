from google import genai
from google.genai import types

from call_function import available_functions, call_function
from config import Settings


class GeminiProvider:
    def __init__(self, settings: Settings):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)
        self.settings = settings

    def run_agent(
        self,
        user_prompt: str,
        system_instruction: str,
        *,
        verbose: bool = False,
        max_turns: int = 20,
    ) -> None:
        contents: list[types.Content] = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_prompt)],
            )
        ]
        for _ in range(max_turns):
            response = self.client.models.generate_content(
                model=self.settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_instruction,
                ),
            )
            if verbose and response.usage_metadata:
                print("Prompt tokens:", response.usage_metadata.prompt_token_count)
                print(
                    "Response tokens:",
                    response.usage_metadata.candidates_token_count,
                )

            if not response.function_calls:
                print("Response:")
                print(response.text or "")
                return

            if not response.candidates:
                raise RuntimeError("Gemini returned function calls but no candidates")

            contents.append(response.candidates[0].content)

            for function_call in response.function_calls:
                print(f"Calling function: {function_call.name}({function_call.args})")
                contents.append(call_function(function_call, verbose=verbose))

        print(
            "Error: Maximum iterations reached without a final text response from the model."
        )
        raise SystemExit(1)
