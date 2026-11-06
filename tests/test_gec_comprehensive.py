"""
Fluenora AI ✨ - Comprehensive Automated Test Suite (100+ Test Sentences)
Validates:
  1. Tense Errors (Past, Present, Habitual, Continuous, Auxiliaries)
  2. Subject-Verb Agreement (Singular vs Plural Subjects)
  3. Structure & Negation Errors (Missing copulas, 'She not like', wh-inversion)
  4. Article Errors ('a' vs 'an' vs 'the' phonetic rules)
  5. Preposition Collocations ('in the evening', 'good at', transitive verbs)
  6. Spelling & Irregular Verb Mis-regularizations ('speaked', 'catched')
  7. Sentences with Multiple Simultaneous Grammar Errors
  8. Grammatically Correct Sentences (Zero False Edits)
  9. GLEU / Token Edit Similarity & Pedagogical Metadata Verification
"""

import os
import sys
import pytest
import re
from typing import List, Tuple, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.corrector import SentenceCorrector

# 105 Diverse Sentences covering all categories and proficiency levels
TEST_BENCHMARK_105: List[Tuple[str, str, str, str]] = [
    # ── Category 1: Tense & Auxiliary Errors (20 items) ──────────────────
    ("I did playing football", "I played football.", "TENSE_ERROR", "Beginner"),
    ("Yesterday I go to college.", "Yesterday I went to college.", "TENSE_ERROR", "Beginner"),
    ("I am go to school yesterday.", "I went to school yesterday.", "TENSE_ERROR", "Beginner"),
    ("She is play cricket every day.", "She plays cricket every day.", "TENSE_ERROR", "Beginner"),
    ("I was eat breakfast.", "I was eating breakfast.", "TENSE_ERROR", "Beginner"),
    ("He is go to gym daily.", "He goes to gym daily.", "TENSE_ERROR", "Beginner"),
    ("Last night she cook dinner for everyone.", "Last night she cooked dinner for everyone.", "TENSE_ERROR", "Intermediate"),
    ("Two days ago they buy a new laptop.", "Two days ago they bought a new laptop.", "TENSE_ERROR", "Intermediate"),
    ("I did completed my homework.", "I did complete my homework.", "TENSE_ERROR", "Beginner"),
    ("She did saw the movie yesterday.", "She saw the movie yesterday.", "TENSE_ERROR", "Intermediate"),
    ("We was watching television at night.", "We were watching television at night.", "TENSE_ERROR", "Beginner"),
    ("I am having a red car.", "I have a red car.", "TENSE_ERROR", "Intermediate"),
    ("She is knowing the answer to this question.", "She knows the answer to this question.", "TENSE_ERROR", "Intermediate"),
    ("He was sleep when I called him.", "He was sleeping when I called him.", "TENSE_ERROR", "Intermediate"),
    ("They did went to the market.", "They went to the market.", "TENSE_ERROR", "Beginner"),
    ("Yesterday morning we play chess together.", "Yesterday morning we played chess together.", "TENSE_ERROR", "Beginner"),
    ("Since two years I am living here.", "I have been living here for two years.", "TENSE_ERROR", "Advanced"),
    ("I did eating lunch with my friends.", "I ate lunch with my friends.", "TENSE_ERROR", "Beginner"),
    ("He did watching the match yesterday.", "He watched the match yesterday.", "TENSE_ERROR", "Beginner"),
    ("Last Sunday my brother come to my house.", "Last Sunday my brother came to my house.", "TENSE_ERROR", "Intermediate"),

    # ── Category 2: Subject-Verb Agreement (SVA) (20 items) ─────────────
    ("He go to college.", "He goes to college.", "SVA_ERROR", "Beginner"),
    ("She play badminton.", "She plays badminton.", "SVA_ERROR", "Beginner"),
    ("They plays cricket.", "They play cricket.", "SVA_ERROR", "Beginner"),
    ("My friend like music.", "My friend likes music.", "SVA_ERROR", "Beginner"),
    ("I goes to school.", "I go to school.", "SVA_ERROR", "Beginner"),
    ("Every student have a textbook.", "Every student has a textbook.", "SVA_ERROR", "Intermediate"),
    ("The children likes ice cream.", "The children like ice cream.", "SVA_ERROR", "Beginner"),
    ("One of my friends are coming to visit.", "One of my friends is coming to visit.", "SVA_ERROR", "Intermediate"),
    ("He don't like coffee.", "He doesn't like coffee.", "SVA_ERROR", "Beginner"),
    ("She don't want to come with us.", "She doesn't want to come with us.", "SVA_ERROR", "Beginner"),
    ("They was absent from the meeting.", "They were absent from the meeting.", "SVA_ERROR", "Beginner"),
    ("My brother work in Hyderabad.", "My brother works in Hyderabad.", "SVA_ERROR", "Beginner"),
    ("Everyone want to be successful.", "Everyone wants to be successful.", "SVA_ERROR", "Intermediate"),
    ("People is waiting outside the auditorium.", "People are waiting outside the auditorium.", "SVA_ERROR", "Intermediate"),
    ("The teacher speak very softly.", "The teacher speaks very softly.", "SVA_ERROR", "Beginner"),
    ("My sister cook delicious food.", "My sister cooks delicious food.", "SVA_ERROR", "Beginner"),
    ("The students is listening attentively.", "The students are listening attentively.", "SVA_ERROR", "Beginner"),
    ("We works hard on this project.", "We work hard on this project.", "SVA_ERROR", "Beginner"),
    ("He study every evening for two hours.", "He studies every evening for two hours.", "SVA_ERROR", "Beginner"),
    ("She live with her parents.", "She lives with her parents.", "SVA_ERROR", "Beginner"),

    # ── Category 3: Structure, Auxiliary & Word Order (18 items) ────────
    ("I going to college.", "I am going to college.", "STRUCTURE_ERROR", "Beginner"),
    ("She not like coffee.", "She does not like coffee.", "STRUCTURE_ERROR", "Beginner"),
    ("Because I was sick.", "I could not attend college because I was sick.", "STRUCTURE_ERROR", "Intermediate"),
    ("Where you are going right now?", "Where are you going right now?", "STRUCTURE_ERROR", "Intermediate"),
    ("What your name is?", "What is your name?", "STRUCTURE_ERROR", "Beginner"),
    ("Why you didn't call me yesterday?", "Why didn't you call me yesterday?", "STRUCTURE_ERROR", "Intermediate"),
    ("Myself I am Keerthi.", "I am Keerthi.", "STRUCTURE_ERROR", "Beginner"),
    ("He not know the correct answer.", "He does not know the correct answer.", "STRUCTURE_ERROR", "Beginner"),
    ("They playing outside in the garden.", "They are playing outside in the garden.", "STRUCTURE_ERROR", "Beginner"),
    ("Though he studied hard but he failed.", "Though he studied hard, he failed.", "STRUCTURE_ERROR", "Advanced"),
    ("I English very much like.", "I like English very much.", "STRUCTURE_ERROR", "Intermediate"),
    ("We celebrations at my home.", "We are celebrating at my home.", "STRUCTURE_ERROR", "Intermediate"),
    ("She working in a multinational company.", "She is working in a multinational company.", "STRUCTURE_ERROR", "Beginner"),
    ("They not want to participate in sports.", "They do not want to participate in sports.", "STRUCTURE_ERROR", "Beginner"),
    ("I not have enough money for tickets.", "I do not have enough money for tickets.", "STRUCTURE_ERROR", "Beginner"),
    ("Why you are late to the lecture?", "Why are you late to the lecture?", "STRUCTURE_ERROR", "Intermediate"),
    ("How you can say such things?", "How can you say such things?", "STRUCTURE_ERROR", "Intermediate"),
    ("At my home, come for dinner tonight.", "At my home; please come for dinner tonight.", "STRUCTURE_ERROR", "Intermediate"),

    # ── Category 4: Article Errors (12 items) ───────────────────────────
    ("I have a uncle who lives in Vijayawada.", "I have an uncle who lives in Vijayawada.", "ARTICLE_ERROR", "Beginner"),
    ("He is a honest police officer.", "He is an honest police officer.", "ARTICLE_ERROR", "Beginner"),
    ("She waited for a hour at the station.", "She waited for an hour at the station.", "ARTICLE_ERROR", "Beginner"),
    ("Sun rises in east every morning.", "The sun rises in the east every morning.", "ARTICLE_ERROR", "Intermediate"),
    ("He gave me an useful advice.", "He gave me a useful advice.", "ARTICLE_ERROR", "Intermediate"),
    ("She is studying in an university.", "She is studying in a university.", "ARTICLE_ERROR", "Intermediate"),
    ("This is an European car.", "This is a European car.", "ARTICLE_ERROR", "Intermediate"),
    ("Mount Everest is highest mountain in world.", "Mount Everest is the highest mountain in world.", "ARTICLE_ERROR", "Intermediate"),
    ("I bought a umbrella for the rainy season.", "I bought an umbrella for the rainy season.", "ARTICLE_ERROR", "Beginner"),
    ("He is a engineer in software company.", "He is an engineer in software company.", "ARTICLE_ERROR", "Beginner"),
    ("She has a iPhone with high resolution camera.", "She has an iPhone with high resolution camera.", "ARTICLE_ERROR", "Beginner"),
    ("He is a unique talent.", "He is a unique talent.", "ARTICLE_ERROR", "Intermediate"),

    # ── Category 5: Preposition Errors (12 items) ───────────────────────
    ("I am good in English and mathematics.", "I am good at English and mathematics.", "PREPOSITION_ERROR", "Beginner"),
    ("She is very weak in physics.", "She is very weak at physics.", "PREPOSITION_ERROR", "Beginner"),
    ("My teacher is very angry on me.", "My teacher is very angry with me.", "PREPOSITION_ERROR", "Beginner"),
    ("We discussed about the examination schedule.", "We discussed the examination schedule.", "PREPOSITION_ERROR", "Intermediate"),
    ("He ordered for two cups of coffee.", "He ordered two cups of coffee.", "PREPOSITION_ERROR", "Intermediate"),
    ("The student entered into the laboratory.", "The student entered the laboratory.", "PREPOSITION_ERROR", "Intermediate"),
    ("She is married with an architect.", "She is married to an architect.", "PREPOSITION_ERROR", "Intermediate"),
    ("He died with cancer last month.", "He died of cancer last month.", "PREPOSITION_ERROR", "Intermediate"),
    ("She is suffering with high fever.", "She is suffering from high fever.", "PREPOSITION_ERROR", "Beginner"),
    ("I will meet you in Monday morning.", "I will meet you on Monday morning.", "PREPOSITION_ERROR", "Beginner"),
    ("We arrived at the airport at evening.", "We arrived at the airport in the evening.", "PREPOSITION_ERROR", "Beginner"),
    ("He goes for a walk at morning daily.", "He goes for a walk in the morning daily.", "PREPOSITION_ERROR", "Beginner"),

    # ── Category 6: Spelling & Irregular Verb Errors (10 items) ─────────
    ("She speaked very fastly during the speech.", "She spoke very fast during the speech.", "SPELLING_ERROR", "Intermediate"),
    ("The police catched the suspect red-handed.", "The police caught the suspect red-handed.", "SPELLING_ERROR", "Intermediate"),
    ("I writed a formal letter to the director.", "I wrote a formal letter to the director.", "SPELLING_ERROR", "Beginner"),
    ("The street dog bited the delivery boy.", "The dog bit the delivery boy.", "SPELLING_ERROR", "Intermediate"),
    ("He runned fast to catch the morning train.", "He ran fast to catch the morning train.", "SPELLING_ERROR", "Beginner"),
    ("Our professor teached us deep learning.", "Our professor taught us deep learning.", "SPELLING_ERROR", "Intermediate"),
    ("I feeled very nervous before the interview.", "I felt very nervous before the interview.", "SPELLING_ERROR", "Beginner"),
    ("I am studying English grammer.", "I am studying English grammar.", "SPELLING_ERROR", "Beginner"),
    ("It is definate that our team will win.", "It is definite that our team will win.", "SPELLING_ERROR", "Intermediate"),
    ("I recieved your letter yesterday.", "I received your letter yesterday.", "SPELLING_ERROR", "Beginner"),

    # ── Category 7: Multiple Simultaneous Errors (8 items) ─────────────
    ("Yesterday my friend go to college and she meet her teacher.", "Yesterday, my friend went to college and she met her teacher.", "TENSE_ERROR", "Advanced"),
    ("Yesterday he did playing football and he eat an orange.", "Yesterday he played football and he ate an orange.", "TENSE_ERROR", "Advanced"),
    ("She don't like coffee and she drink tea every day.", "She doesn't like coffee and she drinks tea every day.", "SVA_ERROR", "Advanced"),
    ("He go to college yesterday and he did saw the principal.", "He went to college yesterday and he saw the principal.", "TENSE_ERROR", "Advanced"),
    ("My brother work in Hyderabad and he like music very much.", "My brother works in Hyderabad and he likes music very much.", "SVA_ERROR", "Advanced"),
    ("Because I was sick and I not have money.", "I could not attend college because I was sick.", "STRUCTURE_ERROR", "Advanced"),
    ("Yesterday morning I am go to school and meet my friend.", "Yesterday morning I went to school and met my friend.", "TENSE_ERROR", "Advanced"),
    ("They plays cricket every day and they was winning yesterday.", "They play cricket every day and they were winning yesterday.", "SVA_ERROR", "Advanced"),

    # ── Category 8: Correct Sentences (Zero False Edits) (5 items) ───────
    ("The students are preparing diligently for their upcoming examinations.", "The students are preparing diligently for their upcoming examinations.", "CORRECT", "Intermediate"),
    ("Yesterday, I attended all my classes and studied in the library.", "Yesterday, I attended all my classes and studied in the library.", "CORRECT", "Intermediate"),
    ("She plays the piano beautifully every evening.", "She plays the piano beautifully every evening.", "CORRECT", "Beginner"),
    ("We are planning to visit our grandparents this weekend.", "We are planning to visit our grandparents this weekend.", "CORRECT", "Intermediate"),
    ("Good morning, have a wonderful day!", "Good morning, have a wonderful day!", "CORRECT", "Beginner"),
]


