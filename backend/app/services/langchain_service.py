import json
import re
from datetime import date
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.workout import WorkoutPlan
from app.ai.prompts import AROMI_SYSTEM_PROMPT


# ─── DB Action Functions ────────────────────────────────────────────────────

def _get_today_workout(db: Session, user_id: int) -> Optional[WorkoutPlan]:
    today_num = date.today().weekday() + 1
    return db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.day == today_num
    ).first()


def _get_target_workout(db: Session, user_id: int, day_num: Optional[int] = None) -> Optional[WorkoutPlan]:
    if day_num is None:
        return _get_today_workout(db, user_id)
    return db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.day == day_num
    ).first()


def remove_exercise_action(db: Session, user_id: int, exercise_name: str, day_num: Optional[int] = None) -> str:
    workout = _get_target_workout(db, user_id, day_num)
    if not workout:
        return None
    exercises = json.loads(workout.exercises) if workout.exercises else []
    original_count = len(exercises)
    filtered = [ex for ex in exercises if exercise_name.lower() not in ex.get('name', '').lower()]
    if len(filtered) == original_count:
        return None  # Exercise not found, don't claim a change
    workout.exercises = json.dumps(filtered)
    
    # Update duration (approx -5 mins per exercise, min 10)
    removed_count = original_count - len(filtered)
    if workout.duration_minutes:
        workout.duration_minutes = max(10, workout.duration_minutes - (removed_count * 5))
    
    db.commit()
    return f"Removed '{exercise_name}' from today's workout."


async def replace_exercise_action(db: Session, user_id: int, old_name: str, new_name: str, day_num: Optional[int] = None) -> str:
    workout = _get_target_workout(db, user_id, day_num)
    if not workout:
        return None
    exercises = json.loads(workout.exercises) if workout.exercises else []
    found = False
    for ex in exercises:
        if old_name.lower() in ex.get('name', '').lower():
            ex['name'] = new_name.title()
            ex['instructions'] = f"Replacement for {old_name}. Perform with good form."
            ex['youtube_query'] = f"{new_name} proper form"
            from app.services.youtube_service import enrich_exercise
            await enrich_exercise(ex)
            found = True
    if not found:
        return None  # Don't claim a change if we couldn't find the exercise
    workout.exercises = json.dumps(exercises)
    db.commit()
    return f"Replaced '{old_name}' with '{new_name}' in today's workout."


async def add_exercise_action(db: Session, user_id: int, exercise_name: str, day_num: Optional[int] = None) -> str:
    workout = _get_target_workout(db, user_id, day_num)
    if not workout:
        return None
    exercises = json.loads(workout.exercises) if workout.exercises else []
    new_ex = {
        "name": exercise_name.title(),
        "sets": 3,
        "reps": "10-12",
        "rest_seconds": 60,
        "muscle_group": "General",
        "instructions": f"Perform {exercise_name} with good form.",
        "youtube_query": f"{exercise_name} proper form tutorial"
    }
    from app.services.youtube_service import enrich_exercise
    await enrich_exercise(new_ex)
    exercises.append(new_ex)
    workout.exercises = json.dumps(exercises)
    
    # Update duration (+5 mins)
    if workout.duration_minutes:
        workout.duration_minutes += 5
    else:
        workout.duration_minutes = 45 # Default if missing
        
    db.commit()
    return f"Added '{new_ex['name']}' to today's workout."


def compress_workout_action(db: Session, user_id: int, duration_minutes: int, day_num: Optional[int] = None) -> str:
    workout = _get_target_workout(db, user_id, day_num)
    if not workout:
        return None
    exercises = json.loads(workout.exercises) if workout.exercises else []
    compressed = exercises[:3]
    for ex in compressed:
        ex["rest_seconds"] = 30
    workout.exercises = json.dumps(compressed)
    workout.duration_minutes = duration_minutes
    workout.tips = json.dumps("Workout compressed. Focus on compound movements!")
    db.commit()
    return f"Compressed workout to {duration_minutes} minutes with top 3 exercises."


