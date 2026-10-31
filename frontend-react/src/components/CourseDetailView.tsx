import React from 'react';
import { 
  ArrowLeft, 
  BookOpen, 
  CheckCircle2, 
  Circle, 
  Award, 
  Clock, 
  Play, 
  ChevronRight,
  ShieldCheck
} from 'lucide-react';
import { CourseDetailData } from '../types/academy';

interface CourseDetailViewProps {
  course: CourseDetailData;
  onBack: () => void;
  onSelectLesson: (courseSlug: string, lessonSlug: string) => void;
  onStartFinalQuiz: (quizId: number) => void;
}

export const CourseDetailView: React.FC<CourseDetailViewProps> = ({
  course,
  onBack,
  onSelectLesson,
  onStartFinalQuiz,
}) => {
  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Breadcrumb & Back */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Course Catalog</span>
      </button>

      {/* Course Overview Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="relative z-10 space-y-4 max-w-4xl">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs px-3 py-1 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 font-medium">
              {course.category}
            </span>
            <span className="text-xs px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700/60 font-medium">
              Difficulty: {course.difficulty}
            </span>
            {course.status === 'mastered' && (
              <span className="text-xs px-3 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-bold inline-flex items-center gap-1">
                <Award className="w-3.5 h-3.5" /> Course Mastered
              </span>
            )}
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {course.title}
          </h1>

          <p className="text-sm text-slate-300 leading-relaxed">
            {course.summary}
          </p>

          {/* Progress Overview */}
          <div className="pt-2 max-w-md space-y-2">
            <div className="flex justify-between text-xs text-slate-400">
              <span>{course.completed_lessons} of {course.total_lessons} lessons completed</span>
              <span className="font-semibold text-purple-300">{course.progress_pct}%</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all duration-500"
                style={{ width: `${course.progress_pct}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Syllabus Modules & Lessons */}
      <div className="space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-purple-400" />
            <span>Course Syllabus &amp; Modules</span>
          </h2>
          <span className="text-xs text-slate-400">{course.modules.length} Modules &bull; {course.total_lessons} Lessons</span>
        </div>

        <div className="space-y-6">
          {course.modules.map((mod, modIdx) => (
            <div
              key={mod.id}
              className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4"
            >
              <div>
                <h3 className="text-base font-bold text-slate-100">
                  {mod.title}
                </h3>
                {mod.summary && (
                  <p className="text-xs text-slate-400 mt-1">{mod.summary}</p>
                )}
              </div>

              {/* Lesson Items */}
              <div className="grid grid-cols-1 gap-2.5">
                {mod.lessons.map((lesson) => (
                  <div
                    key={lesson.id}
                    onClick={() => onSelectLesson(course.slug, lesson.slug)}
                    className="p-4 rounded-xl bg-slate-950/70 hover:bg-slate-800/80 border border-slate-800/80 hover:border-purple-500/40 cursor-pointer transition flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3.5">
                      {lesson.is_completed ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                      ) : (
                        <Circle className="w-5 h-5 text-slate-600 flex-shrink-0 group-hover:text-purple-400 transition" />
                      )}

                      <div>
                        <div className="text-sm font-semibold text-slate-200 group-hover:text-purple-300 transition">
                          {lesson.title}
                        </div>
                        <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-0.5">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" /> {lesson.reading_time_mins} mins read
                          </span>
                          <span>&bull;</span>
                          <span>Level: {lesson.difficulty}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-slate-400 group-hover:text-purple-300 font-medium transition">
                      <span>{lesson.is_completed ? 'Review' : 'Start'}</span>
                      <ChevronRight className="w-4 h-4 transform group-hover:translate-x-0.5 transition" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comprehensive Final Assessment Card */}
      {course.has_final_assessment && course.final_quiz_id && (
        <div className="bg-gradient-to-r from-amber-950/30 via-slate-900 to-slate-900 border border-amber-800/40 rounded-3xl p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 shadow-xl">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 text-xs font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Comprehensive Final Assessment</span>
            </div>
            <h3 className="text-lg font-bold text-white">
              Course Mastery Certification Exam
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Test your understanding across all concepts and edge cases taught in this course. Passing with <strong>80% or higher</strong> marks the course as <strong>Mastered</strong> in your student transcript.
            </p>
          </div>

          <button
            onClick={() => onStartFinalQuiz(course.final_quiz_id!)}
            className="flex-shrink-0 inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-600/20 transition transform hover:-translate-y-0.5"
          >
            <Play className="w-4 h-4 fill-slate-950" />
            <span>Take Final Assessment</span>
          </button>
        </div>
      )}
    </div>
  );
};
