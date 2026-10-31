import os
import sys
import re
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from typing import Tuple, List, Dict

LABELS = {
    0: "CORRECT",
    1: "TENSE_ERROR",
    2: "SVA_ERROR",
    3: "ARTICLE_ERROR",
    4: "PREPOSITION_ERROR",
    5: "SPELLING_ERROR",
    6: "STRUCTURE_ERROR",
}

LABEL_NAMES = {v: k for k, v in LABELS.items()}


class GrammarDataset(Dataset):
    """
    PyTorch Dataset for Grammar Error Classification.
    Accepts raw sentences, numerical class labels, and an initialized TextPreprocessor.
    """
    def __init__(self, sentences: List[str], labels: List[int], preprocessor):
        self.sentences = list(sentences)
        self.labels = list(labels)
        self.preprocessor = preprocessor

    def __len__(self) -> int:
        return len(self.sentences)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        sentence = self.sentences[idx]
        label = self.labels[idx]
        encoded = self.preprocessor.encode(sentence)
        return torch.tensor(encoded, dtype=torch.long), torch.tensor(label, dtype=torch.long)


def generate_dataset() -> pd.DataFrame:
    """
    Synthesizes 1,050+ labeled English sentences covering all 7 categories (150+ per class),
    focusing on authentic Telugu L1 interference patterns, Indian English learner challenges,
    and standard grammatical corrections.
    """
    rows = []

    def add_sample(sentence: str, label: int, correction: str, explanation: str):
        rows.append({
            "sentence": sentence.strip(),
            "label": label,
            "label_name": LABELS[label],
            "correction": correction.strip(),
            "explanation": explanation.strip()
        })

    # =========================================================================
    # CLASS 0: CORRECT (160+ samples)
    # Natural, fully grammatical sentences across diverse academic, professional,
    # domestic, and conversational topics.
    # =========================================================================
    correct_seeds = [
        ("I go to school every day by bus.", "I go to school every day by bus.", "Correct sentence."),
        ("She completed her engineering degree last year with high honors.", "She completed her engineering degree last year with high honors.", "Correct sentence."),
        ("My brother works at a software company in Hyderabad.", "My brother works at a software company in Hyderabad.", "Correct sentence."),
        ("We have been living in this apartment for five years.", "We have been living in this apartment for five years.", "Correct sentence."),
        ("The sun rises in the east and sets in the west.", "The sun rises in the east and sets in the west.", "Correct sentence."),
        ("He is an honest police officer who serves his country.", "He is an honest police officer who serves his country.", "Correct sentence."),
        ("The students are preparing diligently for their semester exams.", "The students are preparing diligently for their semester exams.", "Correct sentence."),
        ("I bought an umbrella because the sky looked cloudy.", "I bought an umbrella because the sky looked cloudy.", "Correct sentence."),
        ("She speaks three languages fluently including English and Telugu.", "She speaks three languages fluently including English and Telugu.", "Correct sentence."),
        ("The professor explained the machine learning concept clearly.", "The professor explained the machine learning concept clearly.", "Correct sentence."),
        ("We enjoyed our family vacation in Visakhapatnam last summer.", "We enjoyed our family vacation in Visakhapatnam last summer.", "Correct sentence."),
        ("He does not like spicy food very much.", "He does not like spicy food very much.", "Correct sentence."),
        ("Could you please send me the meeting minutes by evening?", "Could you please send me the meeting minutes by evening?", "Correct sentence."),
        ("They played football in the college ground until sunset.", "They played football in the college ground until sunset.", "Correct sentence."),
        ("My parents visited the temple on Sunday morning.", "My parents visited the temple on Sunday morning.", "Correct sentence."),
        ("The express train arrived on platform number four on time.", "The express train arrived on platform number four on time.", "Correct sentence."),
        ("He has already submitted the final project report to the mentor.", "He has already submitted the final project report to the mentor.", "Correct sentence."),
        ("I usually drink a cup of warm tea before starting work.", "I usually drink a cup of warm tea before starting work.", "Correct sentence."),
        ("She solved all the complex mathematics problems correctly.", "She solved all the complex mathematics problems correctly.", "Correct sentence."),
        ("The public library provides high speed internet access to everyone.", "The public library provides high speed internet access to everyone.", "Correct sentence."),
        ("Neither Rahul nor his brother was present at the function.", "Neither Rahul nor his brother was present at the function.", "Correct sentence."),
        ("Every student in the classroom received a certificate of completion.", "Every student in the classroom received a certificate of completion.", "Correct sentence."),
        ("He is interested in learning artificial intelligence and data science.", "He is interested in learning artificial intelligence and data science.", "Correct sentence."),
        ("She congratulated her friend on winning the debate championship.", "She congratulated her friend on winning the debate championship.", "Correct sentence."),
        ("The weather in Bangalore is very pleasant during winter.", "The weather in Bangalore is very pleasant during winter.", "Correct sentence."),
        ("I have known him since our early school days in Vijayawada.", "I have known him since our early school days in Vijayawada.", "Correct sentence."),
        ("Do you know where the nearest medical store is located?", "Do you know where the nearest medical store is located?", "Correct sentence."),
        ("They decided to travel to Ooty during the holidays.", "They decided to travel to Ooty during the holidays.", "Correct sentence."),
        ("He wrote a thoughtful email to the project manager.", "He wrote a thoughtful email to the project manager.", "Correct sentence."),
        ("The dog barked loudly when the stranger approached the gate.", "The dog barked loudly when the stranger approached the gate.", "Correct sentence."),
        ("Mount Everest is the highest mountain peak in the world.", "Mount Everest is the highest mountain peak in the world.", "Correct sentence."),
        ("She works as a senior software architect in Bengaluru.", "She works as a senior software architect in Bengaluru.", "Correct sentence."),
        ("The children were playing happily in the neighborhood park.", "The children were playing happily in the neighborhood park.", "Correct sentence."),
        ("I will call you as soon as I reach the airport.", "I will call you as soon as I reach the airport.", "Correct sentence."),
        ("He answered all the interview questions with great confidence.", "He answered all the interview questions with great confidence.", "Correct sentence."),
        ("We should protect our environment by planting more trees.", "We should protect our environment by planting more trees.", "Correct sentence."),
        ("She made a delicious South Indian meal for the guests.", "She made a delicious South Indian meal for the guests.", "Correct sentence."),
        ("He was reading an interesting novel throughout the train journey.", "He was reading an interesting novel throughout the train journey.", "Correct sentence."),
        ("The conference will begin at nine o'clock tomorrow morning.", "The conference will begin at nine o'clock tomorrow morning.", "Correct sentence."),
        ("They celebrated their wedding anniversary with close relatives.", "They celebrated their wedding anniversary with close relatives.", "Correct sentence.")
    ]
    for s, c, e in correct_seeds:
        add_sample(s, 0, c, e)

    # Systematic generation for CORRECT (125 more samples)
    subjects = ["My sister", "The manager", "Our team", "The principal", "The doctor", "A young researcher", "The chief guest", "His uncle", "The librarian", "My cousin"]
    verbs_obj = [
        ("published a research paper in a reputed journal", "published a research paper in a reputed journal"),
        ("inspected the new laboratory facilities carefully", "inspected the new laboratory facilities carefully"),
        ("delivered an inspiring keynote speech at the seminar", "delivered an inspiring keynote speech at the seminar"),
        ("organized a blood donation camp in the village", "organized a blood donation camp in the village"),
        ("planted twenty fruit saplings in the college garden", "planted twenty fruit saplings in the college garden"),
        ("repaired the electrical wiring in the computer lab", "repaired the electrical wiring in the computer lab"),
        ("donated ten thousand rupees to the local orphanage", "donated ten thousand rupees to the local orphanage"),
        ("reviewed the annual budget proposals thoroughly", "reviewed the annual budget proposals thoroughly"),
        ("guided the final year students with their projects", "guided the final year students with their projects"),
        ("distributed study materials to all registered participants", "distributed study materials to all registered participants"),
        ("monitored the examination hall with strict vigilance", "monitored the examination hall with strict vigilance"),
        ("designed an intuitive user interface for the mobile app", "designed an intuitive user interface for the mobile app"),
        ("attended the international technical symposium in Delhi", "attended the international technical symposium in Delhi")
    ]
    for sub in subjects:
        for v, cv in verbs_obj:
            add_sample(f"{sub} {v}.", 0, f"{sub} {cv}.", "Correct sentence.")

    # =========================================================================
    # CLASS 1: TENSE_ERROR (160+ samples)
    # Telugu L1 interference:
    # 1. Present continuous used for completed past actions ("Yesterday I am going")
    # 2. Stative verbs used in continuous form ("I am knowing", "He is having")
    # 3. 'Did' with past tense verb ("Did you completed", "I didn't saw")
    # 4. Present continuous with 'since/for' ("Since three years I am working")
    # 5. Future conditional duplication ("When you will come, I will give")
    # 6. Present perfect with past time adverb ("He has arrived yesterday")
    # =========================================================================
    tense_seeds = [
        ("Yesterday I am going to college by bus.", "Yesterday I went to college by bus.", "Use simple past tense for past completed actions instead of present continuous."),
        ("Last night she is cooking biryani for dinner.", "Last night she cooked biryani for dinner.", "Use simple past tense for actions completed in the past."),
        ("Yesterday my father is purchasing a new motorcycle.", "Yesterday my father purchased a new motorcycle.", "Use simple past tense with past time markers like 'yesterday'."),
        ("Did you completed your practical record yesterday?", "Did you complete your practical record yesterday?", "Auxiliary 'did' must be followed by base form of verb."),
        ("I didn't saw him at the railway station.", "I didn't see him at the railway station.", "Auxiliary 'didn't' requires the base form of the verb."),
        ("Did she told you about the class test schedule?", "Did she tell you about the class test schedule?", "Use base verb 'tell' after auxiliary 'did'."),
        ("Why did you went to the market in the rain?", "Why did you go to the market in the rain?", "Use base form 'go' with auxiliary 'did'."),
        ("He did not brought his identity card to college.", "He did not bring his identity card to college.", "Use base form 'bring' after 'did not'."),
        ("He is having three elder brothers in village.", "He has three elder brothers in the village.", "Stative verb 'have' indicating possession does not take continuous aspect."),
        ("I am knowing the answer to this question very well.", "I know the answer to this question very well.", "Stative verb 'know' cannot be used in continuous tense."),
        ("She is understanding the mathematical formulas easily.", "She understands the mathematical formulas easily.", "Stative verb 'understand' is not used in continuous form."),
        ("We are liking South Indian food very much.", "We like South Indian food very much.", "Stative verb 'like' expresses a state and should be in simple present."),
        ("They are wanting more time to submit assignments.", "They want more time to submit assignments.", "Stative verb 'want' should not be used in continuous form."),
        ("Since three years I am living in this hostel.", "I have been living in this hostel for three years.", "Use present perfect continuous for actions continuing from the past."),
        ("Since morning she is waiting for the interview call.", "She has been waiting for the interview call since morning.", "Use present perfect continuous with 'since' for continuous duration."),
        ("We are staying in Hyderabad since five years.", "We have been staying in Hyderabad for five years.", "Use present perfect continuous tense and 'for' with duration."),
        ("When you will come to my house, I will give notes.", "When you come to my house, I will give notes.", "Do not use 'will' in subordinate time clauses."),
        ("If it will rain tomorrow, the match will be cancelled.", "If it rains tomorrow, the match will be cancelled.", "Use simple present in first conditional 'if' clauses."),
        ("Until he will apologize, I will not talk to him.", "Until he apologizes, I will not talk to him.", "Subordinate clauses introduced by 'until' use present tense."),
        ("He has completed his graduation in 2020.", "He completed his graduation in 2020.", "Do not use present perfect with specific past time adverbs like 'in 2020'."),
        ("She has visited Tirupati last month with family.", "She visited Tirupati last month with family.", "Use simple past tense with past time markers like 'last month'."),
        ("They have arrived yesterday night from Guntur.", "They arrived last night from Guntur.", "Use simple past with past time adverbs instead of present perfect."),
        ("Last year I am writing the entrance examination.", "Last year I wrote the entrance examination.", "Use simple past tense for past events."),
        ("Tomorrow they came to our house for lunch.", "Tomorrow they will come to our house for lunch.", "Use future tense for future events instead of past tense."),
        ("He was knowing the secret since last month.", "He had known the secret since last month.", "Stative verb 'know' should not be in continuous form.")
    ]
    for s, c, e in tense_seeds:
        add_sample(s, 1, c, e)

    # Systematic generation for TENSE_ERROR (140 more samples)
    time_markers = ["Yesterday", "Last Sunday", "Last week", "Last month", "Two days ago"]
    subjects_tense = ["Ramesh", "Priya", "My brother", "The teacher", "The student", "Suresh", "My friend"]
    actions_tense = [
        ("is writing the final exam", "wrote the final exam", "Use simple past tense for actions completed in the past."),
        ("is watching a Telugu movie", "watched a Telugu movie", "Use simple past tense with past time adverb."),
        ("is submitting the college fee", "submitted the college fee", "Use simple past tense for past events."),
        ("is buying a new laptop", "bought a new laptop", "Use simple past tense instead of present continuous with past time markers."),
        ("is traveling to Vijayawada", "traveled to Vijayawada", "Past events require simple past tense."),
    ]
    for tm in time_markers:
        for sub in subjects_tense:
            for act_err, act_cor, expl in actions_tense:
                add_sample(f"{tm} {sub} {act_err}.", 1, f"{tm} {sub} {act_cor}.", expl)

    # =========================================================================
    # CLASS 2: SVA_ERROR (Subject-Verb Agreement) (160+ samples)
    # Telugu speakers dropping 3rd person singular -s or confusing singular/plural
    # subjects with auxiliary verbs:
    # 1. Omission of 3rd person singular -s ("She go", "He work")
    # 2. Plural subjects with singular verb ("The children likes", "They was")
    # 3. Indefinite pronouns with plural verb ("Every student have", "Everyone want")
    # 4. "One of my friends are"
    # 5. "He don't know"
    # =========================================================================
    sva_seeds = [
        ("She go to school every day by auto.", "She goes to school every day by auto.", "Third-person singular subjects take verbs ending in -s/-es in simple present."),
        ("He work in a multinational software company.", "He works in a multinational software company.", "Third-person singular subject requires the verb to take -s."),
        ("The teacher teach English grammar very well.", "The teacher teaches English grammar very well.", "Singular noun 'teacher' requires singular verb 'teaches'."),
        ("My mother cook delicious sambar every Sunday.", "My mother cooks delicious sambar every Sunday.", "Third-person singular subject requires singular verb 'cooks'."),
        ("The bus stop right in front of our apartment.", "The bus stops right in front of our apartment.", "Singular subject 'bus' requires verb ending in -s."),
        ("The dog bark at strangers during the night.", "The dog barks at strangers during the night.", "Singular subject requires third-person singular verb."),
        ("He speak three different languages very fluently.", "He speaks three different languages very fluently.", "Subject 'he' requires verb with -s."),
        ("The sun give light and heat to our planet.", "The sun gives light and heat to our planet.", "Singular subject 'sun' takes verb 'gives'."),
        ("One of my friends are living in the United States.", "One of my friends is living in the United States.", "'One of + plural noun' takes a singular verb."),
        ("One of the teachers were absent yesterday.", "One of the teachers was absent yesterday.", "Subject is 'one', requiring singular verb 'was'."),
        ("One of these mobile phones belong to my brother.", "One of these mobile phones belongs to my brother.", "Subject 'one' takes singular verb 'belongs'."),
        ("Every student in the college have a library card.", "Every student in the college has a library card.", "'Every' takes a singular verb 'has'."),
        ("Everyone want to become a successful software developer.", "Everyone wants to become a successful software developer.", "Indefinite pronoun 'everyone' is singular and requires 'wants'."),
        ("Each of the candidates were interviewed separately.", "Each of the candidates was interviewed separately.", "'Each' is singular and requires 'was'."),
        ("Somebody have left their umbrella in the classroom.", "Somebody has left their umbrella in the classroom.", "'Somebody' is an indefinite singular pronoun requiring 'has'."),
        ("The children likes playing cricket in the evening.", "The children like playing cricket in the evening.", "Plural subject 'children' requires plural verb 'like'."),
        ("My brothers lives in Bangalore for their studies.", "My brothers live in Bangalore for their studies.", "Plural subject 'brothers' takes plural verb 'live'."),
        ("The students was shouting loudly in the corridor.", "The students were shouting loudly in the corridor.", "Plural subject 'students' requires plural past verb 'were'."),
        ("They was waiting for the train at the platform.", "They were waiting for the train at the platform.", "Plural pronoun 'they' requires 'were' instead of 'was'."),
        ("These mangoes tastes very sweet and delicious.", "These mangoes taste very sweet and delicious.", "Plural noun 'mangoes' requires plural verb 'taste'."),
        ("He don't know the answer to this simple question.", "He doesn't know the answer to this simple question.", "Third-person singular 'he' requires negative auxiliary 'doesn't'."),
        ("She don't like drinking black coffee without milk.", "She doesn't like drinking black coffee without milk.", "Use 'doesn't' with third-person singular pronoun 'she'."),
        ("The quality of these mangoes are not satisfactory.", "The quality of these mangoes is not satisfactory.", "The head noun 'quality' is singular, so the verb must be 'is'."),
        ("Neither Ravi nor Suresh were present in the meeting.", "Neither Ravi nor Suresh was present in the meeting.", "When singular subjects are joined by 'neither...nor', the verb is singular."),
        ("Mathematics are a very difficult subject for many.", "Mathematics is a very difficult subject for many.", "Academic subjects ending in -s take a singular verb.")
    ]
    for s, c, e in sva_seeds:
        add_sample(s, 2, c, e)

    # Systematic generation for SVA_ERROR (140 more samples)
    sva_sing_subjects = ["Rahul", "Anitha", "My uncle", "The mechanic", "The driver", "Our watchman", "The gardener"]
    sva_verbs_base = [
        ("drive very carefully on highway", "drives very carefully on highway", "Singular subject requires third-person singular verb with -s."),
        ("write poems in Telugu language", "writes poems in Telugu language", "Third-person singular subject requires verb ending in -s."),
        ("play chess with great patience", "plays chess with great patience", "Singular subject requires singular verb 'plays'."),
        ("know the shortcut route to temple", "knows the shortcut route to temple", "Third-person singular subject takes 'knows'."),
        ("wake up early at five AM", "wakes up early at five AM", "Subject requires verb with -s for habitual action."),
        ("clean the room every morning", "cleans the room every morning", "Singular subject takes 'cleans'."),
        ("read newspaper before breakfast", "reads newspaper before breakfast", "Singular subject takes verb with -s.")
    ]
    for sub in sva_sing_subjects:
        for vb, vc, expl in sva_verbs_base:
            add_sample(f"{sub} {vb}.", 2, f"{sub} {vc}.", expl)

    sva_plural_subjects = ["The boys", "The girls", "Both students", "The workers", "The police officers", "My friends", "The players"]
    sva_plural_verbs_err = [
        ("was participating in the annual tournament", "were participating in the annual tournament", "Plural subject requires plural verb 'were'."),
        ("has completed the ground maintenance work", "have completed the ground maintenance work", "Plural subject requires plural auxiliary 'have'."),
        ("is demanding higher monthly salaries", "are demanding higher monthly salaries", "Plural subject takes plural verb 'are'."),
        ("likes watching Telugu cinema together", "like watching Telugu cinema together", "Plural subject takes base verb form without -s.")
    ]
    for sub in sva_plural_subjects:
        for vb, vc, expl in sva_plural_verbs_err:
            add_sample(f"{sub} {vb}.", 2, f"{sub} {vc}.", expl)

    sva_one_of_subjects = ["One of my cousins", "One of the players", "One of the doctors", "One of our neighbors"]
    sva_one_of_verbs = [
        ("are working in Hyderabad IT corridor", "is working in Hyderabad IT corridor", "'One of + plural noun' takes singular verb 'is'."),
        ("were selected for state cricket team", "was selected for state cricket team", "Head subject is singular 'one', requiring 'was'."),
        ("have won first prize in competition", "has won first prize in competition", "Singular head 'one' requires singular auxiliary 'has'."),
        ("know how to speak German fluently", "knows how to speak German fluently", "'One of' takes singular verb ending in -s.")
    ]
    for sub in sva_one_of_subjects:
        for vb, vc, expl in sva_one_of_verbs:
            add_sample(f"{sub} {vb}.", 2, f"{sub} {vc}.", expl)

    sva_extra_cases = [
        ("Neither of the candidates are qualified for the position.", "Neither of the candidates is qualified for the position.", "'Neither of' takes a singular verb."),
        ("Neither of the buses go to the railway station.", "Neither of the buses goes to the railway station.", "'Neither of' requires singular verb 'goes'."),
        ("Either of the two options are acceptable to us.", "Either of the two options is acceptable to us.", "'Either of' requires singular verb 'is'."),
        ("A large number of students was protesting outside.", "A large number of students were protesting outside.", "'A number of + plural noun' takes a plural verb."),
        ("The police is investigating the theft case in town.", "The police are investigating the theft case in town.", "'Police' is a plural noun and takes 'are'."),
        ("A pair of leather shoes were left near the temple door.", "A pair of leather shoes was left near the temple door.", "'A pair of' is singular and requires 'was'."),
        ("The cattle is grazing peacefully in the green pasture.", "The cattle are grazing peacefully in the green pasture.", "'Cattle' is a plural collective noun requiring 'are'."),
        ("The majority of members was absent from the meeting.", "The majority of members were absent from the meeting.", "'Majority of + plural noun' takes plural verb 'were'."),
        ("My father work in the postal department.", "My father works in the postal department.", "Singular third person subject requires verb ending in -s."),
        ("His uncle run a small grocery shop in market.", "His uncle runs a small grocery shop in the market.", "Third person singular subject requires 'runs'."),
        ("The software engineer test the code carefully.", "The software engineer tests the code carefully.", "Singular subject requires verb with -s."),
        ("The security guard patrol the apartment at night.", "The security guard patrols the apartment at night.", "Singular subject takes 'patrols'."),
        ("The chef prepare delicious South Indian meals.", "The chef prepares delicious South Indian meals.", "Singular subject takes 'prepares'."),
        ("The farmer cultivate paddy in five acres of land.", "The farmer cultivates paddy in five acres of land.", "Singular subject takes 'cultivates'."),
        ("The tailor stitch formal shirts perfectly.", "The tailor stitches formal shirts perfectly.", "Singular subject takes 'stitches'."),
        ("Our professor explain difficult topics simply.", "Our professor explains difficult topics simply.", "Singular subject takes 'explains'."),
        ("The postman deliver letters around noon every day.", "The postman delivers letters around noon every day.", "Singular subject takes 'delivers'."),
        ("The electrician repair the ceiling fan quickly.", "The electrician repairs the ceiling fan quickly.", "Singular subject takes 'repairs'."),
        ("We was discussing the project roadmap yesterday.", "We were discussing the project roadmap yesterday.", "Plural pronoun 'we' requires 'were'."),
        ("They has submitted their laboratory records on time.", "They have submitted their laboratory records on time.", "Plural subject takes 'have'."),
        ("You was not present in the morning seminar.", "You were not present in the morning seminar.", "Pronoun 'you' always takes plural verb 'were'."),
        ("The children plays with paper boats in the rain.", "The children play with paper boats in the rain.", "Plural subject 'children' takes base verb 'play'."),
        ("These sweet mangoes is very fresh and delicious.", "These sweet mangoes are very fresh and delicious.", "Plural subject requires 'are'."),
        ("Each of the participants have received a gift kit.", "Each of the participants has received a gift kit.", "'Each of' takes singular auxiliary 'has'."),
        ("Everyone in the auditorium want to ask questions.", "Everyone in the auditorium wants to ask questions.", "Indefinite pronoun 'everyone' takes singular verb 'wants'."),
        ("Someone have broken the computer laboratory window.", "Someone has broken the computer laboratory window.", "'Someone' requires singular auxiliary 'has'."),
        ("Nobody know where the confidential files are kept.", "Nobody knows where the confidential files are kept.", "'Nobody' takes singular verb 'knows'."),
        ("Both of the candidates is suitable for the scholarship.", "Both of the candidates are suitable for the scholarship.", "'Both of' takes plural verb 'are'."),
        ("A lot of students has enrolled in the online course.", "A lot of students have enrolled in the online course.", "'A lot of students' takes plural verb 'have'."),
        ("Neither Ravi nor his friends was invited to dinner.", "Neither Ravi nor his friends were invited to dinner.", "Verb agrees with the closer plural subject 'friends'."),
        ("The cost of essential commodities have increased rapidly.", "The cost of essential commodities has increased rapidly.", "Head noun 'cost' is singular, requiring 'has'."),
        ("The bouquet of red roses smell very sweet.", "The bouquet of red roses smells very sweet.", "Head noun 'bouquet' is singular, requiring 'smells'."),
        ("Every man and woman were given equal opportunity.", "Every man and woman was given equal opportunity.", "'Every' requires singular verb 'was'."),
        ("Ten kilometers are a long distance to walk on foot.", "Ten kilometers is a long distance to walk on foot.", "Distances treated as a single unit take singular verb 'is'."),
        ("Fifty thousand rupees are a huge amount of money.", "Fifty thousand rupees is a huge amount of money.", "Sum of money treated as a whole takes singular verb 'is'."),
        ("Bread and butter are his favorite daily breakfast.", "Bread and butter is his favorite daily breakfast.", "Compound idea treated as a single dish takes singular verb 'is'."),
        ("Slow and steady win the race.", "Slow and steady wins the race.", "Single conceptual unit takes singular verb 'wins'."),
        ("The committee have agreed on the proposed agenda.", "The committee has agreed on the proposed agenda.", "Collective noun acting as a single unit takes 'has'."),
        ("Neither of the answers are correct.", "Neither of the answers is correct.", "'Neither' takes singular verb 'is'."),
        ("Either of the two shirts suit you well.", "Either of the two shirts suits you well.", "'Either' takes singular verb 'suits'."),
        ("The news about the cyclone are alarming.", "The news about the cyclone is alarming.", "'News' is uncountable singular noun taking 'is'."),
        ("Physics are my favorite subject in science stream.", "Physics is my favorite subject in science stream.", "Academic branch names ending in -s take singular verb 'is'."),
        ("Measles are a contagious viral disease.", "Measles is a contagious viral disease.", "Disease names take singular verb 'is'."),
        ("The scissors is kept on the wooden table.", "The scissors are kept on the wooden table.", "Plural noun 'scissors' takes plural verb 'are'."),
        ("My trousers is very loose and needs alteration.", "My trousers are very loose and need alteration.", "'Trousers' is plural and takes 'are'."),
        ("The spectacles is lying on the study desk.", "The spectacles are lying on the study desk.", "'Spectacles' is plural and takes 'are'."),
        ("The jury was divided in their opinions.", "The jury were divided in their opinions.", "When members act individually/divided, use plural 'were'."),
        ("All of the milk were spilled on the kitchen floor.", "All of the milk was spilled on the kitchen floor.", "Uncountable noun 'milk' takes singular verb 'was'."),
        ("Some of the water have leaked through the roof.", "Some of the water has leaked through the roof.", "Uncountable noun 'water' takes singular auxiliary 'has'."),
        ("None of the information were reliable.", "None of the information was reliable.", "Uncountable noun 'information' takes singular verb 'was'.")
    ]
    for s, c, e in sva_extra_cases:
        add_sample(s, 2, c, e)

    # =========================================================================
    # CLASS 3: ARTICLE_ERROR (160+ samples)
    # Telugu lacks an article system. Typical errors:
    # 1. Missing 'a/an' before countable singular nouns ("I have uncle who is doctor")
    # 2. 'a' vs 'an' confusion based on spelling instead of sound ("a honest", "an European")
    # 3. Missing 'the' before superlatives or unique entities ("Sun rises in east")
    # 4. Unnecessary 'the' before abstract/uncountable nouns ("The honesty is good")
    # 5. Using 'a' with uncountable nouns ("give me a water")
    # =========================================================================
    art_seeds = [
        ("I have a uncle who is doctor in Guntur.", "I have an uncle who is a doctor in Guntur.", "Use 'an' before vowel sounds and 'a' before professions."),
        ("He is a honest police officer in this town.", "He is an honest police officer in this town.", "Use 'an' before 'honest' because the 'h' is silent."),
        ("She gave me an useful piece of advice yesterday.", "She gave me a useful piece of advice yesterday.", "Use 'a' before 'useful' because it begins with a consonant sound /juː/."),
        ("He is an European tourist visiting historical monuments.", "He is a European tourist visiting historical monuments.", "Use 'a' before 'European' because it begins with a consonant /j/ sound."),
        ("I saw an unique temple near the river bank.", "I saw a unique temple near the river bank.", "'Unique' begins with a consonant glide /j/, requiring article 'a'."),
        ("Sun rises in east and sets in west.", "The sun rises in the east and sets in the west.", "Unique celestial bodies and cardinal directions take definite article 'the'."),
        ("Mount Everest is highest mountain peak in world.", "Mount Everest is the highest mountain peak in the world.", "Superlatives like 'highest' require the definite article 'the'."),
        ("The honesty is always the best policy in life.", "Honesty is always the best policy in life.", "Do not use definite article 'the' before abstract nouns used in general sense."),
        ("Can you please give me a water to drink?", "Can you please give me some water to drink?", "Water is an uncountable noun and cannot be preceded by indefinite article 'a'."),
        ("She works as software engineer in multinational company.", "She works as a software engineer in a multinational company.", "Singular countable professions require indefinite article 'a/an'."),
        ("He bought a iPhone from the electronics store.", "He bought an iPhone from the electronics store.", "Use 'an' before words beginning with vowel sound like 'iPhone'."),
        ("She got an one rupee coin from the shopkeeper.", "She got a one-rupee coin from the shopkeeper.", "'One' begins with consonant sound /w/, so use 'a' instead of 'an'."),
        ("Pacific Ocean is largest ocean on the earth.", "The Pacific Ocean is the largest ocean on the earth.", "Names of oceans and superlatives require definite article 'the'."),
        ("He had a lunch at one o'clock in college canteen.", "He had lunch at one o'clock in the college canteen.", "Do not use article 'a' before names of routine meals."),
        ("Taj Mahal is famous historical monument in Agra.", "The Taj Mahal is a famous historical monument in Agra.", "Historical monuments require definite article 'the'."),
        ("I waited for bus for more than an hour.", "I waited for the bus for more than an hour.", "Use definite article 'the' when referring to a specific public transit."),
        ("She has an headache and cannot attend class today.", "She has a headache and cannot attend class today.", "'Headache' takes indefinite article 'a'."),
        ("He went to university to collect his certificates.", "He went to the university to collect his certificates.", "Use 'the' when referring to a specific university campus."),
        ("The gold is a very precious and expensive metal.", "Gold is a very precious and expensive metal.", "Material nouns used in a general sense do not take article 'the'."),
        ("He wants to purchase car for his family.", "He wants to purchase a car for his family.", "Singular countable noun 'car' requires indefinite article 'a'."),
        ("I read interesting novel written by R K Narayan.", "I read an interesting novel written by R K Narayan.", "Countable noun modified by vowel-initial adjective takes 'an'."),
        ("Ganga is considered holy river in India.", "The Ganga is considered a holy river in India.", "Rivers require definite article 'the', and singular noun takes 'a'."),
        ("She wants to become teacher in government school.", "She wants to become a teacher in a government school.", "Singular professions require indefinite article 'a'."),
        ("He is tallest boy in the entire classroom.", "He is the tallest boy in the entire classroom.", "Superlative adjective 'tallest' requires 'the'."),
        ("We stayed in hotel near the railway station.", "We stayed in a hotel near the railway station.", "Singular countable noun 'hotel' requires indefinite article 'a'.")
    ]
    for s, c, e in art_seeds:
        add_sample(s, 3, c, e)

    # Systematic generation for ARTICLE_ERROR (140 more samples)
    art_professions = ["doctor", "lawyer", "police constable", "lecturer", "software engineer", "bank manager", "data scientist"]
    art_subjects = ["Ravi wants to become", "His sister is working as", "She dreamed of becoming", "My friend is", "He was hired as"]
    for pr in art_professions:
        for sb in art_subjects:
            correct_art = "an" if pr[0] in "aeiou" and not pr.startswith("one") else "a"
            add_sample(
                f"{sb} {pr} in reputed organization.",
                3,
                f"{sb} {correct_art} {pr} in a reputed organization.",
                f"Singular countable professions require article '{correct_art}'."
            )

    art_vowel_words = [
        ("umbrella", "a", "an", "Umbrella begins with vowel sound requiring 'an'."),
        ("honest boy", "a", "an", "Honest begins with silent 'h', requiring 'an'."),
        ("hour delay", "a", "an", "Hour has a silent 'h', requiring 'an'."),
        ("engineer", "a", "an", "Engineer begins with vowel sound /e/, requiring 'an'."),
        ("accident", "a", "an", "Accident begins with vowel sound /æ/, requiring 'an'."),
        ("orange", "a", "an", "Orange begins with vowel sound /ɒ/, requiring 'an'."),
        ("apple", "a", "an", "Apple begins with vowel sound /æ/, requiring 'an'."),
    ]
    contexts = [
        ("I noticed", "near the entrance"),
        ("She carried", "to the examination hall"),
        ("They reported", "yesterday morning"),
        ("He observed", "during the journey"),
        ("We found", "inside the classroom")
    ]
    for n, wrong_art, right_art, expl in art_vowel_words:
        for ctx_pre, ctx_post in contexts:
            add_sample(
                f"{ctx_pre} {wrong_art} {n} {ctx_post}.",
                3,
                f"{ctx_pre} {right_art} {n} {ctx_post}.",
                expl
            )

    art_superlatives = [
        ("smartest student in class", "the smartest student in the class"),
        ("fastest runner in college", "the fastest runner in the college"),
        ("highest score in mathematics", "the highest score in mathematics"),
        ("oldest temple in district", "the oldest temple in the district"),
        ("richest person in city", "the richest person in the city"),
        ("deepest lake in country", "the deepest lake in the country")
    ]
    for sup_err, sup_cor in art_superlatives:
        for sb in ["He is recognized as", "Ramesh is considered", "That place is", "She achieved", "It is known as"]:
            add_sample(
                f"{sb} {sup_err}.",
                3,
                f"{sb} {sup_cor}.",
                "Superlative adjectives require the definite article 'the'."
            )

    art_extra_cases = [
        ("He travelled around world in eighty days.", "He travelled around the world in eighty days.", "Unique entities like 'world' require definite article 'the'."),
        ("Moon shines brightly during the clear night.", "The moon shines brightly during the clear night.", "Celestial bodies take definite article 'the'."),
        ("Sky looks very dark and stormy this evening.", "The sky looks very dark and stormy this evening.", "Natural unique entities like 'sky' take definite article 'the'."),
        ("Earth revolves around sun once every year.", "The earth revolves around the sun once every year.", "Celestial bodies take definite article 'the'."),
        ("Equator divides earth into two equal halves.", "The equator divides the earth into two equal halves.", "Geographical lines take definite article 'the'."),
        ("North pole experiences continuous winter darkness.", "The North Pole experiences continuous winter darkness.", "Geographical poles take definite article 'the'."),
        ("She plays violin very melodiously on stage.", "She plays the violin very melodiously on stage.", "Musical instruments take definite article 'the'."),
        ("He is learning to play classical guitar.", "He is learning to play the classical guitar.", "Musical instruments require definite article 'the'."),
        ("My sister plays piano in Sunday church.", "My sister plays the piano in Sunday church.", "Musical instruments take definite article 'the'."),
        ("The musician played flute at temple festival.", "The musician played the flute at the temple festival.", "Musical instruments take definite article 'the'."),
        ("I saw big elephant crossing the road.", "I saw a big elephant crossing the road.", "Singular countable noun requires indefinite article 'a'."),
        ("She bought beautiful silk saree for wedding.", "She bought a beautiful silk saree for the wedding.", "Singular countable noun requires article 'a'."),
        ("He built small cottage near Krishna river.", "He built a small cottage near the Krishna river.", "Singular countable noun requires 'a'."),
        ("They opened new branch in Guntur city.", "They opened a new branch in Guntur city.", "Singular countable noun requires article 'a'."),
        ("We attended inspiring speech by eminent scientist.", "We attended an inspiring speech by an eminent scientist.", "Singular countable noun requires article 'an'."),
        ("He wrote informative article on renewable energy.", "He wrote an informative article on renewable energy.", "Countable noun modified by vowel requires 'an'."),
        ("He met with terrible bike accident on highway.", "He met with a terrible bike accident on the highway.", "Countable noun requires indefinite article 'a'."),
        ("We had fruitful discussion with college principal.", "We had a fruitful discussion with the college principal.", "Countable event requires indefinite article 'a'."),
        ("They reached formal agreement after negotiations.", "They reached a formal agreement after negotiations.", "Countable noun 'agreement' takes article 'a'."),
        ("He can speak the English with great fluency.", "He can speak English with great fluency.", "Do not use article 'the' before names of languages."),
        ("The Telugu is an ancient classical language.", "Telugu is an ancient classical language.", "Do not use article 'the' before language names."),
        ("We enjoy playing the cricket every Sunday.", "We enjoy playing cricket every Sunday.", "Do not use 'the' before names of sports."),
        ("They had the lunch at two in the afternoon.", "They had lunch at two in the afternoon.", "Do not use 'the' before names of regular meals."),
        ("The breakfast is essential for good health.", "Breakfast is essential for good health.", "Do not use 'the' before names of meals."),
        ("She likes studying the history and literature.", "She likes studying history and literature.", "Do not use 'the' before academic subjects in general."),
        ("He travels to the Hyderabad by government bus.", "He travels to Hyderabad by government bus.", "Do not use 'the' before city names."),
        ("Can you please pass me a salt from rack?", "Can you please pass me the salt from the rack?", "Specific condiment takes 'the', not indefinite 'a'."),
        ("She gave me an advice regarding higher education.", "She gave me advice regarding higher education.", "'Advice' is uncountable and cannot take 'an'."),
        ("He bought a new furniture for his apartment.", "He bought new furniture for his apartment.", "'Furniture' is uncountable and cannot take 'a'."),
        ("I have an important work to finish today.", "I have important work to finish today.", "'Work' in this sense is uncountable and takes no 'an'."),
        ("She received a bad news from her village.", "She received bad news from her village.", "'News' is uncountable and does not take 'a'."),
        ("The knowledge is more valuable than wealth.", "Knowledge is more valuable than wealth.", "Abstract nouns in general sense do not take 'the'."),
        ("The poverty is a major socio economic problem.", "Poverty is a major socio economic problem.", "Abstract nouns in general sense do not take 'the'."),
        ("He goes to the school to study every morning.", "He goes to school to study every morning.", "Omit 'the' when visiting institutions for primary purpose."),
        ("The patients were taken to the hospital.", "The patients were taken to hospital.", "Omit 'the' when hospital is used for primary medical care."),
        ("He was sent to the prison for two years.", "He was sent to prison for two years.", "Omit 'the' when institution is used for its primary purpose."),
        ("We go to the bed at ten o'clock sharp.", "We go to bed at ten o'clock sharp.", "Idiomatic expression 'go to bed' does not take 'the'."),
        ("He is man of great wisdom and humility.", "He is a man of great wisdom and humility.", "Singular countable noun 'man' requires 'a'."),
        ("She showed kindness to poor beggar on street.", "She showed kindness to a poor beggar on the street.", "Singular countable noun requires article 'a'."),
        ("He is MBA student at Osmania University.", "He is an MBA student at Osmania University.", "Acronym MBA begins with vowel sound /em/, requiring 'an'."),
        ("She lodged a FIR at local police station.", "She lodged an FIR at the local police station.", "Acronym FIR begins with vowel sound /ef/, requiring 'an'."),
        ("He is a NCC cadet in our college battalion.", "He is an NCC cadet in our college battalion.", "Acronym NCC begins with vowel sound /en/, requiring 'an'."),
        ("His father is a MLA from this constituency.", "His father is an MLA from this constituency.", "Acronym MLA begins with vowel sound /em/, requiring 'an'."),
        ("He works as a X-ray technician in clinic.", "He works as an X-ray technician in the clinic.", "X-ray begins with vowel sound /eks/, requiring 'an'."),
        ("She is an unique singer with soulful voice.", "She is a unique singer with a soulful voice.", "'Unique' begins with consonant sound /juː/, requiring 'a'."),
        ("It was an one sided cricket match yesterday.", "It was a one-sided cricket match yesterday.", "'One' begins with consonant sound /w/, requiring 'a'."),
        ("He has a university degree in civil engineering.", "He has a university degree in civil engineering.", "'University' begins with consonant sound /j/, requiring 'a'."),
        ("She wore an uniform with blue scarf to school.", "She wore a uniform with a blue scarf to school.", "'Uniform' begins with consonant sound /j/, requiring 'a'."),
        ("This is an universal truth recognized worldwide.", "This is a universal truth recognized worldwide.", "'Universal' begins with consonant sound /j/, requiring 'a'."),
        ("He is an useful resource person for workshop.", "He is a useful resource person for the workshop.", "'Useful' begins with consonant sound /j/, requiring 'a'.")
    ]
    for s, c, e in art_extra_cases:
        add_sample(s, 3, c, e)

    # =========================================================================
    # CLASS 4: PREPOSITION_ERROR (160+ samples)
    # Direct translation of Telugu postpositions into English prepositions:
    # 1. "good in" instead of "good at" (English lo bagunnanu)
    # 2. "angry on" instead of "angry with" (na meeda kopam)
    # 3. "congratulated for" instead of "congratulated on"
    # 4. Redundant prepositions ("discussed about", "entered into", "ordered for")
    # 5. "married with" instead of "married to"
    # 6. "died with" instead of "died of"
    # 7. "in Monday" instead of "on Monday"
    # 8. "between" for >2 items instead of "among"
    # =========================================================================
    prep_seeds = [
        ("I am very good in English speaking and grammar.", "I am very good at English speaking and grammar.", "Use 'good at' for abilities and competencies, not 'good in'."),
        ("My teacher is very angry on me for coming late.", "My teacher is very angry with me for coming late.", "Use 'angry with someone', not 'angry on someone'."),
        ("We congratulated Suresh for his great achievement in sports.", "We congratulated Suresh on his great achievement in sports.", "Use 'congratulate on', not 'congratulate for'."),
        ("The students discussed about the project topic with teacher.", "The students discussed the project topic with the teacher.", "'Discuss' is a transitive verb; do not use 'about' after it."),
        ("The principal entered into the examination hall quietly.", "The principal entered the examination hall quietly.", "'Enter' meaning to go into a physical place takes no preposition 'into'."),
        ("She is married with a senior doctor in Apollo hospital.", "She is married to a senior doctor in Apollo hospital.", "Use 'married to', not 'married with'."),
        ("The patient died with severe malaria fever last night.", "The patient died of severe malaria fever last night.", "Use 'died of' a disease, not 'died with'."),
        ("He has been suffering with viral fever since three days.", "He has been suffering from viral fever for three days.", "Use 'suffering from' an illness, not 'suffering with'."),
        ("She is extremely afraid from street dogs at night.", "She is extremely afraid of street dogs at night.", "Use adjective 'afraid of', not 'afraid from'."),
        ("I will meet you in Monday morning at the canteen.", "I will meet you on Monday morning at the canteen.", "Use 'on' with days of the week, not 'in'."),
        ("The final semester examination will start in 15th March.", "The final semester examination will start on 15th March.", "Use 'on' before specific calendar dates."),
        ("The express train will arrive on 6 PM at platform two.", "The express train will arrive at 6 PM at platform two.", "Use preposition 'at' for specific clock times."),
        ("Distribute these sweet packets between all the ten children.", "Distribute these sweet packets among all the ten children.", "Use 'among' for more than two people; 'between' is for two."),
        ("She sat besides me on the bench during the lecture.", "She sat beside me on the bench during the lecture.", "Use 'beside' (next to), not 'besides' (in addition to)."),
        ("Write your answers with blue ink only in the booklet.", "Write your answers in blue ink only in the booklet.", "Use 'in ink' or 'with a pen', not 'with ink'."),
        ("They reached to the railway station five minutes late.", "They reached the railway station five minutes late.", "'Reach' is transitive and does not take 'to'."),
        ("He ordered for two plates of chicken biryani.", "He ordered two plates of chicken biryani.", "'Order' is transitive; do not use 'for'."),
        ("Please listen what the mathematics teacher is explaining.", "Please listen to what the mathematics teacher is explaining.", "Verb 'listen' requires preposition 'to'."),
        ("He jumped in the river to save the drowning boy.", "He jumped into the river to save the drowning boy.", "Use 'into' to express motion into an enclosed space or water."),
        ("She is senior than me in the engineering college.", "She is senior to me in the engineering college.", "Adjectives ending in -ior (senior, junior, prior) take 'to', not 'than'."),
        ("Open your textbook on page number fifty six.", "Open your textbook to page number fifty six.", "Use 'open to page', not 'open on page'."),
        ("He was accused for stealing the gold chain from room.", "He was accused of stealing the gold chain from the room.", "Use 'accused of', not 'accused for'."),
        ("She insisted for paying the restaurant bill herself.", "She insisted on paying the restaurant bill herself.", "Use 'insist on', not 'insist for'."),
        ("I prefer coffee than tea during study hours.", "I prefer coffee to tea during study hours.", "Use 'prefer ... to ...', not 'prefer ... than ...'."),
        ("He prevented me to attend the special coaching class.", "He prevented me from attending the special coaching class.", "Use 'prevent from + verb-ing', not 'prevent to'.")
    ]
    for s, c, e in prep_seeds:
        add_sample(s, 4, c, e)

    # Systematic generation for PREPOSITION_ERROR (140 more samples)
    prep_skills = [
        ("in mathematics", "at mathematics", "Use 'good/weak at' for skills and subjects."),
        ("in coding in Python", "at coding in Python", "Use 'good at' for activities and abilities."),
        ("in public speaking", "at public speaking", "Use 'good at' for specific skills."),
        ("in playing chess", "at playing chess", "Use 'good at' for games and skills."),
        ("in solving puzzles", "at solving puzzles", "Use 'good at' for activities.")
    ]
    prep_eval_subjects = ["Ravi is good", "My sister is weak", "Priya is excellent", "The student is clever", "He is skilled"]
    for sk_err, sk_cor, expl in prep_skills:
        for sb in prep_eval_subjects:
            add_sample(f"{sb} {sk_err}.", 4, f"{sb} {sk_cor}.", expl)

    prep_angry_cases = [
        ("angry on his younger brother", "angry with his younger brother", "Use 'angry with' a person, not 'angry on'."),
        ("shouted on the auto driver", "shouted at the auto driver", "Use 'shout at' someone, not 'shout on'."),
        ("screamed on the sales boy", "screamed at the sales boy", "Use 'scream at', not 'scream on'."),
        ("annoyed on the noisy neighbours", "annoyed with the noisy neighbours", "Use 'annoyed with' persons, not 'annoyed on'."),
        ("furious on his classmate", "furious with his classmate", "Use 'furious with' a person, not 'furious on'.")
    ]
    for ac_err, ac_cor, expl in prep_angry_cases:
        for sb in ["The father was", "Our teacher became", "The manager got", "My friend was", "The principal seemed"]:
            add_sample(f"{sb} {ac_err}.", 4, f"{sb} {ac_cor}.", expl)

    prep_redundant = [
        ("discussed about the project issues", "discussed the project issues", "Do not use 'about' after transitive verb 'discuss'."),
        ("entered into the computer laboratory", "entered the computer laboratory", "Do not use 'into' after 'enter'."),
        ("ordered for a cold beverage", "ordered a cold beverage", "Do not use 'for' after transitive verb 'order'."),
        ("reached to the bus stop early", "reached the bus stop early", "Do not use 'to' after 'reach'."),
        ("described about the scenic beauty", "described the scenic beauty", "Do not use 'about' after transitive verb 'describe'.")
    ]
    for rd_err, rd_cor, expl in prep_redundant:
        for sb in ["The students", "The professors", "The tourists", "Our family members", "The delegates"]:
            add_sample(f"{sb} {rd_err}.", 4, f"{sb} {rd_cor}.", expl)

    prep_days = [
        ("in Sunday", "on Sunday"),
        ("in Tuesday", "on Tuesday"),
        ("in Wednesday", "on Wednesday"),
        ("in Friday", "on Friday"),
        ("in Saturday", "on Saturday")
    ]
    for d_err, d_cor in prep_days:
        for act in ["We will organize the meeting", "The workshop will take place", "Classes will resume", "They will travel to Guntur", "The test will be conducted"]:
            add_sample(f"{act} {d_err}.", 4, f"{act} {d_cor}.", "Use preposition 'on' before days of the week.")

    prep_extra_cases = [
        ("He is travelling in train right now.", "He is travelling on a train right now.", "Use 'on a train', not 'in train'."),
        ("She was sitting on the private car.", "She was sitting in the private car.", "Use 'in a car', not 'on a car'."),
        ("I met him on the bus station yesterday.", "I met him at the bus station yesterday.", "Use 'at the bus station', not 'on'."),
        ("We arrived in the airport thirty minutes late.", "We arrived at the airport thirty minutes late.", "Use 'at the airport' for specific transit points."),
        ("He has been living at Hyderabad since five years.", "He has been living in Hyderabad for five years.", "Use 'in' for large cities and 'for' with duration."),
        ("She works on a reputed multinational IT company.", "She works in a reputed multinational IT company.", "Use 'in' or 'at' a company, not 'on'."),
        ("He prevented me from to go to the party.", "He prevented me from going to the party.", "Use 'prevent from + verb-ing'."),
        ("I am looking forward to meet you next week.", "I am looking forward to meeting you next week.", "'Look forward to' is followed by a gerund (-ing)."),
        ("She is accustomed with waking up early at dawn.", "She is accustomed to waking up early at dawn.", "Use 'accustomed to', not 'accustomed with'."),
        ("He is very fond for Indian classical music.", "He is very fond of Indian classical music.", "Use 'fond of', not 'fond for'."),
        ("I am totally tired with doing this repetitive task.", "I am totally tired of doing this repetitive task.", "Use 'tired of', not 'tired with'."),
        ("She is capable to complete the work alone.", "She is capable of completing the work alone.", "Use 'capable of + -ing', not 'capable to'."),
        ("He is confident for passing the civil services exam.", "He is confident of passing the civil services exam.", "Use 'confident of', not 'confident for'."),
        ("We are very proud for his academic achievement.", "We are very proud of his academic achievement.", "Use 'proud of', not 'proud for'."),
        ("She feels extremely jealous on her colleague promotion.", "She feels extremely jealous of her colleague's promotion.", "Use 'jealous of', not 'jealous on'."),
        ("He has become addicted with playing online games.", "He has become addicted to playing online games.", "Use 'addicted to', not 'addicted with'."),
        ("This restaurant is famous of its spicy biryani.", "This restaurant is famous for its spicy biryani.", "Use 'famous for', not 'famous of'."),
        ("The suspect was found guilty for committing fraud.", "The suspect was found guilty of committing fraud.", "Use 'guilty of', not 'guilty for'."),
        ("She is extremely keen for learning classical dance.", "She is extremely keen on learning classical dance.", "Use 'keen on', not 'keen for'."),
        ("I am not satisfied by your incomplete explanation.", "I am not satisfied with your incomplete explanation.", "Use 'satisfied with', not 'satisfied by'."),
        ("He is not eligible to this government scholarship.", "He is not eligible for this government scholarship.", "Use 'eligible for', not 'eligible to'."),
        ("She apologized from the teacher for being late.", "She apologized to the teacher for being late.", "Use 'apologize to someone', not 'from someone'."),
        ("He insisted to pay the restaurant dinner bill.", "He insisted on paying the restaurant dinner bill.", "Use 'insist on + -ing', not 'insist to'."),
        ("Please pay attention on what the lecturer writes.", "Please pay attention to what the lecturer writes.", "Use 'pay attention to', not 'pay attention on'."),
        ("She smiled on the little child playing outside.", "She smiled at the little child playing outside.", "Use 'smile at', not 'smile on'."),
        ("The dog was barking on the unfamiliar stranger.", "The dog was barking at the unfamiliar stranger.", "Use 'bark at', not 'bark on'."),
        ("He threw the ball on his younger brother.", "He threw the ball to his younger brother.", "Use 'throw to' for catching; 'throw at' for hitting."),
        ("She aimed the stone on the mango tree branch.", "She aimed the stone at the mango tree branch.", "Use 'aim at', not 'aim on'."),
        ("He laughed on the poor man clothes.", "He laughed at the poor man's clothes.", "Use 'laugh at', not 'laugh on'."),
        ("We reached at the tourist destination safely.", "We reached the tourist destination safely.", "'Reach' is transitive and does not take 'at'."),
        ("He ordered for three cups of hot tea.", "He ordered three cups of hot tea.", "'Order' is transitive and does not take 'for'."),
        ("They signed on the contract agreement yesterday.", "They signed the contract agreement yesterday.", "'Sign' is transitive and does not take 'on'."),
        ("She emphasized on the importance of punctuality.", "She emphasized the importance of punctuality.", "'Emphasize' is transitive; do not use 'on'."),
        ("He investigated about the missing office laptop.", "He investigated the missing office laptop.", "'Investigate' is transitive; do not use 'about'."),
        ("The manager demanded for an immediate explanation.", "The manager demanded an immediate explanation.", "'Demand' is transitive; do not use 'for'."),
        ("We resemble to our maternal grandfather.", "We resemble our maternal grandfather.", "'Resemble' is transitive and takes no preposition."),
        ("He lacks in confidence during group discussions.", "He lacks confidence during group discussions.", "Verb 'lack' takes no preposition."),
        ("I accompanied with him to the medical clinic.", "I accompanied him to the medical clinic.", "'Accompany' is transitive; do not use 'with'."),
        ("She refused from accepting the consolation prize.", "She refused to accept the consolation prize.", "Use 'refuse to accept', not 'refuse from'."),
        ("He resigned from his job yesterday morning.", "He resigned his job yesterday morning.", "Standard formal English prefers transitive 'resigned his position'."),
        ("The cat climbed on the tall mango tree.", "The cat climbed up the tall mango tree.", "Use 'climbed up', not 'climbed on'."),
        ("She fell down from the moving city bus.", "She fell off the moving city bus.", "Use 'fell off a vehicle', not 'from'."),
        ("He parted with his old friends with heavy heart.", "He parted from his old friends with a heavy heart.", "Use 'part from persons' and 'part with things'."),
        ("She died by cancer after fighting bravely.", "She died of cancer after fighting bravely.", "Use 'died of' a disease, not 'by'."),
        ("He cured him from the chronic throat infection.", "He cured him of the chronic throat infection.", "Use 'cure of', not 'from'."),
        ("I was deprived from my basic student rights.", "I was deprived of my basic student rights.", "Use 'deprived of', not 'from'."),
        ("He is devoid from common sense and manners.", "He is devoid of common sense and manners.", "Use 'devoid of', not 'from'."),
        ("She is blind with one eye since birth.", "She is blind in one eye since birth.", "Use 'blind in one eye', not 'with'."),
        ("He was shocked by the tragic accident news.", "He was shocked at the tragic accident news.", "Use 'shocked at news', not 'by'."),
        ("I am tired by walking ten kilometers.", "I am tired of walking ten kilometers.", "Use 'tired of', not 'by'.")
    ]
    for s, c, e in prep_extra_cases:
        add_sample(s, 4, c, e)

    # =========================================================================
    # CLASS 5: SPELLING_ERROR (160+ samples)
    # Common irregular verb mis-regularizations and phonological spelling errors:
    # 1. Irregular verbs + -ed ("speaked", "catched", "writed", "bited", "runned")
    # 2. Confusion with double letters ("grammer", "definate", "recieved", "attendence")
    # 3. Homophones ("loose" vs "lose")
    # 4. Telugu phonetic spelling patterns ("beautifull", "truely", "seperately")
    # =========================================================================
    spell_seeds = [
        ("She speaked very fastly during the debate competition.", "She spoke very fast during the debate competition.", "Past tense of 'speak' is irregular 'spoke', and 'fast' has no '-ly' adverb form."),
        ("The cricket fielder catched the ball with one hand.", "The cricket fielder caught the ball with one hand.", "Irregular past tense of 'catch' is 'caught', not 'catched'."),
        ("I writed a formal leave application to the principal.", "I wrote a formal leave application to the principal.", "Irregular past tense of 'write' is 'wrote'."),
        ("A street dog bited the small boy on the road.", "A street dog bit the small boy on the road.", "Past tense of irregular verb 'bite' is 'bit', not 'bited'."),
        ("He runned five kilometers in the morning marathon.", "He ran five kilometers in the morning marathon.", "Past tense of irregular verb 'run' is 'ran'."),
        ("She feeled very happy after looking at the score.", "She felt very happy after looking at the score.", "Irregular past tense of 'feel' is 'felt'."),
        ("He payed his semester tuition fee at the bank.", "He paid his semester tuition fee at the bank.", "Spelling of past tense for 'pay' is 'paid', not 'payed'."),
        ("The experienced teacher teached mathematics with clarity.", "The experienced teacher taught mathematics with clarity.", "Past tense of 'teach' is 'taught', not 'teached'."),
        ("I have a serious doubt in English grammer.", "I have a serious doubt in English grammar.", "Spelling error: 'grammar' is spelled with 'ar', not 'er'."),
        ("The college principal gave a definate confirmation.", "The college principal gave a definite confirmation.", "Spelling error: 'definite' is spelled with 'i', not 'a'."),
        ("We recieved the registered parcel yesterday evening.", "We received the registered parcel yesterday evening.", "Spelling rule: 'i' before 'e' except after 'c' ('received')."),
        ("His college attendence percentage is below seventy.", "His college attendance percentage is below seventy.", "Spelling error: 'attendance' ends with 'ance', not 'ence'."),
        ("It was a beautifull sunset over the Bay of Bengal.", "It was a beautiful sunset over the Bay of Bengal.", "Spelling error: 'beautiful' has a single 'l'."),
        ("Please write your permanent address seperately.", "Please write your permanent address separately.", "Spelling error: 'separately' contains 'para', not 'pera'."),
        ("Do not loose your confidence before the interview.", "Do not lose your confidence before the interview.", "'Lose' means to misplace; 'loose' means not tight."),
        ("The winter weather is very pleasent in Araku valley.", "The weather is very pleasant in Araku valley.", "Spelling error: 'pleasant' ends with 'ant', not 'ent'."),
        ("I truely appreciate your valuable guidance and help.", "I truly appreciate your valuable guidance and help.", "Spelling error: 'truly' drops the 'e'."),
        ("They had a heated arguement regarding the project.", "They had a heated argument regarding the project.", "Spelling error: 'argument' drops the 'e' from 'argue'."),
        ("We had dinner at a famous South Indian resturant.", "We had dinner at a famous South Indian restaurant.", "Spelling error: 'restaurant' contains 'au'."),
        ("The goverment announced new scholarship schemes for students.", "The government announced new scholarship schemes for students.", "Spelling error: 'government' contains an 'n' before 'ment'."),
        ("We must protect our natural enviroment from pollution.", "We must protect our natural environment from pollution.", "Spelling error: 'environment' contains an 'n' before 'ment'."),
        ("Let us meet tommorow morning at the library.", "Let us meet tomorrow morning at the library.", "Spelling error: 'tomorrow' has one 'm' and two 'r's."),
        ("He is a succesful software entrepreneur in Hyderabad.", "He is a successful software entrepreneur in Hyderabad.", "Spelling error: 'successful' has double 'c' and double 's'."),
        ("The students were dissapointed with the test results.", "The students were disappointed with the test results.", "Spelling error: 'disappointed' has one 's' and two 'p's."),
        ("I beleive that hard work always leads to success.", "I believe that hard work always leads to success.", "Spelling error: 'believe' is spelled with 'ie'.")
    ]
    for s, c, e in spell_seeds:
        add_sample(s, 5, c, e)

    # Systematic generation for SPELLING_ERROR (140 more samples)
    spelling_word_pairs = [
        ("grammer", "grammar", "Spelling error: 'grammar' is spelled with -ar."),
        ("definate", "definite", "Spelling error: 'definite' is spelled with -ite."),
        ("recieved", "received", "Spelling error: 'received' places 'e' before 'i' after 'c'."),
        ("attendence", "attendance", "Spelling error: 'attendance' is spelled with -ance."),
        ("beautifull", "beautiful", "Spelling error: 'beautiful' has one 'l'."),
        ("seperately", "separately", "Spelling error: 'separately' has -para-."),
        ("pleasent", "pleasant", "Spelling error: 'pleasant' ends in -ant."),
        ("truely", "truly", "Spelling error: 'truly' has no 'e'."),
        ("arguement", "argument", "Spelling error: 'argument' drops 'e'."),
        ("resturant", "restaurant", "Spelling error: 'restaurant' is the correct spelling."),
        ("goverment", "government", "Spelling error: 'government' has 'n' before 'ment'."),
        ("enviroment", "environment", "Spelling error: 'environment' has 'n' before 'ment'."),
        ("tommorow", "tomorrow", "Spelling error: 'tomorrow' has one 'm' and two 'r's."),
        ("beleive", "believe", "Spelling error: 'believe' is spelled with 'ie'."),
    ]
    spell_frames = [
        ("The teacher checked the", "in student assignments"),
        ("We discussed about the", "in yesterday meeting"),
        ("He submitted the document", "without any delay"),
        ("She noted down the", "in her personal diary"),
        ("Everyone noticed the", "during the presentation"),
        ("The inspector pointed out", "in official records"),
        ("I observed that the", "needed urgent correction"),
        ("They realized the", "after publishing the notice"),
        ("Our mentor reviewed the", "with great patience"),
        ("The report mentioned the", "on the front page")
    ]
    for wrong_w, right_w, expl in spelling_word_pairs:
        for f_pre, f_post in spell_frames:
            add_sample(f"{f_pre} {wrong_w} {f_post}.", 5, f"{f_pre} {right_w} {f_post}.", expl)

    # =========================================================================
    # CLASS 6: STRUCTURE_ERROR (160+ samples)
    # Telugu SOV word order, question inversion missing, redundant words:
    # 1. SOV word order ("I English very much like", "Book where you kept?")
    # 2. Wh-questions without auxiliary inversion ("Where you are going?", "What your name is?")
    # 3. Redundant conjunctions ("Though he worked hard, but he failed")
    # 4. Redundant adverbs ("Return back", "Revert back", "Repeat again")
    # 5. Reflexive pronoun as subject ("Myself I am Suresh")
    # 6. Misplaced 'only' ("He is having two cars only")
    # =========================================================================
    struct_seeds = [
        ("I English very much like to study and speak.", "I like to study and speak English very much.", "English follows SVO (Subject-Verb-Object) word order, not Telugu SOV."),
        ("Where you are going right now with heavy bag?", "Where are you going right now with a heavy bag?", "In Wh-questions, auxiliary verb must precede the subject (inversion)."),
        ("Why you didn't came to college yesterday?", "Why didn't you come to college yesterday?", "Inverted question structure requires auxiliary before subject and base verb."),
        ("What your father name is?", "What is your father's name?", "In questions, the verb 'is' must precede the subject."),
        ("What they are talking about in the meeting?", "What are they talking about in the meeting?", "Auxiliary verb 'are' must precede the subject 'they' in questions."),
        ("When the bus will arrive at the junction?", "When will the bus arrive at the junction?", "Invert auxiliary 'will' before subject 'the bus' in questions."),
        ("How much money you need for college fee?", "How much money do you need for college fee?", "Questions in simple present require auxiliary 'do/does' before subject."),
        ("He asked me that where I was living.", "He asked me where I was living.", "Do not use conjunction 'that' before wh-question words in indirect speech."),
        ("She asked him that why he was shouting.", "She asked him why he was shouting.", "Omit redundant conjunction 'that' before indirect question word 'why'."),
        ("Though he worked hard, but he failed the exam.", "Though he worked hard, he failed the exam.", "Do not use 'though' and 'but' together in a single sentence."),
        ("Although it was raining heavily, but we went out.", "Although it was raining heavily, we went out.", "Do not combine 'although' with 'but'."),
        ("Because he was sick, so he could not attend.", "Because he was sick, he could not attend.", "Do not use 'so' when the sentence already begins with 'because'."),
        ("Please return back my notebook by tomorrow morning.", "Please return my notebook by tomorrow morning.", "'Return' means to give back; using 'back' with it is redundant pleonasm."),
        ("Kindly revert back to my email as soon as possible.", "Kindly revert to my email as soon as possible.", "'Revert' already means to reply back; 'back' is redundant."),
        ("Please repeat again whatever the professor explained.", "Please repeat whatever the professor explained.", "'Repeat' means to say again; 'again' is redundant."),
        ("Myself I am Suresh from Vijayawada city.", "I am Suresh from Vijayawada city.", "Do not use reflexive pronoun 'myself' as the sentence subject."),
        ("Myself I am studying BTech second year.", "I am studying BTech second year.", "Use subjective personal pronoun 'I' instead of 'myself'."),
        ("Coffee you will drink or tea you prefer?", "Will you drink coffee or do you prefer tea?", "Do not topicalize the object to the front of the sentence (Telugu syntax)."),
        ("Food already you ate in the canteen?", "Did you already eat food in the canteen?", "Questions require auxiliary inversion ('Did you eat...')."),
        ("Bag where you kept after coming home?", "Where did you keep the bag after coming home?", "English questions begin with the Wh-word followed by auxiliary verb."),
        ("College tomorrow is declared holiday by principal.", "A holiday is declared for college tomorrow by the principal.", "Rearrange subject and predicate to follow English syntax."),
        ("He is taller compared to me in height.", "He is taller than me.", "Use comparative 'taller than' instead of 'compared to'."),
        ("Unless you do not work hard, you will not pass.", "Unless you work hard, you will not pass.", "'Unless' is already negative; do not use 'do not' in the same clause."),
        ("Tell me where do you live in Hyderabad.", "Tell me where you live in Hyderabad.", "Indirect questions follow statement word order without auxiliary 'do'."),
        ("I and my brother went to the temple yesterday.", "My brother and I went to the temple yesterday.", "In compound subjects, place the first-person pronoun 'I' last for politeness.")
    ]
    for s, c, e in struct_seeds:
        add_sample(s, 6, c, e)

    # Systematic generation for STRUCTURE_ERROR (140 more samples)
    wh_words = ["Where", "Why", "When", "How", "What"]
    subjects_wh = ["you", "they", "he", "she"]
    questions_wh = [
        ("are going in such a hurry", "are you going in such a hurry", "Auxiliary verb must precede subject in Wh-questions."),
        ("were shouting in the library", "were they shouting in the library", "Invert auxiliary before subject in question."),
        ("will submit the project files", "will you submit the project files", "Auxiliary 'will' must precede subject in interrogatives."),
        ("can solve this difficult riddle", "can you solve this difficult riddle", "Modal verb precedes subject in question form.")
    ]
    for wh in wh_words:
        for sub in subjects_wh:
            for q_err, q_cor, expl in questions_wh:
                add_sample(f"{wh} {sub} {q_err}?", 6, f"{wh} {q_cor}?", expl)

    redundant_pairs = [
        ("return back the borrowed money", "return the borrowed money", "Do not use 'back' with 'return'."),
        ("revert back to this urgent query", "revert to this urgent query", "Do not use 'back' with 'revert'."),
        ("repeat again the poem stanzas", "repeat the poem stanzas", "Do not use 'again' with 'repeat'."),
        ("recall back the pleasant memories", "recall the pleasant memories", "Do not use 'back' with 'recall'."),
        ("regroup back at the pavilion", "regroup at the pavilion", "Do not use 'back' with 'regroup'."),
        ("reply back to my message", "reply to my message", "Do not use 'back' with 'reply'.")
    ]
    for verb_err, verb_cor, expl in redundant_pairs:
        for requester in ["Please", "Kindly", "You must", "Students should", "We request you to", "He forgot to", "They decided to"]:
            add_sample(f"{requester} {verb_err}.", 6, f"{requester} {verb_cor}.", expl)

    sov_patterns = [
        ("homework quickly finished", "quickly finished homework"),
        ("cricket match enthusiastically watched", "enthusiastically watched cricket match"),
        ("Telugu songs happily sang", "happily sang Telugu songs"),
        ("examination results eagerly checked", "eagerly checked examination results")
    ]
    for obj_v_err, v_obj_cor in sov_patterns:
        for pr in ["I", "She", "He", "They", "We"]:
            add_sample(
                f"{pr} {obj_v_err}.",
                6,
                f"{pr} {v_obj_cor}.",
                "English follows Subject-Verb-Object (SVO) order rather than Telugu SOV."
            )

    df = pd.DataFrame(rows)
    # Deduplicate while preserving distribution
    df = df.drop_duplicates(subset=["sentence"]).reset_index(drop=True)
    return df


