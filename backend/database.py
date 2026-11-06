import os
import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "fluenora.db")
)

INITIAL_QUESTIONS = [
    {
        "prompt": "Describe what you did yesterday from morning to evening.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Beginner",
        "context": "Daily routines and past actions. Watch out for simple past vs present continuous.",
        "sample_correct": "Yesterday I woke up early, attended my college classes, and studied in the library."
    },
    {
        "prompt": "Write two sentences about your best friend and what they do every day.",
        "category_target": "SVA_ERROR",
        "difficulty": "Beginner",
        "context": "Third-person singular subjects and habitual actions (verbs taking -s/-es).",
        "sample_correct": "My best friend works at a software firm. He speaks English fluently and loves playing cricket."
    },
    {
        "prompt": "Describe your daily routine or what you do every day before leaving home.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Beginner",
        "context": "Simple present tense for habitual actions and daily facts (watch out for incorrect continuous aspect).",
        "sample_correct": "Every day I wake up early, drink coffee, and prepare my bag for college."
    },
    {
        "prompt": "Write a complete sentence explaining why someone was absent or unable to attend class.",
        "category_target": "STRUCTURE_ERROR",
        "difficulty": "Intermediate",
        "context": "Complete sentence structure, avoiding fragmented 'Because...' clauses, and proper auxiliary placement.",
        "sample_correct": "I could not attend college yesterday because I was sick, but I have completed all the homework."
    },
    {
        "prompt": "Describe an important lesson you learned in school and how it helped you.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Intermediate",
        "context": "Past tense irregular verbs (spoke, wrote, taught, felt, caught) and academic vocabulary.",
        "sample_correct": "Our teacher taught us the importance of discipline, and I wrote down all her valuable advice."
    },
    {
        "prompt": "If you could ask a visiting scientist three questions about artificial intelligence, what would you ask?",
        "category_target": "STRUCTURE_ERROR",
        "difficulty": "Advanced",
        "context": "Interrogative syntax and Wh-question auxiliary inversion ('Where are you going?', 'What do you think?').",
        "sample_correct": "What do you think is the biggest breakthrough in deep learning, and where will AI be in ten years?"
    },
    {
        "prompt": "Write a short note inviting your college friend to an upcoming festival dinner at your home.",
        "category_target": "CORRECT",
        "difficulty": "Beginner",
        "context": "General conversational fluency, greetings, invitations, and politeness.",
        "sample_correct": "Please come to my house this Sunday evening. We have prepared a special dinner for the festival."
    },
    {
        "prompt": "Explain what you have been doing since you graduated or joined your current course.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Intermediate",
        "context": "Present perfect continuous tense with 'since' and 'for' ('I have been living/working...').",
        "sample_correct": "I have been studying computer science at the university for the past two years."
    },
    {
        "prompt": "Discuss the roles and responsibilities of the students and faculty in your department.",
        "category_target": "SVA_ERROR",
        "difficulty": "Intermediate",
        "context": "Plural vs singular subject-verb agreement: 'Each student has...', 'The professors guide...'",
        "sample_correct": "Every student in our class has an assigned mentor, and the professors guide us through our projects."
    },
    {
        "prompt": "Tell us about a delicious dish you ordered or prepared at a restaurant.",
        "category_target": "PREPOSITION_ERROR",
        "difficulty": "Beginner",
        "context": "Transitive verbs without redundant prepositions ('ordered biryani', 'discussed the plan').",
        "sample_correct": "Last night I ordered chicken biryani and discussed our weekend plans with my cousins."
    }
]


