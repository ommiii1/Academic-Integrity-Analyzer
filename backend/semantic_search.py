import requests
import xml.etree.ElementTree as ET
import urllib.parse
from typing import List, Dict

def search_arxiv(query_text: str, max_results: int = 3) -> List[Dict]:
    """
    Search arXiv for potentially matching papers based on chunk text.
    Uses arXiv's API (atom feed).
    """
    # Clean query: take first 200 characters and remove special chars
    clean_query = "".join(e for e in query_text[:200] if e.isalnum() or e.isspace())
    encoded_query = urllib.parse.quote(clean_query)
    
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []
            
        root = ET.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = []
        for entry in root.findall('atom:entry', namespace):
            title = entry.find('atom:title', namespace).text.strip()
            link = entry.find('atom:id', namespace).text.strip()
            summary = entry.find('atom:summary', namespace).text.strip()
            author_elements = entry.findall('atom:author', namespace)
            authors = [a.find('atom:name', namespace).text for a in author_elements]
            
            entries.append({
                "title": title,
                "url": link,
                "authors": authors,
                "relevance_snippet": summary[:200] + "..."
            })
        return entries
    except Exception as e:
        print(f"arXiv search error: {e}")
        return []

def trace_sources_for_suspicious_chunks(suspicious_sections: List[Dict], chunks: List[Dict]) -> List[Dict]:
    """
    For each highly suspicious chunk, fetch probable source papers from arXiv.
    """
    traced_results = []
    
    # Only search for 'high' or 'medium' severity to save time/API hits
    for s in suspicious_sections:
        if s["severity"] in ["high", "medium"]:
            chunk_text = next((c["full_text"] for c in chunks if c["id"] == s["chunk_id"]), "")
            if len(chunk_text) > 100:
                sources = search_arxiv(chunk_text)
                if sources:
                    traced_results.append({
                        "chunk_id": s["chunk_id"],
                        "sources": sources
                    })
    
    return traced_results
