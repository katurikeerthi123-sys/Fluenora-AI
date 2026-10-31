import json
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.academy.database import get_db
from backend.academy.models import (
    User, Course, Module, Lesson, Exercise, Quiz, QuizQuestion,
    UserCourseProgress, UserLessonProgress, QuizAttempt, GrammarWeakness
)
from backend.academy.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_current_user_optional
)
from backend.academy.schemas import (
    UserRegister, UserLogin, UserResponse, TokenResponse,
    CourseCard, CourseDetail, ModuleDetail, LessonSummary, LessonDetail,
    ExerciseResponse, ExerciseSubmission, ExerciseCheckResult,
    QuizDetail, QuizSubmission, QuizResultResponse, QuizQuestionResult, QuizQuestionResponse,
    DashboardOverview
)

router = APIRouter(prefix="/api/academy", tags=["English Learning Academy"])


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@router.post("/auth/register", response_model=TokenResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user account with hashed password and returns a JWT token."""
    # Check for existing email or username
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken. Please choose another."
        )

    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name or payload.username,
        hashed_password=hash_password(payload.password),
        role="student"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns a signed JWT access token."""
    user = db.query(User).filter(
        (User.username == payload.username_or_email) |
        (User.email == payload.username_or_email)
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password."
        )

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)


# =============================================================================
# COURSE CATALOG ENDPOINTS
# =============================================================================

