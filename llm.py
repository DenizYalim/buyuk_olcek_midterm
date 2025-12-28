"""Lightweight LLM wrapper for the project.

This module attempts to use the OpenAI Python client when an
`OPENAI_API_KEY` is available. If no key is set, it falls back to a
simple deterministic responder which helps local development and demoing
the chat frontend without requiring an API key.
"""

import os
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


load_dotenv()


class base_LLM:
    def __init__(self):
        self.prompt = ""
        self.context = ""
        # Keep model name configurable; users can change via env or code
        self.model = os.getenv("LLM_MODEL", "gpt-4o")
        self.allowed_tools = []

    def getResponse(self, prompt: str, justMessage: bool = True):
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key and OpenAI is not None:
            client = OpenAI(api_key=api_key)
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.context},
                        {"role": "user", "content": prompt},
                    ],
                )
                if justMessage:
                    # New OpenAI SDK: choices[0].message.content
                    return response.choices[0].message.content
                return response
            except Exception as e:
                return f"LLM error: {e}"

        # Fallback responder when no API key is configured.
        lower = (prompt or "").lower()
        if "query" in lower and "tuition" in lower:
            return (
                "To query tuition, call GET /mobile/ask_tuition?id=<student_id>"
            )
        if "unpaid" in lower or "unpaid tuition" in lower:
            return (
                "Unpaid tuition: this demo doesn't have persistent data;"
                " call GET /mobile/ask_tuition?id=<student_id> to fetch details."
            )
        if "pay" in lower and "tuition" in lower:
            return (
                "To pay tuition, call POST /mobile/pay_tuition with JSON {\"id\": <student_id>}"
            )

        return f"Echo (no API key): {prompt}"


if __name__ == "__main__":
    llm = base_LLM()
    llm.context = "You are a helpful assistant."
    response = llm.getResponse("Hello, how are you? what's 5+5 ?")
    print(response)