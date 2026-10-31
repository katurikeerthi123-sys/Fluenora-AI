import torch
import torch.nn as nn


class LSTMClassifier(nn.Module):
    """
    Bidirectional LSTM Classifier for Grammar Error Detection.
    Embeds input tokens, processes through a 2-layer Bidirectional LSTM,
    concatenates final forward and backward hidden states, and classifies
    into one of 7 grammar error categories.
    """
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 2,
        num_classes: int = 7,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_classes = num_classes

        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)  # * 2 for bidirectional

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len)
        emb = self.dropout(self.embedding(x))  # (batch_size, seq_len, embed_dim)
        out, (hn, cn) = self.lstm(emb)
        # hn shape: (num_layers * 2, batch_size, hidden_dim)
        # Concatenate the top layer forward (hn[-2]) and backward (hn[-1]) hidden states
        hn_last = torch.cat([hn[-2], hn[-1]], dim=1)  # (batch_size, hidden_dim * 2)
        hn_last = self.dropout(hn_last)
        logits = self.fc(hn_last)  # (batch_size, num_classes)
        return logits


class MLPClassifier(nn.Module):
    """
    Baseline Multi-Layer Perceptron (MLP) Classifier.
    Embedding → Flatten → Linear(256) → ReLU → Dropout → Linear(128) → ReLU → Dropout → Linear(7)
    """
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 64,
        max_len: int = 30,
        hidden_dim: int = 256,
        num_classes: int = 7,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_len = max_len
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes

        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.fc1 = nn.Linear(embed_dim * max_len, hidden_dim)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)

        self.fc2 = nn.Linear(hidden_dim, 128)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)

        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, max_len)
        emb = self.embedding(x)  # (batch_size, max_len, embed_dim)
        flat = emb.view(emb.size(0), -1)  # (batch_size, max_len * embed_dim)
        h1 = self.dropout1(self.relu1(self.fc1(flat)))
        h2 = self.dropout2(self.relu2(self.fc2(h1)))
        logits = self.fc3(h2)  # (batch_size, num_classes)
        return logits
