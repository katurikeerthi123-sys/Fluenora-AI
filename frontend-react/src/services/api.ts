import {
  User,
  CourseCardData,
  CourseDetailData,
  LessonDetailData,
  QuizDetailData,
  QuizResultData,
  DashboardData,
} from '../types/academy';

const API_BASE = '/api/academy';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('academy_token');
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

/** Convert any FastAPI/Pydantic error detail to a readable string. */
function parseApiError(detail: unknown, fallback: string): string {
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((e: any) => {
        const field = e.loc ? e.loc[e.loc.length - 1] : '';
        return field ? `${field}: ${e.msg}` : e.msg;
      })
      .join(' · ');
  }
  if (typeof detail === 'object' && (detail as any).msg) return (detail as any).msg;
  return fallback;
}

export const api = {
  // Auth
  async register(data: { email: string; username: string; password: string; full_name?: string }) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(parseApiError(err.detail, 'Registration failed'));
    }
    return res.json();
  },

  async login(data: { username_or_email: string; password: string }) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(parseApiError(err.detail, 'Invalid username or password'));
    }
    return res.json();
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
  },

  // Courses
  async getCourses(params?: { category?: string; difficulty?: string; search?: string }): Promise<CourseCardData[]> {
    const query = new URLSearchParams();
    if (params?.category && params.category !== 'All') query.set('category', params.category);
    if (params?.difficulty && params.difficulty !== 'All') query.set('difficulty', params.difficulty);
    if (params?.search) query.set('search', params.search);

    const res = await fetch(`${API_BASE}/courses?${query.toString()}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load courses');
    return res.json();
  },

  async getCourseDetail(slug: string): Promise<CourseDetailData> {
    const res = await fetch(`${API_BASE}/courses/${slug}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load course details');
    return res.json();
  },

  // Lessons
  async getLesson(courseSlug: string, lessonSlug: string): Promise<LessonDetailData> {
    const res = await fetch(`${API_BASE}/lessons/${courseSlug}/${lessonSlug}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load lesson content');
    return res.json();
  },

  async markLessonComplete(lessonId: number) {
    const res = await fetch(`${API_BASE}/lessons/${lessonId}/complete`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to mark lesson complete');
    return res.json();
  },

  // Exercises
  async checkExercise(exerciseId: number, submittedAnswer: string) {
    const res = await fetch(`${API_BASE}/exercises/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exercise_id: exerciseId, submitted_answer: submittedAnswer }),
    });
    if (!res.ok) throw new Error('Failed to check exercise');
    return res.json();
  },

  // Quizzes & Assessments
  async getQuiz(quizId: number): Promise<QuizDetailData> {
    const res = await fetch(`${API_BASE}/quizzes/${quizId}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load quiz');
    return res.json();
  },

  async submitQuiz(quizId: number, answers: Array<{ question_id: number; selected_answer: string }>): Promise<QuizResultData> {
    const res = await fetch(`${API_BASE}/quizzes/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ quiz_id: quizId, answers }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to submit quiz' }));
      throw new Error(err.detail || 'Failed to submit quiz');
    }
    return res.json();
  },

  // Dashboard
  async getDashboard(): Promise<DashboardData> {
    const res = await fetch(`${API_BASE}/dashboard`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load dashboard data');
    return res.json();
  },
};
