import json
import datetime
from sqlalchemy.orm import Session
from backend.academy.database import SessionLocal, engine, Base
from backend.academy.models import Course, Module, Lesson, Exercise, Quiz, QuizQuestion, User
from backend.academy.auth import hash_password

def seed_database(force: bool = False):
    """Populates the English Learning Academy with full courses, lessons, exercises, and assessments."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # 1. Ensure Default Admin/Demo User exists
    demo_user = db.query(User).filter(User.username == "demo_student").first()
    if not demo_user:
        demo_user = User(
            email="student@englishacademy.com",
            username="demo_student",
            full_name="Alex Student",
            hashed_password=hash_password("Academy123!"),
            role="student"
        )
        db.add(demo_user)
        db.commit()

    if force:
        # Clear existing courses to reseed full catalog
        db.query(QuizQuestion).delete()
        db.query(Quiz).delete()
        db.query(Exercise).delete()
        db.query(Lesson).delete()
        db.query(Module).delete()
        db.query(Course).delete()
        db.commit()
    elif db.query(Course).count() > 0:
        print("Database already contains courses. Seeding skipped.")
        db.close()
        return

    print("Seeding full courses and curriculum into English Learning Academy...")

    # =========================================================================
    # COURSE 1: Complete English Tenses (All 12 Tenses)
    # =========================================================================
    course_tenses = Course(
        slug="english-tenses",
        title="Complete English Tenses Masterclass",
        category="Tenses",
        difficulty="All Levels",
        summary="Master all 12 English tense forms, their positive, negative, and question structures, time signals, regular/irregular verbs, and common pitfalls.",
        icon="Clock",
        order_index=1
    )
    db.add(course_tenses)
    db.flush()

    # --- Module 1: Present Tenses ---
    mod_present = Module(course_id=course_tenses.id, title="Module 1: Present Tenses", summary="Simple Present, Present Continuous, Present Perfect, and Present Perfect Continuous", order_index=1)
    db.add(mod_present)
    db.flush()

    # Lesson 1.1: Simple Present
    l_simple_pres = Lesson(
        course_id=course_tenses.id,
        module_id=mod_present.id,
        slug="simple-present-tense",
        title="Simple Present Tense",
        order_index=1,
        reading_time_mins=8,
        difficulty="Beginner",
        concept_summary="Used for habits, daily routines, permanent truths, and general facts.",
        formula_structure="Positive: Subject + Verb(s/es) + Object | Negative: Subject + do/does not + Base Verb | Question: Do/Does + Subject + Base Verb?",
        rules_json=json.dumps([
            "Add '-s' or '-es' to the base verb when the subject is third-person singular (He, She, It, or a singular noun).",
            "Use the auxiliary verb 'do' for I, You, We, They; use 'does' for He, She, It in negatives and questions.",
            "Never add '-s' to the main verb after 'does' or 'doesn't' (e.g., 'He does not know', NOT 'He does not knows').",
            "Common signal words include: always, usually, often, sometimes, rarely, never, every day, on Mondays."
        ]),
        positive_examples_json=json.dumps([
            "Water boils at 100 degrees Celsius.",
            "She teaches mathematics at the community college.",
            "They live in London near the central train station.",
            "I walk to the office every morning."
        ]),
        negative_examples_json=json.dumps([
            "He does not drink coffee in the evening.",
            "We do not watch television on weekdays.",
            "The train does not stop at this small station."
        ]),
        question_examples_json=json.dumps([
            "Do you speak English fluently?",
            "Does she know where the conference hall is located?",
            "Where do your parents live?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "She teach English very well.",
                "right": "She teaches English very well.",
                "explanation": "Third-person singular subjects (she) require the '-es' suffix on the verb."
            },
            {
                "wrong": "He doesn't knows the answer.",
                "right": "He doesn't know the answer.",
                "explanation": "When the auxiliary 'does' is used, the main verb returns to its base infinitive form."
            },
            {
                "wrong": "I am knowing your brother.",
                "right": "I know your brother.",
                "explanation": "Stative verbs such as 'know', 'believe', and 'understand' are rarely used in continuous aspect."
            }
        ]),
        content_markdown="""# Understanding the Simple Present Tense

The **Simple Present Tense** is one of the most fundamental structures in English grammar. Learners often confuse it with the Present Continuous, but it is primarily used to describe states that are permanent or repeated over time.

## 1. When to Use the Simple Present

1. **Habits and Regular Routines**:
   - *I wake up at six o'clock every morning.*
   - *He exercises before going to work.*
2. **Universal Truths and Scientific Facts**:
   - *The sun rises in the east.*
   - *Light travels faster than sound.*
3. **Permanent or Long-lasting Situations**:
   - *My uncle lives in New York.*
   - *She works as a software engineer.*
4. **Scheduled Future Events (Timetables)**:
   - *The flight departs at 9:30 PM tonight.*
   - *The semester begins next Monday.*

## 2. Sentence Structures

| Sentence Type | Formula | Example |
| :--- | :--- | :--- |
| **Positive** | Subject + Verb(base / +s/es) | *She writes clear reports.* |
| **Negative** | Subject + do/does not + Base Verb | *She does not write messy reports.* |
| **Yes/No Question** | Do/Does + Subject + Base Verb? | *Does she write clear reports?* |
| **WH Question** | WH Word + do/does + Subject + Base Verb? | *What does she write every day?* |

## 3. Spelling Rules for 3rd Person Singular

- Most verbs: add **-s** (*work -> works*, *read -> reads*).
- Verbs ending in **-s, -sh, -ch, -x, -z, -o**: add **-es** (*watch -> watches*, *go -> goes*, *pass -> passes*).
- Verbs ending in **consonant + y**: change **-y** to **-ies** (*study -> studies*, *carry -> carries*).
- Verbs ending in **vowel + y**: simply add **-s** (*play -> plays*, *enjoy -> enjoys*).
"""
    )
    db.add(l_simple_pres)
    db.flush()

    # Exercises for 1.1
    ex1 = Exercise(
        lesson_id=l_simple_pres.id,
        course_id=course_tenses.id,
        exercise_type="mcq",
        question_text="Choose the correct verb form: 'My brother _____ in an international hospital in Chicago.'",
        options_json=json.dumps(["work", "works", "is work", "working"]),
        correct_answer="works",
        explanation="'My brother' is a third-person singular subject (he), so the verb requires '-s' in simple present tense.",
        difficulty="Beginner"
    )
    ex2 = Exercise(
        lesson_id=l_simple_pres.id,
        course_id=course_tenses.id,
        exercise_type="error_spotting",
        question_text="Identify the error: 'He does not drinks tea in the morning because it upsets his stomach.'",
        options_json=json.dumps(["He does", "not drinks", "in the morning", "upsets his stomach"]),
        correct_answer="not drinks",
        explanation="After the auxiliary verb 'does not', the main verb must be in its base form ('drink', not 'drinks').",
        difficulty="Beginner"
    )
    ex3 = Exercise(
        lesson_id=l_simple_pres.id,
        course_id=course_tenses.id,
        exercise_type="fill_blank",
        question_text="Fill in the blank with the correct auxiliary: '_____ they know about the change in schedule?'",
        options_json=json.dumps(["Do", "Does", "Is", "Are"]),
        correct_answer="Do",
        explanation="The subject 'they' is third-person plural, which takes the auxiliary verb 'Do'.",
        difficulty="Beginner"
    )
    db.add_all([ex1, ex2, ex3])

    # Lesson 1.2: Present Continuous Tense
    l_pres_cont = Lesson(
        course_id=course_tenses.id,
        module_id=mod_present.id,
        slug="present-continuous-tense",
        title="Present Continuous Tense",
        order_index=2,
        reading_time_mins=8,
        difficulty="Beginner",
        concept_summary="Used for actions happening right now at the moment of speaking, or temporary situations around the present time.",
        formula_structure="Positive: Subject + is/am/are + Verb(-ing) | Negative: Subject + is/am/are not + Verb(-ing) | Question: Is/Am/Are + Subject + Verb(-ing)?",
        rules_json=json.dumps([
            "Use 'am' with 'I', 'is' with third-person singular (He, She, It), and 'are' with You, We, They.",
            "Always include both the helping verb (is/am/are) AND the present participle (verb + ing).",
            "Do not use continuous aspect with stative verbs describing emotions, mental states, or possession (e.g., love, like, hate, want, know, belong).",
            "Key signal words: right now, currently, at the moment, look!, listen!, these days."
        ]),
        positive_examples_json=json.dumps([
            "I am preparing a presentation for the engineering seminar.",
            "Listen! The baby is laughing in the other room.",
            "They are renovating their library this month."
        ]),
        negative_examples_json=json.dumps([
            "She is not attending the lecture today.",
            "We are not using the laboratory equipment at this moment."
        ]),
        question_examples_json=json.dumps([
            "Are you working on the deep learning assignment right now?",
            "What is he doing in the laboratory?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "She working on the computer now.",
                "right": "She is working on the computer now.",
                "explanation": "The auxiliary verb 'is' cannot be omitted in the continuous tense."
            },
            {
                "wrong": "I am wanting a cup of coffee.",
                "right": "I want a cup of coffee.",
                "explanation": "'Want' is a stative verb representing desire and is not used in the continuous form."
            }
        ]),
        content_markdown="""# The Present Continuous Tense

