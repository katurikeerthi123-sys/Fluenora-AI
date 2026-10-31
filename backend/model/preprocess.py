import json
import re
from collections import Counter
from typing import List, Iterable, Union


class TextPreprocessor:
    """
    NLP Text Preprocessor for Fluenora AI grammar error detection.
    Handles tokenization, vocabulary construction, token-to-index encoding,
    padding/truncation, and serialization.
    """
    PAD_TOKEN = "<PAD>"
    UNK_TOKEN = "<UNK>"
    PAD_IDX = 0
    UNK_IDX = 1

    def __init__(self, max_vocab: int = 5000, max_len: int = 30):
        self.max_vocab = max_vocab
        self.max_len = max_len
        self.word2idx = {self.PAD_TOKEN: self.PAD_IDX, self.UNK_TOKEN: self.UNK_IDX}
        self.idx2word = {self.PAD_IDX: self.PAD_TOKEN, self.UNK_IDX: self.UNK_TOKEN}

    def tokenize(self, sentence: str) -> List[str]:
        """
        Tokenize an input sentence:
        - Convert to lowercase
        - Strip punctuation (replace non-alphanumeric with whitespace)
        - Split on whitespace
        """
        if not isinstance(sentence, str):
            sentence = str(sentence) if sentence is not None else ""
        cleaned = re.sub(r"[^\w\s]", " ", sentence.lower())
        tokens = [token.strip() for token in cleaned.split() if token.strip()]
        return tokens

    def build_vocab(self, sentences: Iterable[str]) -> None:
        """
        Fit vocabulary on an iterable of text sentences.
        Builds word2idx and idx2word reserving index 0 for <PAD> and index 1 for <UNK>.
        """
        counter = Counter()
        for sentence in sentences:
            tokens = self.tokenize(sentence)
            counter.update(tokens)

        # Reserve 2 slots for PAD and UNK
        num_allowed_words = max(0, self.max_vocab - 2)
        most_common = counter.most_common(num_allowed_words)

        self.word2idx = {self.PAD_TOKEN: self.PAD_IDX, self.UNK_TOKEN: self.UNK_IDX}
        self.idx2word = {self.PAD_IDX: self.PAD_TOKEN, self.UNK_IDX: self.UNK_TOKEN}

        current_idx = 2
        for word, _ in most_common:
            self.word2idx[word] = current_idx
            self.idx2word[current_idx] = word
            current_idx += 1

    def encode(self, sentence: str) -> List[int]:
        """
        Encodes a sentence into a fixed-length list of token IDs.
        Applies padding (0) or truncation to match `max_len`.
        """
        tokens = self.tokenize(sentence)
        ids = [self.word2idx.get(token, self.UNK_IDX) for token in tokens]

        if len(ids) < self.max_len:
            ids = ids + [self.PAD_IDX] * (self.max_len - len(ids))
        else:
            ids = ids[:self.max_len]

        return ids

    def decode(self, ids: List[int]) -> List[str]:
        """
        Converts token IDs back to tokens (omitting PAD tokens).
        """
        return [self.idx2word.get(i, self.UNK_TOKEN) for i in ids if i != self.PAD_IDX]

    @property
    def vocab_size(self) -> int:
        return len(self.word2idx)

    def save(self, path: str) -> None:
        """
        Save vocabulary and preprocessor configuration to a JSON file.
        """
        data = {
            "max_vocab": self.max_vocab,
            "max_len": self.max_len,
            "word2idx": self.word2idx,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "TextPreprocessor":
        """
        Load preprocessor state from a saved JSON file.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        preprocessor = cls(max_vocab=data["max_vocab"], max_len=data["max_len"])
        preprocessor.word2idx = data["word2idx"]
        preprocessor.idx2word = {int(v) if isinstance(v, int) else int(v): k for k, v in preprocessor.word2idx.items()}
        # Ensure inverted map has integer keys
        preprocessor.idx2word = {v: k for k, v in preprocessor.word2idx.items()}
        return preprocessor
