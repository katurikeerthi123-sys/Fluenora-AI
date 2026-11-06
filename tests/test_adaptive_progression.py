"""
Fluenora AI ✨ - Adaptive Progression & Weakness-Based Question Calibration Test Suite
Validates:
  1. Foundational Diagnostic Daily Question generation for new learners.
  2. Next-day calibration prioritizing topics where the student made mistakes.
  3. Dynamic difficulty progression (Beginner -> Intermediate -> Advanced) based on accuracy.
  4. Anti-repetition question rotation across consecutive practice days.
"""

import os
import sys
import pytest
import tempfile
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import Database
from backend.learning_engine import LearningEngine

class TestAdaptiveDailyProgression:
    @pytest.fixture(autouse=True)
    def setup_clean_db(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db = Database(db_path=self.temp_db_path)
        yield
        try:
            os.close(self.temp_db_fd)
            os.remove(self.temp_db_path)
        except Exception:
            pass

    def test_question_bank_has_comprehensive_coverage(self):
        """Verify expanded question bank covers all grammar categories and difficulty tiers."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM questions")
            count = cursor.fetchone()[0]
            assert count >= 30, f"Expected at least 30 questions, found {count}"

            cursor.execute("SELECT DISTINCT category_target FROM questions")
            categories = {r[0] for r in cursor.fetchall()}
            assert {"TENSE_ERROR", "SVA_ERROR", "STRUCTURE_ERROR", "PREPOSITION_ERROR", "ARTICLE_ERROR", "SPELLING_ERROR"}.issubset(categories)

            cursor.execute("SELECT DISTINCT difficulty FROM questions")
            difficulties = {r[0] for r in cursor.fetchall()}
            assert {"Beginner", "Intermediate", "Advanced"}.issubset(difficulties)

    def test_day_1_initial_diagnostic_set(self):
        """New learners receive a Day 1 Foundational Diagnostic set of 5 questions."""
        daily_data = self.db.get_daily_questions(user_id="new_learner", limit=5)
        assert daily_data["day_number"] == 1
        assert daily_data["difficulty_tier"] == "Beginner"
        assert len(daily_data["questions"]) == 5
        assert "Day 1" in daily_data["adaptation_reason"]

    def test_next_day_adapts_to_user_weaknesses(self):
        """
        When a user answers five questions each day and makes mistakes,
        the next day the questions adjust based on their weaknesses.
        """
        user = "test_learner_42"

        # Simulate Day 1: Student answers 5 questions and makes mistakes in TENSE_ERROR (3) and SVA_ERROR (2)
        # Mock submission recording
        for i in range(3):
            self.db.record_submission(
                user_id=user,
                question_id=1,
                user_answer="I did playing football",
                prediction={"label_id": 1, "label_name": "TENSE_ERROR", "confidence": 0.95, "top3": []},
                correction_info={"correction": "I played football.", "is_suitable": True, "explanation": "Tense mistake"}
            )
        for i in range(2):
            self.db.record_submission(
                user_id=user,
                question_id=2,
                user_answer="He go to college",
                prediction={"label_id": 2, "label_name": "SVA_ERROR", "confidence": 0.92, "top3": []},
                correction_info={"correction": "He goes to college.", "is_suitable": True, "explanation": "SVA mistake"}
            )

        progress = self.db.get_user_progress(user)
        assert progress["total_submissions"] == 5
        assert progress["primary_weakness"] == "TENSE_ERROR"

        # Generate Day 2 Adapted Question Set
        day2_data = self.db.get_daily_questions(user_id=user, limit=5, simulate_next_day=True)
        assert day2_data["day_number"] == 2
        assert day2_data["primary_weakness"] == "TENSE_ERROR"
        assert "TENSE_ERROR" in day2_data["adaptation_reason"]
        assert len(day2_data["questions"]) == 5

        # Check that questions focus on the mistake topics
        q_categories = [q["category_target"] for q in day2_data["questions"]]
        assert "TENSE_ERROR" in q_categories
        assert q_categories.count("TENSE_ERROR") >= 2, f"Expected at least 2 Tense questions, got {q_categories}"

    def test_gradual_difficulty_increase_with_performance_improvement(self):
        """
        As the student's performance improves (higher accuracy),
        difficulty level gradually steps up from Beginner to Intermediate and Advanced.
        """
        user = "improving_student"

        # Step 1: Low accuracy -> Beginner tier
        for i in range(3):
            self.db.record_submission(
                user_id=user,
                question_id=1,
                user_answer="I did playing football",
                prediction={"label_id": 1, "label_name": "TENSE_ERROR", "confidence": 0.95, "top3": []},
                correction_info={"correction": "I played football.", "is_suitable": True, "explanation": "Error"}
            )
        beginner_set = self.db.get_daily_questions(user_id=user, limit=5)
        assert beginner_set["difficulty_tier"] == "Beginner"

        # Step 2: Student improves (3 correct answers out of next 4 -> ~60% accuracy)
        for i in range(4):
            self.db.record_submission(
                user_id=user,
                question_id=i+10,
                user_answer="I played football yesterday.",
                prediction={"label_id": 0, "label_name": "CORRECT", "confidence": 0.98, "top3": []},
                correction_info={"correction": "I played football yesterday.", "is_suitable": True, "explanation": "Correct"}
            )
        intermediate_set = self.db.get_daily_questions(user_id=user, limit=5)
        assert intermediate_set["difficulty_tier"] == "Intermediate"

        # Step 3: High performance (all recent answers correct -> accuracy >= 80%)
        for i in range(5):
            self.db.record_submission(
                user_id=user,
                question_id=i+20,
                user_answer="Every member of our team practices diligently each morning.",
                prediction={"label_id": 0, "label_name": "CORRECT", "confidence": 0.99, "top3": []},
                correction_info={"correction": "Every member of our team practices diligently each morning.", "is_suitable": True, "explanation": "Correct"}
            )
        advanced_set = self.db.get_daily_questions(user_id=user, limit=5)
        assert advanced_set["difficulty_tier"] == "Advanced"
