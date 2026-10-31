import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { LoginPage } from './components/LoginPage';
import { DashboardView } from './components/DashboardView';
import { CourseDetailView } from './components/CourseDetailView';
import { LessonView } from './components/LessonView';
import { QuizView } from './components/QuizView';
import { api } from './services/api';
import {
  User,
  DashboardData,
  CourseCardData,
  CourseDetailData,
  LessonDetailData,
  QuizDetailData
} from './types/academy';

type AppState = 'checking_auth' | 'unauthenticated' | 'authenticated';

export default function App() {
  // Auth & loading state
  const [appState, setAppState] = useState<AppState>('checking_auth');
  const [user, setUser] = useState<User | null>(null);

  // Navigation state
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'courses'>('dashboard');
  const [selectedCourseSlug, setSelectedCourseSlug] = useState<string | null>(null);
  const [selectedLessonSlug, setSelectedLessonSlug] = useState<string | null>(null);
  const [activeQuizId, setActiveQuizId] = useState<number | null>(null);

  // Data state
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [courses, setCourses] = useState<CourseCardData[]>([]);
  const [courseDetail, setCourseDetail] = useState<CourseDetailData | null>(null);
  const [lessonDetail, setLessonDetail] = useState<LessonDetailData | null>(null);
  const [quizDetail, setQuizDetail] = useState<QuizDetailData | null>(null);
  const [loading, setLoading] = useState(false);

  // On mount — check if a valid token exists (silent auth check)
  useEffect(() => {
    const token = localStorage.getItem('academy_token');
    if (!token) {
      setAppState('unauthenticated');
      return;
    }
    api.getMe()
      .then((u) => {
        setUser(u);
        setAppState('authenticated');
        loadDashboardData();
        loadCoursesData();
      })
      .catch(() => {
        localStorage.removeItem('academy_token');
        setAppState('unauthenticated');
      });
  }, []);

  const handleAuthSuccess = (u: User) => {
    setUser(u);
    setAppState('authenticated');
    loadDashboardData();
    loadCoursesData();
  };

  const handleLogout = () => {
    localStorage.removeItem('academy_token');
    setUser(null);
    setAppState('unauthenticated');
    // Reset all nav state
    setCurrentTab('dashboard');
    setSelectedCourseSlug(null);
    setSelectedLessonSlug(null);
    setActiveQuizId(null);
    setDashboard(null);
    setCourses([]);
  };

  const loadDashboardData = async () => {
    try {
      const data = await api.getDashboard();
      setDashboard(data);
    } catch (err) {
      console.error('Failed to load dashboard', err);
    }
  };

  const loadCoursesData = async () => {
    try {
      const data = await api.getCourses();
      setCourses(data);
    } catch (err) {
      console.error('Failed to load courses', err);
    }
  };

  const handleSelectTab = (tab: 'dashboard' | 'courses') => {
    setCurrentTab(tab);
    setSelectedCourseSlug(null);
    setSelectedLessonSlug(null);
    setActiveQuizId(null);
    if (tab === 'dashboard') {
      loadDashboardData();
      loadCoursesData();
    }
  };

  const handleSelectCourse = async (slug: string) => {
    setLoading(true);
    setSelectedCourseSlug(slug);
    setSelectedLessonSlug(null);
    setActiveQuizId(null);
    try {
      const detail = await api.getCourseDetail(slug);
      setCourseDetail(detail);
    } catch (err) {
      console.error('Failed to load course detail', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectLesson = async (courseSlug: string, lessonSlug: string) => {
    setLoading(true);
    setSelectedCourseSlug(courseSlug);
    setSelectedLessonSlug(lessonSlug);
    setActiveQuizId(null);
    try {
      const detail = await api.getLesson(courseSlug, lessonSlug);
      setLessonDetail(detail);
    } catch (err) {
      console.error('Failed to load lesson detail', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartQuiz = async (quizId: number) => {
    setLoading(true);
    setActiveQuizId(quizId);
    try {
      const detail = await api.getQuiz(quizId);
      setQuizDetail(detail);
    } catch (err) {
      console.error('Failed to load quiz detail', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToCourse = () => {
    if (selectedCourseSlug) {
      handleSelectCourse(selectedCourseSlug);
    } else {
      handleSelectTab('dashboard');
    }
  };

  // ── RENDER ─────────────────────────────────────────────────────────────────

  // Checking auth — show full-screen spinner
  if (appState === 'checking_auth') {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-3xl shadow-xl shadow-purple-500/30 animate-pulse">
          🎓
        </div>
        <div className="w-8 h-8 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
        <p className="text-xs text-slate-500">Loading Fluenora AI...</p>
      </div>
    );
  }

  // Not authenticated — show ONLY the login/register page
  if (appState === 'unauthenticated') {
    return <LoginPage onAuthSuccess={handleAuthSuccess} />;
  }

  // Authenticated — show the full application
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-purple-600 selection:text-white">
      <Navbar
        currentTab={currentTab}
        onSelectTab={handleSelectTab}
        user={user}
        onOpenAuth={() => {}}
        onLogout={handleLogout}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {loading ? (
          <div className="py-20 text-center space-y-3">
            <div className="w-8 h-8 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin mx-auto" />
            <p className="text-xs text-slate-400">Loading educational content...</p>
          </div>
        ) : activeQuizId && quizDetail ? (
          <QuizView
            quiz={quizDetail}
            onBackToCourse={handleBackToCourse}
            onQuizCompleted={() => {
              loadDashboardData();
              loadCoursesData();
            }}
          />
        ) : selectedLessonSlug && lessonDetail && selectedCourseSlug ? (
          <LessonView
            lesson={lessonDetail}
            courseSlug={selectedCourseSlug}
            onBackToCourse={handleBackToCourse}
            onNavigateLesson={(nextSlug) => handleSelectLesson(selectedCourseSlug, nextSlug)}
            onLessonCompleted={() => {
              loadDashboardData();
              loadCoursesData();
              if (selectedCourseSlug) {
                api.getCourseDetail(selectedCourseSlug).then(setCourseDetail);
              }
            }}
          />
        ) : selectedCourseSlug && courseDetail ? (
          <CourseDetailView
            course={courseDetail}
            onBack={() => {
              setSelectedCourseSlug(null);
              loadDashboardData();
              loadCoursesData();
            }}
            onSelectLesson={handleSelectLesson}
            onStartFinalQuiz={handleStartQuiz}
          />
        ) : (
          <DashboardView
            dashboard={dashboard}
            courses={courses}
            onSelectCourse={handleSelectCourse}
            onSelectLesson={handleSelectLesson}
            user={user}
            onOpenAuth={() => {}}
          />
        )}
      </main>

      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 bg-slate-900/40">
        <div className="max-w-7xl mx-auto px-4 space-y-1">
          <p className="font-semibold text-slate-400">English Learning Academy &mdash; Complete Grammar Learning Platform</p>
          <p className="text-[11px] text-slate-500">
            Comprehensive Grammar &amp; Language Mastery Platform
          </p>
        </div>
      </footer>
    </div>
  );
}