def get_data_splits(
    csv_path: str = "data/grammar_dataset.csv",
    train_size: float = 0.70,
    val_size: float = 0.15,
    test_size: float = 0.15,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads dataset from CSV and splits into Train (70%), Val (15%), Test (15%)
    using stratified sampling to ensure equal class proportions across all sets.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset CSV not found at {csv_path}. Run generate_dataset() first.")

    df = pd.read_csv(csv_path)

    # First split: train (70%) and temp (30%)
    train_df, temp_df = train_test_split(
        df,
        test_size=(val_size + test_size),
        stratify=df["label"],
        random_state=random_state,
    )

    # Second split: split temp equally into val (15%) and test (15%)
    val_ratio = val_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - val_ratio),
        stratify=temp_df["label"],
        random_state=random_state,
    )

    return (
        train_df.reset_index(drop=True),
        val_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    csv_out_path = os.path.join("data", "grammar_dataset.csv")

    print("=" * 60)
    print("Fluenora AI - Generating Grammar Error Dataset...")
    print("=" * 60)

    df = generate_dataset()
    df.to_csv(csv_out_path, index=False, encoding="utf-8")

    print(f"\n[OK] Dataset saved successfully to: {csv_out_path}")
    print(f"Total Sentences: {len(df)}")
    print("\nClass Distribution:")
    class_counts = df["label_name"].value_counts().reset_index()
    class_counts.columns = ["Error Category", "Count"]
    print(class_counts.to_string(index=False))

    # Verification of minimum samples
    min_count = df["label"].value_counts().min()
    print(f"\nMinimum samples per class: {min_count} (Target: >= 150)")
    assert min_count >= 150, f"Error: minimum class count is {min_count}, expected >= 150"

    print("\nSample Rows:")
    print(df[["sentence", "label", "label_name", "correction"]].head(10).to_string())

    print("\nSplitting into Train (70%) / Val (15%) / Test (15%)...")
    train_df, val_df, test_df = get_data_splits(csv_out_path)
    print(f"Train set: {len(train_df)} samples ({len(train_df)/len(df)*100:.1f}%)")
    print(f"Val set:   {len(val_df)} samples ({len(val_df)/len(df)*100:.1f}%)")
    print(f"Test set:  {len(test_df)} samples ({len(test_df)/len(df)*100:.1f}%)")
    print("\n[OK] Dataset generation and split test completed successfully!")
