
import asyncio
import os
import sys

# Add the backend directory to sys.path to import app
sys.path.append(os.path.join(os.getcwd(), "app"))

from app.services.ai_service import generate_plan_with_groq

async def test_groq():
    prompt = "Generate a simple JSON with a key 'test' and value 'success'. Return ONLY JSON."
    try:
        print("Testing Groq...")
        result = await generate_plan_with_groq(prompt)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq())