def travel_workout_action(db: Session, user_id: int, day_num: Optional[int] = None) -> str:
    workout = _get_target_workout(db, user_id, day_num)
    if not workout:
        return None
    exercises = json.loads(workout.exercises) if workout.exercises else []
    for ex in exercises:
        ex["name"] = f"Bodyweight {ex['name']}"
        ex["instructions"] = f"Travel-friendly, no equipment. {ex.get('instructions', '')}"
    workout.exercises = json.dumps(exercises)
    workout.tips = json.dumps("Plan adjusted for travel — bodyweight only!")
    db.commit()
    return "Modified today's workout for travel — bodyweight only."


def fatigue_workout_action(db: Session, user_id: int, day_num: Optional[int] = None) -> str:
    workout = _get_target_workout(db, user_id, day_num)
    if not workout:
        return None
    recovery_exercises = [
        {"name": "Dynamic Stretching", "sets": 2, "reps": "10 mins", "rest_seconds": 30,
         "muscle_group": "Full Body", "instructions": "Focus on breathing and range of motion."},
        {"name": "Light Yoga Flow", "sets": 1, "reps": "15 mins", "rest_seconds": 0,
         "muscle_group": "Full Body", "instructions": "Hold poses gently, no strain."}
    ]
    workout.exercises = json.dumps(recovery_exercises)
    workout.duration_minutes = 25
    workout.tips = json.dumps("Recovery day — listen to your body.")
    db.commit()
    return "Switched today to a recovery/mobility session."


def injury_workout_action(db: Session, user_id: int, body_part: str, day_num: Optional[int] = None) -> str:
    workout = _get_target_workout(db, user_id, day_num)
    if not workout:
        return None
    exercises = json.loads(workout.exercises) if workout.exercises else []
    original_count = len(exercises)
    filtered = [ex for ex in exercises if body_part.lower() not in ex.get('muscle_group', '').lower()]
    
    # Update duration
    removed_count = original_count - len(filtered)
    if workout.duration_minutes and removed_count > 0:
        workout.duration_minutes = max(10, workout.duration_minutes - (removed_count * 5))
        
    workout.exercises = json.dumps(filtered)
    workout.tips = json.dumps(f"Adjusted to protect your {body_part}.")
    db.commit()
    return f"Removed {removed_count} exercises targeting {body_part}."


def skipped_workout_action(db: Session, user_id: int) -> str:
    tomorrow_day = (date.today().weekday() + 2) % 7 or 7
    workout = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.day == tomorrow_day
    ).first()
    if not workout:
        return None
    workout.tips = json.dumps("Catch-up day — moderate pace, stay consistent!")
    db.commit()
    return "Adjusted tomorrow's plan for a catch-up session."


def deduplicate_workout_action(db: Session, user_id: int, day_num: int = None) -> str:
    workout = _get_target_workout(db, user_id, day_num) if day_num else _get_today_workout(db, user_id)
    if not workout:
        return None
    exercises = json.loads(workout.exercises) if workout.exercises else []
    seen = set()
    unique = []
    removed = []
    for ex in exercises:
        name = ex.get('name', '').lower().strip()
        if name not in seen:
            seen.add(name)
            unique.append(ex)
        else:
            removed.append(ex.get('name'))
    
    if not removed:
        return None
        
    workout.exercises = json.dumps(unique)
    db.commit()
    return f"Removed duplicate exercises: {', '.join(set(removed))}."


