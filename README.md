# 🎙️ Fluenora AI ✨
### Deep Learning–Powered English Grammar Classifier & Personalized Learning System
**Deep Learning Project | PyTorch Bi-LSTM & FastAPI Platform**

---

## 🧠 Academic Alignment

| Feature | Syllabus Unit | Topic |
|---|---|---|
| MLP Baseline Classifier | Unit I | Multi-Layer Perceptron, activation functions, loss |
| Bi-LSTM Main Model | Unit IV | RNN, LSTM architecture, hidden states, sequences |
| NLP Preprocessing Pipeline | Unit V | NLP, tokenization, word embeddings |
| CrossEntropy + Adam | Unit I | Loss functions, hyperparameters, backpropagation |
| Class Weights | Unit I | Handling imbalanced training data |
| Evaluation Metrics | Unit I | Accuracy, F1, precision, recall, confusion matrix |
| Personalized Learning | Unit IV | Sequence state tracking across sessions |

---

## 🚀 Quick Start

### 1. Install dependencies
```powershell
pip install -r backend/requirements.txt
```

### 2. Generate dataset & train models
```powershell
Set-Location "c:\Users\User\Downloads\DL project"
python backend/model/dataset.py        # Generate 1,220 labeled sentences
python backend/model/train_lstm.py     # Train Bi-LSTM (50 epochs)
python backend/model/train_mlp.py      # Train MLP baseline (50 epochs)
python backend/model/evaluate.py       # Generate plots + comparison table
```

### 3. Start the backend server
```powershell
Set-Location "c:\Users\User\Downloads\DL project"
uvicorn backend.main:app --reload --port 8000
```

### 4. Open the application
Open your browser at **http://localhost:8000**

---

## 📁 Project Structure
```
DL project/
├── backend/
│   ├── main.py                     # FastAPI app entry point
│   ├── learning_engine.py          # Central orchestrator (model + DB + corrector)
│   ├── corrector.py                # Rule-based sentence correction engine (≠ LSTM)
│   ├── database.py                 # SQLite ORM (SQLAlchemy)
│   ├── requirements.txt
│   └── model/
│       ├── dataset.py              # Synthetic dataset builder (1,220 sentences)
│       ├── preprocess.py           # TextPreprocessor (tokenize, vocab, pad)
│       ├── lstm_model.py           # LSTMClassifier + MLPClassifier (PyTorch)
│       ├── train_lstm.py           # LSTM training script
│       ├── train_mlp.py            # MLP training script
│       ├── evaluate.py             # Metrics, plots, model comparison
│       └── inference.py            # GrammarErrorPredictor (production inference)
├── frontend/
│   ├── index.html                  # Full single-page application UI
│   ├── styles.css                  # UI design system
│   └── app.js                      # Frontend JS controller
├── data/
│   ├── grammar_dataset.csv         # 1,220 labeled sentences (7 categories)
│   └── README_dataset.md           # Dataset documentation & limitations
├── saved/                          # Trained model artifacts (auto-generated)
│   ├── lstm_model.pth              # Best Bi-LSTM weights (84.70% test acc)
│   ├── mlp_model.pth               # Best MLP weights (81.42% test acc)
│   ├── vocab.json                  # 1,094-token vocabulary
│   ├── labels.json                 # 7-class label mapping
│   ├── lstm_training_history.json  # 50-epoch train/val loss & accuracy
│   ├── mlp_training_history.json
│   ├── confusion_matrix_lstm.png   # 300 DPI heatmap
│   ├── confusion_matrix_mlp.png
│   ├── training_curves_lstm.png    # Loss & accuracy over epochs
│   ├── training_curves_mlp.png
│   └── model_comparison.json       # Head-to-head metrics
├── docs/
│   ├── report.md                   # Full academic project report
│   └── model_architecture.md       # Layer-by-layer architecture
└── README.md
```

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                              │
│   ┌────────────────┐     ┌─────────────────────┐     ┌──────────────┐  │
│   │ Interactive    │     │ Daily Practice Prompts│   │ Weakness &   │  │
│   │ Analyzer Tab   │     │ (5 Guided Questions) │   │ Progress Tab │  │
│   └───────┬────────┘     └──────────┬───────────┘     └──────┬───────┘  │
└───────────┼─────────────────────────┼────────────────────────┼─────────┘
            │                         │                        │
            ▼                         ▼                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend (port 8000)                      │
│     POST /api/analyze            GET /api/questions/daily              │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                   LearningEngine                             │    │
│  │  ┌─────────────────────┐   ┌──────────────────────────────┐ │    │
│  │  │  GrammarErrorPredictor│   │   SentenceCorrector          │ │    │
│  │  │  (Bi-LSTM, PyTorch)  │   │   (Rule-based, separate)     │ │    │
│  │  │  vocab.json           │   │   Telugu L1 patterns          │ │    │
│  │  │  lstm_model.pth       │   │                              │ │    │
│  │  └─────────┬────────────┘   └────────────┬─────────────────┘ │    │
│  │            │  label prediction             │  correction text   │    │
│  │            └───────────────┬──────────────┘                   │    │
│  │                            ▼                                   │    │
│  │              ┌─────────────────────────┐                       │    │
│  │              │   SQLite Database       │                       │    │
│  │              │   (fluenora.db)         │                       │    │
│  │              │   submissions, users,   │                       │    │
│  │              │   weakness tracking     │                       │    │
│  │              └─────────────────────────┘                       │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧬 Model Architecture

