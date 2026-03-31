import sqlite3
import json

def inspect_db():
    conn = sqlite3.connect('arogyamitra.db')
    cursor = conn.cursor()
    
    print("--- ALL USERS DETAILS ---")
    cursor.execute("SELECT id, username, email, assessment_completed FROM users")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- ALL WORKOUT PLANS (DASHBOARD SYNC CHECK) ---")
    cursor.execute("SELECT id, user_id, day, duration_minutes FROM workout_plans ORDER BY user_id, day")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    inspect_db()
