const { useState, useEffect, useRef, useMemo } = React;

// ═══════ Helper Functions ═══════
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function heatmapColor(val) {
  const interpolate = (c1, c2, t, alpha) => {
    const r = Math.round(c1[0] + (c2[0] - c1[0]) * t);
    const g = Math.round(c1[1] + (c2[1] - c1[1]) * t);
    const b = Math.round(c1[2] + (c2[2] - c1[2]) * t);
    return `rgba(${r},${g},${b},${alpha})`;
  };
  if (val < 0.4) {
    return interpolate([239, 68, 68], [245, 158, 11], val / 0.4, 0.85);
  } else if (val < 0.7) {
    return interpolate([245, 158, 11], [0, 212, 255], (val - 0.4) / 0.3, 0.75);
  } else {
    return interpolate([0, 212, 255], [16, 185, 129], (val - 0.7) / 0.3, 0.8);
  }
}

// ═══════ Components ═══════

function AnimatedBackground() {
  return (
    <>
      <div className="bg-grid"></div>
      <div className="bg-glow bg-glow--1"></div>
      <div className="bg-glow bg-glow--2"></div>
      <div className="bg-glow bg-glow--3"></div>
    </>
  );
}

function Header() {
  return (
    <header id="app-header">
      <div className="header-content">
        <div className="logo-group">
          <div className="logo-icon">
            <svg viewBox="0 0 40 40" fill="none">
              <circle cx="20" cy="20" r="18" stroke="url(#logoGrad)" strokeWidth="2.5" />
              <path d="M13 20 L18 25 L27 15" stroke="url(#logoGrad)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="40" y2="40">
                  <stop offset="0%" stopColor="#00d4ff"/>
                  <stop offset="100%" stopColor="#7c3aed"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div>
            <h1>Academic Integrity Analyzer</h1>
            <p className="tagline">Detect invisible plagiarism through stylometric fingerprinting</p>
          </div>
        </div>
        <div className="header-badge">
          <span className="badge-dot"></span>
          Forensics Mode Active
        </div>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer id="app-footer">
      <p>Academic Integrity Analyzer • Powered by Stylometric Analysis</p>
      <p className="footer-sub">Detecting invisible plagiarism — not copied text, but copied thinking styles.</p>
    </footer>
  );
}

// ═══════ Views ═══════

function UploadView({ onAnalyze }) {
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      const f = e.dataTransfer.files[0];
      if (f.name.toLowerCase().endsWith('.pdf')) setFile(f);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <section id="upload-section" className="section glass-card">
      <div className="section-header">
        <h2>📄 Upload Document</h2>
        <p>Upload a PDF research paper to analyze writing style and citation consistency</p>
      </div>

      {!file ? (
        <div
          className={`drop-zone ${isDragOver ? 'drag-over' : ''}`}
          onClick={() => fileInputRef.current.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
        >
          <div className="drop-zone-content">
            <div className="upload-icon">
              <svg viewBox="0 0 64 64" fill="none">
                <rect x="8" y="12" width="48" height="44" rx="4" stroke="currentColor" strokeWidth="2"/>
                <path d="M24 36 L32 28 L40 36" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M32 28 L32 48" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M8 24 L28 24 L32 18 L36 24 L56 24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <p className="drop-text">Drag & drop your PDF here</p>
            <p className="drop-subtext">or click to browse files</p>
            <div className="file-constraints">PDF only • Max 50 MB</div>
          </div>
          <input type="file" accept=".pdf" hidden ref={fileInputRef} onChange={handleFileChange} />
        </div>
      ) : (
        <div id="file-info" className="file-info">
          <div className="file-info-icon">📎</div>
          <div className="file-info-details">
            <span className="file-name">{file.name}</span>
            <span className="file-size">{formatFileSize(file.size)}</span>
          </div>
          <button className="btn-icon" title="Remove file" onClick={() => setFile(null)}>✕</button>
        </div>
      )}

      {file && (
        <button id="analyze-btn" className="btn-primary" onClick={() => onAnalyze(file)}>
          <span className="btn-icon-left">🔬</span>
          Analyze Document
        </button>
      )}
    </section>
  );
}

