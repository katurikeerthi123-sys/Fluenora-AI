import os
import sys
import json
import torch
import torch.nn.functional as F
from typing import List, Dict, Any, Union

# Ensure backend/model can be imported directly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from preprocess import TextPreprocessor
from lstm_model import LSTMClassifier, MLPClassifier
from dataset import LABELS


class GrammarErrorPredictor:
    """
    Inference Engine for Fluenora AI ✨ Grammar Error Detection.
    Loads trained PyTorch model (BiLSTM or MLP), vocabulary, and label mappings
    to provide single-sentence and batch grammar error classification with confidence scores.
    """
    def __init__(
        self,
        model_path: str = "saved/lstm_model.pth",
        vocab_path: str = "saved/vocab.json",
        labels_path: str = "saved/labels.json",
        model_type: str = "lstm",
        device: str = None
    ):
        # Resolve paths relative to current script or working directory
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

        def resolve_path(p: str) -> str:
            if os.path.isabs(p):
                return p
            candidate_1 = os.path.join(project_root, p)
            if os.path.exists(candidate_1):
                return candidate_1
            return p

        self.model_path = resolve_path(model_path)
        self.vocab_path = resolve_path(vocab_path)
        self.labels_path = resolve_path(labels_path)
        self.model_type = model_type.lower()

        # Device configuration
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # Load Preprocessor and Labels
        if not os.path.exists(self.vocab_path):
            raise FileNotFoundError(f"Vocabulary file not found at: {self.vocab_path}")
        self.preprocessor = TextPreprocessor.load(self.vocab_path)

        if os.path.exists(self.labels_path):
            with open(self.labels_path, "r", encoding="utf-8") as f:
                raw_labels = json.load(f)
            self.labels = {int(k): v for k, v in raw_labels.items()}
        else:
            self.labels = LABELS

        self.num_classes = len(self.labels)

        # Initialize and Load Model
        if self.model_type == "lstm":
            self.model = LSTMClassifier(
                vocab_size=self.preprocessor.vocab_size,
                embed_dim=64,
                hidden_dim=128,
                num_layers=2,
                num_classes=self.num_classes,
                dropout=0.3
            )
        elif self.model_type == "mlp":
            self.model = MLPClassifier(
                vocab_size=self.preprocessor.vocab_size,
                embed_dim=64,
                max_len=self.preprocessor.max_len,
                hidden_dim=256,
                num_classes=self.num_classes,
                dropout=0.3
            )
        else:
            raise ValueError(f"Unsupported model_type: '{self.model_type}'. Choose 'lstm' or 'mlp'.")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model weights not found at: {self.model_path}")

        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def predict(self, sentence: str) -> Dict[str, Any]:
        """
        Predict the grammatical error category for a single sentence.
        Returns:
            {
                "sentence": str,
                "label_id": int,
                "label_name": str,
                "confidence": float,
                "top3": [
                    {"label": str, "label_id": int, "confidence": float}, ...
                ]
            }
        """
        if not sentence or not sentence.strip():
            return {
                "sentence": sentence,
                "label_id": 0,
                "label_name": self.labels.get(0, "CORRECT"),
                "confidence": 1.0,
                "top3": [{"label": self.labels.get(0, "CORRECT"), "label_id": 0, "confidence": 1.0}]
            }

        encoded = self.preprocessor.encode(sentence)
        input_tensor = torch.tensor([encoded], dtype=torch.long).to(self.device)

        with torch.no_grad():
            logits = self.model(input_tensor)
            probs = F.softmax(logits, dim=1).squeeze(0)

        top_probs, top_indices = torch.topk(probs, k=min(3, self.num_classes))
        top_probs = top_probs.cpu().numpy()
        top_indices = top_indices.cpu().numpy()

        top3 = []
        for prob, idx in zip(top_probs, top_indices):
            top3.append({
                "label": self.labels.get(int(idx), f"CLASS_{idx}"),
                "label_id": int(idx),
                "confidence": round(float(prob), 4)
            })

        best_label_id = int(top_indices[0])
        best_label_name = self.labels.get(best_label_id, f"CLASS_{best_label_id}")
        best_confidence = round(float(top_probs[0]), 4)

        return {
            "sentence": sentence,
            "label_id": best_label_id,
            "label_name": best_label_name,
            "confidence": best_confidence,
            "top3": top3
        }

    def predict_batch(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Batch prediction for a list of sentences.
        """
        if not sentences:
            return []

        batch_encoded = [self.preprocessor.encode(s) for s in sentences]
        input_tensor = torch.tensor(batch_encoded, dtype=torch.long).to(self.device)

        with torch.no_grad():
            logits = self.model(input_tensor)
            probs = F.softmax(logits, dim=1)

        results = []
        top_k = min(3, self.num_classes)
        top_probs, top_indices = torch.topk(probs, k=top_k, dim=1)

        for i, sentence in enumerate(sentences):
            row_probs = top_probs[i].cpu().numpy()
            row_indices = top_indices[i].cpu().numpy()

            top3 = []
            for prob, idx in zip(row_probs, row_indices):
                top3.append({
                    "label": self.labels.get(int(idx), f"CLASS_{idx}"),
                    "label_id": int(idx),
                    "confidence": round(float(prob), 4)
                })

            best_id = int(row_indices[0])
            results.append({
                "sentence": sentence,
                "label_id": best_id,
                "label_name": self.labels.get(best_id, f"CLASS_{best_id}"),
                "confidence": round(float(row_probs[0]), 4),
                "top3": top3
            })

        return results


if __name__ == "__main__":
    print("=" * 65)
    print("Fluenora AI - Real-Time Inference Demo")
    print("=" * 65)

    try:
        predictor = GrammarErrorPredictor()
        test_samples = [
            "Yesterday I am going to college by bus.",
            "She go to school every day by auto.",
            "I have a uncle who is doctor in Guntur.",
            "I am very good in English speaking.",
            "She speaked very fastly in the interview.",
            "I English very much like to study.",
            "I go to school every day by bus."
        ]

        print(f"\nRunning predictions with model: {predictor.model_path}")
        print("-" * 65)
        for s in test_samples:
            res = predictor.predict(s)
            print(f"Input:      \"{res['sentence']}\"")
            print(f"Predicted:  {res['label_name']} (Confidence: {res['confidence']*100:.2f}%)")
            top_str = ", ".join([f"{t['label']}: {t['confidence']*100:.1f}%" for t in res['top3']])
            print(f"Top 3:      [{top_str}]")
            print("-" * 65)

    except Exception as e:
        print(f"Inference setup note: {e}")
        print("Please run training first before evaluating standalone inference.")
