import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.db import get_db
from ai.preprocess import extract_text_from_file, clean_text
from bson import ObjectId
import io

main_bp = Blueprint("main", __name__)

def allowed_file(filename, exts):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in exts

@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "faculty":
            return redirect(url_for("main.faculty_dashboard"))
        return redirect(url_for("main.student_dashboard"))
    return redirect(url_for("auth.login"))

@main_bp.route("/student")
@login_required
def student_dashboard():
    if current_user.role != "student":
        return redirect(url_for("main.faculty_dashboard"))
    db = get_db()
    submissions = list(db.assignments.find({"student_id": current_user.id}).sort("created_at", -1))
    return render_template("student_dashboard.html", submissions=submissions)

@main_bp.route("/faculty")
@login_required
def faculty_dashboard():
    if current_user.role != "faculty":
        return redirect(url_for("main.student_dashboard"))
    db = get_db()
    q = {}
    dept = request.args.get("dept")
    status = request.args.get("status")
    if dept:
        q["department"] = dept
    if status:
        q["status"] = status
    submissions = list(db.assignments.find(q).sort("created_at", -1))
    sim_logs = list(db.similarity_logs.find().sort("created_at", -1)[:10])
    return render_template("faculty_dashboard.html", submissions=submissions, sim_logs=sim_logs)

@main_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if current_user.role != "student":
        return redirect(url_for("main.student_dashboard"))
    db = get_db()
    if request.method == "POST":
        file = request.files.get("file")
        title = request.form.get("title", "Untitled")
        dept = request.form.get("department", "General")
        if not file or file.filename == "":
            flash("Please choose a file", "warning")
            return redirect(request.url)
        if not allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
            flash("Only PDF or DOCX allowed", "warning")
            return redirect(request.url)
        filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(save_path)

        # Extract + clean text
        raw_text = extract_text_from_file(save_path)
        cleaned = clean_text(raw_text or "")
        status = "Pending"
        if not cleaned or cleaned.strip() == "":
            status = "Rejected"
            flash("File seems empty/unreadable. Marked as Rejected.", "danger")

        doc = {
            "title": title,
            "filename": filename,
            "path": save_path,
            "student_id": current_user.id,
            "department": dept,
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "status": status,
            "grade": None,
            "feedback": "",
            "created_at": datetime.utcnow()
        }
        db.assignments.insert_one(doc)
        flash("Uploaded successfully", "success")
        return redirect(url_for("main.student_dashboard"))
    return render_template("upload.html")

@main_bp.route("/download/<assign_id>")
@login_required
def download(assign_id):
    db = get_db()
    a = db.assignments.find_one({"_id": ObjectId(assign_id)})
    if not a:
        flash("Not found", "danger")
        return redirect(url_for("main.index"))
    return send_file(a["path"], as_attachment=True)

@main_bp.route("/feedback/<assign_id>", methods=["POST"])
@login_required
def feedback(assign_id):
    if current_user.role != "faculty":
        return redirect(url_for("main.student_dashboard"))
    db = get_db()
    grade = request.form.get("grade")
    status = request.form.get("status")
    feedback = request.form.get("feedback", "")
    db.assignments.update_one({"_id": ObjectId(assign_id)}, {"$set": {
        "grade": grade, "status": status, "feedback": feedback
    }})
    flash("Feedback saved", "success")
    return redirect(url_for("main.faculty_dashboard"))