The **Present Continuous Tense** (also called Present Progressive) focuses on actions in progress.

## 1. Primary Uses

1. **Actions Happening at the Present Moment**:
   - *Look! It is raining outside.*
   - *The teacher is explaining the problem on the board.*
2. **Temporary Situations**:
   - *I am staying with my cousin while my house is being painted.*
   - *He is studying online this semester.*
3. **Definite Future Arrangements**:
   - *We are meeting the dean tomorrow afternoon.*
"""
    )
    db.add(l_pres_cont)
    db.flush()

    # Exercises for 1.2
    ex_pc1 = Exercise(
        lesson_id=l_pres_cont.id,
        course_id=course_tenses.id,
        exercise_type="mcq",
        question_text="Which sentence is grammatically correct?",
        options_json=json.dumps([
            "I am knowing the answer to this question.",
            "I know the answer to this question.",
            "I knows the answer to this question.",
            "I am know the answer to this question."
        ]),
        correct_answer="I know the answer to this question.",
        explanation="'Know' is a stative verb and cannot take the continuous -ing form in standard English.",
        difficulty="Beginner"
    )
    db.add(ex_pc1)

    # Lesson 1.3: Present Perfect Tense
    l_pres_perf = Lesson(
        course_id=course_tenses.id,
        module_id=mod_present.id,
        slug="present-perfect-tense",
        title="Present Perfect Tense",
        order_index=3,
        reading_time_mins=9,
        difficulty="Intermediate",
        concept_summary="Connects the past to the present: actions completed at an unspecified time with present results, or actions continuing up to now.",
        formula_structure="Positive: Subject + has/have + Past Participle (V3) | Negative: Subject + has/have not + V3 | Question: Has/Have + Subject + V3?",
        rules_json=json.dumps([
            "Use 'has' for third-person singular subjects (He, She, It); use 'have' for I, You, We, They.",
            "Always use the past participle (V3) of the verb (e.g., eaten, written, seen, completed).",
            "Never use the Present Perfect with specific past time indicators like 'yesterday', 'in 2018', or 'two hours ago' (use Simple Past instead).",
            "Common signal words: already, yet, just, ever, never, since, for, recently, so far."
        ]),
        positive_examples_json=json.dumps([
            "She has published two research papers this year.",
            "I have already finished writing the laboratory report.",
            "We have lived in this city since 2015."
        ]),
        negative_examples_json=json.dumps([
            "He has not submitted his project proposal yet.",
            "They have not visited the newly built auditorium."
        ]),
        question_examples_json=json.dumps([
            "Have you ever participated in a hackathon?",
            "Has the professor approved your thesis topic?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "I have completed my degree in 2022.",
                "right": "I completed my degree in 2022.",
                "explanation": "Specific past time markers ('in 2022') require the Simple Past tense, not the Present Perfect."
            },
            {
                "wrong": "She has saw that movie before.",
                "right": "She has seen that movie before.",
                "explanation": "Present Perfect requires the past participle V3 ('seen'), not the simple past V2 ('saw')."
            }
        ]),
        content_markdown="""# The Present Perfect Tense

The **Present Perfect Tense** links past occurrences with present consequences.

## 1. Key Distinctions
- **Present Perfect**: Action finished at an unspecified time with relevance now (*I have lost my key; I cannot enter now*).
- **Simple Past**: Action finished at a definite stated past time (*I lost my key yesterday morning*).
"""
    )
    db.add(l_pres_perf)

    # Lesson 1.4: Present Perfect Continuous Tense
    l_pres_perf_cont = Lesson(
        course_id=course_tenses.id,
        module_id=mod_present.id,
        slug="present-perfect-continuous-tense",
        title="Present Perfect Continuous Tense",
        order_index=4,
        reading_time_mins=8,
        difficulty="Intermediate",
        concept_summary="Emphasizes the duration of an activity that started in the past and is still continuing right now.",
        formula_structure="Positive: Subject + has/have been + Verb(-ing) | Negative: Subject + has/have not been + Verb(-ing) | Question: Has/Have + Subject + been + Verb(-ing)?",
        rules_json=json.dumps([
            "Use 'for' to denote a duration of time (e.g., for three hours, for five years).",
            "Use 'since' to denote a specific starting point in time (e.g., since morning, since 2019, since last Monday).",
            "Highlights ongoing effort or duration rather than completion."
        ]),
        positive_examples_json=json.dumps([
            "She has been studying deep learning architectures for three hours.",
            "They have been working on this web platform since early January."
        ]),
        negative_examples_json=json.dumps([
            "He has not been sleeping well over the past few weeks."
        ]),
        question_examples_json=json.dumps([
            "How long have you been coding in Python?",
            "Has it been raining continuously all afternoon?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "I am studying here since three years.",
                "right": "I have been studying here for three years.",
                "explanation": "Present continuous cannot be used with duration words like 'for/since'. Also, duration requires 'for', not 'since'."
            }
        ]),
        content_markdown="""# Present Perfect Continuous Tense

