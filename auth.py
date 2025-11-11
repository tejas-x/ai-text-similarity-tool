from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from models.db import get_user_by_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully", "success")
            if user.role == "faculty":
                return redirect(url_for("main.faculty_dashboard"))
            return redirect(url_for("main.student_dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("auth.login"))