import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, accuracy_score

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
from lstm_model import LSTMClassifier
from dataset import GrammarDataset, get_data_splits, LABELS


def train_lstm_model():
    print("=" * 65)
    print("Fluenora AI - Training Bidirectional LSTM Grammar Classifier")
    print("=" * 65)

    # Directories
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    data_path = os.path.join(project_root, "data", "grammar_dataset.csv")
    saved_dir = os.path.join(project_root, "saved")
    os.makedirs(saved_dir, exist_ok=True)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load splits
    print(f"Loading data splits from {data_path}...")
    train_df, val_df, test_df = get_data_splits(data_path, random_state=42)
    print(f"Splits: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

    # Initialize Preprocessor and build vocab on Train set only
    preprocessor = TextPreprocessor(max_vocab=5000, max_len=30)
    preprocessor.build_vocab(train_df["sentence"].tolist())
    print(f"Vocabulary size built on Train set: {preprocessor.vocab_size} tokens")

    # Save Preprocessor Vocab & Label mappings
    vocab_save_path = os.path.join(saved_dir, "vocab.json")
    labels_save_path = os.path.join(saved_dir, "labels.json")
    preprocessor.save(vocab_save_path)
    with open(labels_save_path, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in LABELS.items()}, f, indent=2)
    print(f"[OK] Saved preprocessor vocabulary to: {vocab_save_path}")
    print(f"[OK] Saved label mapping to: {labels_save_path}")

    # Create PyTorch Datasets and DataLoaders
    train_dataset = GrammarDataset(train_df["sentence"].tolist(), train_df["label"].tolist(), preprocessor)
    val_dataset = GrammarDataset(val_df["sentence"].tolist(), val_df["label"].tolist(), preprocessor)
    test_dataset = GrammarDataset(test_df["sentence"].tolist(), test_df["label"].tolist(), preprocessor)

    batch_size = 32
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # Compute Class Weights for balanced CrossEntropyLoss
    y_train = train_df["label"].values
    unique_classes = np.unique(y_train)
    weights = compute_class_weight(class_weight="balanced", classes=unique_classes, y=y_train)
    weights_tensor = torch.tensor(weights, dtype=torch.float32).to(device)

    # Initialize LSTM Model
    model = LSTMClassifier(
        vocab_size=preprocessor.vocab_size,
        embed_dim=64,
        hidden_dim=128,
        num_layers=2,
        num_classes=len(LABELS),
        dropout=0.3
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Initialized LSTMClassifier with {total_params:,} trainable parameters.")

    criterion = nn.CrossEntropyLoss(weight=weights_tensor)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # Training Loop
    epochs = 50
    best_val_acc = 0.0
    best_model_path = os.path.join(saved_dir, "lstm_model.pth")
    history = []

    print("\nStarting training for 50 epochs...")
    print("-" * 65)

    for epoch in range(1, epochs + 1):
        # Training Phase
        model.train()
        running_train_loss = 0.0
        train_correct = 0
        train_total = 0

        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_train_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            train_correct += (predicted == targets).sum().item()
            train_total += targets.size(0)

        epoch_train_loss = running_train_loss / train_total
        epoch_train_acc = train_correct / train_total

        # Validation Phase
        model.eval()
        running_val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)

                running_val_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs, 1)
                val_correct += (predicted == targets).sum().item()
                val_total += targets.size(0)

        epoch_val_loss = running_val_loss / val_total
        epoch_val_acc = val_correct / val_total

        is_best = epoch_val_acc > best_val_acc
        if is_best:
            best_val_acc = epoch_val_acc
            torch.save(model.state_dict(), best_model_path)

        epoch_info = {
            "epoch": epoch,
            "train_loss": round(float(epoch_train_loss), 4),
            "val_loss": round(float(epoch_val_loss), 4),
            "train_acc": round(float(epoch_train_acc), 4),
            "val_acc": round(float(epoch_val_acc), 4)
        }
        history.append(epoch_info)

        star = " * (Best)" if is_best else ""
        print(f"Epoch [{epoch:02d}/{epochs:02d}] | Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc*100:6.2f}% | Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc*100:6.2f}%{star}")

    print("-" * 65)
    print(f"Training finished. Best Validation Accuracy: {best_val_acc*100:.2f}%")
    print(f"Best model saved to: {best_model_path}")

    # Save History
    history_path = os.path.join(saved_dir, "lstm_training_history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    print(f"Saved training history to: {history_path}")

    # Final Test Set Evaluation using the Best Model
    print("\n" + "=" * 65)
    print("Evaluating Best LSTM Model on Unseen Test Set...")
    print("=" * 65)

    model.load_state_dict(torch.load(best_model_path, map_location=device))
    model.eval()

    all_preds = []
    all_targets = []
    running_test_loss = 0.0
    test_total = 0

    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            running_test_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)

            all_preds.extend(predicted.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            test_total += targets.size(0)

    test_loss = running_test_loss / test_total
    test_acc = accuracy_score(all_targets, all_preds)
    print(f"Test Loss: {test_loss:.4f} | Test Accuracy: {test_acc*100:.2f}%\n")

    target_names = [LABELS[i] for i in range(len(LABELS))]
    report = classification_report(all_targets, all_preds, target_names=target_names, digits=4)
    print("Classification Report (LSTM):")
    print(report)

    return model, history, test_acc


if __name__ == "__main__":
    train_lstm_model()