This tense highlights continuous duration starting in the past and leading directly into the present moment.
"""
    )
    db.add(l_pres_perf_cont)

    # --- Module 2: Past Tenses ---
    mod_past = Module(course_id=course_tenses.id, title="Module 2: Past Tenses", summary="Simple Past, Past Continuous, Past Perfect, and Past Perfect Continuous", order_index=2)
    db.add(mod_past)
    db.flush()

    l_past_simple = Lesson(
        course_id=course_tenses.id,
        module_id=mod_past.id,
        slug="simple-past-tense",
        title="Simple Past Tense",
        order_index=5,
        reading_time_mins=8,
        difficulty="Beginner",
        concept_summary="Used for completed actions that took place at a definite time in the past.",
        formula_structure="Positive: Subject + Past Verb (V2) | Negative: Subject + did not + Base Verb | Question: Did + Subject + Base Verb?",
        rules_json=json.dumps([
            "Use regular verb endings with -ed (walked, played) or memorized irregular verb forms (went, saw, ate, wrote).",
            "In negatives and questions, use the auxiliary 'did' and revert the main verb to base form.",
            "Never double the past tense: 'He didn't went' is strictly incorrect."
        ]),
        positive_examples_json=json.dumps([
            "Yesterday our team won the collegiate debate championship.",
            "Dr. Rao delivered an inspiring keynote address last Friday."
        ]),
        negative_examples_json=json.dumps([
            "We did not receive the official notification yesterday."
        ]),
        question_examples_json=json.dumps([
            "Did you submit your project file before the deadline?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "She didn't went to the library.",
                "right": "She didn't go to the library.",
                "explanation": "After 'didn't', the main verb must be in base infinitive form ('go')."
            }
        ]),
        content_markdown="""# The Simple Past Tense

The **Simple Past Tense** narrates events that began and ended in the past.
"""
    )
    db.add(l_past_simple)

    l_past_cont = Lesson(
        course_id=course_tenses.id,
        module_id=mod_past.id,
        slug="past-continuous-tense",
        title="Past Continuous Tense",
        order_index=6,
        reading_time_mins=7,
        difficulty="Intermediate",
        concept_summary="Used for ongoing actions interrupted by another past event, or simultaneous past actions.",
        formula_structure="Positive: Subject + was/were + Verb(-ing) | Negative: Subject + was/were not + Verb(-ing) | Question: Was/Were + Subject + Verb(-ing)?",
        rules_json=json.dumps([
            "Use 'was' with I, He, She, It; use 'were' with You, We, They.",
            "Commonly combined with Simple Past using 'when' and 'while': While I was reading, the telephone rang."
        ]),
        positive_examples_json=json.dumps([
            "I was preparing dinner when the electricity went out.",
            "The students were discussing the algorithm when the professor walked in."
        ]),
        negative_examples_json=json.dumps([
            "They were not paying attention during the laboratory briefing."
        ]),
        question_examples_json=json.dumps([
            "Were you watching television at eight o'clock last night?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "When the bell rang, we was packing our bags.",
                "right": "When the bell rang, we were packing our bags.",
                "explanation": "Plural subject 'we' takes the auxiliary verb 'were', not 'was'."
            }
        ]),
        content_markdown="""# The Past Continuous Tense

Describes ongoing background activities in past narratives.
"""
    )
    db.add(l_past_cont)

    l_past_perf = Lesson(
        course_id=course_tenses.id,
        module_id=mod_past.id,
        slug="past-perfect-tense",
        title="Past Perfect Tense",
        order_index=7,
        reading_time_mins=8,
        difficulty="Intermediate",
        concept_summary="Identifies the earlier of two completed past actions (the 'past of the past').",
        formula_structure="Positive: Subject + had + Past Participle (V3) | Negative: Subject + had not + V3 | Question: Had + Subject + V3?",
        rules_json=json.dumps([
            "Used to clarify sequence when two events happened in the past: The first event uses Past Perfect (had + V3), the second uses Simple Past.",
            "Signal words: before, after, by the time, already, when."
        ]),
        positive_examples_json=json.dumps([
            "When we reached the station, the express train had already departed.",
            "She had completed her degree before she joined the multinational company."
        ]),
        negative_examples_json=json.dumps([
            "He had not reviewed the lecture slides before attending the examination."
        ]),
        question_examples_json=json.dumps([
            "Had you finished your dinner before your friends arrived?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "The movie started before we had reached the cinema.",
                "right": "The movie had started before we reached the cinema.",
                "explanation": "The movie starting occurred first, so it requires 'had started'. Reaching the cinema happened second, requiring simple past 'reached'."
            }
        ]),
        content_markdown="""# The Past Perfect Tense

The **Past Perfect Tense** eliminates chronological ambiguity between two past events.
"""
    )
    db.add(l_past_perf)

    l_past_perf_cont = Lesson(
        course_id=course_tenses.id,
        module_id=mod_past.id,
        slug="past-perfect-continuous-tense",
        title="Past Perfect Continuous Tense",
        order_index=8,
        reading_time_mins=7,
        difficulty="Advanced",
        concept_summary="Shows that an ongoing action was in progress for a period of time up until another past moment.",
        formula_structure="Positive: Subject + had been + Verb(-ing) | Negative: Subject + had not been + Verb(-ing) | Question: Had + Subject + been + Verb(-ing)?",
        rules_json=json.dumps([
            "Emphasizes duration leading up to a specific past milestone.",
            "Formula: Subject + had been + Verb-ing."
        ]),
        positive_examples_json=json.dumps([
            "He had been driving for six continuous hours before he stopped for rest.",
            "The ground was wet because it had been raining heavily all night."
        ]),
        negative_examples_json=json.dumps([
            "She had not been working there long when she received the promotion."
        ]),
        question_examples_json=json.dumps([
            "How long had they been researching the topic before finding the solution?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "She was working for four years before quitting.",
                "right": "She had been working for four years before quitting.",
                "explanation": "Duration prior to a past point in time requires the Past Perfect Continuous."
            }
        ]),
        content_markdown="""# The Past Perfect Continuous Tense

Highlights sustained duration preceding a past interruption or consequence.
"""
    )
    db.add(l_past_perf_cont)

    # --- Module 3: Future Tenses ---
    mod_future = Module(course_id=course_tenses.id, title="Module 3: Future Tenses & Comprehensive Comparison", summary="Simple Future, Future Continuous, Future Perfect, Future Perfect Continuous, and Tense Comparison", order_index=3)
    db.add(mod_future)
    db.flush()

    l_fut_simple = Lesson(
        course_id=course_tenses.id,
        module_id=mod_future.id,
        slug="simple-future-tense",
        title="Simple Future Tense (Will & Going to)",
        order_index=9,
        reading_time_mins=8,
        difficulty="Beginner",
        concept_summary="Used for spontaneous decisions, predictions, promises, and future plans.",
        formula_structure="Positive: Subject + will + Base Verb | Negative: Subject + will not (won't) + Base Verb | Question: Will + Subject + Base Verb?",
        rules_json=json.dumps([
            "Use 'will' for instant decisions, offers, promises, and general predictions.",
            "Use 'be going to' for planned future intentions or predictions supported by visible present evidence."
        ]),
        positive_examples_json=json.dumps([
            "I will help you with your programming code tomorrow.",
            "Look at those dark clouds; it is going to rain."
        ]),
        negative_examples_json=json.dumps([
            "We will not compromise on academic integrity."
        ]),
        question_examples_json=json.dumps([
            "Will you attend the workshop on machine learning next Saturday?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "I will to see you tomorrow.",
                "right": "I will see you tomorrow.",
                "explanation": "Modal auxiliary 'will' is followed directly by the bare infinitive without 'to'."
            }
        ]),
        content_markdown="""# The Simple Future Tense

