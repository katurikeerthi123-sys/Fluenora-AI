import os
import sys
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.main import app
from backend.academy.database import SessionLocal, Base, engine
from backend.academy.seed_content import seed_database

@pytest.fixture(scope="session", autouse=True)
def setup_academy_db():
    seed_database()

@pytest.fixture
def client():
    return TestClient(app)

def test_auth_registration_and_login(client):
    unique_suffix = os.urandom(4).hex()
    email = f"user_{unique_suffix}@academy.edu"
    username = f"student_{unique_suffix}"
    password = "SecurePassword123!"

    # 1. Register
    reg_res = client.post("/api/academy/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
        "full_name": "Test Student"
    })
    assert reg_res.status_code == 200, reg_res.text
    token_data = reg_res.json()
    assert "access_token" in token_data
    assert token_data["user"]["username"] == username

    # 2. Login
    login_res = client.post("/api/academy/auth/login", json={
        "username_or_email": username,
        "password": password
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 3. Get profile
    token = login_res.json()["access_token"]
    me_res = client.get("/api/academy/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

def test_course_catalog_retrieval(client):
    res = client.get("/api/academy/courses")
    assert res.status_code == 200
    courses = res.json()
    assert len(courses) >= 6
    slugs = [c["slug"] for c in courses]
    assert "english-tenses" in slugs
    assert "subject-verb-agreement" in slugs

def test_lesson_detail_structure(client):
    res = client.get("/api/academy/lessons/english-tenses/simple-present-tense")
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Simple Present Tense"
    assert len(data["rules"]) > 0
    assert len(data["positive_examples"]) > 0
    assert len(data["common_mistakes"]) > 0
    assert len(data["exercises"]) > 0

def test_exercise_checking(client):
    res = client.post("/api/academy/exercises/check", json={
        "exercise_id": 1,
        "submitted_answer": "works"
    })
    assert res.status_code == 200
    result = res.json()
    assert result["is_correct"] is True
    assert "explanation" in result

def test_dashboard_retrieval(client):
    res = client.get("/api/academy/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "courses_in_progress" in data
    assert "courses_completed" in data
    assert "overall_progress_pct" in data
    assert "total_quizzes_taken" in data
