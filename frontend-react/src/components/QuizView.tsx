import React, { useState } from 'react';
import { 
  ArrowLeft, 
  CheckCircle2, 
  XCircle, 
  Award, 
  RotateCcw, 
  AlertCircle,
  HelpCircle,
  Send,
  BookOpen
} from 'lucide-react';
import { QuizDetailData, QuizResultData } from '../types/academy';
import { api } from '../services/api';

interface QuizViewProps {
  quiz: QuizDetailData;
  onBackToCourse: () => void;
  onQuizCompleted: () => void;
}

export const QuizView: React.FC<QuizViewProps> = ({
  quiz,
  onBackToCourse,
  onQuizCompleted,
}) => {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [quizResult, setQuizResult] = useState<QuizResultData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelectOption = (questionId: number, option: string) => {
    if (quizResult) return; // Locked once submitted
    setSelectedAnswers(prev => ({ ...prev, [questionId]: option }));
  };

  const handleSubmit = async () => {
    const answeredCount = Object.keys(selectedAnswers).length;
    if (answeredCount < quiz.questions.length) {
      if (!confirm(`You have answered ${answeredCount} of ${quiz.questions.length} questions. Submit anyway?`)) {
        return;
      }
    }

    setIsSubmitting(true);
    setError(null);

    const formattedAnswers = quiz.questions.map(q => ({
      question_id: q.id,
      selected_answer: selectedAnswers[q.id] || '',
    }));

    try {
      const res = await api.submitQuiz(quiz.id, formattedAnswers);
      setQuizResult(res);
      onQuizCompleted();
    } catch (err: any) {
      setError(err.message || 'Failed to grade assessment.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = () => {
    setSelectedAnswers({});
    setQuizResult(null);
    setError(null);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Top Breadcrumb */}
      <button
        onClick={onBackToCourse}
        className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Course</span>
      </button>

      {/* Assessment Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="text-xs px-3 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-bold uppercase tracking-wider">
            {quiz.is_final_assessment ? 'Comprehensive Final Assessment' : 'Lesson Quiz'}
          </span>
          <span className="text-xs text-slate-400">
            Passing Threshold: <strong>{quiz.passing_score_pct}%</strong>
          </span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
          {quiz.title}
        </h1>
        {quiz.description && (
          <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">{quiz.description}</p>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results Banner (If Submitted) */}
      {quizResult && (
        <div
          className={`border rounded-3xl p-6 sm:p-8 space-y-4 animate-in fade-in duration-300 ${
            quizResult.passed
              ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-200'
              : 'bg-amber-950/20 border-amber-800/40 text-amber-200'
          }`}
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div
                className={`w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shadow-lg ${
                  quizResult.passed
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}
              >
                {quizResult.passed ? '🏆' : '📚'}
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">
                  {quizResult.passed ? 'Assessment Passed with Honors!' : 'Assessment Not Yet Passed'}
                </h2>
                <p className="text-xs text-slate-300 mt-0.5">
                  You scored <strong>{quizResult.score_pct}%</strong> ({quizResult.correct_count} of {quizResult.total_questions} correct).
                </p>
              </div>
            </div>

            <button
              onClick={handleRetake}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retake Assessment</span>
            </button>
          </div>

          {/* Recommendations */}
          {quizResult.recommendations.length > 0 && (
            <div className="pt-3 border-t border-slate-800/80 text-xs text-slate-300 space-y-1">
              <span className="font-semibold text-white">Educational Guidance:</span>
              <ul className="list-disc list-inside space-y-1 text-slate-400">
                {quizResult.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Questions List */}
      <div className="space-y-6">
        {quiz.questions.map((q, idx) => {
          const resultDetail = quizResult?.results.find(r => r.question_id === q.id);
          const isAnswered = selectedAnswers[q.id] !== undefined;

          return (
            <div
              key={q.id}
              className={`bg-slate-900/60 border rounded-2xl p-6 space-y-4 transition ${
                resultDetail
                  ? resultDetail.is_correct
                    ? 'border-emerald-800/60 bg-emerald-950/10'
                    : 'border-red-800/60 bg-red-950/10'
                  : 'border-slate-800'
              }`}
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono text-purple-400 font-bold">Question {idx + 1} of {quiz.questions.length}</span>
                {resultDetail && (
                  <span
                    className={`font-semibold inline-flex items-center gap-1 ${
                      resultDetail.is_correct ? 'text-emerald-400' : 'text-red-400'
                    }`}
                  >
                    {resultDetail.is_correct ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : (
                      <XCircle className="w-4 h-4" />
                    )}
                    <span>{resultDetail.is_correct ? 'Correct' : 'Incorrect'}</span>
                  </span>
                )}
              </div>

              <h3 className="text-sm font-semibold text-slate-100 leading-relaxed">
                {q.question_text}
              </h3>

              {/* Options */}
              <div className="grid grid-cols-1 gap-2.5 pt-1">
                {q.options.map((opt, optIdx) => {
                  const isSelected = selectedAnswers[q.id] === opt;
                  const isCorrectChoice = resultDetail && resultDetail.correct_answer === opt;
                  const isWrongChoice = resultDetail && isSelected && !resultDetail.is_correct;

                  return (
                    <button
                      key={optIdx}
                      disabled={quizResult !== null}
                      onClick={() => handleSelectOption(q.id, opt)}
                      className={`p-3.5 rounded-xl text-xs text-left font-medium border transition flex items-center justify-between ${
                        isCorrectChoice
                          ? 'bg-emerald-950/40 border-emerald-500 text-emerald-200'
                          : isWrongChoice
                          ? 'bg-red-950/40 border-red-500 text-red-200'
                          : isSelected
                          ? 'bg-purple-600/25 border-purple-500 text-purple-200'
                          : 'bg-slate-950/80 border-slate-800/80 text-slate-300 hover:bg-slate-800/60'
                      }`}
                    >
                      <span>{opt}</span>
                      {isCorrectChoice && <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
                      {isWrongChoice && <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />}
                    </button>
                  );
                })}
              </div>

              {/* Question Explanation (After Submission) */}
              {resultDetail && (
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                  <div className="font-semibold text-purple-300">Explanation &amp; Rule:</div>
                  <p className="text-slate-300 leading-relaxed">{resultDetail.explanation}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Submission Footer */}
      {!quizResult && (
        <div className="flex items-center justify-between border-t border-slate-800 pt-6">
          <span className="text-xs text-slate-400">
            {Object.keys(selectedAnswers).length} of {quiz.questions.length} questions answered
          </span>

          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-purple-500/20 disabled:opacity-50 transition"
          >
            <Send className="w-4 h-4" />
            <span>{isSubmitting ? 'Grading Assessment...' : 'Submit Assessment for Grading'}</span>
          </button>
        </div>
      )}
    </div>
  );
};
