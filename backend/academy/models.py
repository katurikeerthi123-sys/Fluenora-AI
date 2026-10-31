import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.academy.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="student")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    course_progress = relationship("UserCourseProgress", back_populates="user", cascade="all, delete-orphan")
    lesson_progress = relationship("UserLessonProgress", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    weaknesses = relationship("GrammarWeakness", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)  # e.g., Tenses, Syntax, Mechanics
    difficulty = Column(String(50), default="All Levels")       # Beginner, Intermediate, Advanced, All Levels
    summary = Column(Text, nullable=False)
    icon = Column(String(50), default="BookOpen")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.order_index")
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    slug = Column(String(100), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    order_index = Column(Integer, default=0)
    reading_time_mins = Column(Integer, default=5)
    difficulty = Column(String(50), default="Beginner")

    # Core Structured Content (Pure simple English)
    concept_summary = Column(Text, nullable=False)
    formula_structure = Column(Text, nullable=True)   # Positive / Negative / Question structures
    rules_json = Column(Text, nullable=True)          # JSON list of grammatical rules
    positive_examples_json = Column(Text, nullable=True)  # JSON list of positive sentences
    negative_examples_json = Column(Text, nullable=True)  # JSON list of negative sentences
    question_examples_json = Column(Text, nullable=True)  # JSON list of yes/no & WH questions
    common_mistakes_json = Column(Text, nullable=True)    # JSON list of {wrong, right, explanation}
    content_markdown = Column(Text, nullable=False)       # Comprehensive in-depth explanation

    # Relationships
    course = relationship("Course", back_populates="lessons")
    module = relationship("Module", back_populates="lessons")
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    exercise_type = Column(String(50), default="mcq")  # mcq, fill_blank, error_spotting, sentence_transformation
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=True)         # JSON list of options for MCQs
    correct_answer = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty = Column(String(50), default="Beginner")

    # Relationships
    lesson = relationship("Lesson", back_populates="exercises")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    passing_score_pct = Column(Float, default=80.0)
    is_final_assessment = Column(Boolean, default=False)

    # Relationships
    course = relationship("Course", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="mcq")
    options_json = Column(Text, nullable=False)       # JSON list of choices
    correct_answer = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    points = Column(Integer, default=1)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed, mastered
    completed_lessons_count = Column(Integer, default=0)
    total_lessons_count = Column(Integer, default=0)
    score_avg = Column(Float, default=0.0)
    last_studied_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="course_progress")
    course = relationship("Course")


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    score_pct = Column(Float, nullable=False)
    passed = Column(Boolean, default=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    responses_json = Column(Text, nullable=True)       # JSON list of user answers & verification
    attempted_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")


class GrammarWeakness(Base):
    __tablename__ = "grammar_weaknesses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic_slug = Column(String(100), nullable=False)
    error_category = Column(String(100), nullable=False)  # TENSE_ERROR, SVA_ERROR, etc.
    error_count = Column(Integer, default=1)
    last_detected_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="weaknesses")