function LoadingView() {
  const [stepIdx, setStepIdx] = useState(0);
  const steps = useMemo(() => [
    { text: 'Extracting text from PDF...', sub: 'Reading document content and cleaning noise', pct: 15 },
    { text: 'Detecting Citation Boundaries...', sub: 'Identifying references and publication years', pct: 25 },
    { text: 'Splitting into analyzable chunks...', sub: 'Creating segments of 100 words each', pct: 35 },
    { text: 'Extracting stylometric features...', sub: 'Analyzing linguistic fingerprints', pct: 50 },
    { text: 'Mapping Citation Temporal Drift...', sub: 'Checking for chronological inconsistencies', pct: 65 },
    { text: 'Computing similarity matrix...', sub: 'Comparing styles between all chunk pairs', pct: 80 },
    { text: 'Calculating integrity score...', sub: 'Generating forensic report', pct: 95 },
    { text: 'Analysis complete!', sub: 'Finalizing report...', pct: 100 },
  ], []);

  useEffect(() => {
    const timer = setInterval(() => {
      setStepIdx((prev) => Math.min(prev + 1, steps.length - 2));
    }, 800);
    return () => clearInterval(timer);
  }, [steps]);

  const step = steps[stepIdx];

  return (
    <section id="loading-section" className="section glass-card">
      <div className="loading-container">
        <div className="dna-helix">
          <div className="helix-strand"></div>
          <div className="helix-strand"></div>
          <div className="helix-strand"></div>
        </div>
        <h3 id="loading-text">{step.text}</h3>
        <div className="progress-bar">
          <div id="progress-fill" className="progress-fill" style={{ width: `${step.pct}%` }}></div>
        </div>
        <p className="loading-sub" id="loading-sub">{step.sub}</p>
      </div>
    </section>
  );
}

