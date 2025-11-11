import os
from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm

try:
    from sentence_transformers import SentenceTransformer
    _HAS_SBERT = True
except Exception:
    _HAS_SBERT = False

def _color_for_score(score: float):
    if score >= 0.85:
        return colors.red
    if score >= 0.60:
        return colors.orange
    return colors.green

def run_similarity_analysis(submissions: List[Dict], use_embeddings: bool = False):
    texts = [s.get("cleaned_text") or "" for s in submissions]
    titles = [s.get("title") or s.get("_id") for s in submissions]

    if use_embeddings and _HAS_SBERT:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        X = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    else:
        tfidf = TfidfVectorizer(min_df=1, max_df=0.95)
        X = tfidf.fit_transform(texts).toarray()

    sim_matrix = cosine_similarity(X)
    # Simple clustering for overview
    k = min(3, max(1, len(submissions)//2))
    try:
        km = KMeans(n_clusters=k, n_init="auto", random_state=42)
        labels = km.fit_predict(X)
    except Exception:
        labels = np.zeros(len(submissions), dtype=int)

    # Build pairwise results
    results = []
    for i in range(len(submissions)):
        for j in range(i+1, len(submissions)):
            score = float(sim_matrix[i, j])
            results.append({
                "a_id": str(submissions[i]["_id"]),
                "b_id": str(submissions[j]["_id"]),
                "a_title": titles[i],
                "b_title": titles[j],
                "similarity": round(score*100, 2),
                "bucket": "High" if score>=0.85 else ("Moderate" if score>=0.60 else "Low")
            })

    summary = {
        "num_submissions": len(submissions),
        "high": sum(1 for r in results if r["bucket"] == "High"),
        "moderate": sum(1 for r in results if r["bucket"] == "Moderate"),
        "low": sum(1 for r in results if r["bucket"] == "Low"),
        "clusters": int(len(set(labels)))
    }
    return results, summary

def build_report_pdf(log: Dict, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    filename = f"similarity_report_{str(log['_id'])}.pdf"
    path = os.path.join(out_dir, filename)
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, "AI Similarity Report")

    c.setFont("Helvetica", 11)
    s = log.get("summary", {})
    c.drawString(2*cm, height-3*cm, f"Total Submissions: {s.get('num_submissions', 0)}")
    c.drawString(2*cm, height-3.6*cm, f"High: {s.get('high', 0)}  Moderate: {s.get('moderate', 0)}  Low: {s.get('low', 0)}")
    c.drawString(2*cm, height-4.2*cm, f"Clusters: {s.get('clusters', 0)}")

    # Table header
    y = height-5.2*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "A Title")
    c.drawString(7*cm, y, "B Title")
    c.drawString(12*cm, y, "Similarity")
    y -= 0.5*cm
    c.setFont("Helvetica", 9)

    for row in log.get("results", [])[:40]:
        if y < 3*cm:
            c.showPage()
            y = height-2*cm
        c.setFillColor(_color_for_score(row["similarity"]/100.0))
        c.drawString(2*cm, y, (row["a_title"] or "")[:26])
        c.drawString(7*cm, y, (row["b_title"] or "")[:26])
        c.drawString(12*cm, y, f"{row['similarity']}%")
        c.setFillColor(colors.black)
        y -= 0.5*cm

    c.showPage()
    c.save()
    return path