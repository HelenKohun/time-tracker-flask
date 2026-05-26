import os

from cs50 import SQL
from datetime import date, datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)


app.secret_key = os.urandom(24)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///time_tracker.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))


    tasks_progress  = db.execute("SELECT daily_progress.date, daily_progress.satisfaction, daily_progress.time_spent, tasks.name FROM daily_progress JOIN tasks ON daily_progress.task_id = tasks.id WHERE daily_progress.user_id = ? ORDER BY daily_progress.date ASC", session["user_id"])

    dates = [f"{task['date']} ({task['name']})" for task in tasks_progress]
    scores = [task['satisfaction'] for task in tasks_progress]
    time_spent = [task['time_spent'] for task in tasks_progress]

    plans = db.execute("SELECT tasks.name, tasks.type, planner.hours_per_day, planner.estimated_days, planner.created_at FROM tasks JOIN planner ON tasks.id = planner.task_id WHERE tasks.user_id = ? ORDER BY planner.created_at DESC", session["user_id"])

    for plan in plans:
        start_date = datetime.strptime(plan["created_at"], "%Y-%m-%d").date()
        end_date = start_date + timedelta(days=plan["estimated_days"] - 1)
        plan["end_date"] = end_date.strftime("%Y-%m-%d")

    return render_template("index.html", active_page="home", plans=plans, dates=dates, scores=scores, time_spent=time_spent)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("user_login")
        password = request.form.get("user_password")

        if not username or not password:
            return render_template("apology.html", message="Please fill in both fields")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not user or not check_password_hash(user[0]["hash"], password):
            return render_template("apology.html", message="Invalid username or password")

        session["user_id"] = user[0]["id"]
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("user_login")
        password = request.form.get("user_password")
        confirmation = request.form.get("password_confirmation")

        if not username or not password or not confirmation:
            return render_template("apology.thml", message="All fields are required")

        if password != confirmation:
            return render_template("apology.html", message="Passwords do not match")

        if len(username) < 3 or len(password) < 6:
            return render_template("apology.html", message="Username or password too short")

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        except Exception:
            return render_template("apology.html", message="Username already exists")

        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    if request.method == "POST":
        name = request.form.get("name")
        task_type = request.form.get("type")
        planned_time_str = float(request.form.get("planned_time"))

        if not name or not task_type or not planned_time_str:
            return render_template("apology.html", message="All fields are required")

        try:
            planned_time = float(planned_time_str)
        except ValueError:
            return render_template("apology.html", message="Planned time must be a number")

        if planned_time <= 0:
            return render_template("apology.html", message="Planned time must be greater than 0")

        db.execute("INSERT INTO tasks (user_id, name, type, planned_time) VALUES (?, ?, ?, ?)", session["user_id"], name, task_type, planned_time)

        return redirect(url_for("tasks"))

    tasks_list = db.execute("SELECT * FROM tasks WHERE user_id = ?", session["user_id"])

    return render_template("tasks.html", active_page="tasks", tasks_list=tasks_list)

@app.route("/planner", methods=["GET", "POST"])
@login_required
def planner():

    tasks = db.execute("SELECT id, name, planned_time FROM tasks WHERE user_id = ?", session["user_id"])
    plan = None

    if request.method == "POST":
        task_id = int(request.form.get("task_id"))
        hours_per_day = float(request.form.get("hours_per_day"))

        if hours_per_day <= 0:
            return render_template("apology.html", message="Hours per day must be positive")

        task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])[0]
        total_hours = task["planned_time"]

        import math
        days_needed = math.ceil(total_hours / hours_per_day)
        today = datetime.today().date()

        plan = {}
        for i in range(days_needed):
            day = today + timedelta(days=i)
            if i < days_needed - 1:
                plan[str(day)] = hours_per_day
            else:
                plan[str(day)] = round(total_hours - hours_per_day * (days_needed - 1), 2 )

        db.execute("INSERT INTO planner (user_id, task_id, hours_per_day, estimated_days) VALUES (?, ?, ?, ?)", session["user_id"],
                   task_id, hours_per_day, days_needed)

    return render_template("planner.html", tasks=tasks, plan=plan)


@app.route("/tasks/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    satisfaction = int(request.form.get("satisfaction"))
    time_spent = float(request.form.get("time_spent"))

    if satisfaction < 1 or satisfaction > 5:
        return render_template("apology.html", message="Satisfaction must be 1-5")
    if time_spent <= 0:
        return render_template("apology.html", message="Time spent must be positive")

    db.execute("UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?", task_id, session["user_id"])

    db.execute("INSERT INTO daily_progress (user_id, task_id, date, satisfaction, time_spent) VALUES(?, ?, DATE('now'), ?, ?)", session["user_id"], task_id, satisfaction, time_spent)

    return redirect(url_for("tasks"))


@app.route("/tasks/delete/<int:task_id>")
@login_required
def delete_task(task_id):

    db.execute("DELETE FROM daily_progress WHERE task_id = ? AND user_id = ?", task_id, session["user_id"])
    db.execute("DELETE FROM planner WHERE task_id = ? AND user_id = ?", task_id, session["user_id"])
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])


    return redirect(url_for("tasks"))



@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))



# NOTE: I used ChatGPT as a helper during this project. All code and implementation decisions are my own.
