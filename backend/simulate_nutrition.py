
import asyncio
import os
import sys
import json

# Add the backend directory to sys.path to import app
sys.path.append(os.path.join(os.getcwd(), "app"))

from app.services.ai_service import generate_plan_with_groq
from app.ai.prompts import get_nutrition_prompt

async def simulate_shrita_nutrition():
    user_profile = {
        "age": 25,
        "weight": 70,
        "height": 170,
        "fitness_goal": "muscle gain",
        "diet_preference": "non-vegetarian",
        "allergies": "none"
    }
    
    prompt = get_nutrition_prompt(user_profile)
    print("--- Nutrition Prompt ---")
    print(prompt)
    print("------------------------")
    
    try:
        print("Calling Groq for Nutrition Plan (this might take a few seconds)...")
        # I'll use a wrapper to capture the RAW response_text if it fails
        from groq import Groq
        from app.core.config import settings
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert fitness and nutrition coach. Always respond with valid JSON only. No markdown, no explanations, just JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        
        raw_response = completion.choices[0].message.content
        print(f"RAW Response Length: {len(raw_response)}")
        print(f"RAW Response Start: {raw_response[:100]}...")
        print(f"RAW Response End: ...{raw_response[-100:]}")
        
        # Now try to parse it using the same logic as in ai_service.py
        response_text = raw_response.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        
        try:
            data = json.loads(response_text)
            print("Successfully parsed JSON!")
            print(f"Keys in data: {data.keys()}")
            if "plan" in data:
                print(f"Number of days in plan: {len(data['plan'])}")
        except json.JSONDecodeError as je:
            print(f"JSON Decode Error: {je}")
            # Write raw response to a file for investigation
            with open("failed_response.txt", "w", encoding='utf-8') as f:
                f.write(raw_response)
            print("Wrote failed response to failed_response.txt")
            
    except Exception as e:
        print(f"Error during simulation: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_shrita_nutrition())