function DownloadReportButton({ data }) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async (format = 'pdf') => {
    setIsDownloading(true);
    try {
      const res = await fetch(`/report?format=${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      if (!res.ok) throw new Error('Failed to generate report');
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Forensic_Report_${data.filename || 'document'}.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Download failed: ' + err.message);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="download-group" style={{ display: 'flex', gap: '8px' }}>
      <button 
        className="btn-primary" 
        onClick={() => handleDownload('pdf')} 
        disabled={isDownloading}
        style={{ background: 'linear-gradient(135deg, #7c3aed 0%, #00d4ff 100%)' }}
      >
        <span className="btn-icon-left">{isDownloading ? '⏳' : '📄'}</span>
        {isDownloading ? 'Generating...' : 'Download PDF Report'}
      </button>
      <button 
        className="btn-secondary" 
        onClick={() => handleDownload('txt')} 
        disabled={isDownloading}
        title="Download as Text"
        style={{ padding: '14px 20px', marginTop: '20px' }}
      >
        <span className="btn-icon-left">📝</span>
      </button>
    </div>
  );
}

function ResultsView({ data, onNewAnalysis }) {
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  return (
    <section id="results-section">
      <ScoreHero data={data} />

      <ClusterMap chunks={data.chunks} authorInfo={data.author_estimation} />

      <div className="viz-row">
        <HeatmapCard matrix={data.similarity_matrix} />
        <TrendsChartCard trends={data.feature_trends} chunkCount={data.num_chunks} />
      </div>

      <NeighborChartCard matrix={data.similarity_matrix} />
      
      {/* Integrated Forensic Sections */}
      <SuspiciousSections 
        sections={data.suspicious_sections} 
        citations={data.citation_analysis} 
        semanticSources={data.semantic_sources}
      />
      
      <AIDetectionSection ai={data.ai_detection} />
      
      <ChunksList chunks={data.chunks} citations={data.citation_analysis} />

      <div className="center-action" style={{ display: 'flex', justifyContent: 'center', gap: '15px', marginTop: '20px' }}>
        <button id="new-analysis-btn" className="btn-secondary" onClick={onNewAnalysis}>
          <span className="btn-icon-left">🔄</span> New Analysis
        </button>
        <DownloadReportButton data={data} />
      </div>
    </section>
  );
}

function ScoreHero({ data }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const size = 220; const cx = size / 2; const cy = size / 2;
    const radius = 90; const lineWidth = 12;

    canvas.width = size * 2; canvas.height = size * 2;
    canvas.style.width = size + 'px'; canvas.style.height = size + 'px';
    ctx.scale(2, 2);

    let current = 0;
    const target = data.integrity_score;
    const totalAngle = 1.5 * Math.PI;
    let animId;

    function draw() {
      if (current >= target) current = target;
      ctx.clearRect(0, 0, size, size);

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0.75 * Math.PI, 2.25 * Math.PI);
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.lineWidth = lineWidth;
      ctx.lineCap = 'round';
      ctx.stroke();

      const endAngle = 0.75 * Math.PI + (current / 100) * totalAngle;
      const gradient = ctx.createLinearGradient(0, 0, size, size);
      if (current >= 75) { gradient.addColorStop(0, '#10b981'); gradient.addColorStop(1, '#3b82f6'); }
      else if (current >= 50) { gradient.addColorStop(0, '#f59e0b'); gradient.addColorStop(1, '#3b82f6'); }
      else { gradient.addColorStop(0, '#ef4444'); gradient.addColorStop(1, '#f59e0b'); }

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0.75 * Math.PI, endAngle);
      ctx.strokeStyle = gradient;
      ctx.lineWidth = lineWidth;
      ctx.lineCap = 'round';
      ctx.stroke();

      if (current < target) {
        current += Math.max(0.5, (target - current) * 0.08);
        animId = requestAnimationFrame(draw);
      }
    }
    animId = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animId);
  }, [data.integrity_score]);

  let verdictColor = '#10b981';
  let verdictText = '✅ High Integrity — Consistent Writing Style';
  let verdictDesc = 'The document exhibits a highly consistent writing style and chronological citation pattern.';
  
  if (data.integrity_score < 50) {
    verdictColor = '#dc2626'; verdictText = '🔴 Critical Alert — "Stitched" Authorship Likely';
    verdictDesc = 'Multiple style shifts and citation age drifts suggest content was assembled from diverse sources.';
  } else if (data.integrity_score < 75) {
    verdictColor = '#f59e0b'; verdictText = '⚠️ Moderate Integrity — Style Deviations Detected';
    verdictDesc = 'Noticeable variations in linguistic patterns or source publication dates.';
  }

  // Calculate Citation Drift Badge
  const citationDriftCount = data.citation_analysis?.filter(c => c.is_temporally_inconsistent).length || 0;

  return (
    <div className="section glass-card score-hero">
      <div className="score-gauge-container">
        <canvas ref={canvasRef} id="score-gauge"></canvas>
        <div className="score-value-overlay">
          <span className="score-number">{Math.round(data.integrity_score)}</span><span className="score-percent">%</span>
        </div>
        <div className="score-label">Integrity Score</div>
      </div>
      <div className="score-details">
        <h2 className="score-verdict" style={{ color: verdictColor }}>{verdictText}</h2>
        <p className="score-desc">{verdictDesc}</p>
        <div className="score-meta-grid">
          <div className="meta-card">
            <span className="meta-value">{data.num_chunks}</span><span className="meta-label">Chunks</span>
          </div>
          <div className="meta-card">
            <span className="meta-value">{data.total_words?.toLocaleString()}</span><span className="meta-label">Total Words</span>
          </div>
          <div className="meta-card meta-card--warn">
            <span className="meta-value">{citationDriftCount}</span><span className="meta-label">Citation Anomaly</span>
          </div>
          <div className="meta-card meta-card--authors">
            <span className="meta-value">{data.author_estimation?.estimated_authors || 1}</span><span className="meta-label">Est. Authors</span>
          </div>
          <div className="meta-card meta-card--ai">
            <span className="meta-value">{data.ai_detection.ai_score}%</span><span className="meta-label">AI Score</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function ClusterMap({ chunks, authorInfo }) {
  return (
    <div className="section glass-card viz-card">
      <div className="section-header">
        <h2>🎨 Stylistic Cluster Map</h2>
        <p>Inferred authorship clusters across the document</p>
      </div>
      <div className="cluster-map-container">
        {chunks.map((c, i) => (
          <div 
            key={i} 
            className={`cluster-block cluster-badge--${c.cluster}`}
            title={`Chunk ${i+1}: Author ${String.fromCharCode(65 + (c.cluster % 26))}`}
          >
            {String.fromCharCode(65 + (c.cluster % 26))}
          </div>
        ))}
      </div>
      <div className="cluster-legend">
        <span>Estimated Authors: <strong>{authorInfo.estimated_authors}</strong></span>
        <span className="legend-hint">Blocks of the same color indicate the same writing style.</span>
      </div>
    </div>
  );
}

function HeatmapCard({ matrix }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !matrix) return;
    const canvas = canvasRef.current;
    const n = matrix.length;
    const cellSize = Math.min(48, Math.max(28, 400 / n));
    const labelSpace = 50; const padding = 10;
    const totalSize = labelSpace + n * cellSize + padding;
    
    canvas.width = totalSize * 2; canvas.height = totalSize * 2;
    canvas.style.width = totalSize + 'px'; canvas.style.height = totalSize + 'px';
    
    const ctx = canvas.getContext('2d');
    ctx.scale(2, 2);
    
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const val = matrix[i][j];
        const x = labelSpace + j * cellSize; const y = labelSpace + i * cellSize;
        ctx.fillStyle = heatmapColor(val);
        ctx.fillRect(x, y, cellSize - 1, cellSize - 1);

        if (cellSize >= 34) {
          ctx.fillStyle = val > 0.6 ? 'white' : 'rgba(255,255,255,0.6)';
          ctx.font = '500 8px Inter';
          ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          ctx.fillText(val.toFixed(2), x + cellSize / 2, y + cellSize / 2);
        }
      }
    }
  }, [matrix]);

  return (
    <div className="section glass-card viz-card">
      <div className="section-header"><h2>🗺️ Similarity Heatmap</h2><p>Linguistic overlap between sections</p></div>
      <div className="heatmap-wrapper"><canvas ref={canvasRef}></canvas></div>
    </div>
  );
}

function TrendsChartCard({ trends, chunkCount }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [activeFeature, setActiveFeature] = useState('avg_sentence_length');

  const configs = useMemo(() => ({
    avg_sentence_length: { label: 'Sent. Length', color: '#00d4ff' },
    avg_word_length: { label: 'Word Length', color: '#7c3aed' },
    type_token_ratio: { label: 'Vocab Richness', color: '#10b981' },
    stopword_frequency: { label: 'Stopwords', color: '#f59e0b' },
  }), []);

  useEffect(() => {
    if (!chartRef.current || !trends) return;
    const ctx = chartRef.current.getContext('2d');
    if (chartInstance.current) chartInstance.current.destroy();

    const labels = Array.from({ length: chunkCount }, (_, i) => `C${i + 1}`);
    const cfg = configs[activeFeature];
    
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: cfg.label,
          data: trends[activeFeature],
          borderColor: cfg.color,
          backgroundColor: cfg.color + '10',
          fill: true, tension: 0.4,
          pointBackgroundColor: cfg.color,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#8892a8' }, grid: { display: false } },
          y: { ticks: { color: '#8892a8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });
  }, [trends, activeFeature, chunkCount, configs]);

  return (
    <div className="section glass-card viz-card">
      <div className="section-header"><h2>📈 Stylometric Trends</h2><p>Structural consistency flow</p></div>
      <div className="chart-container"><canvas ref={chartRef}></canvas></div>
      <div className="chart-controls">
        {Object.entries(configs).map(([key, cfg]) => (
          <button key={key} className={`chip ${activeFeature === key ? 'active' : ''}`} onClick={() => setActiveFeature(key)}>
            {cfg.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function NeighborChartCard({ matrix }) {
  const chartRef = useRef(null);
  
  useEffect(() => {
    if (!chartRef.current || !matrix) return;
    const n = matrix.length;
    const sims = []; const labels = [];
    for (let i = 0; i < n - 1; i++) {
      sims.push(matrix[i][i + 1]);
      labels.push(`${i + 1}↔${i + 2}`);
    }
    const colors = sims.map(v => v >= 0.7 ? '#10b981' : v >= 0.55 ? '#f59e0b' : '#ef4444');

    const chartInstance = new Chart(chartRef.current.getContext('2d'), {
      type: 'bar',
      data: {
        labels,
        datasets: [{ data: sims, backgroundColor: colors, borderRadius: 4 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { display: true },
          y: { min: 0, max: 1, ticks: { callback: v => (v * 100) + '%' } }
        }
      }
    });
    return () => chartInstance.destroy();
  }, [matrix]);

  return (
    <div className="section glass-card">
      <div className="section-header"><h2>📊 Continuity Timeline</h2><p>Transition similarity between neighbors</p></div>
      <div className="chart-container"><canvas ref={chartRef}></canvas></div>
    </div>
  );
}

function SuspiciousSections({ sections, citations, semanticSources }) {
  const citationFlags = citations?.filter(c => c.is_temporally_inconsistent) || [];
  
  if (!sections.length && !citationFlags.length) {
    return (
      <div className="section glass-card">
        <div className="section-header"><h2>🚨 Anomalies & Flags</h2><p>No major style shifts found</p></div>
        <div className="no-suspicious">
          <span className="check-icon">✅</span>
          <h3>All Checkpoints Passed</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="section glass-card">
      <div className="section-header"><h2>🚨 Anomalies & Flags</h2><p>{sections.length + citationFlags.length} forensic alerts</p></div>
      <div className="suspicious-list">
        {sections.map(s => {
          const sources = semanticSources?.find(src => src.chunk_id === s.chunk_id)?.sources || [];
          return (
            <div key={s.chunk_id} className={`suspicious-item suspicious-item--${s.severity}`}>
              <div className="suspicious-header">
                <span className="suspicious-title">🚩 Style Shift: Chunk {s.chunk_id + 1}</span>
                <span className={`severity-badge severity-badge--${s.severity}`}>{s.severity}</span>
              </div>
              <ul className="suspicious-reasons">
                {s.reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
              
              {sources.length > 0 && (
                <div className="semantic-evidence">
                  <div className="evidence-label">🔗 Traceable Evidence (Potential Sources):</div>
                  <div className="source-links">
                    {sources.map((src, i) => (
                      <a key={i} href={src.url} target="_blank" rel="noopener noreferrer" className="source-link-item">
                        <span className="source-title">{src.title}</span>
                        <span className="source-meta">{src.authors.slice(0, 2).join(', ')}...</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
        {citationFlags.map(c => (
          <div key={`cite-${c.chunk_index}`} className="suspicious-item suspicious-item--medium">
            <div className="suspicious-header">
              <span className="suspicious-title">📅 Temporal Drift: Chunk {c.chunk_index + 1}</span>
              <span className="severity-badge severity-badge--medium">Citations</span>
            </div>
            <p className="drift-desc">This section cites research from <strong>{c.avg_year}</strong>, which deviates significantly from the rest of the document.</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function AIDetectionSection({ ai }) {
  const score = ai.ai_score;
  const barClass = score >= 60 ? 'high' : score >= 30 ? 'medium' : 'low';
  return (
    <div className="section glass-card">
      <div className="section-header"><h2>🤖 AI-Generation Heuristics</h2><p>Uniformity & perplexity score</p></div>
      <div className="ai-content">
        <div className="ai-score-bar">
          <div className="ai-bar-track">
            <div className={`ai-bar-fill ai-bar-fill--${barClass}`} style={{ width: `${score}%` }}></div>
          </div>
          <span className="ai-score-label">{score}%</span>
        </div>
        <p className="verdict-small">{score >= 60 ? 'Suspiciously uniform.' : 'Natural variation present.'}</p>
        <ul className="ai-indicators">
          {ai.indicators.map((ind, i) => <li key={i}>{ind}</li>)}
        </ul>
      </div>
    </div>
  );
}

function ChunksList({ chunks, citations }) {
  const [openChunks, setOpenChunks] = useState({});
  const toggleChunk = (id) => setOpenChunks(prev => ({ ...prev, [id]: !prev[id] }));

  return (
    <div className="section glass-card">
      <div className="section-header"><h2>📝 Forensic Chunk Map</h2><p>Granular text & citation metadata</p></div>
      <div className="chunks-list">
        {chunks.map(chunk => {
          const citeInfo = citations?.find(c => c.chunk_index === chunk.id);
          const hasTemporalDrift = citeInfo?.is_temporally_inconsistent;
          const isOpen = !!openChunks[chunk.id];
          
          return (
            <div key={chunk.id} className={`chunk-item ${chunk.is_suspicious || hasTemporalDrift ? 'chunk-item--flagged' : ''}`}>
              <div className="chunk-header" onClick={() => toggleChunk(chunk.id)}>
                <div className="chunk-id-group">
                   <span className="chunk-id">Chunk {chunk.id + 1}</span>
                   <span className={`cluster-badge cluster-badge--${chunk.cluster}`}>
                     {String.fromCharCode(65 + (chunk.cluster % 26))}
                   </span>
                   {hasTemporalDrift && <span className="cite-badge">📅 {citeInfo.avg_year}</span>}
                </div>
                <div className="chunk-meta">
                  <span>{chunk.word_count} w</span>
                  <span className="chunk-sim-tag">Sim: {(chunk.avg_similarity*100).toFixed(0)}%</span>
                </div>
              </div>
              <div className={`chunk-body ${isOpen ? 'open' : ''}`} style={{ display: isOpen ? 'block' : 'none' }}>
                <div className="chunk-text">{chunk.full_text || chunk.text}</div>
                {hasTemporalDrift && (
                  <div className="citation-evidence">
                    🔎 <strong>Citation Evidence:</strong> This chunk relies on sources from {citeInfo.avg_year}.
                  </div>
                )}
                <div className="chunk-features">
                  {Object.entries(chunk.features).slice(0, 4).map(([k, v]) => (
                    <div key={k} className="feature-tag">
                      <span className="feature-tag-name">{k.replace(/_/g, ' ')}</span>
                      <span className="feature-tag-value">{v.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════ Main App ═══════

function App() {
  const [appState, setAppState] = useState('UPLOAD'); 
  const [data, setData] = useState(null);

  const handleAnalyze = async (file) => {
    setAppState('LOADING');
    try {
      const formData = new FormData();
      formData.append('file', file);
      // Ensure your backend endpoint is correctly matched here
      const res = await fetch('/analyze', { method: 'POST', body: formData });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Analysis failed');
      }
      const resultData = await res.json();
      setData(resultData);
      setAppState('RESULTS');
    } catch (err) {
      alert('Error: ' + err.message);
      setAppState('UPLOAD');
    }
  };

  return (
    <>
      <AnimatedBackground />
      <Header />
      <main id="app-main">
        {appState === 'UPLOAD' && <UploadView onAnalyze={handleAnalyze} />}
        {appState === 'LOADING' && <LoadingView />}
        {appState === 'RESULTS' && <ResultsView data={data} onNewAnalysis={() => setAppState('UPLOAD')} />}
      </main>
      <Footer />
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);