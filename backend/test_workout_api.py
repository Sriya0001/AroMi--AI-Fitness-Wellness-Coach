import sqlite3
import json

def test_json_validity():
    conn = sqlite3.connect('arogyamitra.db')
    cursor = conn.cursor()
    user_id = 3
    
    print(f"Testing JSON validity for user {user_id}...")
    cursor.execute("SELECT day, id, exercises, tips FROM workout_plans WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    
    for day, row_id, exercises, tips in rows:
        print(f"\nDay {day} (ID {row_id}):")
        try:
            ex_list = json.loads(exercises)
            print(f"  Exercises: OK ({len(ex_list)})")
        except Exception as e:
            print(f"  Exercises: INVALID - {e}")
            print(f"  Content: {exercises!r}")
            
        try:
            tips_data = json.loads(tips)
            print(f"  Tips: OK")
        except Exception as e:
            print(f"  Tips: INVALID - {e}")
            print(f"  Content: {tips!r}")
            
    conn.close()

if __name__ == "__main__":
    test_json_validity()
