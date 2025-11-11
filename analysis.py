from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app, send_file
from flask_login import login_required, current_user
from models.db import get_db
from ai.similarity import run_similarity_analysis, build_report_pdf
from bson import ObjectId
from datetime import datetime
import os

analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")

@analysis_bp.route("/run", methods=["POST"])
@login_required
def run():
    if current_user.role != "faculty":
        flash("Only faculty can run analysis", "warning")
        return redirect(url_for("main.student_dashboard"))
    db = get_db()
    submissions = list(db.assignments.find({"status": {"$ne": "Rejected"}}))
    if len(submissions) < 2:
        flash("Need at least two valid submissions to compare", "warning")
        return redirect(url_for("main.faculty_dashboard"))

    results, summary = run_similarity_analysis(submissions, use_embeddings=current_app.config.get("USE_EMBEDDINGS", False))
    log = {
        "created_at": datetime.utcnow(),
        "summary": summary,
        "results": results
    }
    db.similarity_logs.insert_one(log)
    flash("Similarity analysis completed", "success")
    return redirect(url_for("main.faculty_dashboard"))

@analysis_bp.route("/report/<log_id>")
@login_required
def report(log_id):
    db = get_db()
    log = db.similarity_logs.find_one({"_id": ObjectId(log_id)})
    if not log:
        flash("Report not found", "danger")
        return redirect(url_for("main.faculty_dashboard"))
    pdf_path = build_report_pdf(log, current_app.config["REPORT_FOLDER"])
    return send_file(pdf_path, as_attachment=True)