Expresses actions projected to happen after the present moment.
"""
    )
    db.add(l_fut_simple)

    l_fut_cont = Lesson(
        course_id=course_tenses.id,
        module_id=mod_future.id,
        slug="future-continuous-tense",
        title="Future Continuous Tense",
        order_index=10,
        reading_time_mins=7,
        difficulty="Intermediate",
        concept_summary="Describes an action that will be in progress at a specific time in the future.",
        formula_structure="Positive: Subject + will be + Verb(-ing) | Negative: Subject + will not be + Verb(-ing) | Question: Will + Subject + be + Verb(-ing)?",
        rules_json=json.dumps([
            "Formula: will be + present participle (-ing).",
            "Useful for polite inquiries about future intentions."
        ]),
        positive_examples_json=json.dumps([
            "At 10:00 AM tomorrow, our batch will be writing the semester exam.",
            "This time next week, I will be traveling through southern India."
        ]),
        negative_examples_json=json.dumps([
            "She will not be attending classes this Friday due to sickness."
        ]),
        question_examples_json=json.dumps([
            "Will you be using the computer lab this afternoon?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "At eight tonight, I will watching the live seminar.",
                "right": "At eight tonight, I will be watching the live seminar.",
                "explanation": "The auxiliary 'be' is mandatory in the Future Continuous construction."
            }
        ]),
        content_markdown="""# The Future Continuous Tense

Visualizes an event unfolding at a projected future moment.
"""
    )
    db.add(l_fut_cont)

    l_fut_perf = Lesson(
        course_id=course_tenses.id,
        module_id=mod_future.id,
        slug="future-perfect-tense",
        title="Future Perfect & Future Perfect Continuous",
        order_index=11,
        reading_time_mins=9,
        difficulty="Advanced",
        concept_summary="Signifies an action that will be completed before a designated deadline in the future.",
        formula_structure="Future Perfect: Subject + will have + V3 | Future Perfect Continuous: Subject + will have been + Verb(-ing)",
        rules_json=json.dumps([
            "Signal words: by then, by tomorrow, by the end of this year, by 5 o'clock.",
            "Future Perfect formula: will have + past participle (V3).",
            "Future Perfect Continuous formula: will have been + verb(-ing)."
        ]),
        positive_examples_json=json.dumps([
            "By the end of this month, we will have completed the entire course curriculum.",
            "By December, she will have been working at the technology firm for five full years."
        ]),
        negative_examples_json=json.dumps([
            "I will not have finished reading the textbook before Monday's lecture."
        ]),
        question_examples_json=json.dumps([
            "Will you have graduated by the time the placement drive begins?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "By next year, I will finish my post-graduate degree.",
                "right": "By next year, I will have finished my post-graduate degree.",
                "explanation": "When an action will be completed before a future deadline ('by next year'), use the Future Perfect."
            }
        ]),
        content_markdown="""# Future Perfect and Future Perfect Continuous

Looking back at a completed achievement from a future viewpoint.
"""
    )
    db.add(l_fut_perf)

    l_tense_compare = Lesson(
        course_id=course_tenses.id,
        module_id=mod_future.id,
        slug="tense-consistency-and-comparison",
        title="Tense Consistency & Comparison Guide",
        order_index=12,
        reading_time_mins=10,
        difficulty="All Levels",
        concept_summary="Mastering tense harmony across sentences, narrative paragraphs, and avoiding unnecessary shifts.",
        formula_structure="Maintain consistent temporal reference points unless context explicitly demands a shift.",
        rules_json=json.dumps([
            "Do not switch between past and present without a logical reason in storytelling.",
            "When telling a past story, keep main clauses in past tense.",
            "Universal truths embedded in past narration stay in simple present: 'Galileo proved that the Earth revolves around the Sun.'"
        ]),
        positive_examples_json=json.dumps([
            "The engineer inspected the circuit, found the damaged resistor, and replaced it immediately.",
            "She explained that water freezes at zero degrees Celsius."
        ]),
        negative_examples_json=json.dumps([
            "The engineer inspected the circuit, finds the damaged resistor, and replaced it immediately."
        ]),
        question_examples_json=json.dumps([
            "Why is consistent verb tense crucial in technical writing and academic essays?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "Yesterday I opened the door and I see a strange bird.",
                "right": "Yesterday I opened the door and I saw a strange bird.",
                "explanation": "Maintain past tense consistency throughout the narrative."
            }
        ]),
        content_markdown="""# Tense Consistency and Master Comparison

This guide synthesizes all 12 tenses into a unified mental framework.
"""
    )
    db.add(l_tense_compare)
    db.flush()

    # Final Comprehensive Assessment for Course 1
    quiz_tenses = Quiz(
        course_id=course_tenses.id,
        title="Comprehensive English Tenses Final Assessment",
        description="Test your mastery across all 12 tenses, signal words, irregular verbs, and sentence structures.",
        passing_score_pct=80.0,
        is_final_assessment=True
    )
    db.add(quiz_tenses)
    db.flush()

    q_t1 = QuizQuestion(
        quiz_id=quiz_tenses.id,
        question_text="Select the correct sentence for an action in progress right now:",
        options_json=json.dumps([
            "The software compiles the source code at this moment.",
            "The software is compiling the source code at this moment.",
            "The software has compiled the source code at this moment.",
            "The software was compiling the source code at this moment."
        ]),
        correct_answer="The software is compiling the source code at this moment.",
        explanation="'At this moment' signals the present continuous tense (is compiling).",
        points=1
    )
    q_t2 = QuizQuestion(
        quiz_id=quiz_tenses.id,
        question_text="'When we arrived at the venue, the guest speaker _____ speaking.' Which form indicates an earlier completed event?",
        options_json=json.dumps([
            "already finished",
            "has already finished",
            "had already finished",
            "is already finishing"
        ]),
        correct_answer="had already finished",
        explanation="The speaker finishing occurred before our arrival in the past, requiring the Past Perfect ('had already finished').",
        points=1
    )
    q_t3 = QuizQuestion(
        quiz_id=quiz_tenses.id,
        question_text="Identify the grammatical error: 'By this time next month, Dr. Sen will complete thirty years of research service.'",
        options_json=json.dumps([
            "By this time next month",
            "will complete",
            "thirty years of",
            "research service"
        ]),
        correct_answer="will complete",
        explanation="A future completion deadline signaled by 'by this time next month' requires the Future Perfect: 'will have completed'.",
        points=1
    )
    q_t4 = QuizQuestion(
        quiz_id=quiz_tenses.id,
        question_text="Which sentence correctly uses a stative verb?",
        options_json=json.dumps([
            "I am believing your story.",
            "I believe your story.",
            "I was believing your story.",
            "I will be believing your story."
        ]),
        correct_answer="I believe your story.",
        explanation="'Believe' expresses a mental conviction and is a stative verb that does not take the continuous aspect.",
        points=1
    )
    q_t5 = QuizQuestion(
        quiz_id=quiz_tenses.id,
        question_text="Fill in the blank: 'He _____ as a senior analyst in Hyderabad since graduating in 2021.'",
        options_json=json.dumps([
            "works",
            "is working",
            "has been working",
            "was worked"
        ]),
        correct_answer="has been working",
        explanation="An action that began in the past (since 2021) and is still continuing requires the Present Perfect Continuous.",
        points=1
    )
    db.add_all([q_t1, q_t2, q_t3, q_t4, q_t5])

    # =========================================================================
    # COURSE 2: Subject–Verb Agreement Masterclass
    # =========================================================================
    course_sva = Course(
        slug="subject-verb-agreement",
        title="Subject–Verb Agreement Masterclass",
        category="Syntax",
        difficulty="All Levels",
        summary="Master singular and plural agreement, intervening phrases, compound subjects, either/or, indefinite pronouns, collective nouns, and tricky exceptions.",
        icon="Layers",
        order_index=2
    )
    db.add(course_sva)
    db.flush()

    mod_sva_basics = Module(course_id=course_sva.id, title="Module 1: Core Agreement Rules", summary="Foundational rules, intervening phrases, and compound subjects", order_index=1)
    db.add(mod_sva_basics)
    db.flush()

    l_sva_1 = Lesson(
        course_id=course_sva.id,
        module_id=mod_sva_basics.id,
        slug="basic-agreement-and-intervening-phrases",
        title="Basic Agreement & Intervening Phrases",
        order_index=1,
        reading_time_mins=8,
        difficulty="Beginner",
        concept_summary="A verb must agree with its true grammatical subject in number and person, ignoring any intervening prepositional or parenthetical phrases.",
        formula_structure="Singular Subject + Singular Verb (with -s) | Plural Subject + Plural Verb (base form)",
        rules_json=json.dumps([
            "Singular subjects take singular verbs: The student speaks.",
            "Plural subjects take plural verbs: The students speak.",
            "Do not be distracted by phrases placed between the subject and the verb (e.g., 'as well as', 'together with', 'in addition to', 'along with', prepositional phrases).",
            "Identify the true head noun of the subject before selecting the verb."
        ]),
        positive_examples_json=json.dumps([
            "The box of antique jewelry is extremely valuable.",
            "The professor, along with her research scholars, attends the global symposium.",
            "The colors of the rainbow are vivid and distinct."
        ]),
        negative_examples_json=json.dumps([
            "The box of antique jewelry are extremely valuable."
        ]),
        question_examples_json=json.dumps([
            "Does the bouquet of red roses smell fragrant?",
            "Why do the results of the experiment vary under different pressures?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "The quality of these mangoes are not good.",
                "right": "The quality of these mangoes is not good.",
                "explanation": "The true subject is the singular noun 'quality', not the plural object of preposition 'mangoes'."
            },
            {
                "wrong": "The captain, as well as the players, are ready.",
                "right": "The captain, as well as the players, is ready.",
                "explanation": "'As well as the players' is an intervening phrase; the true grammatical subject is the singular 'captain'."
            }
        ]),
        content_markdown="""# Subject-Verb Agreement Fundamentals

