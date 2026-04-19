"""
Text Chunking Module
Splits cleaned text into semantically meaningful chunks of 150–300 words.
"""

import re
from typing import List


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using regex-based rules."""
    # Split on sentence-ending punctuation followed by space + capital letter or end
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, window_size: int = 200, overlap: int = 100) -> List[dict]:
    """
    Split text into overlapping chunks using a sliding window.
    This increases detection accuracy by ensuring stitch points are captured
    within at least one full chunk.
    
    Returns list of dicts with 'id', 'text', 'word_count'.
    """
    words = text.split()
    total_words = len(words)
    
    if total_words <= window_size:
        return [{"id": 0, "text": text, "word_count": total_words}]
    
    chunks = []
    start = 0
    while start < total_words:
        end = min(start + window_size, total_words)
        chunk_words = words[start:end]
        
        # If the last chunk is too small, just merge it with the previous one
        if len(chunk_words) < window_size // 2 and chunks:
            prev_words = chunks[-1]["text"].split()
            combined = prev_words + chunk_words[overlap:] # avoid duplicate overlap
            chunks[-1]["text"] = " ".join(combined)
            chunks[-1]["word_count"] = len(combined)
            break
            
        chunks.append({
            "id": len(chunks),
            "text": " ".join(chunk_words),
            "word_count": len(chunk_words)
        })
        
        if end == total_words:
            break
            
        start += (window_size - overlap)
        
    return chunks
