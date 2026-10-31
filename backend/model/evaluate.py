import os
import sys
import json
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
from torch.utils.data import DataLoader

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
from dataset import GrammarDataset, get_data_splits, LABELS


def plot_confusion_matrix(y_true, y_pred, class_names, save_path, title):
    """
    Plots and saves a high-resolution confusion matrix heatmap using seaborn.
    """
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        cbar=True,
    )
    plt.title(title, fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Predicted Category", fontsize=12, labelpad=8)
    plt.ylabel("Actual Category", fontsize=12, labelpad=8)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[OK] Confusion matrix saved: {save_path}")


def plot_training_curves(history_path, save_path, model_name):
    """
    Plots training and validation loss and accuracy curves over epochs.
    """
    if not os.path.exists(history_path):
        print(f"[WARN] History file not found at {history_path}. Skipping plot.")
        return

    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)

    epochs = [h["epoch"] for h in history]
    train_loss = [h["train_loss"] for h in history]
    val_loss = [h["val_loss"] for h in history]
    train_acc = [h["train_acc"] for h in history]
    val_acc = [h["val_acc"] for h in history]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Loss Plot
    ax1.plot(epochs, train_loss, label="Train Loss", color="#1f77b4", linewidth=2)
    ax1.plot(epochs, val_loss, label="Val Loss", color="#ff7f0e", linewidth=2, linestyle="--")
    ax1.set_title(f"{model_name} - Loss vs. Epochs", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Epoch", fontsize=11)
    ax1.set_ylabel("Cross Entropy Loss", fontsize=11)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(fontsize=10)

    # Accuracy Plot
    ax2.plot(epochs, [a * 100 for a in train_acc], label="Train Accuracy", color="#2ca02c", linewidth=2)
    ax2.plot(epochs, [a * 100 for a in val_acc], label="Val Accuracy", color="#d62728", linewidth=2, linestyle="--")
    ax2.set_title(f"{model_name} - Accuracy vs. Epochs", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Epoch", fontsize=11)
    ax2.set_ylabel("Accuracy (%)", fontsize=11)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(fontsize=10)

    plt.suptitle(f"Fluenora AI - {model_name} Training History", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Training curves saved: {save_path}")


def evaluate_all():
    print("=" * 70)
    print("Fluenora AI - Comprehensive Evaluation & Model Comparison")
    print("=" * 70)

    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    data_path = os.path.join(project_root, "data", "grammar_dataset.csv")
    saved_dir = os.path.join(project_root, "saved")

    vocab_path = os.path.join(saved_dir, "vocab.json")
    labels_path = os.path.join(saved_dir, "labels.json")
    lstm_model_path = os.path.join(saved_dir, "lstm_model.pth")
    mlp_model_path = os.path.join(saved_dir, "mlp_model.pth")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Check required files
    for p in [vocab_path, labels_path, lstm_model_path, mlp_model_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Required artifact not found: {p}. Train models first!")

    preprocessor = TextPreprocessor.load(vocab_path)
    with open(labels_path, "r", encoding="utf-8") as f:
        labels_map = json.load(f)
    class_names = [labels_map[str(i)] for i in range(len(labels_map))]

    # Load Test Split
    _, _, test_df = get_data_splits(data_path, random_state=42)
    test_dataset = GrammarDataset(test_df["sentence"].tolist(), test_df["label"].tolist(), preprocessor)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    y_true = test_df["label"].tolist()

    # Instantiate Models
    lstm_model = LSTMClassifier(
        vocab_size=preprocessor.vocab_size,
        embed_dim=64,
        hidden_dim=128,
        num_layers=2,
        num_classes=len(class_names),
        dropout=0.3,
    ).to(device)
    lstm_model.load_state_dict(torch.load(lstm_model_path, map_location=device))
    lstm_model.eval()

    mlp_model = MLPClassifier(
        vocab_size=preprocessor.vocab_size,
        embed_dim=64,
        max_len=preprocessor.max_len,
        hidden_dim=256,
        num_classes=len(class_names),
        dropout=0.3,
    ).to(device)
    mlp_model.load_state_dict(torch.load(mlp_model_path, map_location=device))
    mlp_model.eval()

    # Predictions Helper
    def run_inference(model):
        preds = []
        with torch.no_grad():
            for inputs, _ in test_loader:
                inputs = inputs.to(device)
                outputs = model(inputs)
                _, pred = torch.max(outputs, 1)
                preds.extend(pred.cpu().numpy().tolist())
        return preds

    print("\nEvaluating BiLSTM Classifier on Test Set...")
    lstm_preds = run_inference(lstm_model)

    print("Evaluating Baseline MLP Classifier on Test Set...")
    mlp_preds = run_inference(mlp_model)

    # Calculate Metrics
    def compute_metrics(y_t, y_p, model_name, params_count):
        acc = accuracy_score(y_t, y_p)
        prec_macro = precision_score(y_t, y_p, average="macro", zero_division=0)
        rec_macro = recall_score(y_t, y_p, average="macro", zero_division=0)
        f1_macro = f1_score(y_t, y_p, average="macro", zero_division=0)

        prec_weighted = precision_score(y_t, y_p, average="weighted", zero_division=0)
        rec_weighted = recall_score(y_t, y_p, average="weighted", zero_division=0)
        f1_weighted = f1_score(y_t, y_p, average="weighted", zero_division=0)

        return {
            "model_name": model_name,
            "parameter_count": params_count,
            "accuracy": round(float(acc), 4),
            "precision_macro": round(float(prec_macro), 4),
            "recall_macro": round(float(rec_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "precision_weighted": round(float(prec_weighted), 4),
            "recall_weighted": round(float(rec_weighted), 4),
            "f1_weighted": round(float(f1_weighted), 4),
        }

    lstm_param_count = sum(p.numel() for p in lstm_model.parameters() if p.requires_grad)
    mlp_param_count = sum(p.numel() for p in mlp_model.parameters() if p.requires_grad)

    lstm_metrics = compute_metrics(y_true, lstm_preds, "Bi-LSTM Classifier", lstm_param_count)
    mlp_metrics = compute_metrics(y_true, mlp_preds, "MLP Baseline", mlp_param_count)

    # Print Classification Reports
    print("\n" + "=" * 70)
    print("CLASSIFICATION REPORT: Bi-LSTM Classifier")
    print("=" * 70)
    print(classification_report(y_true, lstm_preds, target_names=class_names, digits=4))

    print("\n" + "=" * 70)
    print("CLASSIFICATION REPORT: MLP Baseline Classifier")
    print("=" * 70)
    print(classification_report(y_true, mlp_preds, target_names=class_names, digits=4))

    # Confusion Matrices
    cm_lstm_path = os.path.join(saved_dir, "confusion_matrix_lstm.png")
    cm_mlp_path = os.path.join(saved_dir, "confusion_matrix_mlp.png")
    plot_confusion_matrix(y_true, lstm_preds, class_names, cm_lstm_path, "Confusion Matrix - BiLSTM Classifier")
    plot_confusion_matrix(y_true, mlp_preds, class_names, cm_mlp_path, "Confusion Matrix - Baseline MLP")

    # Training Curves
    curves_lstm_path = os.path.join(saved_dir, "training_curves_lstm.png")
    curves_mlp_path = os.path.join(saved_dir, "training_curves_mlp.png")
    plot_training_curves(os.path.join(saved_dir, "lstm_training_history.json"), curves_lstm_path, "Bi-LSTM")
    plot_training_curves(os.path.join(saved_dir, "mlp_training_history.json"), curves_mlp_path, "MLP Baseline")

    # Model Comparison Table
    comparison = {
        "Bi-LSTM Classifier": lstm_metrics,
        "MLP Baseline": mlp_metrics,
    }
    comparison_json_path = os.path.join(saved_dir, "model_comparison.json")
    with open(comparison_json_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)
    print(f"\n[OK] Model comparison saved to: {comparison_json_path}")

    # Display Pretty Table
    df_comp = pd.DataFrame([lstm_metrics, mlp_metrics])
    cols_display = [
        "model_name", "parameter_count", "accuracy",
        "precision_macro", "recall_macro", "f1_macro",
        "precision_weighted", "recall_weighted", "f1_weighted"
    ]
    print("\n" + "=" * 70)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 70)
    print(df_comp[cols_display].to_string(index=False))
    print("=" * 70)


if __name__ == "__main__":
    evaluate_all()