async def generate_rest_day_plan_action(db: Session, user_id: int, day_num: int) -> str:
    """Turn a rest day into a workout day by generating a fresh plan for it."""
    from app.services.workout_service import generate_7_day_plan
    from app.models.user import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
        
    user_profile = {
        "age": user.age, "gender": user.gender, "weight": user.weight, "height": user.height,
        "fitness_level": user.fitness_level, "fitness_goal": user.fitness_goal,
        "workout_preference": user.workout_preference, "workout_time": user.workout_time,
        "health_conditions": user.health_conditions, "injuries": user.injuries
    }
    
    # We use the existing prompt logic but filter for just one day
    from app.ai.prompts import get_workout_prompt
    from app.services.ai_service import generate_plan_with_groq
    from app.services.youtube_service import enrich_exercise
    
    prompt = get_workout_prompt(user_profile)
    prompt += f"\n\nIMPORTANT: Only generate the plan for Day {day_num}. Return it in the standard JSON format as an array containing one day."
    
    plan_data = await generate_plan_with_groq(prompt)
    days_data = plan_data.get("plan", [])
    if not days_data:
        return None
        
    day_data = days_data[0]
    exercises = day_data.get("exercises", [])
    for ex in exercises:
        await enrich_exercise(ex)
        
    workout = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id, WorkoutPlan.day == day_num).first()
    if workout:
        workout.exercises = json.dumps(exercises)
        workout.warmup = day_data.get("warmup", "")
        workout.cooldown = day_data.get("cooldown", "")
        workout.tips = json.dumps(day_data.get("tips", ""))
        workout.duration_minutes = day_data.get("duration_minutes", 45)
        workout.day_name = day_data.get("day_name", workout.day_name)
    else:
        # Create if missing (shouldn't happen with current 7-day init)
        workout = WorkoutPlan(
            user_id=user_id, day=day_num, exercises=json.dumps(exercises),
            warmup=day_data.get("warmup", ""), cooldown=day_data.get("cooldown", ""),
            tips=json.dumps(day_data.get("tips", "")), duration_minutes=day_data.get("duration_minutes", 45)
        )
        db.add(workout)
        
    db.commit()
    return f"Generated a new workout plan for {workout.day_name}!"


# ─── Intent Detection ───────────────────────────────────────────────────────

INJURY_BODY_PARTS = ["knee", "shoulder", "back", "wrist", "ankle", "elbow", "neck", "hip"]
INJURY_SIGNALS = ["hurt", "injur", "pain", "sore", "ache", "sprained"]
EXERCISE_NAMES = [
    "leg extension", "leg press", "calf raise", "glute bridge", "squat", "lunge",
    "deadlift", "bench press", "chest press", "push-up", "pull-up", "row",
    "curl", "tricep", "shoulder press", "plank", "crunch"
]


# Words that are NOT exercise names — prevent literal addition of pronouns/vague words
PRONOUNS = {"them", "those", "these", "it", "that", "this", "all", "everything"}


def extract_exercises_from_text(text: str) -> list:
    """Pull exercise names from a block of AROMI text (e.g. last chat response)."""
    found = []
    text_lower = text.lower()
    for name in EXERCISE_NAMES:
        if name in text_lower:
            found.append(name.title())
    # Also try comma-separated lists mentioned after 'such as', 'including', 'like'
    for pattern in [r'such as (.+?)[\.\!\?]', r'including (.+?)[\.\!\?]', r'like (.+?)[\.\!\?]',
                    r'recommend (.+?)[\.\!\?]', r'suggest (.+?)[\.\!\?]']:
        m = re.search(pattern, text_lower)
        if m:
            # Split by commas/"and" to get individual names
            items = re.split(r',\s*|\s+and\s+', m.group(1))
            for item in items:
                item = item.strip().rstrip('.')
                if item and len(item.split()) <= 4:  # max 4-word exercise names
                    found.append(item.title())
    return list(dict.fromkeys(found))  # deduplicate, preserve order


