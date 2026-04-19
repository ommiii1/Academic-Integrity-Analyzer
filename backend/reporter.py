import io
import datetime

def generate_text_report(data):
    """
    Generates a professional forensic text report from analysis data.
    """
    report = []
    report.append("=" * 60)
    report.append("          ACADEMIC INTEGRITY FORENSIC REPORT          ")
    report.append("=" * 60)
    report.append(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Document:     {data.get('filename', 'Unknown')}")
    report.append("-" * 60)
    
    # Summary
    report.append("\n[ EXECUTIVE SUMMARY ]")
    report.append(f"Integrity Score:     {data.get('integrity_score', 0):.1f}%")
    report.append(f"Estimated Authors:   {data.get('author_estimation', {}).get('estimated_authors', 1)}")
    report.append(f"Total Words:         {data.get('total_words', 0)}")
    report.append(f"AI Generation Prob:  {data.get('ai_detection', {}).get('ai_score', 0)}%")
    
    verdict = "HIGH INTEGRITY"
    score = data.get('integrity_score', 0)
    if score < 50:
        verdict = "CRITICAL ALERT - LIKELY STITCHED"
    elif score < 75:
        verdict = "MODERATE RISK - STYLE DEVIATIONS"
    report.append(f"Verdict:             {verdict}")
    
    # Stylometric Anomalies
    report.append("\n[ STYLOMETRIC ANOMALIES ]")
    suspicious = data.get('suspicious_sections', [])
    if not suspicious:
        report.append("No significant stylometric shifts detected.")
    else:
        for s in suspicious:
            report.append(f"🚩 Chunk {s['chunk_id'] + 1} ({s['severity'].upper()}):")
            for reason in s.get('reasons', []):
                report.append(f"   - {reason}")
            
            # Add semantic sources if they exist for this chunk
            sources = [src for src in data.get('semantic_sources', []) if src['chunk_id'] == s['chunk_id']]
            if sources:
                report.append("   - Potential Sources Found:")
                for src in sources[0].get('sources', []):
                    report.append(f"     * {src['title']} ({src['url']})")

    # Citation Analysis
    report.append("\n[ CITATION FORENSICS ]")
    citations = data.get('citation_analysis', [])
    anomalies = [c for c in citations if c.get('is_temporally_inconsistent')]
    if not anomalies:
        report.append("Citation patterns appear chronologically consistent.")
    else:
        for c in anomalies:
            report.append(f"⚠️ Chunk {c['chunk_index'] + 1}: Temporal Drift Detected")
            report.append(f"   - Average citation year: {c['avg_year']}")
            report.append(f"   - Deviation from document baseline: {c['deviation']:.1f} years")

    # AI Detection
    report.append("\n[ AI DETECTION HEURISTICS ]")
    ai = data.get('ai_detection', {})
    report.append(f"AI Confidence Score: {ai.get('ai_score', 0)}%")
    for indicator in ai.get('indicators', []):
        report.append(f" - {indicator}")

    report.append("\n" + "=" * 60)
    report.append("          END OF FORENSIC REPORT          ")
    report.append("=" * 60)
    
    return "\n".join(report)

def generate_pdf_report(data):
    """
    Generates a PDF forensic report by wrapping the text report.
    """
    import fitz
    text = generate_text_report(data)
    doc = fitz.open()
    page = doc.new_page()
    
    # Very basic wrapping and pagination
    lines = text.split('\n')
    y = 50
    margin = 50
    page_height = 800
    line_height = 12
    
    for line in lines:
        if y > page_height - margin:
            page = doc.new_page()
            y = margin
            
        # If line is too long, it might still overflow horizontally, 
        # but for a text report courier usually fits 80 chars.
        page.insert_text((margin, y), line, fontsize=9, fontname="courier")
        y += line_height
        
    return doc.tobytes()
