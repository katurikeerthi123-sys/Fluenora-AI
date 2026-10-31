export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: string;
}

export interface CourseCardData {
  id: number;
  slug: string;
  title: string;
  category: string;
  difficulty: string;
  summary: string;
  icon: string;
  total_lessons: number;
  completed_lessons: number;
  progress_pct: number;
  status: 'not_started' | 'in_progress' | 'completed' | 'mastered';
}

export interface LessonSummaryData {
  id: number;
  slug: string;
  title: string;
  order_index: number;
  reading_time_mins: number;
  difficulty: string;
  is_completed: boolean;
}

export interface ModuleData {
  id: number;
  title: string;
  summary?: string;
  order_index: number;
  lessons: LessonSummaryData[];
}

export interface CourseDetailData extends CourseCardData {
  modules: ModuleData[];
  has_final_assessment: boolean;
  final_quiz_id?: number;
}

export interface ExerciseData {
  id: number;
  exercise_type: string;
  question_text: string;
  options: string[];
  explanation: string;
  difficulty: string;
}

export interface LessonDetailData {
  id: number;
  course_id: number;
  module_id: number;
  slug: string;
  title: string;
  order_index: number;
  reading_time_mins: number;
  difficulty: string;
  concept_summary: string;
  formula_structure?: string;
  rules: string[];
  positive_examples: string[];
  negative_examples: string[];
  question_examples: string[];
  common_mistakes: Array<{ wrong: string; right: string; explanation: string }>;
  content_markdown: string;
  is_completed: boolean;
  exercises: ExerciseData[];
  prev_lesson_slug?: string;
  next_lesson_slug?: string;
}

export interface QuizQuestionData {
  id: number;
  question_text: string;
  question_type: string;
  options: string[];
  points: number;
}

export interface QuizDetailData {
  id: number;
  course_id: number;
  title: string;
  description?: string;
  passing_score_pct: number;
  is_final_assessment: boolean;
  total_questions: number;
  questions: QuizQuestionData[];
}

export interface QuizQuestionResultData {
  question_id: number;
  question_text: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
}

export interface QuizResultData {
  attempt_id: number;
  quiz_id: number;
  title: string;
  score_pct: number;
  passed: boolean;
  total_questions: number;
  correct_count: number;
  results: QuizQuestionResultData[];
  recommendations: string[];
}

export interface DashboardData {
  overall_progress_pct: number;
  courses_in_progress: number;
  courses_completed: number;
  courses_mastered: number;
  total_quizzes_taken: number;
  average_quiz_score: number;
  weak_grammar_areas: Array<{ topic: string; category: string; mistakes_count: number }>;
  recent_lessons: Array<{
    lesson_title: string;
    course_title: string;
    course_slug: string;
    lesson_slug: string;
    completed_at: string;
  }>;
  continue_course?: CourseCardData;
}
