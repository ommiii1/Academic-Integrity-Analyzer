"""
Integrity Analysis Module
Computes similarity matrix, detects style shifts, calculates integrity score,
and generates explanations for suspicious sections.
"""

import math
import numpy as np
from typing import List, Dict, Tuple


from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


FEATURE_KEYS = [
    "avg_sentence_length",
    "sentence_length_std",
    "avg_word_length",
    "type_token_ratio",
    "hapax_legomena_ratio",
    "stopword_frequency",
    "conjunction_frequency",
    "punctuation_frequency",
    "long_word_ratio",
    "comma_frequency",
]

FEATURE_LABELS = {
    "avg_sentence_length": "Avg Sentence Length",
    "sentence_length_std": "Sentence Length Variety",
    "avg_word_length": "Word Length",
    "type_token_ratio": "Vocabulary Richness",
    "hapax_legomena_ratio": "Unique Phraseology",
    "stopword_frequency": "Stopword Usage",
    "conjunction_frequency": "Logical Flow",
    "punctuation_frequency": "Punctuation Usage",
    "long_word_ratio": "Long Word Ratio",
    "comma_frequency": "Comma Usage",
}


def _features_to_vector(features: dict) -> np.ndarray:
    """Convert feature dict to numpy vector."""
    return np.array([features.get(k, 0) for k in FEATURE_KEYS], dtype=float)


def compute_similarity_matrix(chunks: List[dict]) -> List[List[float]]:
    """
    Compute pairwise cosine similarity matrix from chunk features.
    Returns NxN matrix as nested list.
    """
    n = len(chunks)
    vectors = [_features_to_vector(c["features"]) for c in chunks]

    # Normalize features using Z-score (StandardScaler equivalent)
    # This ensures features with different scales (e.g. word length vs sentence length) 
    # contribute equally to the distance calculation.
    matrix_data = np.array(vectors)
    if n > 1:
        means = matrix_data.mean(axis=0)
        stds = matrix_data.std(axis=0)
        stds[stds == 0] = 1.0  # avoid division by zero for constant features
        matrix_data = (matrix_data - means) / stds

    sim_matrix = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            # Calculate Euclidean distance between the standardized features
            dist = float(np.linalg.norm(matrix_data[i] - matrix_data[j]))
            # Use a steeper decay for standardized distances
            sim = 1.0 / (1.0 + (dist / math.sqrt(len(FEATURE_KEYS))))
            sim_matrix[i][j] = round(sim, 4)
            sim_matrix[j][i] = round(sim, 4)

    return sim_matrix.tolist()


def estimate_authors_clustering(chunks: List[dict]) -> dict:
    """
    Use KMeans and Silhouette analysis to estimate the number of distinct authors.
    """
    n = len(chunks)
    if n < 2:
        return {"estimated_authors": 1, "clusters": [0] * n, "confidence": "none"}

    vectors = np.array([_features_to_vector(c["features"]) for c in chunks])
    scaler = StandardScaler()
    scaled_vectors = scaler.fit_transform(vectors)

    best_k = 1
    best_score = -1
    best_labels = [0] * n

    # Try 2 to 4 clusters
    limit = min(5, n)
    if n >= 2:
        for k in range(2, limit):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(scaled_vectors)
            
            # Silhouette score to measure cluster quality
            # Range is [-1, 1]. For text, > 0.1 is often enough to suggest a real shift.
            score = float(silhouette_score(scaled_vectors, cluster_labels))
            
            # Use a more sensitive threshold (0.15) for linguistic shifts
            if score > 0.15 and score > best_score:
                best_score = score
                best_k = k
                best_labels = cluster_labels.tolist()

    # Fallback: If similarity matrix showed high suspicion but clustering is on the edge,
    # we might still see a distinct k=2 shift.
    return {
        "estimated_authors": int(best_k),
        "clusters": best_labels,
        "silhouette_score": round(best_score, 3) if best_k > 1 else 0
    }


