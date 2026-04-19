"""
PDF Text Extraction Module
Extracts academic prose from Abstract to References, stripping
tables, bullet points, citations, equations, and metadata.
"""

import re
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using PyMuPDF, excluding tables."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []

    for page in doc:
        # Find tables and their bounding boxes
        tables = page.find_tables().tables
        table_bboxes = [fitz.Rect(t.bbox) for t in tables]

        # Extract by blocks to preserve paragraphs, sorted by vertical placement
        blocks = page.get_text("blocks", sort=True)
        for b in blocks:
            # block type 0 is text
            if b[6] != 0:
                continue

            block_rect = fitz.Rect(b[:4])
            is_table = False

            # Check if block significantly overlaps with any table
            for tbox in table_bboxes:
                intersect = block_rect.intersect(tbox)
                if not intersect.is_empty:
                    if intersect.get_area() > block_rect.get_area() * 0.4:
                        is_table = True
                        break

            if not is_table:
                full_text.append(b[4])

    doc.close()
    return "\n".join(full_text)


def clean_structure(raw_text: str) -> str:
    """
    Step 1: Structural Cleaning
    1. Start from Abstract
    2. Stop at References
    3. Remove tables, captions, noise
    4. Keep in-text citations for forensics
    """
    text = raw_text

    # ── 1. Start from Abstract ──
    abstract_match = re.search(r'(?im)^\s*abstract\s*$', text)
    if abstract_match:
        text = text[abstract_match.start():]
    else:
        abstract_match = re.search(r'(?i)\babstract\b', text)
        if abstract_match:
            text = text[abstract_match.start():]

    # ── 2. Strip References from the prose (but we'll keep a copy of the whole doc for citation extraction) ──
    for pat in [
        r'(?im)^\s*references\s*$',
        r'(?im)^\s*bibliography\s*$',
        r'(?im)^\s*works\s+cited\s*$',
    ]:
        m = re.search(pat, text)
        if m:
            text = text[:m.start()]

    # ── 3. Remove table-like content ──
    text = re.sub(r'^.*(?:\t|  {2,}).*(?:\t|  {2,}).*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*(?:[\d.,%±]+\s+){2,}[\d.,%±]+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'(?im)^(?:figure|fig\.|table)\s*\d+[.:]?\s*[^\n]*$', '', text, flags=re.MULTILINE)

    # ── 4. Remove bullet points and numbered lists ──
    text = re.sub(r'^\s*[•●○▪▸▹➤➢–—-]\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+[.)]\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[a-z][.)]\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[ivxIVX]+[.)]\s+.*$', '', text, flags=re.MULTILINE)

    # ── 5. Normalize whitespace slightly ──
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def purify_text(text: str) -> str:
    """
    Step 2: Linguistic Purification
    Removes in-text citations and math for stylometric analysis.
    """
    # ── 1. Remove in-text citations ──
    text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
    text = re.sub(r'\[\d+\s*-\s*\d+\]', '', text)
    text = re.sub(
        r'\((?:[A-Z][a-z]+(?:\s+(?:et\s+al\.?|and|&)\s+[A-Z][a-z]+)?'
        r',?\s*\d{4}(?:;\s*[A-Z][a-z]+(?:\s+(?:et\s+al\.?|and|&)'
        r'\s+[A-Z][a-z]+)?,?\s*\d{4})*)\)', '', text
    )

    # ── 2. Remove equations / math ──
    text = re.sub(r'\$[^$]+\$', '', text)
    text = re.sub(r'\\\[.*?\\\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', text, flags=re.DOTALL)
    text = re.sub(r'[∑∏∫∂∇√∞≈≠≤≥±×÷αβγδεζηθικλμνξπρσςτυφχψω]+', ' ', text)

    # ── 3. Remove standalone page numbers, URLs, headers ──
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'https?://\S+', '', text)

    return text.strip()


def pdf_to_clean_text(pdf_bytes: bytes) -> dict:
    """
    Full pipeline: PDF bytes → dict with raw, structural, and linguistic text.
    """
    raw = extract_text_from_pdf(pdf_bytes)
    structural = clean_structure(raw)
    return {
        "raw": raw,
        "structural": structural
    }