async def detect_intent(message: str, db: Session, user_id: int, chat_history: list = None) -> Tuple[Optional[str], bool]:
    """Parse user message, execute DB action if needed. Returns (result_text, plan_modified)."""
    msg = message.lower()

    # 0. Identify target day (defaut to today)
    target_day = date.today().weekday() + 1
    day_map = {"mon": 1, "monday": 1, "tue": 2, "tuesday": 2, "wed": 3, "wednesday": 3, 
               "thu": 4, "thursday": 4, "fri": 5, "friday": 5, "sat": 6, "saturday": 6, 
               "sun": 7, "sunday": 7}
    
    for day_str, day_num in day_map.items():
        if day_str in msg:
            target_day = day_num
            break

    # Update all to use day_num for target workouts
    target_workout = _get_target_workout(db, user_id, target_day)
    has_exercises = target_workout and target_workout.exercises and len(json.loads(target_workout.exercises)) > 0

    # 0.1 NEW: Handle rest-day to workout-day conversion
    if not has_exercises:
        if any(w in msg for w in ["workout", "plan", "exercise", "give me", "update"]):
            result = await generate_rest_day_plan_action(db, user_id, target_day)
            if result:
                return result, True

    # 1. Remove + replace: "remove X and replace with Y" / "replace X with Y"
    # Use .+? so multi-word names like "leg press" are fully captured.
    # Terminate on punctuation or end-of-string only (NOT whitespace).
    remove_and_replace = re.search(
        r'remove\s+(.+?)\s+and\s+(?:replace|substitute)\s+(?:it\s+)?with\s+(.+?)(?:[.,!?]|$)',
        msg
    )
    replace_match = re.search(
        r'replace\s+(.+?)\s+with\s+(.+?)(?:[.,!?]|$)',
        msg
    )

    if remove_and_replace:
        old = remove_and_replace.group(1).strip()
        new = remove_and_replace.group(2).strip()
        result = await replace_exercise_action(db, user_id, old, new, target_day)
        if result:
            return result, True

    elif replace_match:
        old = replace_match.group(1).strip()
        new = replace_match.group(2).strip()
        result = await replace_exercise_action(db, user_id, old, new, target_day)
        if result:
            return result, True

    # 2. Just remove: "remove leg extensions" / "delete X" / "- X"
    remove_match = re.search(r'(?:remove|delete|remove the|delete the)\s+(.+?)(?:[.,!?]|$)', msg)
    minus_match = re.search(r'^-\s*(.+?)(?:[.,!?]|$)', msg)
    
    if remove_match or minus_match:
        ex_name = (remove_match or minus_match).group(1).strip()
        result = remove_exercise_action(db, user_id, ex_name, target_day)
        if result:
            return result, True

    # 3. Add exercise: "add chest press" / "can you add X"
    #    Handle pronoun references: "add them" / "yes add those" / "add these"
    is_pronoun_add = bool(re.search(r'(?:add|include|yes)\s+(them|those|these|it|all)\b', msg))

    if is_pronoun_add:
        # Extract exercises AROMI suggested in the previous message
        if chat_history:
            last_aromi_msg = chat_history[-1].get('response', '') if chat_history else ''
            exercises_to_add = extract_exercises_from_text(last_aromi_msg)
            if exercises_to_add:
                added = []
                for ex_name in exercises_to_add:
                    r = await add_exercise_action(db, user_id, ex_name, target_day)
                    if r:
                        added.append(ex_name)
                if added:
                    return f"Added {', '.join(added)} to the workout.", True
        return None, False

    # Improved regex for add/include: stop at "to my workout", "to today", etc.
    # Anchors are now optional or allow trailing text
    add_match = re.search(r'(?:add|include|can you add|could you add)\s+(.+?)(?:\s+to (?:my|today|the) (?:workout|plan|session)|$|[.,!?])', msg)
    if add_match:
        ex_name = add_match.group(1).strip()
        # Clean up common trailing words and noise
        ex_name = re.sub(r'\b(?:please|thanks|thank you|now|today|and)\b.*', '', ex_name).strip()

        # Skip if it's a pronoun or too vague
        if ex_name in PRONOUNS or len(ex_name) <= 2:
            pass
        else:
            result = await add_exercise_action(db, user_id, ex_name, target_day)
            if result:
                return result, True

    # 4. Injury: "hurt my knee", "knee pain"
    for part in INJURY_BODY_PARTS:
        if part in msg:
            if any(sig in msg for sig in INJURY_SIGNALS):
                result = injury_workout_action(db, user_id, part, target_day)
                if result:
                    return result, True

    # 5. Travel
    if any(w in msg for w in ["traveling", "travel", "on a trip", "hotel"]):
        result = travel_workout_action(db, user_id, target_day)
        if result:
            return result, True

    # 6. Time constraint
    # Handle phrases like "only have 20 mins", "accomodate for 15 min", "change 45 to 20 mins"
    
    # Try to find a duration that is explicitly a target: "to 20 mins", "into 20 mins", "for 20 min"
    target_match = re.search(r'(?:to|into|for|accommodate|accomodate|only|have|now)\s*(?:a\s+)?(\d+)\s*min', msg)
    # Also generic X min match
    general_time_match = re.search(r'\b(\d+)\s*min', msg)
    
    time_triggers = ["only have", "short on time", "quick workout", "less time", "accommodate", "accomodate", "enough time", "no time"]
    if any(w in msg for w in time_triggers) or general_time_match:
        if target_match:
            duration = int(target_match.group(1))
        elif general_time_match:
            # If there are multiple "X min" matches, pick the last one mentioned as it's often the target
            all_times = re.findall(r'\b(\d+)\s*min', msg)
            duration = int(all_times[-1])
        else:
            nums = re.findall(r'\b(\d+)\b', msg)
            valid_nums = [int(n) for n in nums if int(n) <= 60]
            # If multiple numbers, and the user is asking to compress/change, pick the smallest reasonable one
            duration = min(valid_nums) if valid_nums else 20
        
        # Safety check: pick a reasonable duration
        if 5 <= duration <= 60:
            result = compress_workout_action(db, user_id, duration, target_day)
            if result:
                return result, True

    # 7. Fatigue
    if any(w in msg for w in ["tired", "exhausted", "fatigue", "no energy", "too tired"]):
        result = fatigue_workout_action(db, user_id, target_day)
        if result:
            return result, True

    # 8. Skipped
    if any(w in msg for w in ["skipped", "missed", "couldn't workout", "didn't workout"]):
        result = skipped_workout_action(db, user_id)
        if result:
            return result, True

    # 9. Deduplicate
    if any(w in msg for w in ["duplicate", "twice", "repeated", "same exercise"]):
        result = deduplicate_workout_action(db, user_id, target_day)
        if result:
            return result, True

    return None, False


