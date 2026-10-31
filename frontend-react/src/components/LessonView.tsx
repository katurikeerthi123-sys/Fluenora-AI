import React, { useState } from 'react';
import { 
  ArrowLeft, 
  ArrowRight, 
  CheckCircle2, 
  Circle, 
  Clock, 
  Check, 
  X, 
  RotateCcw, 
  HelpCircle,
  AlertOctagon,
  Sparkles
} from 'lucide-react';
import { LessonDetailData } from '../types/academy';
import { api } from '../services/api';

interface LessonViewProps {
  lesson: LessonDetailData;
  courseSlug: string;
  onBackToCourse: () => void;
  onNavigateLesson: (lessonSlug: string) => void;
  onLessonCompleted: (lessonId: number) => void;
}

export const LessonView: React.FC<LessonViewProps> = ({
  lesson,
  courseSlug,
  onBackToCourse,
  onNavigateLesson,
  onLessonCompleted,
}) => {
  const [activeTab, setActiveTab] = useState<'content' | 'rules' | 'examples' | 'mistakes' | 'exercises'>('content');
  const [isCompleted, setIsCompleted] = useState(lesson.is_completed);
  const [markingComplete, setMarkingComplete] = useState(false);

  // Interactive exercise state
  const [exerciseAnswers, setExerciseAnswers] = useState<Record<number, string>>({});
  const [exerciseResults, setExerciseResults] = useState<Record<number, { is_correct: boolean; explanation: string; correct_answer: string }>>({});
  const [checkingExercise, setCheckingExercise] = useState<number | null>(null);

  const handleMarkComplete = async () => {
    setMarkingComplete(true);
    try {
      await api.markLessonComplete(lesson.id);
      setIsCompleted(true);
      onLessonCompleted(lesson.id);
    } catch (err) {
      console.error('Failed to mark complete', err);
    } finally {
      setMarkingComplete(false);
    }
  };

  const handleCheckExercise = async (exId: number) => {
    const ans = exerciseAnswers[exId];
    if (!ans) {
      alert('Please select or type an answer before checking.');
      return;
    }

    setCheckingExercise(exId);
    try {
      const res = await api.checkExercise(exId, ans);
      setExerciseResults(prev => ({
        ...prev,
        [exId]: {
          is_correct: res.is_correct,
          explanation: res.explanation,
          correct_answer: res.correct_answer,
        }
      }));
    } catch (err) {
      console.error('Check error', err);
    } finally {
      setCheckingExercise(null);
    }
  };

  const handleRetryExercise = (exId: number) => {
    setExerciseAnswers(prev => ({ ...prev, [exId]: '' }));
    setExerciseResults(prev => {
      const copy = { ...prev };
      delete copy[exId];
      return copy;
    });
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Header & Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <button
          onClick={onBackToCourse}
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Course Outline</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={handleMarkComplete}
            disabled={markingComplete || isCompleted}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition ${
              isCompleted
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
            }`}
          >
            {isCompleted ? <Check className="w-3.5 h-3.5" /> : <Circle className="w-3.5 h-3.5" />}
            <span>{isCompleted ? 'Completed' : 'Mark as Complete'}</span>
          </button>

          {lesson.next_lesson_slug && (
            <button
              onClick={() => onNavigateLesson(lesson.next_lesson_slug!)}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow transition"
            >
              <span>Next Lesson</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Lesson Title & Summary Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
          <span className="px-2.5 py-0.5 rounded-md bg-purple-500/10 text-purple-300 border border-purple-500/20 font-medium">
            Lesson {lesson.order_index}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" /> {lesson.reading_time_mins} mins
          </span>
          <span>&bull;</span>
          <span>Difficulty: {lesson.difficulty}</span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
          {lesson.title}
        </h1>

        <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
          <strong>Key Concept:</strong> {lesson.concept_summary}
        </p>

        {lesson.formula_structure && (
          <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-800/30 space-y-1 font-mono text-xs text-purple-200">
            <div className="text-[10px] uppercase tracking-wider text-purple-400 font-bold font-sans">
              Sentence Formula &amp; Structure
            </div>
            <div>{lesson.formula_structure}</div>
          </div>
        )}
      </div>

      {/* Structured Content Tabs */}
      <div className="space-y-6">
        <div className="flex border-b border-slate-800 overflow-x-auto gap-2">
          {[
            { id: 'content', label: 'In-Depth Theory' },
            { id: 'rules', label: `Grammar Rules (${lesson.rules.length})` },
            { id: 'examples', label: 'Sentence Examples' },
            { id: 'mistakes', label: `Common Mistakes (${lesson.common_mistakes.length})` },
            { id: 'exercises', label: `Interactive Practice (${lesson.exercises.length})` },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-3 text-xs font-semibold whitespace-nowrap border-b-2 transition ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-300 bg-slate-900/40 rounded-t-lg'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: IN-DEPTH THEORY */}
        {activeTab === 'content' && (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 text-slate-200 leading-relaxed text-sm">
            <div className="prose prose-invert max-w-none space-y-4">
              <div dangerouslySetInnerHTML={{ __html: lesson.content_markdown.replace(/\n/g, '<br/>') }} />
            </div>
          </div>
        )}

        {/* TAB 2: GRAMMAR RULES */}
        {activeTab === 'rules' && (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-purple-400" />
              <span>Core Grammatical Rules</span>
            </h3>
            <div className="grid grid-cols-1 gap-3">
              {lesson.rules.map((rule, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 flex items-start gap-3.5"
                >
                  <span className="w-6 h-6 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center text-xs font-bold flex-shrink-0">
                    {idx + 1}
                  </span>
                  <p className="text-xs text-slate-200 leading-relaxed pt-0.5">{rule}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: EXAMPLES */}
        {activeTab === 'examples' && (
          <div className="space-y-6">
            {lesson.positive_examples.length > 0 && (
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
                <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  Positive (Affirmative) Sentences
                </h3>
                <div className="space-y-2">
                  {lesson.positive_examples.map((ex, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/30 text-xs text-emerald-200 font-medium">
                      &bull; {ex}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {lesson.negative_examples.length > 0 && (
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
                <h3 className="text-xs font-bold text-red-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-red-400" />
                  Negative Sentences
                </h3>
                <div className="space-y-2">
                  {lesson.negative_examples.map((ex, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-red-950/20 border border-red-800/30 text-xs text-red-200 font-medium">
                      &bull; {ex}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {lesson.question_examples.length > 0 && (
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
                <h3 className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-sky-400" />
                  Question (Interrogative) Sentences
                </h3>
                <div className="space-y-2">
                  {lesson.question_examples.map((ex, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-sky-950/20 border border-sky-800/30 text-xs text-sky-200 font-medium">
                      &bull; {ex}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: COMMON MISTAKES */}
        {activeTab === 'mistakes' && (
          <div className="space-y-4">
            {lesson.common_mistakes.map((m, idx) => (
              <div
                key={idx}
                className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3"
              >
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-800/40 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-red-400">❌ Incorrect (Common Mistake)</span>
                    <p className="text-xs text-red-200 font-medium line-through">{m.wrong}</p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-800/40 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-emerald-400">✅ Correct Usage</span>
                    <p className="text-xs text-emerald-200 font-medium">{m.right}</p>
                  </div>
                </div>
                <div className="text-xs text-slate-300 bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
                  <span className="font-semibold text-purple-300">Why? </span>
                  {m.explanation}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* TAB 5: INTERACTIVE PRACTICE EXERCISES */}
        {activeTab === 'exercises' && (
          <div className="space-y-6">
            {lesson.exercises.map((ex, idx) => {
              const result = exerciseResults[ex.id];
              return (
                <div
                  key={ex.id}
                  className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      Exercise {idx + 1} ({ex.exercise_type.replace('_', ' ').toUpperCase()})
                    </span>
                    <span className="text-xs text-slate-500">Difficulty: {ex.difficulty}</span>
                  </div>

                  <h4 className="text-sm font-semibold text-slate-100">
                    {ex.question_text}
                  </h4>

                  {/* Options */}
                  {ex.options && ex.options.length > 0 && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                      {ex.options.map((opt, optIdx) => (
                        <button
                          key={optIdx}
                          disabled={result !== undefined}
                          onClick={() => setExerciseAnswers(prev => ({ ...prev, [ex.id]: opt }))}
                          className={`p-3 rounded-xl text-xs text-left font-medium border transition ${
                            exerciseAnswers[ex.id] === opt
                              ? 'bg-purple-600/20 border-purple-500 text-purple-200'
                              : 'bg-slate-950/80 border-slate-800 text-slate-300 hover:bg-slate-800/60'
                          }`}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-3 pt-2">
                    {!result ? (
                      <button
                        onClick={() => handleCheckExercise(ex.id)}
                        disabled={checkingExercise === ex.id || !exerciseAnswers[ex.id]}
                        className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-xs font-semibold shadow transition"
                      >
                        {checkingExercise === ex.id ? 'Checking...' : 'Check Answer ✨'}
                      </button>
                    ) : (
                      <button
                        onClick={() => handleRetryExercise(ex.id)}
                        className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span>Retry Question</span>
                      </button>
                    )}
                  </div>

                  {/* Result & Explanation */}
                  {result && (
                    <div
                      className={`p-4 rounded-xl text-xs space-y-1.5 border animate-in fade-in duration-200 ${
                        result.is_correct
                          ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-200'
                          : 'bg-red-950/20 border-red-800/40 text-red-200'
                      }`}
                    >
                      <div className="flex items-center gap-2 font-bold text-sm">
                        {result.is_correct ? (
                          <>
                            <Check className="w-4 h-4 text-emerald-400" />
                            <span>Correct Answer! 🎉</span>
                          </>
                        ) : (
                          <>
                            <X className="w-4 h-4 text-red-400" />
                            <span>Incorrect. Correct answer: "{result.correct_answer}"</span>
                          </>
                        )}
                      </div>
                      <p className="text-slate-300 leading-relaxed pt-1">
                        <strong>Explanation:</strong> {result.explanation}
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Bottom Navigation Footer */}
      <div className="flex items-center justify-between border-t border-slate-800 pt-6">
        {lesson.prev_lesson_slug ? (
          <button
            onClick={() => onNavigateLesson(lesson.prev_lesson_slug!)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous Lesson</span>
          </button>
        ) : <div />}

        {lesson.next_lesson_slug ? (
          <button
            onClick={() => onNavigateLesson(lesson.next_lesson_slug!)}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow transition"
          >
            <span>Next Lesson</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={onBackToCourse}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow transition"
          >
            <span>Finish Course Review</span>
            <Check className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
