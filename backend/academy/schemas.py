from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Exercise Schemas ---
class ExerciseResponse(BaseModel):
    id: int
    exercise_type: str
    question_text: str
    options: List[str] = []
    explanation: str
    difficulty: str

    class Config:
        from_attributes = True

class ExerciseSubmission(BaseModel):
    exercise_id: int
    submitted_answer: str

class ExerciseCheckResult(BaseModel):
    exercise_id: int
    is_correct: bool
    submitted_answer: str
    correct_answer: str
    explanation: str


# --- Lesson Schemas ---
class LessonSummary(BaseModel):
    id: int
    slug: str
    title: str
    order_index: int
    reading_time_mins: int
    difficulty: str
    is_completed: bool = False

    class Config:
        from_attributes = True

class LessonDetail(BaseModel):
    id: int
    course_id: int
    module_id: int
    slug: str
    title: str
    order_index: int
    reading_time_mins: int
    difficulty: str
    concept_summary: str
    formula_structure: Optional[str] = None
    rules: List[str] = []
    positive_examples: List[str] = []
    negative_examples: List[str] = []
    question_examples: List[str] = []
    common_mistakes: List[Dict[str, str]] = []
    content_markdown: str
    is_completed: bool = False
    exercises: List[ExerciseResponse] = []
    prev_lesson_slug: Optional[str] = None
    next_lesson_slug: Optional[str] = None

    class Config:
        from_attributes = True


# --- Module Schemas ---
class ModuleDetail(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    order_index: int
    lessons: List[LessonSummary] = []

    class Config:
        from_attributes = True


# --- Course Schemas ---
class CourseCard(BaseModel):
    id: int
    slug: str
    title: str
    category: str
    difficulty: str
    summary: str
    icon: str
    total_lessons: int
    completed_lessons: int = 0
    progress_pct: float = 0.0
    status: str = "not_started"

    class Config:
        from_attributes = True

class CourseDetail(BaseModel):
    id: int
    slug: str
    title: str
    category: str
    difficulty: str
    summary: str
    icon: str
    total_lessons: int
    completed_lessons: int = 0
    progress_pct: float = 0.0
    status: str = "not_started"
    modules: List[ModuleDetail] = []
    has_final_assessment: bool = True
    final_quiz_id: Optional[int] = None

    class Config:
        from_attributes = True


# --- Quiz & Assessment Schemas ---
class QuizQuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: List[str]
    points: int

class QuizDetail(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    passing_score_pct: float
    is_final_assessment: bool
    total_questions: int
    questions: List[QuizQuestionResponse]

class QuizAnswerSubmission(BaseModel):
    question_id: int
    selected_answer: str

class QuizSubmission(BaseModel):
    quiz_id: int
    answers: List[QuizAnswerSubmission]

class QuizQuestionResult(BaseModel):
    question_id: int
    question_text: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str

class QuizResultResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    title: str
    score_pct: float
    passed: bool
    total_questions: int
    correct_count: int
    results: List[QuizQuestionResult]
    recommendations: List[str] = []


# --- Progress & Dashboard Schemas ---
class DashboardOverview(BaseModel):
    overall_progress_pct: float
    courses_in_progress: int
    courses_completed: int
    courses_mastered: int
    total_quizzes_taken: int
    average_quiz_score: float
    weak_grammar_areas: List[Dict[str, Any]]
    recent_lessons: List[Dict[str, Any]]
    continue_course: Optional[CourseCard] = None