# ─── Main AROMI Agent ───────────────────────────────────────────────────────

class LangChainAromi:
    def __init__(self, db: Session, user_id: int, user_profile: dict):
        self.db = db
        self.user_id = user_id
        self.user_profile = user_profile

    async def chat(self, user_message: str, chat_history: list) -> Tuple[str, bool]:
        from groq import Groq
        from app.core.config import settings

        # Step 1: Try to execute a DB plan action, passing chat_history for context
        action_result, plan_modified = await detect_intent(user_message, self.db, self.user_id, chat_history)

        # Step 2: Build conversation context
        history_text = ""
        for h in chat_history[-6:]:
            history_text += f"User: {h['message']}\nAROMI: {h['response']}\n"

        user_context = (
            f"User Profile: Age {self.user_profile.get('age', 'unknown')}, "
            f"Goal: {self.user_profile.get('fitness_goal', 'general fitness')}, "
            f"Level: {self.user_profile.get('fitness_level', 'beginner')}\n\n"
            f"{history_text}"
        )

        # Step 3: Build system prompt
        # CRITICAL: Only tell AI a change happened if one actually happened
        if plan_modified and action_result:
            action_note = (
                f"\n\n[SYSTEM: PLAN UPDATED] The following change was made to the user's plan in the database: "
                f"{action_result}. This change has ALREADY been applied to their view automatically. "
                f"Confirm the specific change to the user and mention that their dashboard has been updated."
            )
        else:
            action_note = (
                "\n\n[SYSTEM: NO PLAN CHANGE] Do NOT claim you updated or modified the workout plan. "
                "Only answer the user's question conversationally."
            )

        system_prompt = AROMI_SYSTEM_PROMPT + action_note

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {user_context}\n\nUser's message: {user_message}"}
        ]

        # Step 4: Get AI response
        client = Groq(api_key=settings.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=512,
        )

        return completion.choices[0].message.content, plan_modified
