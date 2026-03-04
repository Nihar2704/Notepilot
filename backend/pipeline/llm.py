import json
import asyncio
from groq import Groq
from typing import Optional, Dict
from config import GROQ_API_KEY, MODEL_NAME

client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

async def groq_call(prompt: str, system_message: str = "You are a helpful assistant.") -> Optional[str]:
    """
    Calls the Groq API with the specified prompt.
    """
    if not client:
        print("Groq client not initialized. Check API key.")
        return None

    try:
        # groq client is synchronous, so we wrap it in an executor or just run it in a thread
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                model=MODEL_NAME,
                temperature=0.1, # Low temperature for structured output
                response_format={"type": "json_object"} if "JSON" in prompt else None
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq API error: {e}")
        return None

def safe_parse_json(text: str) -> Optional[Dict]:
    """
    Safely parses JSON from LLM response.
    """
    if not text:
        return None
        
    cleaned = text.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON: {text[:100]}...")
        return None