A verb must strictly agree in number with its true subject noun.
"""
    )
    db.add(l_sva_1)
    db.flush()

    ex_sva1 = Exercise(
        lesson_id=l_sva_1.id,
        course_id=course_sva.id,
        exercise_type="mcq",
        question_text="Choose the correct verb: 'The list of shortlisted candidates _____ posted on the official notice board.'",
        options_json=json.dumps(["is", "are", "were", "have been"]),
        correct_answer="is",
        explanation="The subject is the singular noun 'list'. 'Of shortlisted candidates' is a prepositional modifier.",
        difficulty="Beginner"
    )
    db.add(ex_sva1)

    l_sva_2 = Lesson(
        course_id=course_sva.id,
        module_id=mod_sva_basics.id,
        slug="compound-subjects-and-or-nor",
        title="Compound Subjects & Either/Or, Neither/Nor",
        order_index=2,
        reading_time_mins=8,
        difficulty="Intermediate",
        concept_summary="Rules governing subjects joined by 'and', 'or', 'nor', 'either...or', and 'neither...nor'.",
        formula_structure="Subject A and Subject B = Plural Verb | Either A or B = Verb agrees with the subject closest to it",
        rules_json=json.dumps([
            "Two or more subjects joined by 'and' typically take a plural verb: 'John and Mary are arriving today.'",
            "Exception: If two nouns joined by 'and' refer to the same person, item, or idea, use a singular verb: 'Bread and butter is his favorite breakfast.'",
            "When subjects are joined by 'or', 'nor', 'either...or', or 'neither...nor', the verb agrees with the subject closest to it (proximity rule)."
        ]),
        positive_examples_json=json.dumps([
            "Neither the principal nor the teachers were present in the hall.",
            "Neither the teachers nor the principal was present in the hall.",
            "Slow and steady wins the race."
        ]),
        negative_examples_json=json.dumps([
            "Neither the principal nor the teachers was present in the hall."
        ]),
        question_examples_json=json.dumps([
            "Are either the monitor or the cables defective?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "Either my brother or my parents is picking me up.",
                "right": "Either my brother or my parents are picking me up.",
                "explanation": "Under the proximity rule, the verb must agree with 'parents' (plural), which is closest to the verb."
            }
        ]),
        content_markdown="""# Compound Subjects and the Rule of Proximity

Learn how paired conjunctions determine verb agreement.
"""
    )
    db.add(l_sva_2)

    mod_sva_tricky = Module(course_id=course_sva.id, title="Module 2: Tricky Subjects & Exceptions", summary="Indefinite pronouns, collective nouns, amounts, and relative clauses", order_index=2)
    db.add(mod_sva_tricky)
    db.flush()

    l_sva_3 = Lesson(
        course_id=course_sva.id,
        module_id=mod_sva_tricky.id,
        slug="indefinite-pronouns-and-collective-nouns",
        title="Indefinite Pronouns & Collective Nouns",
        order_index=3,
        reading_time_mins=9,
        difficulty="Intermediate",
        concept_summary="Handling pronouns like 'each', 'everyone', 'nobody', and collective nouns like 'team', 'committee', 'jury'.",
        formula_structure="Everyone / Somebody / Each = Singular Verb | Collective Noun acting as a single unit = Singular Verb",
        rules_json=json.dumps([
            "Indefinite pronouns ending in -body, -one, -thing (everyone, somebody, anything, each) are grammatically singular.",
            "Collective nouns (committee, jury, team, audience) take a singular verb when acting as a unified unit.",
            "Expressions of money, time, and distance take a singular verb when treated as a single quantity: 'Ten thousand dollars is a large sum.'"
        ]),
        positive_examples_json=json.dumps([
            "Each of the participants receives a certificate of participation.",
            "The committee has reached an unanimous decision.",
            "Fifty kilometers is a long distance to cycle in one day."
        ]),
        negative_examples_json=json.dumps([
            "Everyone in the classroom have finished the quiz."
        ]),
        question_examples_json=json.dumps([
            "Does everyone have their textbook ready?"
        ]),
        common_mistakes_json=json.dumps([
            {
                "wrong": "Each of the students have submitted their assignment.",
                "right": "Each of the students has submitted their assignment.",
                "explanation": "'Each' is an indefinite pronoun that requires the singular verb 'has'."
            }
        ]),
        content_markdown="""# Indefinite Pronouns and Collective Nouns

