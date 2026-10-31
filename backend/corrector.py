import os
import re
import csv
from typing import Dict, Any, Optional

DISCLAIMER_TEXT = (
    "Sentence corrections and grammatical explanations are provided by the dedicated "
    "Sentence Correction Engine, NOT by the Bi-LSTM error classification model. "
    "The Bi-LSTM model is strictly an error-category classifier."
)


class SentenceCorrector:
    """
    Dedicated Sentence Correction Engine for Fluenora AI.

    Important Architectural Principle:
    The Bi-LSTM model classifies error categories (TENSE_ERROR, SVA_ERROR, etc.).
    It is a classification model and DOES NOT generate text corrections.
    Text corrections and pedagogical explanations are provided independently
    by this module via:
      1. Verified Telugu-English Learner Corpus matching
      2. Deterministic linguistic rule transformations for Telugu L1 negative transfer
      3. Optional external LLM provider (when configured via API key)
      4. Explicit fallback communication when a correction provider is unavailable.
    """

    def __init__(self, dataset_csv_path: Optional[str] = None):
        self.dataset_corrections: Dict[str, Dict[str, str]] = {}
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        if dataset_csv_path is None:
            dataset_csv_path = os.path.join(project_root, "data", "grammar_dataset.csv")

        self.dataset_csv_path = dataset_csv_path
        self._load_corpus_corrections()

    def _normalize_key(self, text: str) -> str:
        """Normalize text for insensitive lookup (lowercased, stripped, extra whitespace removed)."""
        clean = re.sub(r"[^\w\s]", "", text.lower())
        return " ".join(clean.split())

    def _load_corpus_corrections(self) -> None:
        """Load verified sentence-correction pairs from dataset CSV if present."""
        if not os.path.exists(self.dataset_csv_path):
            return

        try:
            with open(self.dataset_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sentence = row.get("sentence", "").strip()
                    correction = row.get("correction", "").strip()
                    explanation = row.get("explanation", "").strip()
                    label_name = row.get("label_name", "").strip()
                    if sentence and correction:
                        norm = self._normalize_key(sentence)
                        self.dataset_corrections[norm] = {
                            "correction": correction,
                            "explanation": explanation,
                            "category": label_name,
                        }
        except Exception:
            pass

    def correct(self, sentence: str, predicted_category: Optional[str] = None) -> Dict[str, Any]:
        """
        Produce a correction and linguistic explanation for a learner sentence.

        Returns:
            {
                "original_sentence": str,
                "correction": Optional[str],
                "explanation": str,
                "provider": str ("corpus_match" | "rule_based" | "external_llm" | "none"),
                "status": str ("success" | "unavailable"),
                "disclaimer": str
            }
        """
        if not sentence or not sentence.strip():
            return {
                "original_sentence": sentence,
                "correction": sentence,
                "explanation": "Input sentence is empty.",
                "provider": "rule_based",
                "status": "success",
                "disclaimer": DISCLAIMER_TEXT,
            }

        sentence_stripped = sentence.strip()

        # If predicted as CORRECT by model and no obvious errors
        if predicted_category == "CORRECT":
            # Check if it matches an error in corpus
            norm = self._normalize_key(sentence_stripped)
            if norm not in self.dataset_corrections:
                return {
                    "original_sentence": sentence_stripped,
                    "correction": sentence_stripped,
                    "explanation": "The sentence is grammatically sound. No correction is required.",
                    "provider": "rule_based",
                    "status": "success",
                    "disclaimer": DISCLAIMER_TEXT,
                }

        # 1. Check verified Corpus match
        norm = self._normalize_key(sentence_stripped)
        if norm in self.dataset_corrections:
            match = self.dataset_corrections[norm]
            return {
                "original_sentence": sentence_stripped,
                "correction": match["correction"],
                "explanation": match["explanation"],
                "provider": "corpus_match",
                "status": "success",
                "disclaimer": DISCLAIMER_TEXT,
            }

        # 2. Apply Rule-Based Transformations for Telugu L1 patterns
        rule_result = self._apply_rule_transformations(sentence_stripped, predicted_category)
        if rule_result:
            return {
                "original_sentence": sentence_stripped,
                "correction": rule_result["correction"],
                "explanation": rule_result["explanation"],
                "provider": "rule_based",
                "status": "success",
                "disclaimer": DISCLAIMER_TEXT,
            }

        # 3. External LLM Provider Check
        llm_result = self._try_external_llm_provider(sentence_stripped, predicted_category)
        if llm_result:
            return llm_result

        # 4. Graceful Fallback Communication
        return {
            "original_sentence": sentence_stripped,
            "correction": None,
            "explanation": (
                "An automated sentence correction is currently unavailable for this specific input pattern. "
                "The separate Sentence Correction Engine could not locate a matching template rule, and an "
                "external LLM correction service is not configured. "
                "Note: The Bi-LSTM model performs error-type classification only and does not generate text."
            ),
            "provider": "none",
            "status": "unavailable",
            "disclaimer": DISCLAIMER_TEXT,
        }

    def _apply_rule_transformations(
        self, sentence: str, category: Optional[str]
    ) -> Optional[Dict[str, str]]:
        """
        Deterministic linguistic repair rules addressing frequent Telugu L1 interference.
        """
        text = sentence
        explanation = ""
        modified = False

        # Rule Set A: Auxiliary 'did' + past tense ("did completed" -> "did complete")
        did_past_patterns = [
            (r"\b(did|didn't|did not)\s+completed\b", r"\1 complete", "Use base verb 'complete' after auxiliary 'did'."),
            (r"\b(did|didn't|did not)\s+saw\b", r"\1 see", "Use base verb 'see' after auxiliary 'didn't'."),
            (r"\b(did|didn't|did not)\s+came\b", r"\1 come", "Use base verb 'come' after auxiliary 'did'."),
            (r"\b(did|didn't|did not)\s+went\b", r"\1 go", "Use base verb 'go' after auxiliary 'did'."),
            (r"\b(did|didn't|did not)\s+told\b", r"\1 tell", "Use base verb 'tell' after auxiliary 'did'."),
            (r"\b(did|didn't|did not)\s+brought\b", r"\1 bring", "Use base verb 'bring' after auxiliary 'did'."),
            (r"\b(did|didn't|did not)\s+wrote\b", r"\1 write", "Use base verb 'write' after auxiliary 'did'."),
        ]
        for pat, repl, expl in did_past_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                explanation = expl
                modified = True
                break

        # Rule Set B: Stative verbs in continuous aspect ("am knowing", "is having")
        stative_patterns = [
            (r"\b(is|are|am)\s+having\b", "has" if re.search(r"\b(he|she|it)\b", text, re.I) else "have", "Stative verb 'have' indicating possession is not used in continuous aspect."),
            (r"\b(is|are|am)\s+knowing\b", "knows" if re.search(r"\b(he|she|it)\b", text, re.I) else "know", "Stative verb 'know' should be in simple present, not continuous."),
            (r"\b(is|are|am)\s+understanding\b", "understands" if re.search(r"\b(he|she|it)\b", text, re.I) else "understand", "Stative verb 'understand' is not used in continuous aspect."),
            (r"\b(is|are|am)\s+liking\b", "likes" if re.search(r"\b(he|she|it)\b", text, re.I) else "like", "Stative verb 'like' expresses state and should be simple present."),
            (r"\b(is|are|am)\s+wanting\b", "wants" if re.search(r"\b(he|she|it)\b", text, re.I) else "want", "Stative verb 'want' should be simple present."),
        ]
        if not modified:
            for pat, repl, expl in stative_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                    explanation = expl
                    modified = True
                    break

        # Rule Set C: Redundant Pleonasms ("return back", "revert back", "repeat again")
        pleonasm_patterns = [
            (r"\breturn\s+back\b", "return", "'Return' means to give or come back; 'back' is redundant pleonasm."),
            (r"\brevert\s+back\b", "revert", "'Revert' already means reply back; 'back' is redundant."),
            (r"\brepeat\s+again\b", "repeat", "'Repeat' means say again; 'again' is redundant."),
            (r"\brecall\s+back\b", "recall", "'Recall' means to call back into memory; 'back' is redundant."),
            (r"\breply\s+back\b", "reply", "'Reply' already includes the concept of responding back."),
        ]
        if not modified:
            for pat, repl, expl in pleonasm_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                    explanation = expl
                    modified = True
                    break

        # Rule Set D: Common Phonetic & Irregular verb mis-regularization (Spelling errors)
        spelling_patterns = [
            (r"\bspeaked\s+very\s+fastly\b", "spoke very fast", "Irregular verb: speak -> spoke. 'Fast' has no -ly adverb form."),
            (r"\bspeaked\b", "spoke", "Irregular verb 'speak' becomes 'spoke' in simple past, not 'speaked'."),
            (r"\bfastly\b", "fast", "'Fast' serves as both adjective and adverb; 'fastly' is not a standard English word."),
            (r"\bcatched\b", "caught", "Irregular past tense of 'catch' is 'caught', not 'catched'."),
            (r"\bwrited\b", "wrote", "Irregular past tense of 'write' is 'wrote', not 'writed'."),
            (r"\bbited\b", "bit", "Irregular past tense of 'bite' is 'bit', not 'bited'."),
            (r"\brunned\b", "ran", "Irregular past tense of 'run' is 'ran', not 'runned'."),
            (r"\bfeeled\b", "felt", "Irregular past tense of 'feel' is 'felt', not 'feeled'."),
            (r"\bpayed\b", "paid", "Past tense of 'pay' is spelled 'paid'."),
            (r"\bteached\b", "taught", "Irregular past tense of 'teach' is 'taught', not 'teached'."),
            (r"\bgrammer\b", "grammar", "Spelling error: 'grammar' is spelled with -ar."),
            (r"\bdefinate\b", "definite", "Spelling error: 'definite' is spelled with -ite."),
            (r"\brecieved\b", "received", "Spelling rule: 'e' before 'i' after 'c' ('received')."),
            (r"\battendence\b", "attendance", "Spelling error: 'attendance' ends with -ance."),
            (r"\bbeautifull\b", "beautiful", "Spelling error: 'beautiful' has a single 'l' at the end."),
            (r"\bseperately\b", "separately", "Spelling error: 'separately' contains -para-, not -pera-."),
            (r"\bloose\s+your\b", "lose your", "Homophone error: 'lose' means to misplace; 'loose' means not tight."),
            (r"\bpleasent\b", "pleasant", "Spelling error: 'pleasant' ends in -ant."),
            (r"\btruely\b", "truly", "Spelling error: 'truly' drops the 'e'."),
            (r"\barguement\b", "argument", "Spelling error: 'argument' drops the 'e' from 'argue'."),
            (r"\bresturant\b", "restaurant", "Spelling error: 'restaurant' is the correct spelling."),
            (r"\btommorow\b", "tomorrow", "Spelling error: 'tomorrow' has one 'm' and double 'r'."),
            (r"\bbeleive\b", "believe", "Spelling error: 'believe' is spelled with -ie-."),
        ]
        if not modified:
            for pat, repl, expl in spelling_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                    explanation = expl
                    modified = True
                    break

        # Rule Set E: Preposition Interference
        prep_patterns = [
            (r"\bgood\s+in\s+english\b", "good at English", "Use preposition 'at' for competencies and subjects ('good at English')."),
            (r"\bweak\s+in\s+english\b", "weak at English", "Use preposition 'at' for abilities ('weak at English')."),
            (r"\bangry\s+on\s+(me|him|her|them|us)\b", r"angry with \1", "Use preposition 'with' when angry at a person, not 'on'."),
            (r"\bdiscussed\s+about\b", "discussed", "'Discuss' is a transitive verb; do not use 'about' after it."),
            (r"\bentered\s+into\s+the\b", "entered the", "'Enter' into a physical place takes no preposition 'into'."),
            (r"\bordered\s+for\s+a\b", "ordered a", "'Order' is a transitive verb; omit 'for'."),
            (r"\bordered\s+for\s+two\b", "ordered two", "'Order' is transitive; omit 'for'."),
            (r"\bmarried\s+with\s+a\b", "married to a", "Use 'married to', not 'married with'."),
            (r"\bdied\s+with\s+(cancer|malaria|cholera|fever)\b", r"died of \1", "Use 'died of' a disease, not 'died with'."),
            (r"\bsuffering\s+with\s+(fever|cough|cold)\b", r"suffering from \1", "Use 'suffering from' an illness, not 'with'."),
            (r"\bin\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", r"on \1", "Use preposition 'on' with days of the week."),
            (r"\bafraid\s+from\b", "afraid of", "Use 'afraid of', not 'afraid from'."),
            (r"\bsenior\s+than\s+me\b", "senior to me", "Comparative adjectives ending in -ior take 'to', not 'than'."),
            (r"\bcongratulated\s+(.*?)\s+for\s+his\b", r"congratulated \1 on his", "Use 'congratulate on an achievement', not 'for'."),
        ]
        if not modified:
            for pat, repl, expl in prep_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                    explanation = expl
                    modified = True
                    break

        # Rule Set F: Article Errors
        art_patterns = [
            (r"\ba\s+honest\b", "an honest", "Use 'an' before 'honest' because the 'h' is silent (vowel sound /ɒ/)."),
            (r"\ban\s+useful\b", "a useful", "Use 'a' before 'useful' because it begins with consonant glide /juː/."),
            (r"\ban\s+european\b", "a European", "Use 'a' before 'European' because it starts with consonant /j/ sound."),
            (r"\ban\s+unique\b", "a unique", "Use 'a' before 'unique' because it begins with consonant /juː/ sound."),
            (r"\ba\s+uncle\b", "an uncle", "Use 'an' before vowel sound in 'uncle'."),
            (r"\ba\s+iphone\b", "an iPhone", "Use 'an' before vowel sound in 'iPhone'."),
            (r"\ba\s+umbrella\b", "an umbrella", "Use 'an' before vowel sound in 'umbrella'."),
            (r"\ba\s+apple\b", "an apple", "Use 'an' before vowel sound in 'apple'."),
            (r"\ba\s+orange\b", "an orange", "Use 'an' before vowel sound in 'orange'."),
            (r"\ba\s+engineer\b", "an engineer", "Use 'an' before vowel sound in 'engineer'."),
            (r"\ba\s+accident\b", "an accident", "Use 'an' before vowel sound in 'accident'."),
            (r"\bgive\s+me\s+a\s+water\b", "give me water", "Water is an uncountable noun and cannot be preceded by 'a'."),
            (r"\bthe\s+honesty\s+is\b", "honesty is", "Do not use definite article 'the' before abstract nouns used in general sense."),
            (r"\bsun\s+rises\s+in\s+east\b", "the sun rises in the east", "Celestial bodies and cardinal directions require 'the'."),
            (r"\bmount\s+everest\s+is\s+highest\b", "Mount Everest is the highest", "Superlative adjectives require definite article 'the'."),
        ]
        if not modified:
            for pat, repl, expl in art_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                    explanation = expl
                    modified = True
                    break

        # Rule Set G: Subject-Verb Agreement (SVA)
        sva_patterns = [
            (r"\bshe\s+go\b", "she goes", "Third-person singular 'she' requires verb ending in -es ('goes')."),
            (r"\bhe\s+work\b", "he works", "Third-person singular 'he' requires verb with -s ('works')."),
            (r"\bmy\s+brother\s+work\b", "my brother works", "Singular subject requires third-person singular verb 'works'."),
            (r"\bhe\s+don't\b", "he doesn't", "Third-person singular subject requires negative auxiliary 'doesn't'."),
            (r"\bshe\s+don't\b", "she doesn't", "Third-person singular subject requires negative auxiliary 'doesn't'."),
            (r"\bone\s+of\s+my\s+friends\s+are\b", "one of my friends is", "'One of + plural noun' takes singular verb 'is'."),
            (r"\bevery\s+student\s+have\b", "every student has", "'Every' takes singular auxiliary 'has'."),
            (r"\beveryone\s+want\b", "everyone wants", "Indefinite pronoun 'everyone' takes singular verb 'wants'."),
            (r"\bthe\s+children\s+likes\b", "the children like", "Plural noun 'children' requires plural base verb 'like'."),
            (r"\bthey\s+was\b", "they were", "Plural pronoun 'they' requires 'were', not 'was'."),
            (r"\bwe\s+was\b", "we were", "Plural pronoun 'we' requires 'were', not 'was'."),
            (r"\byou\s+was\b", "you were", "Pronoun 'you' takes plural past verb 'were'."),
        ]
        if not modified:
            for pat, repl, expl in sva_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                    explanation = expl
                    modified = True
                    break

        # Rule Set H: Structure & Word Order
        struct_patterns = [
            (r"\bi\s+english\s+very\s+much\s+like\b", "I like English very much", "English follows Subject-Verb-Object (SVO) word order, not Telugu SOV."),
            (r"\bwhere\s+you\s+are\s+going\b", "where are you going", "In Wh-questions, auxiliary verb 'are' must precede the subject 'you'."),
            (r"\bwhy\s+you\s+didn't\b", "why didn't you", "Inverted interrogative requires auxiliary before subject ('why didn't you')."),
            (r"\bwhat\s+your\s+name\s+is\b", "what is your name", "In question form, auxiliary 'is' must precede subject."),
            (r"\bmyself\s+i\s+am\s+(.*?)\b", r"I am \1", "Do not use reflexive pronoun 'myself' as the sentence subject."),
            (r"\bthough\s+(.*?)\s+but\s+", r"Though \1, ", "Do not use 'though' and 'but' together in a single sentence."),
        ]
        if not modified:
            for pat, repl, expl in struct_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                    explanation = expl
                    modified = True
                    break

        # Rule Set I: Present continuous with past time markers (Tense Error)
        tense_patterns = [
            (r"\byesterday\s+i\s+am\s+going\b", "yesterday I went", "Use simple past tense ('went') for past completed actions."),
            (r"\byesterday\s+he\s+is\s+going\b", "yesterday he went", "Use simple past tense with past time markers like 'yesterday'."),
            (r"\blast\s+night\s+she\s+is\s+cooking\b", "last night she cooked", "Use simple past tense ('cooked') for completed past actions."),
            (r"\bsince\s+(\w+)\s+years\s+i\s+am\s+living\b", r"I have been living here for \1 years", "Use present perfect continuous ('have been living') with duration."),
        ]
        if not modified:
            for pat, repl, expl in tense_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                    explanation = expl
                    modified = True
                    break

        if modified:
            # Capitalize first letter and ensure proper punctuation
            corrected_text = text.strip()
            if corrected_text and corrected_text[0].islower():
                corrected_text = corrected_text[0].upper() + corrected_text[1:]
            if not corrected_text.endswith((".", "?", "!")):
                corrected_text += "."
            return {"correction": corrected_text, "explanation": explanation}

        return None

    def _try_external_llm_provider(
        self, sentence: str, category: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Optional external LLM integration if an API key is present in environment.
        Gracefully returns None if no external provider is configured or available.
        """
        api_key = os.getenv("CORRECTION_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        # Placeholder for external LLM call (e.g. httpx call to LLM service)
        # If API fails or is not reached, returns None to trigger graceful unavailable status.
        return None
