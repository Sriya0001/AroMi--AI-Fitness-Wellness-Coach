import json
import re
from groq import Groq
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.chat import ChatSession
from app.ai.prompts import AROMI_SYSTEM_PROMPT, get_chat_prompt


def get_groq_client():
    print(f"DEBUG: Using Groq API Key: {settings.GROQ_API_KEY[:10]}...{settings.GROQ_API_KEY[-5:]}")
    return Groq(api_key=settings.GROQ_API_KEY)


def clean_user_profile(profile: dict) -> dict:
    """Ensure user profile has sensible defaults and no None values for AI prompts."""
    defaults = {
        "age": 25,
        "gender": "not specified",
        "weight": 70,
        "height": 170,
        "fitness_level": "beginner",
        "fitness_goal": "general fitness",
        "workout_preference": "home",
        "workout_time": "flexible",
        "diet_preference": "vegetarian",
        "allergies": "none",
        "health_conditions": "none",
        "injuries": "none",
        "username": "User"
    }
    cleaned = {}
    for key, default in defaults.items():
        val = profile.get(key)
        cleaned[key] = val if val not in [None, "", "null"] else default
    
    # Pass through other keys like performance context
    for key, val in profile.items():
        if key not in cleaned:
            cleaned[key] = val
            
    return cleaned


async def chat_with_aromi(
    user_message: str,
    user_profile: dict,
    chat_history: list,
    db: Session,
    user_id: int
) -> tuple[str, bool]:
    """Main AROMI chat handler using LangChain + tool calling."""
    try:
        from app.services.langchain_service import LangChainAromi
        
        # Clean profile before passing to LangChain
        safe_profile = clean_user_profile(user_profile)
        
        agent = LangChainAromi(db, user_id, safe_profile)
        response_text, plan_modified = await agent.chat(user_message, chat_history)
        
        # Save to DB
        chat_record = ChatSession(
            user_id=user_id,
            message=user_message,
            response=response_text,
            timestamp=datetime.utcnow()
        )
        db.add(chat_record)
        db.commit()
        
        return response_text, plan_modified
        
    except Exception as e:
        print(f"LangChain Aromi error: {e}")
        return "I'm having a brief moment of internal processing issues. Please try again! 🙏", False


async def generate_plan_with_groq(prompt: str) -> dict:
    """Generate workout or nutrition plan using Groq."""
    try:
        client = get_groq_client()
        
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
        
        raw_response = completion.choices[0].message.content.strip()
        
        # Robust JSON extraction
        # Try to find the first '{' and the last '}'
        start_idx = raw_response.find('{')
        end_idx = raw_response.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            response_text = raw_response[start_idx:end_idx+1]
        else:
            response_text = raw_response

        # Deep clean response (remove potential trailing commas or markdown artifacts inside)
        response_text = re.sub(r',\s*}', '}', response_text)
        response_text = re.sub(r',\s*]', ']', response_text)
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback regex search for nested JSON if basic slice failed
            json_match = re.search(r'(\{.*\}|\[.*\])', raw_response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # Log the failure for debugging
            with open("error_log.txt", "a", encoding="utf-8") as f:
                f.write(f"\n--- JSON Parse Error {datetime.now()} ---\n")
                f.write(f"Error: {str(e)}\n")
                f.write(f"Raw Response: {raw_response}\n")
                f.write("-" * 40 + "\n")
            print(f"JSON parse error: {e}. Raw response logged to error_log.txt")
            raise Exception("Failed to parse AI response. Please try again.")
            
    except Exception as e:
        print(f"Groq plan generation error: {e}")
        raise Exception(f"AI service unavailable: {str(e)}")