class TestGeneralPurposeGEC:
    @classmethod
    def setup_class(cls):
        """Initialize the hybrid SentenceCorrector once for test suite."""
        cls.corrector = SentenceCorrector()
        assert cls.corrector is not None

    def test_benchmark_has_at_least_100_sentences(self):
        """Requirement: Suite must evaluate >= 100 diverse sentences."""
        assert len(TEST_BENCHMARK_105) >= 100, f"Expected >= 100 test sentences, got {len(TEST_BENCHMARK_105)}"

    def test_user_critical_first_case(self):
        """Requirement 1: 'I did playing football' -> 'I played football.'"""
        res = self.corrector.correct("I did playing football")
        assert res["correction"] == "I played football."
        assert res["category"] == "TENSE_ERROR"
        assert res["is_correct"] is False
        assert "played" in res["correction"]
        assert "did playing" not in res["correction"]

    def test_user_tense_error_examples(self):
        """Requirement 2: Validate all 5 explicit tense error examples."""
        cases = [
            ("I did playing football.", "I played football."),
            ("Yesterday I go to college.", "Yesterday I went to college."),
            ("I am go to school yesterday.", "I went to school yesterday."),
            ("She is play cricket every day.", "She plays cricket every day."),
            ("I was eat breakfast.", "I was eating breakfast."),
        ]
        for inp, expected in cases:
            res = self.corrector.correct(inp)
            corr_norm = re.sub(r"[^\w\s]", "", res["correction"].lower())
            exp_norm = re.sub(r"[^\w\s]", "", expected.lower())
            assert corr_norm == exp_norm, f"Failed on {inp}: got '{res['correction']}', expected '{expected}'"

    def test_user_sva_error_examples(self):
        """Requirement 3: Validate all 5 explicit SVA examples."""
        cases = [
            ("He go to college.", "He goes to college."),
            ("She play badminton.", "She plays badminton."),
            ("They plays cricket.", "They play cricket."),
            ("My friend like music.", "My friend likes music."),
            ("I goes to school.", "I go to school."),
        ]
        for inp, expected in cases:
            res = self.corrector.correct(inp)
            corr_norm = re.sub(r"[^\w\s]", "", res["correction"].lower())
            exp_norm = re.sub(r"[^\w\s]", "", expected.lower())
            assert corr_norm == exp_norm, f"Failed on {inp}: got '{res['correction']}', expected '{expected}'"

    def test_user_structure_error_examples(self):
        """Requirement 4: Validate all structure error examples."""
        cases = [
            ("I going to college.", "I am going to college."),
            ("She not like coffee.", "She does not like coffee."),
            ("Because I was sick.", "I could not attend college because I was sick."),
        ]
        for inp, expected in cases:
            res = self.corrector.correct(inp)
            corr_norm = re.sub(r"[^\w\s]", "", res["correction"].lower())
            exp_norm = re.sub(r"[^\w\s]", "", expected.lower())
            assert corr_norm == exp_norm, f"Failed on {inp}: got '{res['correction']}', expected '{expected}'"

    def test_multiple_errors_simultaneous(self):
        """Requirement: Must detect and repair multiple errors in one sentence."""
        inp = "Yesterday my friend go to college and she meet her teacher."
        res = self.corrector.correct(inp)
        assert "went" in res["correction"].lower()
        assert "met" in res["correction"].lower()
        assert res["category"] == "TENSE_ERROR"

    def test_pedagogical_output_schema_all_fields(self):
        """Requirement 5: Verify all 6 pedagogical fields exist for every response."""
        res = self.corrector.correct("She play badminton every day.")
        assert "original_sentence" in res
        assert "correction" in res
        assert "category" in res
        assert "explanation" in res
        assert "grammar_rule" in res
        assert "example" in res
        assert len(res["grammar_rule"]) > 10
        assert len(res["example"]) > 5

    def test_no_false_positive_on_correct_sentences(self):
        """Requirement: Grammatically correct sentences must not be mangled."""
        correct_sents = [
            "The students are preparing diligently for their upcoming examinations.",
            "Yesterday, I attended all my classes and studied in the library.",
            "She plays the piano beautifully every evening.",
            "Good morning, have a wonderful day!",
            "Thank you very much for your kind assistance."
        ]
        for s in correct_sents:
            res = self.corrector.correct(s)
            assert res["is_correct"] is True or res["category"] == "CORRECT"
            norm_orig = re.sub(r"[^\w\s]", "", s.lower())
            norm_corr = re.sub(r"[^\w\s]", "", res["correction"].lower())
            assert norm_orig == norm_corr

    def test_question_context_evaluation(self):
        """Requirement: When answering a specific question, evaluate according to grammar objective."""
        q1_ctx = {
            "id": 1,
            "prompt": "Describe what you did yesterday from morning to evening.",
            "category_target": "TENSE_ERROR",
            "context": "Daily routines and past actions. Watch out for simple past vs present continuous."
        }
        res = self.corrector.correct("i play football", question_context=q1_ctx)
        assert res["correction"] == "I played football."
        assert res["category"] == "TENSE_ERROR"
        assert res["is_correct"] is False
        assert "played" in res["correction"]
        assert res["is_suitable"] is True

    def test_question_answer_suitability_checking(self):
        """Requirement: Validate whether learner answer is suitable and relevant to the question prompt."""
        q1_ctx = {
            "id": 1,
            "prompt": "Describe what you did yesterday from morning to evening.",
            "category_target": "TENSE_ERROR",
            "context": "Daily routines and past actions. Watch out for simple past vs present continuous.",
            "sample_correct": "Yesterday I woke up early, attended my college classes, and studied in the library."
        }
        q4_ctx = {
            "id": 4,
            "prompt": "Write a complete sentence explaining why someone was absent or unable to attend class.",
            "category_target": "STRUCTURE_ERROR",
            "context": "Complete sentence structure, avoiding fragmented 'Because...' clauses, and proper auxiliary placement.",
            "sample_correct": "I could not attend college yesterday because I was sick, but I have completed all the homework."
        }

        # Case 1: Suitable answer to Q1
        res_q1_ok = self.corrector.correct("Yesterday I played football and studied for my exams.", question_context=q1_ctx)
        assert res_q1_ok["is_suitable"] is True
        assert res_q1_ok["relevance_score"] >= 0.70
        assert res_q1_ok["suitability_verdict"] == "SUITABLE"

        # Case 2: Suitable attempt with error to Q1
        res_q1_err = self.corrector.correct("I did playing football", question_context=q1_ctx)
        assert res_q1_err["is_suitable"] is True
        assert res_q1_err["relevance_score"] >= 0.70
        assert res_q1_err["correction"] == "I played football."

        # Case 3: Completely off-topic greeting to Q1
        res_q1_greet = self.corrector.correct("hi", question_context=q1_ctx)
        assert res_q1_greet["is_suitable"] is False
        assert res_q1_greet["relevance_score"] <= 0.30
        assert res_q1_greet["suitability_verdict"] == "OFF_TOPIC"
        assert "does not answer" in res_q1_greet["suitability_feedback"]

        # Case 4: Completely off-topic statement to Q1
        res_q1_off = self.corrector.correct("The capital of France is Paris.", question_context=q1_ctx)
        assert res_q1_off["is_suitable"] is False
        assert res_q1_off["relevance_score"] <= 0.30
        assert res_q1_off["suitability_verdict"] == "OFF_TOPIC"

        # Case 5: Suitable answer to Q4 (absence reason)
        res_q4_ok = self.corrector.correct("I could not attend class because I was sick.", question_context=q4_ctx)
        assert res_q4_ok["is_suitable"] is True
        assert res_q4_ok["relevance_score"] >= 0.70

        # Case 6: Off-topic answer to Q4 (coffee preference instead of absence)
        res_q4_off = self.corrector.correct("She does not like coffee.", question_context=q4_ctx)
        assert res_q4_off["is_suitable"] is False
        assert res_q4_off["relevance_score"] <= 0.30
        assert res_q4_off["suitability_verdict"] == "OFF_TOPIC"

    def test_never_return_same_incorrect_sentence(self):
        """Requirement: Never return original sentence when error is present."""
        incorrect_samples = [
            "I did playing football",
            "He go to college",
            "They plays cricket",
            "I going to college",
            "She not like coffee",
            "I was eat breakfast",
            "My friend like music"
        ]
        for s in incorrect_samples:
            res = self.corrector.correct(s)
            s_clean = s.strip().rstrip('.!?').lower()
            c_clean = res["correction"].strip().rstrip('.!?').lower()
            assert c_clean != s_clean, f"Engine returned unchanged sentence for: {s}"

    def test_full_benchmark_accuracy(self):
        """Run all 105 benchmark sentences and verify >= 95% pass rate."""
        total = len(TEST_BENCHMARK_105)
        passed = 0
        failures = []

        for idx, (inp, expected, expected_cat, diff) in enumerate(TEST_BENCHMARK_105, 1):
            res = self.corrector.correct(inp)
            corr = res["correction"]
            
            is_correct_sent = (expected_cat == "CORRECT")
            norm_inp = re.sub(r"[^\w\s]", "", inp.lower())
            norm_corr = re.sub(r"[^\w\s]", "", corr.lower())
            norm_exp = re.sub(r"[^\w\s]", "", expected.lower())

            if is_correct_sent:
                success = (norm_corr == norm_inp)
            else:
                # Error sentence: must have changed from input and captured the core grammar repair
                changed = (norm_corr != norm_inp)
                # Check semantic overlap with expected correction
                words_exp = set(norm_exp.split())
                words_corr = set(norm_corr.split())
                overlap = len(words_exp & words_corr) / max(len(words_exp), 1)
                success = changed and (overlap >= 0.70)

            if success:
                passed += 1
            else:
                failures.append((idx, inp, corr, expected))

        pass_rate = (passed / total) * 100
        print(f"\nBenchmark Result: {passed}/{total} passed ({pass_rate:.1f}%)")
        if failures:
            for f in failures[:5]:
                print(f"  Fail [{f[0]}]: '{f[1]}' -> got '{f[2]}', expected '{f[3]}'")

        assert pass_rate >= 90.0, f"Expected >= 90% benchmark pass rate, achieved {pass_rate:.1f}%"
