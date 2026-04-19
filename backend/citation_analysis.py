import re
import numpy as np

def extract_reference_metadata(full_text):
    """
    Finds the References section and extracts years linked to citation numbers.
    Returns a dict: { '1': 2021, '2': 2018, ... }
    """
    ref_metadata = {}
    # Look for the References section
    ref_split = re.split(r'(?i)\n(?:References|Bibliography|REFERENCES)\s*\n', full_text)
    if len(ref_split) < 2:
        return {}

    ref_section = ref_split[-1]
    
    # Pattern to find [1] Author, Title, 2022.
    # It looks for a number in brackets/start of line, then a 4-digit year.
    ref_entries = re.findall(r'(?:\[(\d+)\]|(\d+)\.)[\s\w,.-]+((?:19|20)\d{2})', ref_section)
    
    for entry in ref_entries:
        # entry is (num1, num2, year) -> num1 or num2 will be the citation index
        ref_id = entry[0] or entry[1]
        year = int(entry[2])
        ref_metadata[ref_id] = year
        
    return ref_metadata

def analyze_citations_in_chunks(chunks, ref_metadata):
    """
    Analyzes each chunk to see which references it uses and calculates 
    the 'Temporal Signature' (Average Year) of that chunk.
    """
    temporal_report = []
    global_years = list(ref_metadata.values())
    avg_global_year = np.mean(global_years) if global_years else 0

    for i, chunk in enumerate(chunks):
        # Find citations like [1] or [1, 2, 5]
        found_cites = re.findall(r'\[([\d,\s]+)\]', chunk)
        flattened_cites = []
        for c in found_cites:
            flattened_cites.extend([x.strip() for x in c.split(',')])

        # Get years for the citations found in this chunk
        chunk_years = [ref_metadata[c] for c in flattened_cites if c in ref_metadata]
        
        chunk_avg_year = np.mean(chunk_years) if chunk_years else 0
        # Drift is the difference from the document's average citation age
        drift = abs(chunk_avg_year - avg_global_year) if chunk_avg_year > 0 else 0
        
        temporal_report.append({
            "chunk_index": i,
            "citations_found": flattened_cites,
            "avg_year": round(float(chunk_avg_year), 1),
            "is_temporally_inconsistent": bool(drift > 5) # Flagged if > 5 year gap
        })
        
    return temporal_report