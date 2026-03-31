import sqlite3

def check_shrita():
    conn = sqlite3.connect('arogyamitra.db')
    cursor = conn.cursor()
    
    print("--- Searching for users with 'shrita' ---")
    cursor.execute("SELECT id, username, email, assessment_completed FROM users WHERE username LIKE '%shrita%' OR email LIKE '%shrita%'")
    users = cursor.fetchall()
    for u in users:
        print(f"User: {u}")
        uid = u[0]
        
        # Check Workout Plans
        cursor.execute("SELECT COUNT(*) FROM workout_plans WHERE user_id = ?", (uid,))
        print(f"  Workout Plans: {cursor.fetchone()[0]}")
        
        # Check Nutrition Plans
        cursor.execute("SELECT COUNT(*) FROM nutrition_plans WHERE user_id = ?", (uid,))
        print(f"  Nutrition Plans: {cursor.fetchone()[0]}")
        
    conn.close()

if __name__ == "__main__":
    check_shrita()