### Bi-LSTM Classifier (Main Model)
```
Input Tokens  →  Embedding(1094, 64)  →  Dropout(0.3)
             →  BiLSTM(64→128, 2 layers, bidirectional)
             →  Concat[forward_hn, backward_hn]  (256-dim)
             →  Dropout(0.3)
             →  Linear(256 → 7)
             →  Softmax (probability per class)
Total parameters: 665,735
```

### MLP Baseline
```
Input Tokens  →  Embedding(1094, 64)  →  Flatten (64×30=1920)
             →  Linear(1920→256)  →  ReLU  →  Dropout(0.3)
             →  Linear(256→128)  →  ReLU
             →  Linear(128→7)
Total parameters: 595,591
```

---

## 📊 Experimental Results (Actual, Not Fabricated)

> ⚠️ All results below are from actual PyTorch training on the synthetic TeLuEnGramma-1K dataset. Results may not generalize to real learner data.

| Model | Parameters | Test Accuracy | Macro F1 | Weighted F1 |
|---|---|---|---|---|
| **Bi-LSTM (Main)** | 665,735 | **84.70%** | **0.8463** | **0.8470** |
| MLP Baseline | 595,591 | 81.42% | 0.8103 | 0.8125 |

**LSTM advantage: +3.28% accuracy, +3.60% Macro F1 over MLP baseline**

### Per-class F1 (Bi-LSTM)
| Error Category | Precision | Recall | F1 |
|---|---|---|---|
| CORRECT | 0.920 | 0.885 | 0.902 |
| TENSE_ERROR | 0.853 | 0.967 | 0.906 |
| SVA_ERROR | 0.826 | 0.760 | 0.792 |
| ARTICLE_ERROR | 0.808 | 0.778 | 0.793 |
| PREPOSITION_ERROR | 0.724 | 0.808 | 0.764 |
| SPELLING_ERROR | 1.000 | 0.792 | 0.884 |
| STRUCTURE_ERROR | 0.852 | 0.920 | 0.885 |

---

## 🎯 Features

| Feature | How it works |
|---|---|
| 7-class grammar classification | Bi-LSTM model trained on 1,220 sentences |
| Sentence correction | Separate rule-based engine (NOT the LSTM) |
| Daily practice questions | Rotated by calendar day from 60+ question bank |
| Adaptive question selection | Targets user's most frequent error type (SQLite) |
| Progress tracking | Submission history, streak, weakness bars |
| English Learning Academy | Complete grammar curriculum with 17 courses, lessons, and 80% mastery quizzes |
| Speech input | Web Speech API (browser mic) |

---

## ⚠️ Dataset Limitations

This project uses a **synthetic dataset** (TeLuEnGramma-1K) generated from documented Telugu L1 interference patterns. It is **not real human learner data**.

- Sentences mostly exhibit single, isolated grammar errors
- Results on real student essays may differ significantly
- Recommended future work: Evaluate on LANG-8, ICLE, or unscripted university corpora

---

## 🎓 English Learning Academy Platform

In addition to the Deep Learning Diagnostic Lab, the project includes the **English Learning Academy** — a comprehensive web application for learning English grammar from beginner to advanced levels.

### Platform Capabilities:
- **Independent Course Learning**: Select any topic in any order without forced progression.
- **Pure Simple English Instruction**: Clear explanations without regional language dependencies.
- **In-Depth Lessons**:
  - Theory, rules, and formulas (Positive, Negative, Interrogative).
  - Contrasting sentence examples.
  - Common mistakes vs. correct usage comparisons with detailed explanations.
- **Interactive Practice & Quizzes**:
  - Multiple-choice questions, fill-in-the-blanks, error spotting, and sentence transformations.
  - Immediate feedback, retry capabilities, and answer explanations.
  - Comprehensive Final Assessments with an **80% passing mastery threshold**.
- **Deep Learning Bi-LSTM Grammar Diagnosis**:
  - Real-time sentence evaluation connected to the trained PyTorch sequence model.
  - Speech-to-Text input using the Web Speech API.
- **Secure Authentication & Progress Tracking**:
  - Bcrypt password hashing and JWT authorization.
  - SQLite tracking of completed lessons, quiz scores, course mastery, and recurring weaknesses.

### Course Catalog:
1. **Complete English Tenses Masterclass** (12 Full Lessons + Final Assessment)
2. **Subject–Verb Agreement Masterclass** (3 Lessons + Final Assessment)
3. **Parts of Speech & Sentence Structure**
4. **Articles & Determiners Masterclass**
5. **Prepositions & Prepositional Collocations**
6. **Active & Passive Voice Transformations**
7. **Sentence Correction & Error Spotting**

### Access URLs:
- **English Learning Academy (React App)**: [http://localhost:8000/academy](http://localhost:8000/academy)
- **Deep Learning Diagnostic Lab**: [http://localhost:8000/](http://localhost:8000/)
- **Vite React Dev Server (Optional)**: [http://localhost:5173](http://localhost:5173)

### Running Backend Tests:
```powershell
Set-Location "c:\Users\User\Downloads\DL project"
pytest tests/test_academy.py -v
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Server + model status |
| POST | `/api/analyze` | Predict error + correction |
| GET | `/api/questions/daily?limit=5` | Today's practice questions |
| GET | `/api/questions/next?user_id=X` | Personalized next question |
| GET | `/api/user/{user_id}/progress` | Weakness analytics |
| GET | `/api/metrics` | Evaluation benchmarks |

---

## 📄 License
MIT — Free for educational use.
