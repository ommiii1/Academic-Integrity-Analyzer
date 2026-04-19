"""
Stylometric Feature Extraction Module
Extracts writing style fingerprints from text chunks.
"""

import re
import string
import math
import numpy as np
from typing import List, Dict

# ── Common English stopwords (no NLTK dependency needed) ──
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
    "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself',
    'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her',
    'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
    'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
    'with', 'about', 'against', 'between', 'through', 'during', 'before',
    'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
    'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now',
    'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't",
    'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn',
    "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't",
    'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren',
    "weren't", 'won', "won't", 'wouldn', "wouldn't", 'also', 'however',
    'thus', 'therefore', 'moreover', 'furthermore', 'although', 'though',
    'yet', 'still', 'already', 'even', 'well', 'back', 'much', 'every',
}


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 3]


def _get_words(text: str) -> List[str]:
    """Extract words (alphabetic tokens) from text."""
    return re.findall(r"[a-zA-Z']+", text.lower())


def extract_features(text: str) -> Dict[str, float]:
    """
    Extract stylometric features from a text chunk.
    
    Returns dict with:
    - avg_sentence_length: average number of words per sentence
    - avg_word_length: average character length of words
    - type_token_ratio: unique words / total words (vocabulary richness)
    - stopword_frequency: proportion of words that are stopwords
    - punctuation_frequency: punctuation chars / total chars
    - long_word_ratio: proportion of words with 7+ characters
    - comma_frequency: commas per sentence
    - passive_voice_score: approximate passive voice usage
    """
    sentences = _split_sentences(text)
    words = _get_words(text)

    if not words or not sentences:
        return {
            "avg_sentence_length": 0,
            "avg_word_length": 0,
            "type_token_ratio": 0,
            "stopword_frequency": 0,
            "punctuation_frequency": 0,
            "long_word_ratio": 0,
            "comma_frequency": 0,
        }

    total_words = len(words)
    unique_words = len(set(words))

    # ── Average sentence length and variance ──
    words_per_sentence = []
    for sent in sentences:
        sent_words = _get_words(sent)
        if sent_words:
            words_per_sentence.append(len(sent_words))
    
    avg_sentence_length = sum(words_per_sentence) / len(words_per_sentence) if words_per_sentence else 0
    sentence_length_std = float(np.std(words_per_sentence)) if len(words_per_sentence) > 1 else 0

    # ── Average word length ──
    avg_word_length = sum(len(w) for w in words) / total_words

    # ── Type-Token Ratio (vocabulary richness) ──
    type_token_ratio = unique_words / total_words if total_words > 0 else 0

    # ── Hapax Legomena (lexical richness) ──
    word_counts = {}
    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1
    hapax_count = sum(1 for w in word_counts if word_counts[w] == 1)
    hapax_legomena_ratio = hapax_count / total_words if total_words > 0 else 0

    # ── Stopword frequency ──
    stopword_count = sum(1 for w in words if w in STOPWORDS)
    stopword_frequency = stopword_count / total_words

    # ── Conjunction / Logical Connector Frequency ──
    conjunctions = {'and', 'but', 'or', 'so', 'yet', 'for', 'nor', 'however', 'therefore', 'moreover', 'furthermore', 'consequently', 'nonetheless', 'nevertheless'}
    conj_count = sum(1 for w in words if w in conjunctions)
    conjunction_frequency = conj_count / total_words

    # ── Punctuation frequency ──
    total_chars = len(text)
    punct_count = sum(1 for c in text if c in string.punctuation)
    punctuation_frequency = punct_count / total_chars if total_chars > 0 else 0

    # ── Long word ratio (words with 7+ chars) ──
    long_words = sum(1 for w in words if len(w) >= 7)
    long_word_ratio = long_words / total_words

    # ── Comma frequency (commas per sentence) ──
    comma_count = text.count(',')
    comma_frequency = comma_count / len(sentences) if sentences else 0

    return {
        "avg_sentence_length": round(avg_sentence_length, 2),
        "sentence_length_std": round(sentence_length_std, 2),
        "avg_word_length": round(avg_word_length, 2),
        "type_token_ratio": round(type_token_ratio, 4),
        "hapax_legomena_ratio": round(hapax_legomena_ratio, 4),
        "stopword_frequency": round(stopword_frequency, 4),
        "conjunction_frequency": round(conjunction_frequency, 4),
        "punctuation_frequency": round(punctuation_frequency, 4),
        "long_word_ratio": round(long_word_ratio, 4),
        "comma_frequency": round(comma_frequency, 2),
    }


def extract_features_batch(chunks: List[dict]) -> List[dict]:
    """
    Extract features for a batch of chunks.
    Each chunk dict must have 'text' key.
    Returns chunks with added 'features' key.
    """
    for chunk in chunks:
        chunk["features"] = extract_features(chunk["text"])
    return chunks