class Database:
    """
    SQLite persistence layer for Fluenora AI ✨.
    Tracks user profiles, question bank, answer submissions, grammar weakness frequencies,
    and daily learning streaks.
    """
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Create tables and initialize baseline question bank if empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Questions Bank
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    category_target TEXT NOT NULL,
                    difficulty TEXT DEFAULT 'Beginner',
                    context TEXT,
                    sample_correct TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Submissions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    question_id INTEGER,
                    user_answer TEXT NOT NULL,
                    predicted_label_id INTEGER NOT NULL,
                    predicted_label_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    top3_json TEXT NOT NULL,
                    is_correct INTEGER NOT NULL,
                    correction TEXT,
                    explanation TEXT,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            """)

            # 4. User Weaknesses Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_weaknesses (
                    user_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    error_count INTEGER DEFAULT 0,
                    total_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, category),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 5. Daily Streaks Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_streaks (
                    user_id TEXT PRIMARY KEY,
                    current_streak INTEGER DEFAULT 1,
                    last_active_date TEXT,
                    total_days_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Ensure default user exists
            cursor.execute("""
                INSERT OR IGNORE INTO users (id, username)
                VALUES ('default_user', 'Learner')
            """)

            # Seed questions if table is empty or update first 5 questions
            cursor.execute("SELECT COUNT(*) FROM questions")
            count = cursor.fetchone()[0]
            if count == 0:
                for q in INITIAL_QUESTIONS:
                    cursor.execute("""
                        INSERT INTO questions (prompt, category_target, difficulty, context, sample_correct)
                        VALUES (?, ?, ?, ?, ?)
                    """, (q["prompt"], q["category_target"], q["difficulty"], q["context"], q["sample_correct"]))
            else:
                # Ensure the primary 5 questions reflect the updated pedagogical prompts
                for idx, q in enumerate(INITIAL_QUESTIONS[:5], start=1):
                    cursor.execute("""
                        UPDATE questions
                        SET prompt = ?, category_target = ?, difficulty = ?, context = ?, sample_correct = ?
                        WHERE id = ?
                    """, (q["prompt"], q["category_target"], q["difficulty"], q["context"], q["sample_correct"], idx))

            conn.commit()

    def get_or_create_user(self, user_id: str, username: Optional[str] = None) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)

            uname = username or user_id.capitalize()
            cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, uname))
            conn.commit()
            return {"id": user_id, "username": uname, "created_at": datetime.now().isoformat()}

    def get_question_by_id(self, question_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve question metadata and pedagogical target by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_submission(
        self,
        user_id: str,
        question_id: Optional[int],
        user_answer: str,
        prediction: Dict[str, Any],
        correction_info: Dict[str, Any]
    ) -> int:
        """
        Record user submission, update user_weaknesses, and update daily streak.
        """
        self.get_or_create_user(user_id)
        label_id = prediction["label_id"]
        label_name = prediction["label_name"]
        confidence = prediction["confidence"]
        top3_json = json.dumps(prediction.get("top3", []))
        is_correct = 1 if label_name == "CORRECT" else 0
        correction = correction_info.get("correction")
        explanation = correction_info.get("explanation")
        if question_id and correction_info.get("is_suitable") is False:
            explanation = f"[{correction_info.get('suitability_verdict', 'OFF_TOPIC')}] {explanation}"

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Insert submission
            cursor.execute("""
                INSERT INTO submissions (
                    user_id, question_id, user_answer, predicted_label_id,
                    predicted_label_name, confidence, top3_json, is_correct,
                    correction, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, question_id, user_answer, label_id, label_name,
                confidence, top3_json, is_correct, correction, explanation
            ))
            submission_id = cursor.lastrowid

            # Update weaknesses
            # We track all attempts and increment error_count for the identified category if not CORRECT
            cursor.execute("""
                INSERT INTO user_weaknesses (user_id, category, error_count, total_count, last_updated)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, category) DO UPDATE SET
                    error_count = error_count + ?,
                    total_count = total_count + 1,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                user_id, label_name,
                0 if is_correct else 1,
                0 if is_correct else 1
            ))

            # Update Daily Streak
            today_str = date.today().isoformat()
            cursor.execute("SELECT current_streak, last_active_date, total_days_active FROM daily_streaks WHERE user_id = ?", (user_id,))
            streak_row = cursor.fetchone()

            if not streak_row:
                cursor.execute("""
                    INSERT INTO daily_streaks (user_id, current_streak, last_active_date, total_days_active)
                    VALUES (?, 1, ?, 1)
                """, (user_id, today_str))
            else:
                current_streak, last_date, total_days = streak_row
                if last_date != today_str:
                    try:
                        last_d = date.fromisoformat(last_date)
                        delta = (date.today() - last_d).days
                        if delta == 1:
                            new_streak = current_streak + 1
                        else:
                            new_streak = 1
                    except Exception:
                        new_streak = 1

                    cursor.execute("""
                        UPDATE daily_streaks
                        SET current_streak = ?, last_active_date = ?, total_days_active = total_days_active + 1
                        WHERE user_id = ?
                    """, (new_streak, today_str, user_id))

            conn.commit()
            return submission_id

    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Calculates aggregate user learning metrics:
        - Total submissions, correct count, accuracy
        - Category-by-category error counts and weakness scores
        - Streak stats
        - Recent submission history
        """
        self.get_or_create_user(user_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Overall counts
            cursor.execute("""
                SELECT
                    COUNT(*) as total_submissions,
                    SUM(is_correct) as correct_count
                FROM submissions WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            total = row["total_submissions"] or 0
            correct = row["correct_count"] or 0
            accuracy = round((correct / total * 100), 2) if total > 0 else 0.0

            # Streak
            cursor.execute("SELECT current_streak, total_days_active, last_active_date FROM daily_streaks WHERE user_id = ?", (user_id,))
            streak_row = cursor.fetchone()
            streak = streak_row["current_streak"] if streak_row else 0
            total_days = streak_row["total_days_active"] if streak_row else 0

            # Weaknesses by category
            cursor.execute("""
                SELECT category, error_count, total_count, last_updated
                FROM user_weaknesses
                WHERE user_id = ?
                ORDER BY error_count DESC
            """, (user_id,))
            weakness_rows = cursor.fetchall()

            weaknesses = {}
            for r in weakness_rows:
                cat = r["category"]
                err = r["error_count"]
                tot = r["total_count"]
                err_rate = round((err / tot * 100), 1) if tot > 0 else 0.0
                weaknesses[cat] = {
                    "error_count": err,
                    "total_count": tot,
                    "error_rate": err_rate
                }

            # Top primary weakness (excluding CORRECT)
            primary_weakness = None
            highest_err = 0
            for cat, data in weaknesses.items():
                if cat != "CORRECT" and data["error_count"] > highest_err:
                    highest_err = data["error_count"]
                    primary_weakness = cat

            # Recent 10 submissions
            cursor.execute("""
                SELECT s.id, s.user_answer, s.predicted_label_name, s.confidence,
                       s.is_correct, s.correction, s.explanation, s.submitted_at,
                       q.prompt as question_prompt
                FROM submissions s
                LEFT JOIN questions q ON s.question_id = q.id
                WHERE s.user_id = ?
                ORDER BY s.submitted_at DESC
                LIMIT 10
            """, (user_id,))
            recent = [dict(r) for r in cursor.fetchall()]

            return {
                "user_id": user_id,
                "total_submissions": total,
                "correct_submissions": correct,
                "accuracy_percentage": accuracy,
                "current_streak": streak,
                "total_days_active": total_days,
                "primary_weakness": primary_weakness or "None detected yet",
                "category_breakdown": weaknesses,
                "recent_submissions": recent
            }

    def get_daily_questions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Return the core daily practice challenges (Questions 1 through 5)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions ORDER BY id ASC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    def get_personalized_next_question(self, user_id: str) -> Dict[str, Any]:
        """
        Adaptive Next Question Selection:
        1. Tracks student's most frequent grammar mistakes across multiple submissions.
        2. Selects an exercise targeting their weakest grammar topic.
        3. Excludes recent question IDs to prevent repetitive drills.
        4. Scales difficulty (Beginner -> Intermediate -> Advanced) based on overall accuracy.
        """
        progress = self.get_user_progress(user_id)
        primary_weakness = progress.get("primary_weakness")
        total_subs = progress.get("total_submissions", 0)
        accuracy = progress.get("accuracy_percentage", 0.0)

        # Determine target difficulty based on student progress
        if total_subs < 3 or accuracy < 55.0:
            target_diff = "Beginner"
        elif accuracy >= 80.0 and total_subs >= 5:
            target_diff = "Advanced"
        else:
            target_diff = "Intermediate"

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Find recent question IDs submitted by this user to avoid repeats
            cursor.execute("""
                SELECT question_id FROM submissions
                WHERE user_id = ? AND question_id IS NOT NULL
                ORDER BY submitted_at DESC
                LIMIT 5
            """, (user_id,))
            recent_ids = [r[0] for r in cursor.fetchall() if r[0] is not None]

            placeholders = ",".join("?" for _ in recent_ids) if recent_ids else ""

            # Attempt 1: Target primary weakness + adaptive difficulty + non-recent
            if primary_weakness and primary_weakness != "None detected yet":
                query = f"""
                    SELECT * FROM questions
                    WHERE category_target = ?
                    {"AND id NOT IN (" + placeholders + ")" if placeholders else ""}
                    ORDER BY CASE WHEN difficulty = ? THEN 0 ELSE 1 END, RANDOM()
                    LIMIT 1
                """
                params = [primary_weakness]
                if recent_ids:
                    params.extend(recent_ids)
                params.append(target_diff)

                cursor.execute(query, params)
                row = cursor.fetchone()
                if row:
                    q = dict(row)
                    err_info = progress.get("category_breakdown", {}).get(primary_weakness, {})
                    err_cnt = err_info.get("error_count", "multiple")
                    q["recommendation_reason"] = (
                        f"Targeted {q['difficulty']} exercise designed to strengthen your detected weakness "
                        f"in {primary_weakness} ({err_cnt} past errors logged)."
                    )
                    return q

            # Attempt 2: Target adaptive difficulty + non-recent
            if placeholders:
                cursor.execute(f"""
                    SELECT * FROM questions
                    WHERE id NOT IN ({placeholders})
                    ORDER BY CASE WHEN difficulty = ? THEN 0 ELSE 1 END, RANDOM()
                    LIMIT 1
                """, (*recent_ids, target_diff))
                row = cursor.fetchone()
                if row:
                    q = dict(row)
                    q["recommendation_reason"] = f"Adaptive {q['difficulty']} exercise selected for well-rounded English grammar practice."
                    return q

            # Attempt 3: Any question matching target difficulty
            cursor.execute("""
                SELECT * FROM questions
                ORDER BY CASE WHEN difficulty = ? THEN 0 ELSE 1 END, RANDOM()
                LIMIT 1
            """, (target_diff,))
            q = dict(cursor.fetchone())
            q["recommendation_reason"] = f"Daily {q['difficulty']} revision prompt to maintain your learning streak."
            return q
