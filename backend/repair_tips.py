import sqlite3
import json

def repair_db():
    conn = sqlite3.connect('arogyamitra.db')
    cursor = conn.cursor()
    
    print("Finding invalid JSON tips...")
    cursor.execute("SELECT id, tips FROM workout_plans")
    rows = cursor.fetchall()
    
    repaired_count = 0
    for row_id, tips in rows:
        if not tips:
            continue
            
        try:
            json.loads(tips)
        except Exception:
            # It's a plain string, repair it by dumping it to JSON
            print(f"  Repairing ID {row_id}: {tips!r}")
            repaired_tips = json.dumps(tips)
            cursor.execute("UPDATE workout_plans SET tips = ? WHERE id = ?", (repaired_tips, row_id))
            repaired_count += 1
            
    conn.commit()
    print(f"Total repaired: {repaired_count}")
    conn.close()

if __name__ == "__main__":
    repair_db()