def detect_suspicious_sections(
    chunks: List[dict],
    sim_matrix: List[List[float]],
    threshold: float = 0.55
) -> List[dict]:
    """
    Detect chunks with low similarity to neighbors and the document majority.
    """
    n = len(chunks)
    if n < 2:
        return []

    suspicious = []

    # Compute average features across all chunks for comparison
    all_features = {}
    for key in FEATURE_KEYS:
        values = [c["features"][key] for c in chunks]
        all_features[key] = {
            "mean": np.mean(values),
            "std": np.std(values) if len(values) > 1 else 0,
        }

    for i in range(n):
        sims = [sim_matrix[i][j] for j in range(n) if i != j]
        avg_sim = float(np.mean(sims))

        neighbor_sims = []
        if i > 0:
            neighbor_sims.append(sim_matrix[i][i - 1])
        if i < n - 1:
            neighbor_sims.append(sim_matrix[i][i + 1])
        
        min_neighbor_sim = min(neighbor_sims) if neighbor_sims else avg_sim
        
        is_suspicious = bool(avg_sim < threshold or min_neighbor_sim < (threshold - 0.15))

        if is_suspicious:
            reasons = _generate_explanations(chunks[i], all_features)
            
            if avg_sim < 0.4:
                severity = "high"
            elif avg_sim < 0.5 or min_neighbor_sim < 0.4:
                severity = "medium"
            else:
                severity = "low"
                
            suspicious.append({
                "chunk_id": i,
                "avg_similarity": round(avg_sim, 4),
                "min_neighbor_similarity": round(min_neighbor_sim, 4),
                "severity": severity,
                "reasons": reasons,
            })

        chunks[i]["is_suspicious"] = is_suspicious
        chunks[i]["avg_similarity"] = round(avg_sim, 4)
        chunks[i]["suspicion_reasons"] = _generate_explanations(chunks[i], all_features) if is_suspicious else []

    return suspicious


def _generate_explanations(chunk: dict, global_features: dict) -> List[str]:
    """Generate human-readable explanations for why a chunk is flagged."""
    reasons = []
    features = chunk["features"]

    for key in FEATURE_KEYS:
        value = features[key]
        mean = global_features[key]["mean"]
        std = global_features[key]["std"]

        if std == 0 or mean == 0:
            continue

        deviation = abs(value - mean) / mean * 100
        z_score = abs(value - mean) / std if std > 0 else 0

        if z_score > 1.5 and deviation > 20:
            direction = "higher" if value > mean else "lower"
            label = FEATURE_LABELS.get(key, key)
            reasons.append(
                f"{label} is {deviation:.0f}% {direction} than document average "
                f"({value:.2f} vs {mean:.2f})"
            )

    if not reasons:
        reasons.append("Overall writing style differs from the document's dominant pattern")

    return reasons


def calculate_integrity_score(sim_matrix: List[List[float]], n: int, author_info: dict) -> dict:
    """
    Calculate the final integrity score.
    Higher penalty if more than 1 author is estimated.
    """
    if n < 2:
        return {
            "integrity_score": 100.0,
            "avg_similarity": 1.0,
            "consistency_score": 1.0,
            "similarity_variance": 0.0,
        }

    upper_triangle = []
    for i in range(n):
        for j in range(i + 1, n):
            upper_triangle.append(sim_matrix[i][j])

    avg_sim = float(np.mean(upper_triangle))
    variance = float(np.var(upper_triangle))
    consistency = 1.0 / (1.0 + variance * 10)

    # Base score
    integrity = (0.5 * avg_sim + 0.5 * consistency) * 100
    
    # Author penalty
    if author_info["estimated_authors"] > 1:
        integrity -= (author_info["estimated_authors"] - 1) * 15

    integrity = max(0, min(100, integrity))

    return {
        "integrity_score": round(integrity, 1),
        "avg_similarity": round(avg_sim, 4),
        "consistency_score": round(consistency, 4),
        "similarity_variance": round(variance, 6),
    }


