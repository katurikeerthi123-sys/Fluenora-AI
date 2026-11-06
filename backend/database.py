import os
import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "fluenora.db")
)

INITIAL_QUESTIONS = [
    # ── TENSE_ERROR (Beginner, Intermediate, Advanced) ─────────────────────
    {
        "prompt": "Describe what you did yesterday from morning to evening.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Beginner",
        "context": "Daily routines and past actions. Watch out for simple past vs present continuous.",
        "sample_correct": "Yesterday I woke up early, attended my college classes, and studied in the library."
    },
    {
        "prompt": "Describe your daily routine or what you do every day before leaving home.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Beginner",
        "context": "Simple present tense for habitual actions and daily facts (watch out for incorrect continuous aspect).",
        "sample_correct": "Every day I wake up early, drink coffee, and prepare my bag for college."
    },
    {
        "prompt": "Tell us about a fun movie or sports match you watched last weekend with your friends.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Beginner",
        "context": "Simple past tense for completed leisure events (watched, played, enjoyed, went).",
        "sample_correct": "Last Sunday my friends and I watched an exciting cricket match at the stadium."
    },
    {
        "prompt": "Describe an important lesson you learned in school and how it helped you.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Intermediate",
        "context": "Past tense irregular verbs (spoke, wrote, taught, felt, caught) and academic vocabulary.",
        "sample_correct": "Our teacher taught us the importance of discipline, and I wrote down all her valuable advice."
    },
    {
        "prompt": "Explain what you have been doing since you graduated or joined your current course.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Intermediate",
        "context": "Present perfect continuous tense with 'since' and 'for' ('I have been living/working...').",
        "sample_correct": "I have been studying computer science at the university for the past two years."
    },
    {
        "prompt": "Describe what you were doing yesterday evening when it started raining heavily.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Intermediate",
        "context": "Past continuous aspect interrupted by a simple past event ('was studying when it began').",
        "sample_correct": "I was walking back home from the library when it suddenly started raining heavily."
    },
    {
        "prompt": "Reflect on how your personal and career aspirations have evolved over the past three years.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Advanced",
        "context": "Present perfect and past perfect tenses illustrating sequential milestone developments.",
        "sample_correct": "Over the past three years, I have gained substantial clarity regarding my engineering interests."
    },
    {
        "prompt": "Describe what significant milestones you will have accomplished by the end of next year.",
        "category_target": "TENSE_ERROR",
        "difficulty": "Advanced",
        "context": "Future perfect tense construction ('will have completed / graduated / mastered').",
        "sample_correct": "By the end of next year, I will have finished my degree and published my first research paper."
    },

    # ── SVA_ERROR (Subject-Verb Agreement) ──────────────────────────────────
    {
        "prompt": "Write two sentences about your best friend and what they do every day.",
        "category_target": "SVA_ERROR",
        "difficulty": "Beginner",
        "context": "Third-person singular subjects and habitual actions (verbs taking -s/-es: works, plays, studies).",
        "sample_correct": "My best friend works at a software firm. He speaks English fluently and loves playing cricket."
    },
    {
        "prompt": "Describe what your mother or father does at work and what hobbies they enjoy.",
        "category_target": "SVA_ERROR",
        "difficulty": "Beginner",
        "context": "Singular third-person subject-verb agreement: 'My father works...', 'She reads books...'",
        "sample_correct": "My father manages a local business, and he enjoys gardening during the weekends."
    },
    {
        "prompt": "Write two sentences comparing what you like versus what your classmates like.",
        "category_target": "SVA_ERROR",
        "difficulty": "Beginner",
        "context": "Contrasting first-person singular ('I like') with plural third-person subjects ('My classmates like').",
        "sample_correct": "I prefer reading novels, whereas my classmates enjoy playing video games after college."
    },
    {
        "prompt": "Discuss the roles and responsibilities of the students and faculty in your department.",
        "category_target": "SVA_ERROR",
        "difficulty": "Intermediate",
        "context": "Plural vs singular subject-verb agreement: 'Each student has...', 'The professors guide...'",
        "sample_correct": "Every student in our class has an assigned mentor, and the professors guide us through our projects."
    },
    {
        "prompt": "Explain how one of your favorite sports teams or project groups prepares for challenges.",
        "category_target": "SVA_ERROR",
        "difficulty": "Intermediate",
        "context": "Collective nouns and distributive pronouns: 'Every player contributes...', 'Neither of them gives up.'",
        "sample_correct": "Every member of our team practices daily, and our captain motivates everyone before matches."
    },
    {
        "prompt": "Describe how your sibling or roommate handles stressful exam situations.",
        "category_target": "SVA_ERROR",
        "difficulty": "Intermediate",
        "context": "Subject-verb agreement across intervening phrases: 'My brother, along with his friends, stays calm.'",
        "sample_correct": "My roommate always remains calm during exams and prepares concise revision notes."
    },
    {
        "prompt": "Discuss whether everyone in society has equal access to quality higher education.",
        "category_target": "SVA_ERROR",
        "difficulty": "Advanced",
        "context": "Indefinite pronouns ('everyone', 'everybody', 'neither') taking singular verb forms.",
        "sample_correct": "Everyone in modern society deserves equal educational opportunities regardless of their background."
    },
    {
        "prompt": "Analyze the difficulties that arise when neither the administration nor the faculty members agree on reforms.",
        "category_target": "SVA_ERROR",
        "difficulty": "Advanced",
        "context": "Proximity agreement rule with correlative conjunctions 'neither... nor'.",
        "sample_correct": "When neither the administration nor the faculty members reach a consensus, progress slows down."
    },

    # ── STRUCTURE_ERROR ─────────────────────────────────────────────────────
    {
        "prompt": "Write a complete sentence explaining where you are going this evening and who is joining you.",
        "category_target": "STRUCTURE_ERROR",
        "difficulty": "Beginner",
        "context": "Complete SVO order, copula auxiliary placement: 'I am going...', 'My friend is coming.'",
        "sample_correct": "I am going to the evening market, and my brother is coming with me."
    },
    {
        "prompt": "Write two complete sentences explaining what food you do not like to eat and the reason why.",
        "category_target": "STRUCTURE_ERROR",
        "difficulty": "Beginner",
        "context": "Negation auxiliary syntax with 'do not' and 'does not' without double negatives.",
        "sample_correct": "I do not like bitter gourd because it tastes unpleasant, but my sister eats it happily."
    },
    {
        "prompt": "Write a complete sentence explaining why someone was absent or unable to attend class.",
        "category_target": "STRUCTURE_ERROR",
        "difficulty": "Intermediate",
        "context": "Complete sentence structure, avoiding fragmented 'Because...' clauses, and proper auxiliary placement.",
        "sample_correct": "I could not attend college yesterday because I was sick, but I have completed all the homework."
    },
    {
        "prompt": "Write two complete sentences describing why your project team could not complete the assignment on time.",
        "category_target": "STRUCTURE_ERROR",
        "difficulty": "Intermediate",
        "context": "Subordinate clause completion and modal auxiliary coordination ('could not complete because...').",
        "sample_correct": "Our team could not submit the project on time because our primary server encountered a technical issue."
    },
    {
        "prompt": "If you could ask a visiting scientist three questions about artificial intelligence, what would you ask?",
        "category_target": "STRUCTURE_ERROR",
        "difficulty": "Advanced",
        "context": "Interrogative syntax and Wh-question auxiliary inversion ('Where are you going?', 'What do you think?').",
        "sample_correct": "What do you think is the biggest breakthrough in deep learning, and where will AI be in ten years?"
    },
    {
        "prompt": "Construct a complex sentence expressing how overcoming unexpected setbacks can strengthen professional resilience.",
        "category_target": "STRUCTURE_ERROR",
        "difficulty": "Advanced",
        "context": "Multi-clause cohesion using transitional conjunctions and proper punctuation.",
        "sample_correct": "Although unexpected setbacks often cause initial frustration, navigating through them builds enduring professional resilience."
    },

    # ── PREPOSITION_ERROR ───────────────────────────────────────────────────
    {
        "prompt": "Tell us about a delicious dish you ordered or prepared at a restaurant.",
        "category_target": "PREPOSITION_ERROR",
        "difficulty": "Beginner",
        "context": "Transitive verbs without redundant prepositions ('ordered biryani', 'discussed the plan').",
        "sample_correct": "Last night I ordered chicken biryani and discussed our weekend plans with my cousins."
    },
    {
        "prompt": "Describe what academic subjects you are good at and which areas you find challenging.",
        "category_target": "PREPOSITION_ERROR",
        "difficulty": "Beginner",
        "context": "Idiomatic preposition collocations: 'good at math', 'interested in science', 'weak at languages'.",
        "sample_correct": "I am good at mathematics and computer programming, but I am working to improve at public speaking."
    },
    {
        "prompt": "Describe a recent family celebration, including the day, time of day, and location it took place.",
        "category_target": "PREPOSITION_ERROR",
        "difficulty": "Intermediate",
        "context": "Prepositions of time and place ('on Sunday', 'in the evening', 'at home').",
        "sample_correct": "On Sunday evening, our entire family gathered at our ancestral home to celebrate the festival."
    },
    {
        "prompt": "Write about someone recovering from an illness and the medical advice they followed.",
        "category_target": "PREPOSITION_ERROR",
        "difficulty": "Intermediate",
        "context": "Verb-preposition idioms: 'suffering from fever', 'recovered from illness', 'advised by doctor'.",
        "sample_correct": "My cousin was suffering from high fever, but he has fully recovered after following the doctor's advice."
    },
    {
        "prompt": "Discuss whether you agree or disagree with introducing mandatory coding curricula in primary schools.",
        "category_target": "PREPOSITION_ERROR",
        "difficulty": "Advanced",
        "context": "Nuanced prepositions: 'agree with someone', 'agree to a policy', 'conducive to learning'.",
        "sample_correct": "I agree with the educators who believe that early problem-solving skills are conducive to lifelong intellectual growth."
    },

    # ── ARTICLE_ERROR ───────────────────────────────────────────────────────
    {
        "prompt": "Describe an honest person you admire and an interesting hobby they pursue.",
        "category_target": "ARTICLE_ERROR",
        "difficulty": "Beginner",
        "context": "Phonetic article rules: 'an honest person', 'an interesting hobby', 'a useful skill'.",
        "sample_correct": "My grandfather is an honest man who spends his retirement pursuing an interesting hobby in woodworking."
    },
    {
        "prompt": "Write about a university or historical monument in India you would love to visit.",
        "category_target": "ARTICLE_ERROR",
        "difficulty": "Beginner",
        "context": "Phonetic glide /juː/ taking 'a': 'a university', and definite article 'the' for historical monuments: 'the Taj Mahal'.",
        "sample_correct": "I hope to study at a top university in India and visit the iconic Red Fort in Delhi."
    },
    {
        "prompt": "Explain the importance of the sun, moon, and oceans in sustaining life on Earth.",
        "category_target": "ARTICLE_ERROR",
        "difficulty": "Intermediate",
        "context": "Definite article 'the' for unique celestial bodies, planetary systems, and major geographic entities.",
        "sample_correct": "The sun provides essential energy to Earth, while the oceans regulate global climate patterns."
    },
    {
        "prompt": "Evaluate whether earning an international degree provides a unique advantage in today's global job market.",
        "category_target": "ARTICLE_ERROR",
        "difficulty": "Advanced",
        "context": "Vowel glides vs phonetic acronyms: 'a unique advantage', 'an MBA graduate', 'a European institution'.",
        "sample_correct": "Graduating from a European university often grants an applicant a unique edge during international recruitment."
    },

    # ── SPELLING_ERROR ──────────────────────────────────────────────────────
    {
        "prompt": "Write about an athletic event where you ran fast, caught a ball, or cheered for your school team.",
        "category_target": "SPELLING_ERROR",
        "difficulty": "Beginner",
        "context": "Irregular past tense spelling: ran (not runned), caught (not catched), and adverb 'fast' (not fastly).",
        "sample_correct": "During our annual sports meet, I ran very fast and caught the winning cricket ball."
    },
    {
        "prompt": "Describe a memorable day from your school life and how you felt when you received an award.",
        "category_target": "SPELLING_ERROR",
        "difficulty": "Intermediate",
        "context": "Commonly misspelled words: received ('e' before 'i' after 'c'), definitely, felt, grammar.",
        "sample_correct": "I definitely felt proud when our principal presented me with an award for academic excellence."
    },
    {
        "prompt": "Explain how academic discipline and meticulous planning contribute to university success.",
        "category_target": "SPELLING_ERROR",
        "difficulty": "Advanced",
        "context": "Advanced academic vocabulary spelling: conscientious, perseverance, definitely, curriculum.",
        "sample_correct": "Perseverance and conscientious study habits are definitely critical for achieving university success."
    },

    # ── CORRECT / NATURAL FLUENCY (Mastery Tier) ────────────────────────────
    {
        "prompt": "Write a short note inviting your college friend to an upcoming festival dinner at your home.",
        "category_target": "CORRECT",
        "difficulty": "Beginner",
        "context": "General conversational fluency, greetings, invitations, and politeness.",
        "sample_correct": "Please come to my house this Sunday evening. We have prepared a special dinner for the festival."
    },
    {
        "prompt": "Write a polite formal email requesting your professor for feedback on your project submission.",
        "category_target": "CORRECT",
        "difficulty": "Intermediate",
        "context": "Professional academic register, polite modal openers: 'Could you please review...', 'Thank you for your guidance.'",
        "sample_correct": "Could you please provide your valuable feedback on my project submission whenever your schedule permits?"
    },
    {
        "prompt": "Present a persuasive perspective on how continuous skill learning empowers individuals in an automated world.",
        "category_target": "CORRECT",
        "difficulty": "Advanced",
        "context": "Sophisticated cohesive transitions, nuanced vocabulary, and flawless grammatical expression.",
        "sample_correct": "Continuous lifelong learning ensures that professionals remain adaptable, innovative, and indispensable in an evolving economy."
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

            # Seed and synchronize all pedagogical practice questions
            for q in INITIAL_QUESTIONS:
                cursor.execute("SELECT id FROM questions WHERE prompt = ?", (q["prompt"],))
                row = cursor.fetchone()
                if not row:
                    cursor.execute("""
                        INSERT INTO questions (prompt, category_target, difficulty, context, sample_correct)
                        VALUES (?, ?, ?, ?, ?)
                    """, (q["prompt"], q["category_target"], q["difficulty"], q["context"], q["sample_correct"]))
                else:
                    cursor.execute("""
                        UPDATE questions
                        SET category_target = ?, difficulty = ?, context = ?, sample_correct = ?
                        WHERE id = ?
                    """, (q["category_target"], q["difficulty"], q["context"], q["sample_correct"], row[0]))

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
                ORDER BY s.submitted_at DESC, s.id DESC
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

    def get_daily_questions(
        self,
        user_id: str = "default_user",
        limit: int = 5,
        simulate_next_day: bool = False
    ) -> Dict[str, Any]:
        """
        Adaptive Daily Question Set:
        If user answers five questions each day, then the next day the questions
        adjust dynamically based on their weaknesses and performance:
          1. Tracks student errors and ranks their weakest grammar topics.
          2. Gradually increases difficulty (Beginner -> Intermediate -> Advanced)
             as their performance / accuracy improves.
          3. Focuses more questions on the topics where the user made mistakes.
          4. Excludes questions answered in the last 24 hours / last 5-10 submissions
             to guarantee a fresh, non-repetitive daily challenge.
        """
        self.get_or_create_user(user_id)
        progress = self.get_user_progress(user_id)
        total_subs = progress.get("total_submissions", 0)
        overall_accuracy = progress.get("accuracy_percentage", 0.0)
        total_days = progress.get("total_days_active", 0)

        # Recent performance analysis (last 5 submissions)
        recent_subs = progress.get("recent_submissions", [])[:5]
        if recent_subs:
            recent_correct = sum(1 for s in recent_subs if s.get("is_correct"))
            recent_accuracy = round((recent_correct / len(recent_subs)) * 100, 1)
        else:
            recent_accuracy = overall_accuracy

        # 1. Determine Difficulty Tier based on gradual performance improvement
        # Beginner: New users or accuracy < 55%
        # Intermediate: Steady improvement (recent accuracy >= 55% with >= 3 attempts)
        # Advanced: High mastery across sessions (recent accuracy >= 80% with >= 8 attempts)
        if (recent_accuracy >= 80.0 and total_subs >= 8) or (overall_accuracy >= 80.0 and total_subs >= 10):
            target_diff = "Advanced"
        elif (recent_accuracy >= 55.0 and total_subs >= 3) or (overall_accuracy >= 55.0 and total_subs >= 3):
            target_diff = "Intermediate"
        else:
            target_diff = "Beginner"

        # 2. Day Number Calculation
        day_number = (total_days + 1) if (simulate_next_day or total_subs >= 5) else max(1, total_days)

        # 3. Identify and Rank Weakness Topics (where user made mistakes)
        category_breakdown = progress.get("category_breakdown", {})
        ranked_weaknesses = sorted(
            [c for c in category_breakdown.items() if c[0] != "CORRECT" and c[1].get("error_count", 0) > 0],
            key=lambda x: (x[1].get("error_count", 0), x[1].get("error_rate", 0.0)),
            reverse=True
        )

        primary_weakness = ranked_weaknesses[0][0] if ranked_weaknesses else None
        secondary_weakness = ranked_weaknesses[1][0] if len(ranked_weaknesses) > 1 else None
        tertiary_weakness = ranked_weaknesses[2][0] if len(ranked_weaknesses) > 2 else None

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Exclude recently answered question IDs to avoid repeats
            cursor.execute("""
                SELECT question_id FROM submissions
                WHERE user_id = ? AND question_id IS NOT NULL
                ORDER BY submitted_at DESC, id DESC
                LIMIT 10
            """, (user_id,))
            recent_qids = set(r[0] for r in cursor.fetchall() if r[0] is not None)

            selected_ids = []
            selected_questions = []

            def fetch_question(category: Optional[str], diff: str, fallback_diffs: List[str]) -> Optional[Dict[str, Any]]:
                diff_list = [diff] + [d for d in fallback_diffs if d != diff]
                for d in diff_list:
                    conds = []
                    params = []

                    conds.append("difficulty = ?")
                    params.append(d)

                    if category:
                        conds.append("category_target = ?")
                        params.append(category)

                    excluded = set(selected_ids) | set(recent_qids)
                    if excluded:
                        conds.append(f"id NOT IN ({','.join('?' for _ in excluded)})")
                        params.extend(list(excluded))

                    where_clause = " WHERE " + " AND ".join(conds) if conds else ""
                    query = f"SELECT * FROM questions {where_clause} ORDER BY RANDOM() LIMIT 1"
                    cursor.execute(query, params)
                    row = cursor.fetchone()
                    if row:
                        return dict(row)

                # Relax recent_qids if needed, but maintain uniqueness in this set
                for d in diff_list:
                    conds = ["difficulty = ?"]
                    params = [d]
                    if category:
                        conds.append("category_target = ?")
                        params.append(category)
                    if selected_ids:
                        conds.append(f"id NOT IN ({','.join('?' for _ in selected_ids)})")
                        params.extend(selected_ids)
                    where_clause = " WHERE " + " AND ".join(conds)
                    query = f"SELECT * FROM questions {where_clause} ORDER BY RANDOM() LIMIT 1"
                    cursor.execute(query, params)
                    row = cursor.fetchone()
                    if row:
                        return dict(row)
                return None

            diff_fallbacks = ["Intermediate", "Beginner", "Advanced"] if target_diff == "Intermediate" else (
                ["Advanced", "Intermediate", "Beginner"] if target_diff == "Advanced" else ["Beginner", "Intermediate", "Advanced"]
            )

            # Slot 1: Primary Weakness drill
            q1 = fetch_question(primary_weakness, target_diff, diff_fallbacks) if primary_weakness else None
            if q1:
                selected_ids.append(q1["id"])
                selected_questions.append(q1)

            # Slot 2: Primary Weakness drill 2 (or Secondary Weakness)
            q2 = fetch_question(primary_weakness or secondary_weakness, target_diff, diff_fallbacks) if (primary_weakness or secondary_weakness) else None
            if q2:
                selected_ids.append(q2["id"])
                selected_questions.append(q2)

            # Slot 3: Secondary Weakness (or Tertiary Weakness / SVA)
            target_cat3 = secondary_weakness or tertiary_weakness or "SVA_ERROR"
            q3 = fetch_question(target_cat3, target_diff, diff_fallbacks)
            if q3:
                selected_ids.append(q3["id"])
                selected_questions.append(q3)

            # Slot 4: Tertiary Weakness or Structure reinforcement
            target_cat4 = tertiary_weakness or "STRUCTURE_ERROR"
            q4 = fetch_question(target_cat4, target_diff, diff_fallbacks)
            if q4:
                selected_ids.append(q4["id"])
                selected_questions.append(q4)

            # Slot 5: Communicative Mastery / Integrated Challenge
            q5 = fetch_question("CORRECT", target_diff, diff_fallbacks) or fetch_question(None, target_diff, diff_fallbacks)
            if q5:
                selected_ids.append(q5["id"])
                selected_questions.append(q5)

            # Fill up to limit if any slot was empty
            while len(selected_questions) < limit:
                fill_q = fetch_question(None, target_diff, diff_fallbacks)
                if not fill_q:
                    cursor.execute("SELECT * FROM questions ORDER BY id ASC LIMIT ?", (limit,))
                    selected_questions = [dict(r) for r in cursor.fetchall()]
                    break
                selected_ids.append(fill_q["id"])
                selected_questions.append(fill_q)

            # 4. Craft Clear Pedagogical Adaptation Rationale
            if primary_weakness:
                err_cnt = category_breakdown.get(primary_weakness, {}).get("error_count", 1)
                sec_desc = f" and {secondary_weakness}" if secondary_weakness else ""
                adaptation_reason = (
                    f"Day {day_number} Adaptive Set: Questions focused on your primary mistake areas in "
                    f"{primary_weakness} ({err_cnt} error{'s' if err_cnt > 1 else ''}){sec_desc}. "
                    f"Difficulty graduated to {target_diff} based on your performance ({recent_accuracy}% accuracy)."
                )
            elif total_subs > 0:
                adaptation_reason = (
                    f"Day {day_number} Mastery Set: Excellent performance recorded! Difficulty graduated to {target_diff} "
                    f"({recent_accuracy}% accuracy) to build mastery across complex sentence construction and fluency."
                )
            else:
                adaptation_reason = (
                    "Day 1 Foundational Diagnostic Set: 5 structured prompts covering daily actions, subject-verb agreement, "
                    "past irregular verbs, and sentence structure to determine your initial baseline."
                )

            return {
                "day_number": day_number,
                "difficulty_tier": target_diff,
                "primary_weakness": primary_weakness or "None (Diagnostic)",
                "secondary_weakness": secondary_weakness or "None",
                "accuracy_percentage": recent_accuracy,
                "total_submissions": total_subs,
                "adaptation_reason": adaptation_reason,
                "questions": selected_questions[:limit]
            }

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
                ORDER BY submitted_at DESC, id DESC
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
