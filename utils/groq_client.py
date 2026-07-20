"""
Central Groq API wrapper.
Every module calls generate() or generate_json() instead of hitting the
Groq SDK directly, so retries/error handling/model choice live in one place.
"""
import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GROQ_API_KEY")
_MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_client = None


def _get_client():
    global _client
    if not _API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    if _client is None:
        _client = Groq(api_key=_API_KEY)
    return _client


def generate(prompt: str, system_instruction: str = None, temperature: float = 0.4) -> str:
    """Plain text generation. Returns the raw text response."""
    client = _get_client()
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=_MODEL_NAME,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Bubble up a clean error the UI layer can st.error() directly.
        raise RuntimeError(f"Groq API call failed: {e}")


def generate_json(prompt: str, system_instruction: str = None, temperature: float = 0.2) -> dict:
    """
    Generation that expects a JSON object back. Uses Groq's JSON mode where
    supported, and still strips markdown fences / retries parsing as a
    fallback for models or prompts where JSON mode isn't honored exactly.
    Raises ValueError if the response still isn't valid JSON.
    """
    client = _get_client()
    messages = []
    base_system = "You must respond with a single valid JSON object and nothing else."
    messages.append({
        "role": "system",
        "content": f"{system_instruction}\n\n{base_system}" if system_instruction else base_system,
    })
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=_MODEL_NAME,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Groq API call failed: {e}")

    cleaned = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Groq did not return valid JSON. Raw response:\n{raw}\n\nError: {e}"
        )
