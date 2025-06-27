import os
import json
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def setup_client(provider="openai"):
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("Missing OPENAI_API_KEY")
        return OpenAI(api_key=api_key)
    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("Missing GROQ_API_KEY")
        return Groq(api_key=api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def send_message(client, provider, messages, model="gpt-4"):
    if provider == "openai":
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    elif provider == "groq":
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    else:
        raise ValueError("Unknown provider")