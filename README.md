# 🖋️ Academic Integrity Analyzer: Stylometric Stitch Detector

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The **Academic Integrity Analyzer** is a sophisticated forensic tool designed to detect "stitched" authorship in research papers. Unlike traditional plagiarism checkers that rely solely on database matching, this tool analyzes **stylometric fingerprints**, **citation consistency**, and **structural anomalies** to identify text that has been cobbled together from multiple sources (invisible plagiarism).

---

## 🚀 Key Features

- **🔍 Stylometric Fingerprinting**: Extracts 10+ linguistic features (sentence length variety, vocabulary richness, punctuation density, etc.) to create a unique "style profile" for the author.
- **🧩 Stitch Detection**: Uses a sliding-window chunking algorithm and similarity matrices to identify sudden shifts in writing style within a single document.
- **👥 Author Estimation**: Implements KMeans clustering and Silhouette analysis to estimate if a document was likely written by one or multiple distinct authors.
- **📚 Citation Forensics**: Cross-references in-text citations with the bibliography to detect temporal anomalies and "ghost" references.
- **🛰️ Semantic Source Tracing**: Performs automated semantic searches on suspicious sections via the arXiv API to identify potential origin sources.
- **📄 Forensic Reporting**: Generates comprehensive, professional reports in PDF or TXT format detailing the logic behind every flag.
- **🤖 AI Heuristics**: Detects "unnaturally consistent" writing patterns typical of LLM-generated text.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, PyMuPDF (Text Extraction), Scikit-learn (Clustering), NumPy/SciPy (Statistics).
- **Frontend**: React (via Babel standalone), Chart.js (Visualizations), CSS3 (Modern Glassmorphic UI).
- **API**: Asynchronous processing for document analysis.

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.11 or higher installed on your system.

### 1. Set Up Virtual Environment
**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 How to Run

### 1. Start the Backend Server
Run the FastAPI server using Uvicorn. The server doubles as a static file host for the frontend.
```bash
uvicorn main:app --reload
```

### 2. Access the Application
Open your web browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### 3. Analyze a Document
1. Upload a research paper in **PDF format**.
2. Click **"Analyze Document"**.
3. View the **Integrity Score**, **Similarity Heatmaps**, and **Forensic Explanations**.
4. Download the **Forensic Report** for detailed evidence.

---

## 📂 Project Structure

```text
stitch-detector/
├── backend/                # Core logic
│   ├── analyzer.py         # Clustering and integrity scoring
│   ├── chunker.py          # Document segmentation
│   ├── stylometry.py       # Feature extraction (Linguistic fingerprinting)
│   ├── citation_analysis.py# Citation consistency checks
│   ├── extractor.py        # PDF text purification
│   ├── reporter.py         # PDF/TXT report generation
│   └── semantic_search.py  # arXiv API integration
├── frontend/               # UI components
│   ├── index.html          # Entry point
│   ├── app.jsx             # React dashboard logic
│   └── style.css           # Modern UI styling
├── main.py                 # FastAPI Entry point & API routes
├── requirements.txt        # Python dependencies
└── README.md               # You are here
```

---

## 🧠 How It Works (The Pipeline)

1. **Purification**: The PDF is stripped of non-academic prose (headers, footers, tables) to focus on the author's actual voice.
2. **Segmentation**: The text is split into overlapping chunks to ensure "stitch points" (where two sources meet) are captured.
3. **Stylometry**: Each chunk is analyzed for metrics like *Hapax Legomena* (unique words) and *Syntactic Variety*.
4. **Vectorization**: Features are standardized and converted into vectors for mathematical comparison.
5. **Clustering**: The system attempts to partition chunks into $K$ authors. If a 2-author model explains the data significantly better than a 1-author model, a "Stitch Warning" is issued.
6. **Cross-Validation**: Citation patterns and external semantic searches are used to confirm stylistic suspicions.

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.

---

## 📧 Contact
Project Link: [https://github.com/your-username/stitch-detector](https://github.com/your-username/stitch-detector)

*Made with ❤️ for Academic Integrity.*
