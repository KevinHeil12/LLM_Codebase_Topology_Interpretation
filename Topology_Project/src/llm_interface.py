import os
import json
from openai import OpenAI
from groq import Groq
from anthropic import Anthropic
import google.generativeai as genai
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
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("Missing ANTHROPIC_API_KEY")
        return Anthropic(api_key=api_key)
    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("Missing GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        return genai
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def send_message(client, provider, messages, model):
    print("\n===== SENDING MESSAGE TO LLM =====")
    print("Model:", model)
    print("Provider:", provider)
    print("Messages:", json.dumps(messages, indent=2))
    print("===================================")

    try:
        if provider == "openai":
            response = client.chat.completions.create(...)
            content = response.choices[0].message.content

        elif provider == "groq":
            response = client.chat.completions.create(...)
            content = response.choices[0].message.content

        elif provider == "anthropic":
            response = client.messages.create(
                model=model,
                messages=messages,
                max_tokens=1024
            )
            content = response.content[0].text

        elif provider == "gemini":
            chat = client.GenerativeModel(model).start_chat()
            prompt_text = "\n".join([m["content"] for m in messages if m["role"] == "user"])
            response = chat.send_message(prompt_text)
            content = response.text
        else:
            raise ValueError("Unknown provider")

        content = response.choices[0].message.content
        print("\n===== LLM RESPONSE =====")
        print(content)
        print("========================\n")
        return content

    except Exception as e:
        print("\n[ERROR] LLM call failed:", str(e))
        return "{}"  # return empty JSON to prevent crashing
