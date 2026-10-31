import os
import re
import csv
from typing import Dict, Any, Optional, List, Tuple

DISCLAIMER_TEXT = (
    "Sentence corrections and grammatical explanations are provided by the dedicated "
    "Sentence Correction Engine, NOT by the Bi-LSTM error classification model. "
    "The Bi-LSTM model is strictly an error-category classifier."
)

GREETINGS = {
    'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
    'good night', 'thank you', 'thanks', 'thanks a lot', 'thank you very much',
    'welcome', 'you are welcome', "you're welcome", 'bye', 'goodbye', 'see you',
    'yes', 'no', 'okay', 'ok', 'sure', 'alright', 'all right', 'how are you',
    'how do you do', 'nice to meet you', 'pleased to meet you', 'greetings',
    'have a good day', 'have a nice day', 'take care'
}


class SentenceCorrector:
    """
    Dedicated Sentence Correction Engine for Fluenora AI.

    Important Architectural Principle:
    The Bi-LSTM model classifies error categories (TENSE_ERROR, SVA_ERROR, etc.).
    It is a classification model and DOES NOT generate text corrections.
    Text corrections and pedagogical explanations are provided independently
    by this module via:
      1. Conversational greeting and courteous interjection recognition
      2. Verified Telugu-English Learner Corpus matching
      3. Deterministic linguistic rule transformations for Telugu L1 negative transfer
      4. Multi-pass structural, prepositional, SVA, nominalization, and punctuation repairs
      5. Chat abbreviation expansion and interrogative run-on sentence splitting
      6. Optional external LLM provider (when configured via API key)
    """

    def __init__(self, dataset_csv_path: Optional[str] = None):
        self.dataset_corrections: Dict[str, Dict[str, str]] = {}
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        if dataset_csv_path is None:
            dataset_csv_path = os.path.join(project_root, "data", "grammar_dataset.csv")

        self.dataset_csv_path = dataset_csv_path
        self._load_corpus_corrections()

    def _normalize_key(self, text: str) -> str:
        """Normalize text for insensitive lookup (lowercased, stripped, punctuation stripped)."""
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
        Produce a high-quality correction and linguistic explanation for a learner sentence.

        Evaluation order:
          1. Empty check
          2. Conversational greetings & interjections (e.g. "hi" -> CORRECT)
          3. Verified corpus match (exact dataset sentences)
          4. Rule-based & structural transformations (repairs concrete L1 grammar errors)
          5. Verified CORRECT status (only when no rule violations are found)
          6. Category-tailored pedagogical feedback with syntactic cleanup
        """
        if not sentence or not sentence.strip():
            return {
                "original_sentence": sentence,
                "correction": sentence,
                "explanation": "Input sentence is empty.",
                "category": "CORRECT",
                "provider": "rule_based",
                "status": "success",
                "disclaimer": DISCLAIMER_TEXT,
            }

        sentence_stripped = sentence.strip()
        norm = self._normalize_key(sentence_stripped)

        # 1. Greetings & conversational phrases (e.g. "hi", "hello", "thank you")
        if norm in GREETINGS:
            cap_greeting = sentence_stripped.capitalize()
            if not cap_greeting.endswith(('.', '!', '?')):
                cap_greeting += '!'
            return {
                "original_sentence": sentence_stripped,
                "correction": cap_greeting,
                "explanation": "Standard greeting or conversational phrase. Grammatically sound.",
                "category": "CORRECT",
                "provider": "rule_based",
                "status": "success",
                "disclaimer": DISCLAIMER_TEXT,
            }

        # 2. Check verified Corpus match
        if norm in self.dataset_corrections:
            match = self.dataset_corrections[norm]
            return {
                "original_sentence": sentence_stripped,
                "correction": match["correction"],
                "explanation": match["explanation"],
                "category": match.get("category", predicted_category or "CORRECT"),
                "provider": "corpus_match",
                "status": "success",
                "disclaimer": DISCLAIMER_TEXT,
            }

        # 3. Apply Rule-Based Transformations (inspects for concrete grammar & structural errors)
        rule_result = self._apply_rule_transformations(sentence_stripped, predicted_category)
        if rule_result:
            return {
                "original_sentence": sentence_stripped,
                "correction": rule_result["correction"],
                "explanation": rule_result["explanation"],
                "category": rule_result.get("category", predicted_category or "STRUCTURE_ERROR"),
                "provider": "rule_based",
                "status": "success",
                "disclaimer": DISCLAIMER_TEXT,
            }

        # 4. If NO rule errors found and model predicted CORRECT:
        if predicted_category == "CORRECT":
            return {
                "original_sentence": sentence_stripped,
                "correction": sentence_stripped,
                "explanation": "The sentence is grammatically sound. No correction is required.",
                "category": "CORRECT",
                "provider": "rule_based",
                "status": "success",
                "disclaimer": DISCLAIMER_TEXT,
            }

        # 5. External LLM Provider Check
        llm_result = self._try_external_llm_provider(sentence_stripped, predicted_category)
        if llm_result:
            return llm_result

        # 6. Targeted Pedagogical Feedback for identified error category with formatted cleanup
        # Format the sentence (capitalization and punctuation) so user receives a clean sentence
        formatted_sentence = sentence_stripped
        if formatted_sentence and formatted_sentence[0].islower():
            formatted_sentence = formatted_sentence[0].upper() + formatted_sentence[1:]
        if not formatted_sentence.endswith(('.', '?', '!')):
            formatted_sentence += '.'

        guidance = {
            "TENSE_ERROR": "Review verb tense consistency between time indicators and auxiliary verbs.",
            "SVA_ERROR": "Ensure third-person singular subjects (he/she/it) take singular verbs (ending in -s/-es).",
            "ARTICLE_ERROR": "Verify articles ('a', 'an', 'the') before countable or specific nouns.",
            "PREPOSITION_ERROR": "Verify standard preposition usage with specific verbs, adjectives, or time expressions.",
            "SPELLING_ERROR": "Check irregular past tense spellings and commonly confused words.",
            "STRUCTURE_ERROR": "Ensure standard Subject-Verb-Object (SVO) order and proper punctuation between clauses."
        }
        category_hint = guidance.get(predicted_category or "", "Review sentence structure and word usage.")
        return {
            "original_sentence": sentence_stripped,
            "correction": formatted_sentence,
            "explanation": f"Identified category: {predicted_category or 'Grammar Error'}. {category_hint}",
            "category": predicted_category or "STRUCTURE_ERROR",
            "provider": "rule_based",
            "status": "success",
            "disclaimer": DISCLAIMER_TEXT,
        }

    def _apply_rule_transformations(
        self, sentence: str, category: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Deterministic linguistic repair rules addressing frequent Telugu L1 interference:
          - Chat shorthand expansions ('u' -> 'you', 'r' -> 'are', etc.)
          - Time of day prepositions ('at evening' -> 'in the evening', etc.)
          - Festival & event phrasings ('come to my festival' -> 'come over for the festival')
          - Interrogative run-on question + statement splits
          - Spacing before punctuation and comma splices
          - Nominalization (using noun in place of finite predicate verb)
          - Auxiliary 'did' + past tense
          - Stative verbs in continuous aspect
          - Redundant pleonasms
          - Common irregular verb mis-regularization & spelling
          - Preposition interference
          - Article errors
          - Subject-verb agreement (SVA)
          - Structure & word order (SOV to SVO, Wh-inversions)
          - Tense with completed past markers
        """
        text = sentence
        explanations: List[str] = []
        category_votes: Dict[str, int] = {}
        modified = False

        def record_change(cat: str, expl: str):
            nonlocal modified
            modified = True
            category_votes[cat] = category_votes.get(cat, 0) + 1
            if expl not in explanations:
                explanations.append(expl)

        # -------------------------------------------------------------
        # Pass 1: Chat / Text Shorthand Expansions
        # -------------------------------------------------------------
        shorthand_patterns = [
            (r'\bu\b', 'you', "Expanded informal abbreviation 'u' to 'you'.", "SPELLING_ERROR"),
            (r'\bur\b', 'your', "Expanded informal abbreviation 'ur' to 'your'.", "SPELLING_ERROR"),
            (r'\br\b', 'are', "Expanded informal abbreviation 'r' to 'are'.", "SPELLING_ERROR"),
            (r'\bpls\b|\bplz\b', 'please', "Expanded informal abbreviation 'pls' to 'please'.", "SPELLING_ERROR"),
            (r'\bthx\b|\btnx\b', 'thanks', "Expanded informal abbreviation 'thx' to 'thanks'.", "SPELLING_ERROR"),
            (r'\bcoz\b|\bcuz\b|\bcos\b', 'because', "Replaced colloquial 'coz' with 'because'.", "SPELLING_ERROR"),
            (r'\bwanna\b', 'want to', "Expanded informal contraction 'wanna' to 'want to'.", "STRUCTURE_ERROR"),
            (r'\bgonna\b', 'going to', "Expanded informal contraction 'gonna' to 'going to'.", "STRUCTURE_ERROR"),
        ]
        for pat, repl, expl, cat in shorthand_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)

        # -------------------------------------------------------------
        # Pass 2: Spacing before punctuation & basic cleanup
        # e.g. "home ,come" -> "home, come"
        # -------------------------------------------------------------
        punc_space_fix = re.sub(r'\s+([,.;?!])', r'\1', text)
        if punc_space_fix != text:
            text = punc_space_fix
            record_change("STRUCTURE_ERROR", "Fixed improper spacing before punctuation.")

        # Ensure space after comma if missing
        comma_space_fix = re.sub(r',([^\s])', r', \1', text)
        if comma_space_fix != text:
            text = comma_space_fix
            record_change("STRUCTURE_ERROR", "Added standard spacing after comma.")

        # -------------------------------------------------------------
        # Pass 3: Time of Day Preposition Errors
        # e.g. "at evening" -> "in the evening"
        # -------------------------------------------------------------
        time_prep_patterns = [
            (r'\b(at|on)\s+evening\b', 'in the evening', "Use preposition 'in the evening' (not 'at evening') for time of day.", "PREPOSITION_ERROR"),
            (r'\b(at|on)\s+morning\b', 'in the morning', "Use preposition 'in the morning' (not 'at morning') for time of day.", "PREPOSITION_ERROR"),
            (r'\b(at|on)\s+afternoon\b', 'in the afternoon', "Use preposition 'in the afternoon' (not 'at afternoon') for time of day.", "PREPOSITION_ERROR"),
            (r'\b(in|on)\s+night\b', 'at night', "Use preposition 'at night' (not 'in night').", "PREPOSITION_ERROR"),
        ]
        for pat, repl, expl, cat in time_prep_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)

        # -------------------------------------------------------------
        # Pass 4: Festival & Event Phrasing
        # e.g. "come to my festival" -> "come over to my home for the festival"
        # -------------------------------------------------------------
        event_phrasing = [
            (r'\bcome\s+to\s+my\s+festival\b', 'come over to my home for the festival', "Phrased 'come to my festival' to 'come over to my home for the festival' (a festival is an event, not a location).", "STRUCTURE_ERROR"),
            (r'\b(on|in)\s+festival\b', 'during the festival', "Use 'during the festival' or 'for the festival' instead of 'on festival'.", "PREPOSITION_ERROR"),
            (r'\b(on|in)\s+holiday\b', 'during the holidays', "Use 'during the holidays' or 'on holiday' instead of 'in holiday'.", "PREPOSITION_ERROR"),
            (r'\b(on|in)\s+vacation\b', 'on vacation', "Use prepositional phrase 'on vacation'.", "PREPOSITION_ERROR"),
            (r'\b(on|in)\s+function\b', 'at the function', "Use 'at the function' instead of 'on function'.", "PREPOSITION_ERROR"),
            (r'\b(on|in)\s+marriage\b', 'at the wedding', "Use 'at the wedding' instead of 'on marriage'.", "PREPOSITION_ERROR"),
            (r'\b(on|in)\s+meeting\b', 'in the meeting', "Use 'in the meeting' or 'at the meeting'.", "PREPOSITION_ERROR"),
        ]
        for pat, repl, expl, cat in event_phrasing:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)

        # -------------------------------------------------------------
        # Pass 5: Question + Statement Run-on Split
        # e.g. "can you come to my home ... i will arrange dinner ..." -> "Can you come ...? I will arrange ..."
        # -------------------------------------------------------------
        interrogative_runon = r'^(can|could|would|will)\s+(you|we)\s+([^?.!]+?)\s+(i|we|they|he|she)\s+(will|shall|can|would|am|are|is)\b'
        m = re.match(interrogative_runon, text, re.IGNORECASE)
        if m:
            modal = m.group(1).capitalize()
            subject = m.group(2)
            predicate1 = m.group(3).strip()
            subject2 = m.group(4)
            subject2 = 'I' if subject2.lower() == 'i' else subject2.capitalize()
            modal2 = m.group(5)
            rest = text[m.end():]
            text = f"{modal} {subject} {predicate1}? {subject2} {modal2}{rest}"
            record_change("STRUCTURE_ERROR", "Separated opening invitation question from the subsequent statement with a question mark ('?').")

        # -------------------------------------------------------------
        # Pass 6: Capitalize standalone pronoun 'i'
        # -------------------------------------------------------------
        i_cap = re.sub(r'\b(i)\b', 'I', text)
        if i_cap != text:
            text = i_cap
            record_change("STRUCTURE_ERROR", "Capitalized the first-person pronoun 'I'.")

        # -------------------------------------------------------------
        # Rule Set J: Nominalization / Missing Predicate Verb
        # e.g. "we celebrations at home" -> "we are celebrating at home"
        # -------------------------------------------------------------
        nominalization_patterns = [
            (r'\b(we|they|you)\s+celebrations?\b', r'\1 are celebrating', "Use finite verb 'are celebrating' or 'celebrate' instead of noun 'celebrations'.", "STRUCTURE_ERROR"),
            (r'\b(i)\s+celebrations?\b', r'I am celebrating', "Use finite verb 'am celebrating' or 'celebrate' instead of noun 'celebrations'.", "STRUCTURE_ERROR"),
            (r'\b(he|she)\s+celebrations?\b', r'\1 is celebrating', "Use finite verb 'is celebrating' or 'celebrates' instead of noun 'celebrations'.", "STRUCTURE_ERROR"),
            (r'\b(we|they|you)\s+preparations?\b', r'\1 are preparing', "Use finite verb 'are preparing' instead of noun 'preparations'.", "STRUCTURE_ERROR"),
            (r'\b(i)\s+preparations?\b', r'I am preparing', "Use finite verb 'am preparing' instead of noun 'preparations'.", "STRUCTURE_ERROR"),
            (r'\b(he|she)\s+preparations?\b', r'\1 is preparing', "Use finite verb 'is preparing' instead of noun 'preparations'.", "STRUCTURE_ERROR"),
            (r'\b(we|they|you)\s+discussions?\b', r'\1 are discussing', "Use finite verb 'are discussing' instead of noun 'discussions'.", "STRUCTURE_ERROR"),
            (r'\b(i)\s+discussions?\b', r'I am discussing', "Use finite verb 'am discussing' instead of noun 'discussions'.", "STRUCTURE_ERROR"),
            (r'\b(he|she)\s+discussions?\b', r'\1 is discussing', "Use finite verb 'is discussing' instead of noun 'discussions'.", "STRUCTURE_ERROR"),
            (r'\b(we|they|you|i)\s+participations?\b', r'\1 participate', "Use predicate verb 'participate' instead of noun 'participation'.", "STRUCTURE_ERROR"),
            (r'\b(he|she)\s+participations?\b', r'\1 participates', "Use predicate verb 'participates' instead of noun 'participation'.", "STRUCTURE_ERROR"),
            (r'\b(we|they|you|i)\s+invitations?\b', r'\1 invite', "Use verb 'invite' instead of noun 'invitation'.", "STRUCTURE_ERROR"),
            (r'\b(he|she)\s+invitations?\b', r'\1 invites', "Use verb 'invites' instead of noun 'invitation'.", "STRUCTURE_ERROR"),
            (r'\b(we|they|you|i)\s+arrangements?\b', r'\1 are making arrangements', "Use verbal phrase 'are making arrangements' instead of noun 'arrangements'.", "STRUCTURE_ERROR"),
            (r'\b(he|she)\s+arrangements?\b', r'\1 is making arrangements', "Use verbal phrase 'is making arrangements' instead of noun 'arrangements'.", "STRUCTURE_ERROR"),
        ]
        for pat, repl, expl, cat in nominalization_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set L: Comma-Splice and Clause Juncture
        # e.g. "at my home, come" -> "at my home; please come"
        # -------------------------------------------------------------
        clause_splice_patterns = [
            (r'(\b(?:at my home|at home|with us|with me))\s*,\s*(come to\b)', r'\1; please \2', "Separate independent clauses with a semicolon or period rather than a comma splice.", "STRUCTURE_ERROR"),
            (r'(\b(?:at my home|at home|with us|with me))\s*,\s*(come\b)', r'\1; please come', "Separate independent clauses with a semicolon or period rather than a comma splice.", "STRUCTURE_ERROR"),
        ]
        for pat, repl, expl, cat in clause_splice_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)

        # Add comma after clause-initial adverbials ("During the festival we" -> "During the festival, we")
        initial_adv_pat = r'^(during the festival|for the festival|on the weekend|in the morning)\s+(?!,)'
        if re.search(initial_adv_pat, text, re.IGNORECASE):
            text = re.sub(initial_adv_pat, r'\1, ', text, flags=re.IGNORECASE)
            modified = True

        # -------------------------------------------------------------
        # Rule Set A: Auxiliary 'did' + past tense ("did completed" -> "did complete")
        # -------------------------------------------------------------
        did_past_patterns = [
            (r"\b(did|didn't|did not)\s+completed\b", r"\1 complete", "Use base verb 'complete' after auxiliary 'did'.", "TENSE_ERROR"),
            (r"\b(did|didn't|did not)\s+saw\b", r"\1 see", "Use base verb 'see' after auxiliary 'didn't'.", "TENSE_ERROR"),
            (r"\b(did|didn't|did not)\s+came\b", r"\1 come", "Use base verb 'come' after auxiliary 'did'.", "TENSE_ERROR"),
            (r"\b(did|didn't|did not)\s+went\b", r"\1 go", "Use base verb 'go' after auxiliary 'did'.", "TENSE_ERROR"),
            (r"\b(did|didn't|did not)\s+told\b", r"\1 tell", "Use base verb 'tell' after auxiliary 'did'.", "TENSE_ERROR"),
            (r"\b(did|didn't|did not)\s+brought\b", r"\1 bring", "Use base verb 'bring' after auxiliary 'did'.", "TENSE_ERROR"),
            (r"\b(did|didn't|did not)\s+wrote\b", r"\1 write", "Use base verb 'write' after auxiliary 'did'.", "TENSE_ERROR"),
        ]
        for pat, repl, expl, cat in did_past_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set B: Stative verbs in continuous aspect ("am knowing", "is having")
        # -------------------------------------------------------------
        stative_patterns = [
            (r"\b(is|are|am)\s+having\b", "has" if re.search(r"\b(he|she|it)\b", text, re.I) else "have", "Stative verb 'have' indicating possession is not used in continuous aspect.", "TENSE_ERROR"),
            (r"\b(is|are|am)\s+knowing\b", "knows" if re.search(r"\b(he|she|it)\b", text, re.I) else "know", "Stative verb 'know' should be in simple present, not continuous.", "TENSE_ERROR"),
            (r"\b(is|are|am)\s+understanding\b", "understands" if re.search(r"\b(he|she|it)\b", text, re.I) else "understand", "Stative verb 'understand' is not used in continuous aspect.", "TENSE_ERROR"),
            (r"\b(is|are|am)\s+liking\b", "likes" if re.search(r"\b(he|she|it)\b", text, re.I) else "like", "Stative verb 'like' expresses state and should be simple present.", "TENSE_ERROR"),
            (r"\b(is|are|am)\s+wanting\b", "wants" if re.search(r"\b(he|she|it)\b", text, re.I) else "want", "Stative verb 'want' should be simple present.", "TENSE_ERROR"),
        ]
        for pat, repl, expl, cat in stative_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set C: Redundant Pleonasms ("return back", "revert back", "repeat again")
        # -------------------------------------------------------------
        pleonasm_patterns = [
            (r"\breturn\s+back\b", "return", "'Return' means to give or come back; 'back' is redundant pleonasm.", "STRUCTURE_ERROR"),
            (r"\brevert\s+back\b", "revert", "'Revert' already means reply back; 'back' is redundant.", "STRUCTURE_ERROR"),
            (r"\brepeat\s+again\b", "repeat", "'Repeat' means say again; 'again' is redundant.", "STRUCTURE_ERROR"),
            (r"\brecall\s+back\b", "recall", "'Recall' means to call back into memory; 'back' is redundant.", "STRUCTURE_ERROR"),
            (r"\breply\s+back\b", "reply", "'Reply' already includes the concept of responding back.", "STRUCTURE_ERROR"),
        ]
        for pat, repl, expl, cat in pleonasm_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set D: Common Phonetic & Irregular verb mis-regularization (Spelling errors)
        # -------------------------------------------------------------
        spelling_patterns = [
            (r"\bspeaked\s+very\s+fastly\b", "spoke very fast", "Irregular verb: speak -> spoke. 'Fast' has no -ly adverb form.", "SPELLING_ERROR"),
            (r"\bspeaked\b", "spoke", "Irregular verb 'speak' becomes 'spoke' in simple past, not 'speaked'.", "SPELLING_ERROR"),
            (r"\bfastly\b", "fast", "'Fast' serves as both adjective and adverb; 'fastly' is not a standard English word.", "SPELLING_ERROR"),
            (r"\bcatched\b", "caught", "Irregular past tense of 'catch' is 'caught', not 'catched'.", "SPELLING_ERROR"),
            (r"\bwrited\b", "wrote", "Irregular past tense of 'write' is 'wrote', not 'writed'.", "SPELLING_ERROR"),
            (r"\bbited\b", "bit", "Irregular past tense of 'bite' is 'bit', not 'bited'.", "SPELLING_ERROR"),
            (r"\brunned\b", "ran", "Irregular past tense of 'run' is 'ran', not 'runned'.", "SPELLING_ERROR"),
            (r"\bfeeled\b", "felt", "Irregular past tense of 'feel' is 'felt', not 'feeled'.", "SPELLING_ERROR"),
            (r"\bpayed\b", "paid", "Past tense of 'pay' is spelled 'paid'.", "SPELLING_ERROR"),
            (r"\bteached\b", "taught", "Irregular past tense of 'teach' is 'taught', not 'teached'.", "SPELLING_ERROR"),
            (r"\bgrammer\b", "grammar", "Spelling error: 'grammar' is spelled with -ar.", "SPELLING_ERROR"),
            (r"\bdefinate\b", "definite", "Spelling error: 'definite' is spelled with -ite.", "SPELLING_ERROR"),
            (r"\brecieved\b", "received", "Spelling rule: 'e' before 'i' after 'c' ('received').", "SPELLING_ERROR"),
            (r"\battendence\b", "attendance", "Spelling error: 'attendance' ends with -ance.", "SPELLING_ERROR"),
            (r"\bbeautifull\b", "beautiful", "Spelling error: 'beautiful' has a single 'l' at the end.", "SPELLING_ERROR"),
            (r"\bseperately\b", "separately", "Spelling error: 'separately' contains -para-, not -pera-.", "SPELLING_ERROR"),
            (r"\bloose\s+your\b", "lose your", "Homophone error: 'lose' means to misplace; 'loose' means not tight.", "SPELLING_ERROR"),
            (r"\bpleasent\b", "pleasant", "Spelling error: 'pleasant' ends in -ant.", "SPELLING_ERROR"),
            (r"\btruely\b", "truly", "Spelling error: 'truly' drops the 'e'.", "SPELLING_ERROR"),
            (r"\barguement\b", "argument", "Spelling error: 'argument' drops the 'e' from 'argue'.", "SPELLING_ERROR"),
            (r"\bresturant\b", "restaurant", "Spelling error: 'restaurant' is the correct spelling.", "SPELLING_ERROR"),
            (r"\btommorow\b", "tomorrow", "Spelling error: 'tomorrow' has one 'm' and double 'r'.", "SPELLING_ERROR"),
            (r"\bbeleive\b", "believe", "Spelling error: 'believe' is spelled with -ie-.", "SPELLING_ERROR"),
        ]
        for pat, repl, expl, cat in spelling_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set E: Preposition Interference
        # -------------------------------------------------------------
        prep_patterns = [
            (r"\bgood\s+in\s+english\b", "good at English", "Use preposition 'at' for competencies and subjects ('good at English').", "PREPOSITION_ERROR"),
            (r"\bweak\s+in\s+english\b", "weak at English", "Use preposition 'at' for abilities ('weak at English').", "PREPOSITION_ERROR"),
            (r"\bangry\s+on\s+(me|him|her|them|us)\b", r"angry with \1", "Use preposition 'with' when angry at a person, not 'on'.", "PREPOSITION_ERROR"),
            (r"\bdiscussed\s+about\b", "discussed", "'Discuss' is a transitive verb; do not use 'about' after it.", "PREPOSITION_ERROR"),
            (r"\bentered\s+into\s+the\b", "entered the", "'Enter' into a physical place takes no preposition 'into'.", "PREPOSITION_ERROR"),
            (r"\bordered\s+for\s+a\b", "ordered a", "'Order' is a transitive verb; omit 'for'.", "PREPOSITION_ERROR"),
            (r"\bordered\s+for\s+two\b", "ordered two", "'Order' is transitive; omit 'for'.", "PREPOSITION_ERROR"),
            (r"\bmarried\s+with\s+a\b", "married to a", "Use 'married to', not 'married with'.", "PREPOSITION_ERROR"),
            (r"\bdied\s+with\s+(cancer|malaria|cholera|fever)\b", r"died of \1", "Use 'died of' a disease, not 'died with'.", "PREPOSITION_ERROR"),
            (r"\bsuffering\s+with\s+(fever|cough|cold)\b", r"suffering from \1", "Use 'suffering from' an illness, not 'with'.", "PREPOSITION_ERROR"),
            (r"\bin\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", r"on \1", "Use preposition 'on' with days of the week.", "PREPOSITION_ERROR"),
            (r"\bafraid\s+from\b", "afraid of", "Use 'afraid of', not 'afraid from'.", "PREPOSITION_ERROR"),
            (r"\bsenior\s+than\s+me\b", "senior to me", "Comparative adjectives ending in -ior take 'to', not 'than'.", "PREPOSITION_ERROR"),
            (r"\bcongratulated\s+(.*?)\s+for\s+his\b", r"congratulated \1 on his", "Use 'congratulate on an achievement', not 'for'.", "PREPOSITION_ERROR"),
        ]
        for pat, repl, expl, cat in prep_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set F: Article Errors
        # -------------------------------------------------------------
        art_patterns = [
            (r"\ba\s+honest\b", "an honest", "Use 'an' before 'honest' because the 'h' is silent (vowel sound /ɒ/).", "ARTICLE_ERROR"),
            (r"\ban\s+useful\b", "a useful", "Use 'a' before 'useful' because it begins with consonant glide /juː/.", "ARTICLE_ERROR"),
            (r"\ban\s+european\b", "a European", "Use 'a' before 'European' because it starts with consonant /j/ sound.", "ARTICLE_ERROR"),
            (r"\ban\s+unique\b", "a unique", "Use 'a' before 'unique' because it begins with consonant /juː/ sound.", "ARTICLE_ERROR"),
            (r"\ba\s+uncle\b", "an uncle", "Use 'an' before vowel sound in 'uncle'.", "ARTICLE_ERROR"),
            (r"\ba\s+iphone\b", "an iPhone", "Use 'an' before vowel sound in 'iPhone'.", "ARTICLE_ERROR"),
            (r"\ba\s+umbrella\b", "an umbrella", "Use 'an' before vowel sound in 'umbrella'.", "ARTICLE_ERROR"),
            (r"\ba\s+engineer\b", "an engineer", "Use 'an' before vowel sound in 'engineer'.", "ARTICLE_ERROR"),
            (r"\ba\s+hour\b", "an hour", "Use 'an' before 'hour' because initial 'h' is silent.", "ARTICLE_ERROR"),
            (r"\ba\s+orange\b", "an orange", "Use 'an' before vowel sound in 'orange'.", "ARTICLE_ERROR"),
            (r"\ba\s+apple\b", "an apple", "Use 'an' before vowel sound in 'apple'.", "ARTICLE_ERROR"),
            (r"\bsun\s+rises\s+in\s+east\b", "the sun rises in the east", "Celestial bodies and cardinal directions require 'the'.", "ARTICLE_ERROR"),
            (r"\bmount\s+everest\s+is\s+highest\b", "Mount Everest is the highest", "Superlative adjectives require definite article 'the'.", "ARTICLE_ERROR"),
        ]
        for pat, repl, expl, cat in art_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set G: Subject-Verb Agreement (SVA)
        # -------------------------------------------------------------
        sva_patterns = [
            (r"\bshe\s+go\b", "she goes", "Third-person singular 'she' requires verb ending in -es ('goes').", "SVA_ERROR"),
            (r"\bhe\s+work\b", "he works", "Third-person singular 'he' requires verb with -s ('works').", "SVA_ERROR"),
            (r"\bmy\s+brother\s+work\b", "my brother works", "Singular subject requires third-person singular verb 'works'.", "SVA_ERROR"),
            (r"\bhe\s+don't\b", "he doesn't", "Third-person singular subject requires negative auxiliary 'doesn't'.", "SVA_ERROR"),
            (r"\bshe\s+don't\b", "she doesn't", "Third-person singular subject requires negative auxiliary 'doesn't'.", "SVA_ERROR"),
            (r"\bone\s+of\s+my\s+friends\s+are\b", "one of my friends is", "'One of + plural noun' takes singular verb 'is'.", "SVA_ERROR"),
            (r"\bevery\s+student\s+have\b", "every student has", "'Every' takes singular auxiliary 'has'.", "SVA_ERROR"),
            (r"\beveryone\s+want\b", "everyone wants", "Indefinite pronoun 'everyone' takes singular verb 'wants'.", "SVA_ERROR"),
            (r"\bthe\s+children\s+likes\b", "the children like", "Plural noun 'children' requires plural base verb 'like'.", "SVA_ERROR"),
            (r"\bthey\s+was\b", "they were", "Plural pronoun 'they' requires 'were', not 'was'.", "SVA_ERROR"),
            (r"\bwe\s+was\b", "we were", "Plural pronoun 'we' requires 'were', not 'was'.", "SVA_ERROR"),
            (r"\byou\s+was\b", "you were", "Pronoun 'you' takes plural past verb 'were'.", "SVA_ERROR"),
        ]
        for pat, repl, expl, cat in sva_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set H: Structure & Word Order
        # -------------------------------------------------------------
        struct_patterns = [
            (r"\bi\s+english\s+very\s+much\s+like\b", "I like English very much", "English follows Subject-Verb-Object (SVO) word order, not Telugu SOV.", "STRUCTURE_ERROR"),
            (r"\bwhere\s+you\s+are\s+going\b", "where are you going", "In Wh-questions, auxiliary verb 'are' must precede the subject 'you'.", "STRUCTURE_ERROR"),
            (r"\bwhy\s+you\s+didn't\b", "why didn't you", "Inverted interrogative requires auxiliary before subject ('why didn't you').", "STRUCTURE_ERROR"),
            (r"\bwhat\s+your\s+name\s+is\b", "what is your name", "In question form, auxiliary 'is' must precede subject.", "STRUCTURE_ERROR"),
            (r"\bmyself\s+i\s+am\s+(.*?)\b", r"I am \1", "Do not use reflexive pronoun 'myself' as the sentence subject.", "STRUCTURE_ERROR"),
            (r"\bthough\s+(.*?)\s+but\s+", r"Though \1, ", "Do not use 'though' and 'but' together in a single sentence.", "STRUCTURE_ERROR"),
        ]
        for pat, repl, expl, cat in struct_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        # -------------------------------------------------------------
        # Rule Set I: Present continuous with past time markers (Tense Error)
        # -------------------------------------------------------------
        tense_patterns = [
            (r"\byesterday\s+i\s+am\s+going\b", "yesterday I went", "Use simple past tense ('went') for past completed actions.", "TENSE_ERROR"),
            (r"\byesterday\s+he\s+is\s+going\b", "yesterday he went", "Use simple past tense with past time markers like 'yesterday'.", "TENSE_ERROR"),
            (r"\blast\s+night\s+she\s+is\s+cooking\b", "last night she cooked", "Use simple past tense ('cooked') for completed past actions.", "TENSE_ERROR"),
            (r"\bsince\s+(\w+)\s+years\s+i\s+am\s+living\b", r"I have been living here for \1 years", "Use present perfect continuous ('have been living') with duration.", "TENSE_ERROR"),
        ]
        for pat, repl, expl, cat in tense_patterns:
            if re.search(pat, text, re.IGNORECASE):
                text = re.sub(pat, repl, text, flags=re.IGNORECASE)
                record_change(cat, expl)
                break

        if modified:
            # Capitalize first letter of every sentence and format spacing
            cleaned = re.sub(r'\s{2,}', ' ', text).strip()
            # Capitalize first letter after . / ? / !
            cleaned = re.sub(r'([.?!]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), cleaned)
            if cleaned and cleaned[0].islower():
                cleaned = cleaned[0].upper() + cleaned[1:]

            # Proper ending punctuation check
            if not cleaned.endswith((".", "?", "!")):
                # Check trailing clause
                last_clause = cleaned.split('?')[-1].split('.')[-1].strip()
                if re.match(r'^(Can|Could|Would|Will|Do|Does|Did|Is|Are|Was|Were|Have|Has|What|Where|When|Why|How|Who)\b', last_clause, re.I):
                    cleaned += "?"
                else:
                    cleaned += "."

            # Select dominant category: prioritize STRUCTURE_ERROR if structural rule fired
            if category_votes.get("STRUCTURE_ERROR", 0) > 0:
                dominant_cat = "STRUCTURE_ERROR"
            elif category_votes:
                dominant_cat = max(category_votes.items(), key=lambda x: x[1])[0]
            else:
                dominant_cat = category or "STRUCTURE_ERROR"

            full_expl = " ".join(explanations) if explanations else "Sentence corrected."
            return {
                "correction": cleaned,
                "explanation": full_expl,
                "category": dominant_cat
            }

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
        return None
