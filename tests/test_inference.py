import os
import sys
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.model.inference import GrammarErrorPredictor


class TestGrammarInference:
    @classmethod
    def setup_class(cls):
        """Initialize predictor once for test suite."""
        cls.lstm_path = os.path.join(PROJECT_ROOT, "saved", "lstm_model.pth")
        cls.vocab_path = os.path.join(PROJECT_ROOT, "saved", "vocab.json")
        cls.labels_path = os.path.join(PROJECT_ROOT, "saved", "labels.json")

        assert os.path.exists(cls.lstm_path), f"Saved LSTM weights not found at {cls.lstm_path}"
        assert os.path.exists(cls.vocab_path), f"Saved vocab not found at {cls.vocab_path}"
        assert os.path.exists(cls.labels_path), f"Saved labels not found at {cls.labels_path}"

        cls.predictor = GrammarErrorPredictor(
            model_path=cls.lstm_path,
            vocab_path=cls.vocab_path,
            labels_path=cls.labels_path,
            model_type="lstm"
        )

    def test_predictor_initialization(self):
        """Verify model weights and vocabulary loaded properly."""
        assert self.predictor.model is not None
        assert self.predictor.preprocessor is not None
        assert len(self.predictor.labels) == 7
        assert self.predictor.num_classes == 7

    def test_predict_single_sentence_keys(self):
        """Verify returned structure matches required schema."""
        test_sent = "Yesterday I am going to college."
        res = self.predictor.predict(test_sent)

        assert isinstance(res, dict)
        assert "sentence" in res
        assert "label_id" in res
        assert "label_name" in res
        assert "confidence" in res
        assert "top3" in res

        assert res["sentence"] == test_sent
        assert isinstance(res["label_id"], int)
        assert 0 <= res["label_id"] <= 6
        assert isinstance(res["label_name"], str)
        assert 0.0 <= res["confidence"] <= 1.0

    def test_predict_top3_distribution(self):
        """Verify top-3 predictions are sorted, have valid probabilities, and sum <= 1.0."""
        test_sent = "She go to school every day."
        res = self.predictor.predict(test_sent)

        top3 = res["top3"]
        assert len(top3) == 3

        # Probabilities should be in descending order
        confidences = [t["confidence"] for t in top3]
        assert confidences == sorted(confidences, reverse=True)

        for item in top3:
            assert "label" in item
            assert "label_id" in item
            assert "confidence" in item
            assert 0.0 <= item["confidence"] <= 1.0

        assert sum(confidences) <= 1.05

    def test_predict_empty_or_whitespace(self):
        """Verify empty input handling in predictor."""
        res_empty = self.predictor.predict("")
        assert res_empty["label_id"] == 0
        assert res_empty["label_name"] == "CORRECT"
        assert res_empty["confidence"] == 1.0

        res_spaces = self.predictor.predict("   ")
        assert res_spaces["label_id"] == 0

    def test_mlp_baseline_loading_and_inference(self):
        """Verify MLP baseline model can also be initialized and run."""
        mlp_path = os.path.join(PROJECT_ROOT, "saved", "mlp_model.pth")
        if os.path.exists(mlp_path):
            mlp_predictor = GrammarErrorPredictor(
                model_path=mlp_path,
                vocab_path=self.vocab_path,
                labels_path=self.labels_path,
                model_type="mlp"
            )
            assert mlp_predictor.model is not None
            res = mlp_predictor.predict("I have a uncle who is doctor.")
            assert "label_name" in res
            assert len(res["top3"]) == 3
