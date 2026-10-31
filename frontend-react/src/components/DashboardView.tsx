import React, { useState } from 'react';
import { 
  BookOpen, 
  CheckCircle2, 
  Award, 
  Clock, 
  Search, 
  AlertTriangle, 
  Play, 
  ArrowRight,
  TrendingUp,
  Filter
} from 'lucide-react';
import { DashboardData, CourseCardData } from '../types/academy';

interface DashboardViewProps {
  dashboard: DashboardData | null;
  courses: CourseCardData[];
  onSelectCourse: (slug: string) => void;
  onSelectLesson: (courseSlug: string, lessonSlug: string) => void;
  user: any;
  onOpenAuth: () => void;
}

const CATEGORIES = ['All', 'Tenses', 'Syntax', 'Mechanics', 'Vocabulary & Usage', 'Examination & Advanced'];
const DIFFICULTIES = ['All', 'Beginner', 'Intermediate', 'Advanced'];

export const DashboardView: React.FC<DashboardViewProps> = ({
  dashboard,
  courses,
  onSelectCourse,
  onSelectLesson,
  user,
  onOpenAuth,
}) => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCourses = courses.filter((c) => {
    const matchesCat = selectedCategory === 'All' || c.category === selectedCategory;
    const matchesDiff = selectedDifficulty === 'All' || c.difficulty === selectedDifficulty || c.difficulty === 'All Levels';
    const matchesSearch =
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.summary.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesDiff && matchesSearch;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-purple-950/40 to-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-medium">
            <span>✨</span>
            <span>Independent Self-Paced English Mastery</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Welcome back, {user ? (user.full_name || user.username) : 'Learner'}! 👋
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Select any grammar topic to learn independently from beginner to advanced level. Every course contains full instructional lessons, sentence formulas, contrast examples, interactive quizzes, and comprehensive assessments.
          </p>

          {/* Quick Continue Learning Banner */}
          {dashboard?.continue_course ? (
            <div className="pt-2">
              <button
                onClick={() => onSelectCourse(dashboard.continue_course!.slug)}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/30 transition transform hover:-translate-y-0.5"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Continue Learning: {dashboard.continue_course.title}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : !user ? (
            <div className="pt-2">
              <button
                onClick={onOpenAuth}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg transition"
              >
                <span>Sign in to Track Your Mastery</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : null}
        </div>

        {/* Decorative background glow */}
        <div className="absolute right-0 top-0 -mt-10 -mr-10 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Progress & Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Overall Progress</span>
            <TrendingUp className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">{dashboard?.overall_progress_pct || 0}%</div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full"
              style={{ width: `${dashboard?.overall_progress_pct || 0}%` }}
            />
          </div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">In Progress</span>
            <Clock className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white">{dashboard?.courses_in_progress || 0}</div>
          <p className="text-[11px] text-slate-400">Active courses</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Completed</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">{dashboard?.courses_completed || 0}</div>
          <p className="text-[11px] text-slate-400">Lessons finished</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Mastered Courses</span>
            <Award className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-300">{dashboard?.courses_mastered || 0}</div>
          <p className="text-[11px] text-slate-400">&gt;80% on Final Tests</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2 col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Quiz Average</span>
            <span className="text-xs font-bold text-indigo-400">{dashboard?.total_quizzes_taken || 0} tests</span>
          </div>
          <div className="text-2xl font-bold text-white">{dashboard?.average_quiz_score || 0}%</div>
          <p className="text-[11px] text-slate-400">Overall score</p>
        </div>
      </div>

      {/* Weak Areas Alert (if any detected) */}
      {dashboard?.weak_grammar_areas && dashboard.weak_grammar_areas.length > 0 && (
        <div className="bg-amber-950/20 border border-amber-800/40 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 mt-0.5">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-amber-200">Recommended Grammar Focus Areas</h3>
              <p className="text-xs text-amber-300/80 mt-0.5">
                Our diagnostic engine identified recurring difficulties in these topics. Review lessons to reinforce your mastery:
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {dashboard.weak_grammar_areas.map((w, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] px-2.5 py-1 rounded-md bg-amber-900/40 border border-amber-700/50 text-amber-200 font-mono"
                  >
                    {w.category} ({w.mistakes_count} errors)
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Course Search and Filters */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white">Complete Grammar Course Catalog</h2>
            <p className="text-xs text-slate-400">Explore comprehensive courses in any order you choose.</p>
          </div>

          {/* Search Input */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search grammar topics..."
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800/60">
          <span className="text-xs text-slate-500 font-medium mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Categories:
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`text-xs px-3 py-1.5 rounded-lg font-medium transition ${
                selectedCategory === cat
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Course Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCourses.map((course) => (
          <div
            key={course.id}
            className="group bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-purple-500/50 rounded-2xl p-6 shadow-xl hover:shadow-purple-500/5 transition-all duration-300 flex flex-col justify-between"
          >
            <div className="space-y-4">
              {/* Category & Status Row */}
              <div className="flex items-center justify-between">
                <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700/60 font-medium">
                  {course.category}
                </span>

                {course.status === 'mastered' ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                    <Award className="w-3 h-3" /> Mastered
                  </span>
                ) : course.status === 'completed' ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    <CheckCircle2 className="w-3 h-3" /> Completed
                  </span>
                ) : course.status === 'in_progress' ? (
                  <span className="text-[11px] font-medium text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded-full border border-sky-500/20">
                    In Progress
                  </span>
                ) : (
                  <span className="text-[11px] text-slate-500">Not Started</span>
                )}
              </div>

              {/* Title & Summary */}
              <div>
                <h3 className="text-base font-bold text-white group-hover:text-purple-300 transition">
                  {course.title}
                </h3>
                <p className="text-xs text-slate-400 mt-2 line-clamp-3 leading-relaxed">
                  {course.summary}
                </p>
              </div>

              {/* Progress Bar */}
              <div className="space-y-1.5 pt-2">
                <div className="flex justify-between text-[11px] text-slate-400">
                  <span>{course.completed_lessons} of {course.total_lessons} lessons completed</span>
                  <span className="font-semibold text-slate-300">{course.progress_pct}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all duration-500"
                    style={{ width: `${course.progress_pct}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Action Button */}
            <div className="pt-6 border-t border-slate-800/80 mt-6 flex items-center justify-between">
              <span className="text-xs text-slate-500 font-medium">Difficulty: {course.difficulty}</span>

              <button
                onClick={() => onSelectCourse(course.slug)}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600/20 hover:bg-purple-600 text-purple-300 hover:text-white border border-purple-500/30 text-xs font-semibold transition"
              >
                <span>{course.progress_pct > 0 ? 'Continue' : 'Start Course'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}

        {filteredCourses.length === 0 && (
          <div className="col-span-full py-12 text-center text-slate-500">
            <BookOpen className="w-10 h-10 mx-auto text-slate-600 mb-2" />
            <p className="text-sm font-medium">No grammar courses match your current filters.</p>
            <button
              onClick={() => { setSelectedCategory('All'); setSelectedDifficulty('All'); setSearchQuery(''); }}
              className="mt-3 text-xs text-purple-400 hover:text-purple-300 underline"
            >
              Reset all filters
            </button>
          </div>
        )}
      </div>

      {/* Recently Studied Lessons */}
      {dashboard?.recent_lessons && dashboard.recent_lessons.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-purple-400" />
            <span>Recently Studied Lessons</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {dashboard.recent_lessons.map((rec, idx) => (
              <div
                key={idx}
                onClick={() => onSelectLesson(rec.course_slug, rec.lesson_slug)}
                className="p-3.5 rounded-xl bg-slate-950/80 hover:bg-slate-800/60 border border-slate-800/80 cursor-pointer transition flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-purple-300 transition">
                    {rec.lesson_title}
                  </div>
                  <div className="text-[11px] text-slate-500">{rec.course_title}</div>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-purple-400 transition transform group-hover:translate-x-0.5" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
