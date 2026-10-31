# Fluenora AI ✨ - Telugu-English Grammar Error Dataset

## 1. Overview
The **Fluenora AI Grammar Dataset** is a curated and synthetically synthesized linguistic dataset designed specifically to model, detect, and categorize grammatical errors committed by English language learners from Telugu-speaking backgrounds (Telugu L1 interference).

Telugu is a Dravidian language characterized by Subject-Object-Verb (SOV) syntactic word order, agglutinative inflectional morphology, absence of definite/indefinite grammatical articles, and distinct verbal aspect semantics. When Telugu speakers acquire English (an SVO language with a rich article and prepositional system), characteristic L1 negative transfer errors emerge.

---

## 2. Dataset Schema & Structure
The dataset is serialized at `data/grammar_dataset.csv` with the following 5 standard columns:

| Column | Type | Description |
| :--- | :--- | :--- |
| `sentence` | String | Raw learner sentence containing a grammatical flaw or correct usage. |
| `label` | Integer | Class index ranging from `0` to `6`. |
| `label_name` | String | Standardized error category designation. |
| `correction` | String | Standard grammatically correct reference English sentence. |
| `explanation` | String | Pedagogical and linguistic explanation of why the sentence is erroneous and how to correct it. |

---

## 3. Categories & Linguistic Error Analysis

The dataset defines 7 distinct mutually exclusive classes:

```python
LABELS = {
    0: "CORRECT",
    1: "TENSE_ERROR",
    2: "SVA_ERROR",
    3: "ARTICLE_ERROR",
    4: "PREPOSITION_ERROR",
    5: "SPELLING_ERROR",
    6: "STRUCTURE_ERROR"
}
```

### Class Breakdown:

### `0: CORRECT`
- **Description**: Grammatically and syntactically sound Standard English sentences spanning academic, professional, and daily conversational topics.
- **Example**: `"The students are preparing diligently for their upcoming examinations."`

### `1: TENSE_ERROR`
- **Linguistic Root**: Telugu speakers often use present continuous aspect for past actions (*Telugu: ninna nenu college ki velthunnanu*), misapply stative verbs in progressive aspect (*"I am knowing the answer"*), repeat future modals in conditional clauses (*"When you will come..."*), or misapply the auxiliary *did* with past tense (*"Did you completed your record?"*).
- **Example**: `"Yesterday I am going to college by bus."` $\rightarrow$ `"Yesterday I went to college by bus."`

### `2: SVA_ERROR` (Subject-Verb Agreement)
- **Linguistic Root**: Telugu verb agreement marks gender, number, and person differently. Learners commonly drop third-person singular present `-s/-es` (*"She go to school"*), use plural verbs with indefinite pronouns (*"Every student have a mobile"*), or confuse collective and distributive nouns (*"One of my friends are coming"*).
- **Example**: `"She go to school every day."` $\rightarrow$ `"She goes to school every day."`

### `3: ARTICLE_ERROR`
- **Linguistic Root**: Telugu does not possess indefinite (*a, an*) or definite (*the*) articles. Errors include omission before singular countable nouns, misuse of *a/an* based on orthography instead of phonetics (*"a honest officer"*, *"an European"*), or dropping *the* before unique celestial bodies and superlatives.
- **Example**: `"I have a uncle who is doctor in Guntur."` $\rightarrow$ `"I have an uncle who is a doctor in Guntur."`

### `4: PREPOSITION_ERROR`
- **Linguistic Root**: Direct literal translation of Telugu postpositions (*-lo* $\rightarrow$ *in*, *-meeda* $\rightarrow$ *on*, *-thoti* $\rightarrow$ *with*). This results in errors such as *"good in English"* instead of *"good at"*, *"angry on me"* instead of *"angry with me"*, and redundant prepositions with transitive verbs (*"discussed about"*, *"entered into"*).
- **Example**: `"My teacher is very angry on me for coming late."` $\rightarrow$ `"My teacher is very angry with me for coming late."`

### `5: SPELLING_ERROR`
- **Linguistic Root**: Over-regularization of irregular past tense verbs with `-ed` (*speaked*, *catched*, *writed*, *bited*), phonetic spelling habits (*grammer*, *definate*, *recieved*, *attendence*), and homophone confusions (*loose* vs *lose*).
- **Example**: `"She speaked very fastly during the debate competition."` $\rightarrow$ `"She spoke very fast during the debate competition."`

### `6: STRUCTURE_ERROR`
- **Linguistic Root**: Telugu SOV (Subject-Object-Verb) interference (*"I English very much like"*), lack of auxiliary inversion in Wh-questions (*"Where you are going?"*, *"What your name is?"*), pleonastic redundancies (*"return back"*, *"revert back"*), and double conjunctions (*"Though... but"*).
- **Example**: `"Where you are going right now with heavy bag?"` $\rightarrow$ `"Where are you going right now with a heavy bag?"`

---

## 4. Dataset Splits & Statistics
The dataset is split using stratified random sampling to preserve exact class ratios:
- **Total Samples**: 1,050+ sentences
- **Minimum per Class**: $\ge 150$ samples
- **Split Ratio**:
  - **Train Set**: 70%
  - **Validation Set**: 15%
  - **Test Set**: 15%

---

## 5. Known Limitations
1. **Synthetic & Semi-Automated Composition**: While patterns are grounded in documented L1 Telugu interference studies and Indian ESL learner corpora, sentences are synthetically generated rather than harvested from human essay transcriptions.
2. **Single-Error Dominance**: Sentences primarily exhibit one primary error category to ensure high discriminative learning for classification baselines, whereas real student writing frequently contains composite multiple overlapping errors.
3. **Lexical Domain**: Vocabulary is tailored around common collegiate, domestic, and professional Indian contexts.

---

## 6. How to Extend the Dataset
1. **Incorporate Real Student Essays**: Ingest digitized Telugu-English learner essays from university writing centers or public ESL corpora (e.g., ICLE, Lang-8).
2. **Fine-Grained Sub-categories**: Subdivide `TENSE_ERROR` into *Stative Aspect*, *Past Marker Incompatibility*, and *Auxiliary Redundancy*.
3. **Sequence-to-Sequence Modeling**: Extend beyond category classification to token-level sequence labeling (BIO tagging) and generative sequence-to-sequence correction using T5 / BART.