Mastering indefinite pronoun agreement is essential for writing and examinations.
"""
    )
    db.add(l_sva_3)
    db.flush()

    # SVA Final Assessment
    quiz_sva = Quiz(
        course_id=course_sva.id,
        title="Subject–Verb Agreement Comprehensive Final Test",
        description="Verify your mastery of subject-verb agreement across all rules and edge cases.",
        passing_score_pct=80.0,
        is_final_assessment=True
    )
    db.add(quiz_sva)
    db.flush()

    q_s1 = QuizQuestion(
        quiz_id=quiz_sva.id,
        question_text="Select the correct sentence:",
        options_json=json.dumps([
            "The prime minister, accompanied by his advisors, are visiting the state.",
            "The prime minister, accompanied by his advisors, is visiting the state.",
            "The prime minister, accompanied by his advisors, were visiting the state.",
            "The prime minister, accompanied by his advisors, have been visiting the state."
        ]),
        correct_answer="The prime minister, accompanied by his advisors, is visiting the state.",
        explanation="'Accompanied by his advisors' is a parenthetical phrase. The singular subject 'prime minister' takes 'is'.",
        points=1
    )
    q_s2 = QuizQuestion(
        quiz_id=quiz_sva.id,
        question_text="'Neither the doctor nor the nurses _____ aware of the updated clinical trial results.' Choose the correct verb:",
        options_json=json.dumps(["was", "were", "is", "has been"]),
        correct_answer="were",
        explanation="Under the proximity rule for 'neither...nor', the verb agrees with 'nurses' (plural), which is closest to the verb.",
        points=1
    )
    q_s3 = QuizQuestion(
        quiz_id=quiz_sva.id,
        question_text="Which sentence violates standard subject-verb agreement?",
        options_json=json.dumps([
            "Every student and teacher was evacuated safely.",
            "Ten miles is too far to walk in this scorching heat.",
            "The jury have reached its unanimous verdict.",
            "Bread and butter is served every morning in the hostel cafeteria."
        ]),
        correct_answer="The jury have reached its unanimous verdict.",
        explanation="The collective noun 'jury' is acting as a single unit with a singular pronoun ('its'), so it requires the singular verb 'has reached'.",
        points=1
    )
    db.add_all([q_s1, q_s2, q_s3])

    # =========================================================================
    # ADDITIONAL COURSES (Parts of Speech, Articles, Prepositions, Voice, etc.)
    # =========================================================================
    additional_courses_data = [
        {
            "slug": "parts-of-speech-and-sentence-structure",
            "title": "Parts of Speech & Sentence Structure",
            "category": "Syntax",
            "difficulty": "All Levels",
            "summary": "Master the eight parts of speech, subjects, predicates, objects, clauses, and sentence building.",
            "icon": "FileText",
            "order": 3,
            "modules": [
                {
                    "title": "Module 1: The Eight Parts of Speech",
                    "lessons": [
                        {
                            "slug": "nouns-pronouns-verbs",
                            "title": "Nouns, Pronouns, and Verbs in Action",
                            "summary": "Core foundational building blocks of English sentences.",
                            "content": "Nouns name entities, pronouns replace nouns, and verbs describe states and actions."
                        },
                        {
                            "slug": "adjectives-and-adverbs",
                            "title": "Modifiers: Adjectives and Adverbs",
                            "summary": "How adjectives modify nouns and adverbs modify verbs, adjectives, and other adverbs.",
                            "content": "Adjectives qualify nouns (a brilliant idea). Adverbs describe how, when, where, and to what degree."
                        }
                    ]
                },
                {
                    "title": "Module 2: Sentence Structure & Clauses",
                    "lessons": [
                        {
                            "slug": "clauses-and-sentence-types",
                            "title": "Clauses: Simple, Compound, and Complex Sentences",
                            "summary": "Independent vs dependent clauses, coordination, and subordination.",
                            "content": "A simple sentence contains one independent clause. Compound sentences join two independent clauses with coordinating conjunctions."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "articles-and-determiners",
            "title": "Articles & Determiners Masterclass",
            "category": "Mechanics",
            "difficulty": "All Levels",
            "summary": "Complete guide to 'a', 'an', 'the', zero articles, quantifiers, demonstratives, and phonetics.",
            "icon": "Bookmark",
            "order": 4,
            "modules": [
                {
                    "title": "Module 1: Indefinite and Definite Articles",
                    "lessons": [
                        {
                            "slug": "a-an-phonetic-rules",
                            "title": "Rules for 'A' vs 'An' & Phonetics",
                            "summary": "Using 'an' before vowel sounds (an honest man, an hour, a university).",
                            "content": "Article selection depends strictly on the phonetic initial sound of the following word, not its spelling."
                        },
                        {
                            "slug": "definite-and-zero-article",
                            "title": "The Definite Article 'The' and Zero Article",
                            "summary": "When to use 'the' and when to omit articles before plural, abstract, or proper nouns.",
                            "content": "Use 'the' for specific, unique, or previously referenced items. Omit articles before general plural or uncountable nouns."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "prepositions-and-phrasal-verbs",
            "title": "Prepositions & Prepositional Collocations",
            "category": "Vocabulary & Usage",
            "difficulty": "All Levels",
            "summary": "Prepositions of time, place, direction, movement, dependent prepositions, and common collocations.",
            "icon": "Compass",
            "order": 5,
            "modules": [
                {
                    "title": "Module 1: Prepositions of Time and Place",
                    "lessons": [
                        {
                            "slug": "in-on-at-mastery",
                            "title": "Mastering In, On, and At for Time and Place",
                            "summary": "The pyramid rule: general (In), specific (On), very precise (At).",
                            "content": "Time: in 2026, on Monday, at 5 PM. Place: in India, on MG Road, at the bus terminal."
                        },
                        {
                            "slug": "dependent-prepositions-collocations",
                            "title": "Dependent Prepositions and Confusing Pairs",
                            "summary": "Good at, interested in, angry with/at, prevent from, congratulated on.",
                            "content": "English verbs, adjectives, and nouns bond with fixed prepositions. Memorizing collocations prevents error transfer."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "active-and-passive-voice",
            "title": "Active & Passive Voice Transformations",
            "category": "Syntax",
            "difficulty": "Intermediate to Advanced",
            "summary": "Mechanics of voice transformation, tense preservation, auxiliary verbs, and academic writing usage.",
            "icon": "Repeat",
            "order": 6,
            "modules": [
                {
                    "title": "Module 1: Mechanics of Voice Conversion",
                    "lessons": [
                        {
                            "slug": "active-to-passive-rules",
                            "title": "Standard Rules for Converting Active to Passive",
                            "summary": "Object becomes subject, insert appropriate form of 'be', main verb becomes V3.",
                            "content": "Formula: Object + appropriate form of 'be' + Past Participle (V3) + [by Agent]."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "sentence-correction-and-error-spotting",
            "title": "Sentence Correction & Error Spotting",
            "category": "Examination & Advanced",
            "difficulty": "Advanced",
            "summary": "Systematic diagnostic strategies to spot and correct grammatical, syntactic, and structural errors.",
            "icon": "CheckCircle2",
            "order": 7,
            "modules": [
                {
                    "title": "Module 1: Diagnostic Error Identification",
                    "lessons": [
                        {
                            "slug": "systematic-error-spotting",
                            "title": "Systematic Framework for Spotting Grammar Errors",
                            "summary": "Check subject-verb agreement first, tense second, pronouns third, prepositions fourth.",
                            "content": "Follow a structured five-step diagnostic checklist when reviewing sentences in competitive examinations and professional writing."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "conjunctions-and-connectors",
            "title": "Conjunctions & Sentence Combination",
            "category": "Syntax & Connectors",
            "difficulty": "All Levels",
            "summary": "Master coordinating (FANBOYS), subordinating, and correlative conjunctions with proper punctuation and sentence flow.",
            "icon": "Link",
            "order": 8,
            "modules": [
                {
                    "title": "Module 1: Conjunction Types and Rules",
                    "lessons": [
                        {
                            "slug": "coordinating-conjunctions-fanboys",
                            "title": "Coordinating Conjunctions (FANBOYS)",
                            "summary": "Learn to join equal grammatical words, phrases, or clauses using For, And, Nor, But, Or, Yet, So.",
                            "content": "Coordinating conjunctions connect two words, phrases, or independent clauses of equal rank. The acronym FANBOYS stands for For, And, Nor, But, Or, Yet, So.\n\n### Punctuation Rule:\nWhen joining two independent clauses, always place a comma before the coordinating conjunction:\n*Example: The laboratory completed the test, but the results were inconclusive.*\n\nWhen joining two words or simple items, do not use a comma:\n*Example: She ordered tea and coffee.*"
                        },
                        {
                            "slug": "subordinating-and-correlative-conjunctions",
                            "title": "Subordinating & Correlative Conjunctions",
                            "summary": "Master dependent clause connectors (because, although, unless) and paired connectors (either/or, neither/nor, not only/but also).",
                            "content": "Subordinating conjunctions connect a dependent clause to an independent clause:\n*Examples: although, because, since, unless, whereas, if.*\n\n### Correlative Conjunctions:\nAlways appear in pairs: *either...or*, *neither...nor*, *not only...but also*, *both...and*.\nRule: Elements following each conjunction part must be parallel in structure."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "modifiers-and-participles",
            "title": "Modifiers & Participial Phrases",
            "category": "Sentence Structure",
            "difficulty": "Intermediate to Advanced",
            "summary": "Spot and fix misplaced modifiers, dangling participles, and clarify descriptive clauses.",
            "icon": "Target",
            "order": 9,
            "modules": [
                {
                    "title": "Module 1: Modifier Placement",
                    "lessons": [
                        {
                            "slug": "misplaced-and-dangling-modifiers",
                            "title": "Fixing Misplaced & Dangling Modifiers",
                            "summary": "Modifiers must appear immediately adjacent to the noun they modify.",
                            "content": "A modifier is a word, phrase, or clause that describes another word.\n\n### Misplaced Modifier:\nA modifier separated too far from the word it describes, causing confusion:\n*Incorrect: Walking through the library, the book was found by Ravi.*\n*Correct: Walking through the library, Ravi found the book.*\n\n### Dangling Modifier:\nA modifier where the noun being described is missing completely from the sentence."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "parallelism-in-sentences",
            "title": "Parallelism & Balanced Structures",
            "category": "Advanced Syntax",
            "difficulty": "Intermediate to Advanced",
            "summary": "Ensure grammatical symmetry in lists, comparisons, pairings, and series of actions.",
            "icon": "GitCommit",
            "order": 10,
            "modules": [
                {
                    "title": "Module 1: Parallel Grammar Structures",
                    "lessons": [
                        {
                            "slug": "parallel-lists-and-paired-items",
                            "title": "Parallelism in Lists, Series & Comparisons",
                            "summary": "Items in a list or series must share identical grammatical forms (all gerunds, all infinitives, or all nouns).",
                            "content": "Parallelism means using similar grammatical form for words, phrases, or clauses with the same grammatical function.\n\n### Non-parallel vs Parallel:\n*Incorrect: She likes dancing, to swim, and reading.*\n*Correct: She likes dancing, swimming, and reading.*\n\n### Comparison Parallelism:\n*Incorrect: Driving a car is faster than to ride a bicycle.*\n*Correct: Driving a car is faster than riding a bicycle.*"
                        }
                    ]
                }
            ]
        },
        {
            "slug": "relative-pronouns-and-clauses",
            "title": "Relative Pronouns & Clauses",
            "category": "Syntax",
            "difficulty": "All Levels",
            "summary": "Master who, whom, whose, which, that, and understand defining vs non-defining relative clauses.",
            "icon": "Users",
            "order": 11,
            "modules": [
                {
                    "title": "Module 1: Relative Pronoun Usage",
                    "lessons": [
                        {
                            "slug": "who-whom-whose-which-that",
                            "title": "Choosing Between Who, Whom, Which, and That",
                            "summary": "Who is for subjects, whom is for objects, which is for things in non-defining clauses, and that is for essential defining clauses.",
                            "content": "### Subject vs Object Pronouns:\n- **Who:** acts as subject (*The professor who gave the lecture is renowned.*)\n- **Whom:** acts as object (*The author whom we interviewed yesterday was insightful.*)\n- **Whose:** shows possession (*The student whose project won first prize received an award.*)\n- **That vs Which:** Use 'that' for essential (restrictive) clauses without commas; use 'which' for non-essential (non-restrictive) clauses preceded by a comma."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "para-jumbles-and-rearrangement",
            "title": "Para Jumbles & Sentence Rearrangement",
            "category": "Reading & Writing Skills",
            "difficulty": "Advanced",
            "summary": "Strategies for discovering introductory sentences, pronoun references, chronological transitions, and concluding thoughts.",
            "icon": "Shuffle",
            "order": 12,
            "modules": [
                {
                    "title": "Module 1: Paragraph Coherence & Order",
                    "lessons": [
                        {
                            "slug": "logical-sentence-sequencing",
                            "title": "Logical Sentence Sequencing Strategies",
                            "summary": "Identify opening themes, match noun-pronoun antecedents, and link cause-and-effect transitions.",
                            "content": "Para jumbles require assembling scrambled sentences into a coherent, logically sound paragraph.\n\n### Key Strategies:\n1. **Identify the Opening Sentence:** Look for an independent idea that introduces the main topic without starting with pronouns (he, she, they) or contrast words (however, but).\n2. **Look for Transition Connectors:** Words like 'Furthermore', 'Consequently', and 'In contrast' signal connections.\n3. **Noun-Pronoun Pairs:** A noun must precede its pronoun.\n4. **Chronology:** Follow time sequences (past → present → future)."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "conditionals-and-hypotheticals",
            "title": "Conditionals & Hypothetical Sentences",
            "category": "Tenses & Syntax",
            "difficulty": "Intermediate to Advanced",
            "summary": "Master Zero, First, Second, Third, and Mixed conditionals for real facts, possibilities, and unreal past situations.",
            "icon": "HelpCircle",
            "order": 13,
            "modules": [
                {
                    "title": "Module 1: The Four Main Conditionals",
                    "lessons": [
                        {
                            "slug": "zero-first-second-third-conditionals",
                            "title": "Complete Guide to Conditionals (0, 1, 2, 3)",
                            "summary": "Learn the exact clause formulas and verb tenses for every conditional type.",
                            "content": "### 1. Zero Conditional (General Truths / Facts):\n*Formula:* If + Simple Present, ... Simple Present.\n*Example:* If you heat ice, it melts.\n\n### 2. First Conditional (Real Future Possibility):\n*Formula:* If + Simple Present, ... will + V1 (base verb).\n*Example:* If it rains tomorrow, we will postpone the match.\n\n### 3. Second Conditional (Hypothetical / Unreal Present):\n*Formula:* If + Simple Past, ... would + V1.\n*Example:* If I had a million dollars, I would travel the world.\n*(Note: Use 'were' for all persons: 'If I were you...')*\n\n### 4. Third Conditional (Unreal Past Regret):\n*Formula:* If + Past Perfect (had + V3), ... would have + V3.\n*Example:* If you had studied harder, you would have passed the examination."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "direct-and-reported-speech",
            "title": "Direct & Reported (Indirect) Speech",
            "category": "Advanced Syntax",
            "difficulty": "Intermediate to Advanced",
            "summary": "Rules for shifting tenses, updating pronouns, time and place adverb changes, and converting questions.",
            "icon": "MessageSquare",
            "order": 14,
            "modules": [
                {
                    "title": "Module 1: Speech Transformation Rules",
                    "lessons": [
                        {
                            "slug": "tense-backshift-and-reporting-verbs",
                            "title": "Tense Backshifts & Pronoun Changes",
                            "summary": "When the reporting verb is in the past, backshift present tenses to past tenses.",
                            "content": "Reported speech conveys what someone said without quoting their exact words.\n\n### Tense Backshift Rules:\n- Simple Present → Simple Past (*\"I study hard\" → He said that he studied hard.*)\n- Present Continuous → Past Continuous (*\"I am writing\" → She said she was writing.*)\n- Simple Past → Past Perfect (*\"I saw him\" → He said he had seen him.*)\n- Will → Would (*\"I will call\" → She said she would call.*)\n\n### Time & Place Shifts:\n- today → that day\n- tomorrow → the following day\n- yesterday → the previous day\n- here → there"
                        }
                    ]
                }
            ]
        },
        {
            "slug": "modal-verbs-and-auxiliaries",
            "title": "Modal Verbs & Helping Auxiliaries",
            "category": "Verbs & Mechanics",
            "difficulty": "All Levels",
            "summary": "Understand can, could, may, might, must, should, would, ought to for ability, permission, necessity, and advice.",
            "icon": "Award",
            "order": 15,
            "modules": [
                {
                    "title": "Module 1: Modal Auxiliary Usage",
                    "lessons": [
                        {
                            "slug": "modals-of-ability-permission-obligation",
                            "title": "Modals of Ability, Obligation & Deduction",
                            "summary": "Modal verbs do not take -s in third person and are followed directly by the base verb (V1).",
                            "content": "Modals express mood, possibility, ability, permission, and necessity.\n\n### Key Modal Rules:\n1. Never add '-s' to a modal (*He can, NOT He cans*).\n2. Follow with the base infinitive without 'to' (*You must go, NOT You must to go*).\n\n### Modal Functions:\n- **Can / Could:** Ability or polite requests.\n- **May / Might:** Possibility or formal permission.\n- **Must / Have to:** Strong necessity or logical deduction.\n- **Should / Ought to:** Recommendation, duty, or moral advice."
                        }
                    ]
                }
            ]
        },
        {
            "slug": "question-tags-mastery",
            "title": "Question Tags & Short Responses",
            "category": "Everyday Conversation",
            "difficulty": "Beginner to Intermediate",
            "summary": "Master the polarity rule (positive statement = negative tag), auxiliary matching, and irregular tags like 'aren't I?'.",
            "icon": "HelpCircle",
            "order": 16,
            "modules": [
                {
                    "title": "Module 1: Question Tag Polarity",
                    "lessons": [
                        {
                            "slug": "polarity-and-auxiliary-matching",
                            "title": "The Polarity Rule & Auxiliary Matching",
                            "summary": "Positive statements take negative tags; negative statements take positive tags.",
                            "content": "Question tags are short questions added to the end of a statement to ask for agreement or confirmation.\n\n### The Golden Rule of Polarity:\n- **Positive statement → Negative tag:** *She is an engineer, isn't she?*\n- **Negative statement → Positive tag:** *You don't like spicy food, do you?*\n\n### Special Cases:\n- *I am right, aren't I?* (Never 'amn't I')\n- *Let's go for lunch, shall we?*\n- *Open the door, will you?* (Imperatives)"
                        }
                    ]
                }
            ]
        },
        {
            "slug": "punctuation-and-mechanics",
            "title": "Punctuation & Capitalization Mechanics",
            "category": "Writing Mechanics",
            "difficulty": "All Levels",
            "summary": "Proper usage of commas, semicolons, colons, apostrophes, quotation marks, and capitalization rules.",
            "icon": "FileCheck",
            "order": 17,
            "modules": [
                {
                    "title": "Module 1: Punctuation Essentials",
                    "lessons": [
                        {
                            "slug": "commas-semicolons-colons",
                            "title": "Commas, Semicolons & Colons",
                            "summary": "Avoid comma splices by using semicolons or coordinating conjunctions between independent clauses.",
                            "content": "Accurate punctuation ensures clarity and prevents misinterpretation.\n\n### The Semicolon (;):\nLinks two independent clauses that are closely related in thought without a conjunction:\n*Example: The sun had set; the temperature began to drop rapidly.*\n\n### The Colon (:):\nIntroduces a list, explanation, or elaboration following an independent clause:\n*Example: Please bring three items: a notebook, a pencil, and an eraser.*\n\n### The Comma (,):\nUsed after introductory clauses, between items in a series, and before coordinating conjunctions connecting independent clauses."
                        }
                    ]
                }
            ]
        }
    ]

    for c_data in additional_courses_data:
        course_obj = Course(
            slug=c_data["slug"],
            title=c_data["title"],
            category=c_data["category"],
            difficulty=c_data["difficulty"],
            summary=c_data["summary"],
            icon=c_data["icon"],
            order_index=c_data["order"]
        )
        db.add(course_obj)
        db.flush()

        for m_idx, m_data in enumerate(c_data["modules"], start=1):
            mod_obj = Module(
                course_id=course_obj.id,
                title=m_data["title"],
                summary=m_data.get("summary", ""),
                order_index=m_idx
            )
            db.add(mod_obj)
            db.flush()

            for l_idx, l_data in enumerate(m_data["lessons"], start=1):
                lesson_obj = Lesson(
                    course_id=course_obj.id,
                    module_id=mod_obj.id,
                    slug=l_data["slug"],
                    title=l_data["title"],
                    order_index=l_idx,
                    reading_time_mins=8,
                    difficulty=c_data["difficulty"],
                    concept_summary=l_data["summary"],
                    formula_structure="Standard grammatical structures apply.",
                    rules_json=json.dumps(["Follow standard English grammar rules without negative L1 transfer."]),
                    positive_examples_json=json.dumps(["The academic report presented clear and verified experimental results."]),
                    negative_examples_json=json.dumps(["The academic report presenting unverified result."]),
                    question_examples_json=json.dumps(["Did the researcher follow standard protocol?"]),
                    common_mistakes_json=json.dumps([{
                        "wrong": "She is good in English.",
                        "right": "She is good at English.",
                        "explanation": "Use 'good at' for skills, abilities, and academic subjects."
                    }]),
                    content_markdown=f"# {l_data['title']}\n\n{l_data['content']}\n\n## Practice & Revision\nReview the rules and attempt the interactive exercises below."
                )
                db.add(lesson_obj)
                db.flush()

                # Sample exercise for each lesson
                ex_obj = Exercise(
                    lesson_id=lesson_obj.id,
                    course_id=course_obj.id,
                    exercise_type="mcq",
                    question_text=f"Which sentence demonstrates correct grammatical usage for {l_data['title']}?",
                    options_json=json.dumps([
                        "She completed her assignment on time with great care.",
                        "She completing her assignment on time with great care.",
                        "She have completed her assignment on time with great care.",
                        "She was complete her assignment on time with great care."
                    ]),
                    correct_answer="She completed her assignment on time with great care.",
                    explanation="The subject and verb agree properly in the simple past tense.",
                    difficulty="Intermediate"
                )
                db.add(ex_obj)

        # Final quiz for each course
        quiz_obj = Quiz(
            course_id=course_obj.id,
            title=f"{c_data['title']} Comprehensive Assessment",
            description=f"Test your mastery across all concepts taught in {c_data['title']}.",
            passing_score_pct=80.0,
            is_final_assessment=True
        )
        db.add(quiz_obj)
        db.flush()

        qq_obj = QuizQuestion(
            quiz_id=quiz_obj.id,
            question_text=f"Select the grammatically accurate sentence according to {c_data['title']} rules:",
            options_json=json.dumps([
                "The findings of the study were confirmed by three independent laboratories.",
                "The findings of the study was confirmed by three independent laboratories.",
                "The findings of the study is confirmed by three independent laboratories.",
                "The findings of the study has confirmed by three independent laboratories."
            ]),
            correct_answer="The findings of the study were confirmed by three independent laboratories.",
            explanation="The plural subject 'findings' takes the plural auxiliary 'were'.",
            points=1
        )
        db.add(qq_obj)

    db.commit()
    print("Successfully seeded all courses, modules, lessons, exercises, and assessments!")
    db.close()

if __name__ == "__main__":
    seed_database(force=True)