@router.get("/courses", response_model=List[CourseCard])
def list_courses(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Returns the comprehensive catalog of grammar courses.
    Calculates completion percentages and progress states for authenticated users.
    """
    query = db.query(Course)
    if category and category != "All":
        query = query.filter(Course.category == category)
    if difficulty and difficulty != "All":
        query = query.filter(Course.difficulty == difficulty)
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter((Course.title.ilike(search_fmt)) | (Course.summary.ilike(search_fmt)))

    courses = query.order_by(Course.order_index).all()
    results = []

    for c in courses:
        total_lessons = len(c.lessons)
        completed_lessons = 0
        status_val = "not_started"
        progress_pct = 0.0

        if current_user:
            prog = db.query(UserCourseProgress).filter(
                UserCourseProgress.user_id == current_user.id,
                UserCourseProgress.course_id == c.id
            ).first()
            if prog:
                completed_lessons = prog.completed_lessons_count
                status_val = prog.status
                if total_lessons > 0:
                    progress_pct = round((completed_lessons / total_lessons) * 100.0, 1)

        results.append(CourseCard(
            id=c.id,
            slug=c.slug,
            title=c.title,
            category=c.category,
            difficulty=c.difficulty,
            summary=c.summary,
            icon=c.icon,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            progress_pct=progress_pct,
            status=status_val
        ))

    return results


@router.get("/courses/{slug}", response_model=CourseDetail)
def get_course_detail(
    slug: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Retrieves full course information including modules and lesson outlines."""
    course = db.query(Course).filter(Course.slug == slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Completed lesson ids for this user
    completed_ids = set()
    completed_count = 0
    status_val = "not_started"
    progress_pct = 0.0

    if current_user:
        completions = db.query(UserLessonProgress.lesson_id).filter(
            UserLessonProgress.user_id == current_user.id,
            UserLessonProgress.course_id == course.id,
            UserLessonProgress.is_completed == True
        ).all()
        completed_ids = {c[0] for c in completions}
        completed_count = len(completed_ids)

        prog = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == current_user.id,
            UserCourseProgress.course_id == course.id
        ).first()
        if prog:
            status_val = prog.status

    total_lessons = len(course.lessons)
    if total_lessons > 0:
        progress_pct = round((completed_count / total_lessons) * 100.0, 1)

    # Format modules and lesson summaries
    modules_res = []
    for m in course.modules:
        lessons_res = []
        for l in m.lessons:
            lessons_res.append(LessonSummary(
                id=l.id,
                slug=l.slug,
                title=l.title,
                order_index=l.order_index,
                reading_time_mins=l.reading_time_mins,
                difficulty=l.difficulty,
                is_completed=(l.id in completed_ids)
            ))
        modules_res.append(ModuleDetail(
            id=m.id,
            title=m.title,
            summary=m.summary,
            order_index=m.order_index,
            lessons=lessons_res
        ))

    # Check for final assessment quiz
    final_quiz = db.query(Quiz).filter(
        Quiz.course_id == course.id,
        Quiz.is_final_assessment == True
    ).first()

    return CourseDetail(
        id=course.id,
        slug=course.slug,
        title=course.title,
        category=course.category,
        difficulty=course.difficulty,
        summary=course.summary,
        icon=course.icon,
        total_lessons=total_lessons,
        completed_lessons=completed_count,
        progress_pct=progress_pct,
        status=status_val,
        modules=modules_res,
        has_final_assessment=(final_quiz is not None),
        final_quiz_id=final_quiz.id if final_quiz else None
    )


# =============================================================================
# LESSON & EXERCISE ENDPOINTS
# =============================================================================

@router.get("/lessons/{course_slug}/{lesson_slug}", response_model=LessonDetail)
def get_lesson(
    course_slug: str,
    lesson_slug: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Retrieves full lesson content:
    - Theoretical rules in clear, accessible English
    - Formula and sentence structures
    - Positive, negative, and question examples
    - Common mistakes with corrections and explanations
    - Interactive practice exercises
    - Next and previous lesson links for seamless navigation
    """
    course = db.query(Course).filter(Course.slug == course_slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson = db.query(Lesson).filter(
        Lesson.course_id == course.id,
        Lesson.slug == lesson_slug
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    is_completed = False
    if current_user:
        up = db.query(UserLessonProgress).filter(
            UserLessonProgress.user_id == current_user.id,
            UserLessonProgress.lesson_id == lesson.id,
            UserLessonProgress.is_completed == True
        ).first()
        is_completed = (up is not None)

    # Decode JSON fields
    rules = json.loads(lesson.rules_json) if lesson.rules_json else []
    positive_ex = json.loads(lesson.positive_examples_json) if lesson.positive_examples_json else []
    negative_ex = json.loads(lesson.negative_examples_json) if lesson.negative_examples_json else []
    question_ex = json.loads(lesson.question_examples_json) if lesson.question_examples_json else []
    common_mistakes = json.loads(lesson.common_mistakes_json) if lesson.common_mistakes_json else []

    # Format exercises
    exercises_res = []
    for ex in lesson.exercises:
        opts = json.loads(ex.options_json) if ex.options_json else []
        exercises_res.append(ExerciseResponse(
            id=ex.id,
            exercise_type=ex.exercise_type,
            question_text=ex.question_text,
            options=opts,
            explanation=ex.explanation,
            difficulty=ex.difficulty
        ))

    # Determine Prev / Next lesson within the course
    all_lessons = db.query(Lesson).filter(Lesson.course_id == course.id).order_by(Lesson.order_index).all()
    prev_slug = None
    next_slug = None
    for idx, l in enumerate(all_lessons):
        if l.id == lesson.id:
            if idx > 0:
                prev_slug = all_lessons[idx - 1].slug
            if idx < len(all_lessons) - 1:
                next_slug = all_lessons[idx + 1].slug
            break

    return LessonDetail(
        id=lesson.id,
        course_id=lesson.course_id,
        module_id=lesson.module_id,
        slug=lesson.slug,
        title=lesson.title,
        order_index=lesson.order_index,
        reading_time_mins=lesson.reading_time_mins,
        difficulty=lesson.difficulty,
        concept_summary=lesson.concept_summary,
        formula_structure=lesson.formula_structure,
        rules=rules,
        positive_examples=positive_ex,
        negative_examples=negative_ex,
        question_examples=question_ex,
        common_mistakes=common_mistakes,
        content_markdown=lesson.content_markdown,
        is_completed=is_completed,
        exercises=exercises_res,
        prev_lesson_slug=prev_slug,
        next_lesson_slug=next_slug
    )


@router.post("/lessons/{lesson_id}/complete")
def mark_lesson_complete(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks a lesson as completed for the authenticated user and updates course progress."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    up = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.lesson_id == lesson.id
    ).first()

    if not up:
        up = UserLessonProgress(
            user_id=current_user.id,
            course_id=lesson.course_id,
            lesson_id=lesson.id,
            is_completed=True,
            completed_at=datetime.datetime.utcnow()
        )
        db.add(up)
    else:
        up.is_completed = True
        up.completed_at = datetime.datetime.utcnow()

    # Recalculate Course Progress
    total_lessons = db.query(Lesson).filter(Lesson.course_id == lesson.course_id).count()
    completed_count = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.course_id == lesson.course_id,
        UserLessonProgress.is_completed == True
    ).count()

    course_prog = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == current_user.id,
        UserCourseProgress.course_id == lesson.course_id
    ).first()

    if not course_prog:
        course_prog = UserCourseProgress(
            user_id=current_user.id,
            course_id=lesson.course_id,
            completed_lessons_count=completed_count,
            total_lessons_count=total_lessons,
            status="completed" if completed_count >= total_lessons else "in_progress",
            last_studied_at=datetime.datetime.utcnow()
        )
        db.add(course_prog)
    else:
        course_prog.completed_lessons_count = completed_count
        course_prog.total_lessons_count = total_lessons
        course_prog.last_studied_at = datetime.datetime.utcnow()
        if completed_count >= total_lessons and course_prog.status != "mastered":
            course_prog.status = "completed"
        elif course_prog.status == "not_started":
            course_prog.status = "in_progress"

    db.commit()
    return {
        "status": "success",
        "message": "Lesson marked as complete",
        "completed_count": completed_count,
        "total_lessons": total_lessons,
        "course_status": course_prog.status
    }


@router.post("/exercises/check", response_model=ExerciseCheckResult)
def check_exercise(payload: ExerciseSubmission, db: Session = Depends(get_db)):
    """Validates an interactive exercise attempt server-side and returns the explanation."""
    ex = db.query(Exercise).filter(Exercise.id == payload.exercise_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")

    submitted = payload.submitted_answer.strip().lower()
    correct = ex.correct_answer.strip().lower()
    is_correct = (submitted == correct)

    return ExerciseCheckResult(
        exercise_id=ex.id,
        is_correct=is_correct,
        submitted_answer=payload.submitted_answer,
        correct_answer=ex.correct_answer,
        explanation=ex.explanation
    )


# =============================================================================
# QUIZ & ASSESSMENT ENGINE
# =============================================================================

@router.get("/quizzes/{quiz_id}", response_model=QuizDetail)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Returns quiz questions and options without leaking correct answers."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    q_responses = []
    for q in quiz.questions:
        opts = json.loads(q.options_json) if q.options_json else []
        q_responses.append(QuizQuestionResponse(
            id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=opts,
            points=q.points
        ))

    return QuizDetail(
        id=quiz.id,
        course_id=quiz.course_id,
        title=quiz.title,
        description=quiz.description,
        passing_score_pct=quiz.passing_score_pct,
        is_final_assessment=quiz.is_final_assessment,
        total_questions=len(q_responses),
        questions=q_responses
    )


@router.post("/quizzes/submit", response_model=QuizResultResponse)
def submit_quiz(
    payload: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits and grades a quiz server-side:
    - Calculates exact percentage score
    - Evaluates against the 80% passing mastery threshold
    - Logs attempt in SQLite
    - Updates course status to 'mastered' when passing the comprehensive final assessment
    - Returns full question-by-question breakdown with educational explanations
    """
    quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Map submitted answers
    answers_dict = {a.question_id: a.selected_answer.strip().lower() for a in payload.answers}

    correct_count = 0
    total_count = len(quiz.questions)
    results_list = []
    incorrect_concepts = []

    for q in quiz.questions:
        user_ans_raw = answers_dict.get(q.id, "")
        correct_ans_raw = q.correct_answer.strip()
        is_corr = (user_ans_raw == correct_ans_raw.lower())

        if is_corr:
            correct_count += 1
        else:
            incorrect_concepts.append(q.question_text)

        results_list.append(QuizQuestionResult(
            question_id=q.id,
            question_text=q.question_text,
            selected_answer=answers_dict.get(q.id, "No answer selected"),
            correct_answer=q.correct_answer,
            is_correct=is_corr,
            explanation=q.explanation
        ))

    score_pct = round((correct_count / max(total_count, 1)) * 100.0, 1)
    passed = (score_pct >= quiz.passing_score_pct)

    # Record attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        score_pct=score_pct,
        passed=passed,
        total_questions=total_count,
        correct_answers=correct_count,
        responses_json=json.dumps([r.model_dump() for r in results_list]),
        attempted_at=datetime.datetime.utcnow()
    )
    db.add(attempt)
    db.flush()

    # If this was a final assessment and the user passed, mark course as 'mastered'
    if quiz.is_final_assessment:
        course_prog = db.query(UserCourseProgress).filter(
            UserCourseProgress.user_id == current_user.id,
            UserCourseProgress.course_id == quiz.course_id
        ).first()

        if course_prog:
            if passed:
                course_prog.status = "mastered"
            elif course_prog.status != "mastered":
                course_prog.status = "completed"
            course_prog.score_avg = score_pct
            course_prog.last_studied_at = datetime.datetime.utcnow()

    # Track Weakness if quiz had mistakes
    if not passed and quiz.course:
        weakness = db.query(GrammarWeakness).filter(
            GrammarWeakness.user_id == current_user.id,
            GrammarWeakness.topic_slug == quiz.course.slug
        ).first()
        if not weakness:
            weakness = GrammarWeakness(
                user_id=current_user.id,
                topic_slug=quiz.course.slug,
                error_category=quiz.course.category,
                error_count=total_count - correct_count,
                last_detected_at=datetime.datetime.utcnow()
            )
            db.add(weakness)
        else:
            weakness.error_count += (total_count - correct_count)
            weakness.last_detected_at = datetime.datetime.utcnow()

    db.commit()

    recommendations = []
    if not passed:
        recommendations.append(f"Review the lessons in '{quiz.title}' focusing on signal words and verb agreement.")
        recommendations.append("Re-attempt this assessment once you achieve 80%+ on individual lesson exercises.")
    else:
        recommendations.append("Excellent work! You have proven strong grammatical proficiency in this topic.")

    return QuizResultResponse(
        attempt_id=attempt.id,
        quiz_id=quiz.id,
        title=quiz.title,
        score_pct=score_pct,
        passed=passed,
        total_questions=total_count,
        correct_count=correct_count,
        results=results_list,
        recommendations=recommendations
    )


# =============================================================================
# DASHBOARD & PROGRESS ENDPOINTS
# =============================================================================

@router.get("/dashboard", response_model=DashboardOverview)
def get_dashboard(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Returns real-time learning statistics, courses in progress, and weak areas."""
    total_courses = db.query(Course).count()
    if not current_user:
        # Default view for guest or unauthenticated visitor
        return DashboardOverview(
            overall_progress_pct=0.0,
            courses_in_progress=0,
            courses_completed=0,
            courses_mastered=0,
            total_quizzes_taken=0,
            average_quiz_score=0.0,
            weak_grammar_areas=[],
            recent_lessons=[]
        )

    # Authenticated user stats
    progress_records = db.query(UserCourseProgress).filter(UserCourseProgress.user_id == current_user.id).all()
    in_progress = sum(1 for p in progress_records if p.status == "in_progress")
    completed = sum(1 for p in progress_records if p.status == "completed")
    mastered = sum(1 for p in progress_records if p.status == "mastered")

    total_lessons_in_platform = db.query(Lesson).count()
    completed_lessons_user = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id,
        UserLessonProgress.is_completed == True
    ).count()

    overall_pct = round((completed_lessons_user / max(total_lessons_in_platform, 1)) * 100.0, 1)

    # Quiz stats
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id).all()
    avg_score = round(sum(a.score_pct for a in attempts) / len(attempts), 1) if attempts else 0.0

    # Weak areas
    weak_records = db.query(GrammarWeakness).filter(
        GrammarWeakness.user_id == current_user.id
    ).order_by(GrammarWeakness.error_count.desc()).limit(4).all()

    weak_areas = [
        {"topic": w.topic_slug, "category": w.error_category, "mistakes_count": w.error_count}
        for w in weak_records
    ]

    # Recent lessons
    recent_l = db.query(UserLessonProgress).filter(
        UserLessonProgress.user_id == current_user.id
    ).order_by(UserLessonProgress.completed_at.desc()).limit(5).all()

    recent_lessons = []
    for r in recent_l:
        if r.lesson and r.lesson.course:
            recent_lessons.append({
                "lesson_title": r.lesson.title,
                "course_title": r.lesson.course.title,
                "course_slug": r.lesson.course.slug,
                "lesson_slug": r.lesson.slug,
                "completed_at": str(r.completed_at)
            })

    # Recommended continue course
    continue_card = None
    most_recent_p = db.query(UserCourseProgress).filter(
        UserCourseProgress.user_id == current_user.id,
        UserCourseProgress.status.in_(["in_progress", "not_started"])
    ).order_by(UserCourseProgress.last_studied_at.desc()).first()

    if most_recent_p and most_recent_p.course:
        c = most_recent_p.course
        continue_card = CourseCard(
            id=c.id,
            slug=c.slug,
            title=c.title,
            category=c.category,
            difficulty=c.difficulty,
            summary=c.summary,
            icon=c.icon,
            total_lessons=len(c.lessons),
            completed_lessons=most_recent_p.completed_lessons_count,
            progress_pct=round((most_recent_p.completed_lessons_count / max(len(c.lessons), 1)) * 100.0, 1),
            status=most_recent_p.status
        )

    return DashboardOverview(
        overall_progress_pct=overall_pct,
        courses_in_progress=in_progress,
        courses_completed=completed,
        courses_mastered=mastered,
        total_quizzes_taken=len(attempts),
        average_quiz_score=avg_score,
        weak_grammar_areas=weak_areas,
        recent_lessons=recent_lessons,
        continue_course=continue_card
    )