def estimate_ai_detection(chunks: List[dict]) -> dict:
    """Heuristic AI-generated text detection."""
    if len(chunks) < 2:
        return {"ai_score": 0, "confidence": "low", "indicators": []}

    features_data = {key: [] for key in FEATURE_KEYS}
    for chunk in chunks:
        for key in FEATURE_KEYS:
            features_data[key].append(chunk["features"][key])

    indicators = []
    ai_signals = 0
    total_checks = 0

    sl_cv = np.std(features_data["avg_sentence_length"]) / (np.mean(features_data["avg_sentence_length"]) + 1e-9)
    total_checks += 1
    if sl_cv < 0.07:
        ai_signals += 1
        indicators.append("Unusually uniform sentence lengths (CV={:.3f})".format(sl_cv))

    sl_std_avg = np.mean(features_data["sentence_length_std"])
    total_checks += 1
    if sl_std_avg < 4.0:
        ai_signals += 1
        indicators.append("Low internal sentence variety (mean std={:.2f})".format(sl_std_avg))

    ttr_cv = np.std(features_data["type_token_ratio"]) / (np.mean(features_data["type_token_ratio"]) + 1e-9)
    total_checks += 1
    if ttr_cv < 0.04:
        ai_signals += 1
        indicators.append("Highly consistent vocabulary richness (CV={:.3f})".format(ttr_cv))

    hl_cv = np.std(features_data["hapax_legomena_ratio"]) / (np.mean(features_data["hapax_legomena_ratio"]) + 1e-9)
    total_checks += 1
    if hl_cv < 0.06:
        ai_signals += 1
        indicators.append("Unnatural stability in unique word usage (CV={:.3f})".format(hl_cv))

    sw_cv = np.std(features_data["stopword_frequency"]) / (np.mean(features_data["stopword_frequency"]) + 1e-9)
    total_checks += 1
    if sw_cv < 0.04:
        ai_signals += 1
        indicators.append("Stopword usage is unnaturally consistent (CV={:.3f})".format(sw_cv))

    conj_cv = np.std(features_data["conjunction_frequency"]) / (np.mean(features_data["conjunction_frequency"]) + 1e-9)
    total_checks += 1
    if conj_cv < 0.05:
        ai_signals += 1
        indicators.append("Mathematical consistency in logical connectors (CV={:.3f})".format(conj_cv))

    ai_score = (ai_signals / total_checks) * 100

    if ai_score >= 60:
        confidence = "high"
    elif ai_score >= 30:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "ai_score": round(ai_score, 1),
        "confidence": confidence,
        "indicators": indicators,
    }


def build_feature_trends(chunks: List[dict]) -> dict:
    """Build feature trends across chunks for visualization."""
    trends = {key: [] for key in FEATURE_KEYS}
    for chunk in chunks:
        for key in FEATURE_KEYS:
            trends[key].append(chunk["features"][key])
    return trends


def full_analysis(chunks: List[dict], citation_report: List[dict] = None) -> dict:
    """Run the complete analysis pipeline."""
    n = len(chunks)

    if n == 0:
        return {
            "integrity_score": 0,
            "num_chunks": 0,
            "num_suspicious": 0,
            "similarity_matrix": [],
            "suspicious_sections": [],
            "ai_detection": {"ai_score": 0, "confidence": "low", "indicators": []},
            "feature_trends": {},
            "chunks": [],
            "citation_analysis": [],
            "author_estimation": {"estimated_authors": 1}
        }

    # Step 1: Compute similarity matrix
    sim_matrix = compute_similarity_matrix(chunks)

    # Step 2: Detect suspicious sections
    suspicious = detect_suspicious_sections(chunks, sim_matrix)

    # Step 3: Author Estimating & Clustering
    author_info = estimate_authors_clustering(chunks)

    # Step 4: Calculate integrity score
    scores = calculate_integrity_score(sim_matrix, n, author_info)

    # Step 5: AI detection heuristic
    ai_detection = estimate_ai_detection(chunks)

    # Step 6: Feature trends for visualization
    feature_trends = build_feature_trends(chunks)

    # Map cluster labels back to chunks
    for i in range(n):
        chunks[i]["cluster"] = author_info["clusters"][i]

    # Build clean chunk data for response
    clean_chunks = []
    for c in chunks:
        clean_chunks.append({
            "id": c["id"],
            "text": c["text"][:500] + ("..." if len(c["text"]) > 500 else ""),
            "full_text": c["text"],
            "word_count": c["word_count"],
            "features": c["features"],
            "is_suspicious": c.get("is_suspicious", False),
            "avg_similarity": c.get("avg_similarity", 1.0),
            "suspicion_reasons": c.get("suspicion_reasons", []),
            "cluster": c.get("cluster", 0)
        })

    return {
        "integrity_score": scores["integrity_score"],
        "avg_similarity": scores["avg_similarity"],
        "consistency_score": scores["consistency_score"],
        "similarity_variance": scores["similarity_variance"],
        "num_chunks": n,
        "num_suspicious": len(suspicious),
        "similarity_matrix": sim_matrix,
        "suspicious_sections": suspicious,
        "ai_detection": ai_detection,
        "feature_trends": feature_trends,
        "chunks": clean_chunks,
        "citation_analysis": citation_report or [],
        "author_estimation": author_info
    }
