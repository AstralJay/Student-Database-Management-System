from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import FLASK_SECRET_KEY
from database import supabase, auth_client
from utils import login_required, roles_required
from blockchain.chain import add_block, verify_chain, ensure_genesis
from crypto.keys import generate_key_pair, save_key_pair, load_private_key, public_key_pem
from pathlib import Path
import uuid
import os

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

KEY_DIR = Path("keys")
KEY_DIR.mkdir(exist_ok=True)

@app.context_processor
def inject_user():
    return {
        "current_user": session.get("user_id"),
        "current_role": session.get("role"),
        "current_name": session.get("name"),
    }

def get_profile(user_id):
    result = supabase.table("profiles").select("*").eq("id", user_id).limit(1).execute()
    return result.data[0] if result.data else None

def get_validator_private_key(user_id):
    path = KEY_DIR / user_id / "private_key.pem"
    if not path.exists():
        raise FileNotFoundError("Validator private key not found. Generate/register an authority key first.")
    return load_private_key(path)

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        role = request.form["role"]

        if role not in ("student", "faculty"):
            flash("Only student or faculty self-registration is enabled.", "error")
            return redirect(url_for("register"))

        try:
            auth = auth_client.auth.sign_up({"email": email, "password": password})
            user = auth.user
            if not user:
                flash("Registration failed. Check Supabase Auth settings.", "error")
                return redirect(url_for("register"))

            profile = {
                "id": user.id,
                "name": name,
                "email": email,
                "role": role,
                "department": request.form.get("department", "").strip(),
            }
            supabase.table("profiles").insert(profile).execute()

            # Faculty are automatically made PoA validators for the demo.
            if role == "faculty":
                private_key, public_key = generate_key_pair()
                user_dir = KEY_DIR / user.id
                save_key_pair(
                    private_key,
                    public_key,
                    user_dir / "private_key.pem",
                    user_dir / "public_key.pem",
                )
                supabase.table("authority_nodes").insert({
                    "user_id": user.id,
                    "role": "FACULTY",
                    "public_key": public_key_pem(public_key),
                    "status": "ACTIVE",
                }).execute()

            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Registration error: {e}", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]
        try:
            auth = auth_client.auth.sign_in_with_password({"email": email, "password": password})
            user = auth.user
            if not user:
                flash("Invalid email or password.", "error")
                return redirect(url_for("login"))

            profile = get_profile(user.id)
            if not profile:
                flash("Profile not found.", "error")
                return redirect(url_for("login"))

            session["user_id"] = user.id
            session["email"] = user.email
            session["name"] = profile["name"]
            session["role"] = profile["role"]
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Login failed: {e}", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    try:
        auth_client.auth.sign_out()
    except Exception:
        pass
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    role = session["role"]

    if role == "student":
        records = (
            supabase.table("academic_records")
            .select("*,courses(*)")
            .eq("student_id", user_id)
            .order("created_at", desc=True)
            .execute()
        ).data
    else:
        records = (
            supabase.table("academic_records")
            .select("*,courses(*),profiles!academic_records_student_id_fkey(name,email)")
            .order("created_at", desc=True)
            .execute()
        ).data

    return render_template("dashboard.html", records=records)

@app.route("/record/add", methods=["GET", "POST"])
@roles_required("faculty")
def add_record():
    students = supabase.table("profiles").select("id,name,email").eq("role", "student").order("name").execute().data
    courses = supabase.table("courses").select("*").order("code").execute().data

    if request.method == "POST":
        student_id = request.form["student_id"]
        course_id = request.form["course_id"]
        semester = request.form["semester"]
        marks = int(request.form["marks"])
        attendance = float(request.form["attendance"])
        grade = request.form["grade"].strip().upper()
        academic_year = request.form["academic_year"].strip()

        record = {
            "student_id": student_id,
            "course_id": course_id,
            "semester": semester,
            "academic_year": academic_year,
            "marks": marks,
            "attendance": attendance,
            "grade": grade,
            "updated_by": session["user_id"],
        }

        try:
            inserted = supabase.table("academic_records").insert(record).execute().data[0]
            transaction = {
                "type": "ACADEMIC_RECORD_CREATED",
                "record_id": inserted["id"],
                "student_id": student_id,
                "course_id": course_id,
                "semester": semester,
                "academic_year": academic_year,
                "marks": marks,
                "attendance": attendance,
                "grade": grade,
            }
            private_key = get_validator_private_key(session["user_id"])
            add_block(transaction, session["user_id"], private_key)
            flash("Academic record added and anchored to the blockchain.", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Could not add record: {e}", "error")

    return render_template("record_form.html", students=students, courses=courses)

@app.route("/record/<record_id>/edit", methods=["GET", "POST"])
@roles_required("faculty")
def edit_record(record_id):
    record = supabase.table("academic_records").select("*").eq("id", record_id).limit(1).execute().data
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("dashboard"))
    record = record[0]

    students = supabase.table("profiles").select("id,name,email").eq("role", "student").order("name").execute().data
    courses = supabase.table("courses").select("*").order("code").execute().data

    if request.method == "POST":
        new_values = {
            "marks": int(request.form["marks"]),
            "attendance": float(request.form["attendance"]),
            "grade": request.form["grade"].strip().upper(),
            "semester": request.form["semester"],
            "academic_year": request.form["academic_year"].strip(),
            "updated_by": session["user_id"],
        }
        try:
            updated = supabase.table("academic_records").update(new_values).eq("id", record_id).execute().data[0]
            transaction = {
                "type": "ACADEMIC_RECORD_UPDATED",
                "record_id": record_id,
                "student_id": updated["student_id"],
                "course_id": updated["course_id"],
                "semester": updated["semester"],
                "academic_year": updated["academic_year"],
                "marks": updated["marks"],
                "attendance": updated["attendance"],
                "grade": updated["grade"],
            }
            private_key = get_validator_private_key(session["user_id"])
            add_block(transaction, session["user_id"], private_key)
            flash("Record updated and new state anchored to the blockchain.", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Could not update record: {e}", "error")

    return render_template("record_form.html", students=students, courses=courses, record=record, edit_mode=True)

@app.route("/courses", methods=["GET", "POST"])
@roles_required("faculty")
def courses():
    if request.method == "POST":
        data = {
            "code": request.form["code"].strip().upper(),
            "name": request.form["name"].strip(),
            "credits": int(request.form["credits"]),
            "department": request.form["department"].strip(),
        }
        try:
            supabase.table("courses").insert(data).execute()
            flash("Course added.", "success")
        except Exception as e:
            flash(f"Could not add course: {e}", "error")
    rows = supabase.table("courses").select("*").order("code").execute().data
    return render_template("courses.html", courses=rows)

@app.route("/blockchain")
@login_required
def blockchain():
    rows = supabase.table("blocks").select("*").order("block_number", desc=True).execute().data
    valid, message = verify_chain()
    return render_template("blockchain.html", blocks=rows, valid=valid, message=message)

@app.route("/api/verify", methods=["GET"])
@login_required
def api_verify():
    valid, message = verify_chain()
    return jsonify({"valid": valid, "message": message})

@app.route("/health")
def health():
    try:
        ensure_genesis()
        return jsonify({"status": "ok", "blockchain": "initialized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
