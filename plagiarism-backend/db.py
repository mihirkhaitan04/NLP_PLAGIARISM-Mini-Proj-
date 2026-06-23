import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

def save_result(submission_id, filename, raw_text, result_json):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO submissions (id, filename, raw_text, result_json)
            VALUES (%s, %s, %s, %s)
        """
        result_json_str = json.dumps(result_json)
        cursor.execute(query, (submission_id, filename, raw_text, result_json_str))
        conn.commit()
        cursor.close()
        print(f"Saved submission {submission_id} successfully.")
    except Exception as e:
        print(f"Error saving to database: {e}")
    finally:
        if conn:
            conn.close()

def get_history():
    conn = None
    results = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, filename, result_json, uploaded_at
            FROM submissions
            ORDER BY uploaded_at DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            result_json = row[2]
            overall_score = 0
            if result_json and "overall_score" in result_json:
                overall_score = result_json["overall_score"]
            results.append({
                "submission_id": row[0],
                "filename": row[1],
                "overall_score": overall_score,
                "uploaded_at": str(row[3])
            })
        cursor.close()
    except Exception as e:
        print(f"Error fetching history: {e}")
    finally:
        if conn:
            conn.close()
    return results

def get_result_by_id(submission_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, filename, result_json, uploaded_at
            FROM submissions
            WHERE id = %s
        """
        cursor.execute(query, (submission_id,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return None
        return {
            "submission_id": row[0],
            "filename": row[1],
            "result_json": row[2],
            "uploaded_at": str(row[3])
        }
    except Exception as e:
        print(f"Error fetching result: {e}")
        return None
    finally:
        if conn:
            conn.close()