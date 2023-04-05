
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import sessions, Session
from werkzeug.security import check_password_hash
from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///healthManger.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/registerPatient", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        nic = request.form.get("nic")
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        age = request.form.get("age")
        gender = request.form.get("gender")
        blood = request.form.get("blood")
        email = request.form.get("email")
        contact_no = request.form.get("contact_no")
        adress = request.form.get("adress")
        fam_history = request.form.get("famhistory")
        current_medication = request.form.get("medihistory")
        allergies = request.form.get("allergy")
        drug_notice = request.form.get("drug")
        additional = request.form.get("adding")
        try:
            db.execute("INSERT INTO patientRegistration (NIC, fname, lname, age, gender, blood, email, "
                       "contact, adress, familyHealth, currentMedication, allergies, drugNotice, additional)"
                       " VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                       , nic, fname, lname, age, gender, blood, email, contact_no, adress, fam_history,
                       current_medication,
                       allergies, drug_notice, additional)

            flash("Record Successfully Saved!!")
            return render_template("regform.html")
        except Exception as e:
            return apology(f"{e}")

    else:
        return render_template("regform.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("userIdentity"):
            return apology("Please enter a username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Please enter a password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE nic = ?", request.form.get("userIdentity")
        )
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
                rows[0]["password_hash"], request.form.get("password")
        ):
            return apology("Invalid Username OR Password")

        role_chose = request.form.get("role")
        real_role = rows[0]["role"]
        if role_chose == real_role and role_chose == "other":
            # Remember which user has logged-in
            session["user_id"] = rows[0]["nic"]

            # Redirect user to home page
            return redirect("/registerPatient")
        elif role_chose == real_role:
            # Remember which user has logged-in
            session["user_id"] = rows[0]["nic"]
            return redirect("/dashboard")
        else:
            return apology("Invalid Role")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]

    doctor_details = db.execute("SELECT first_name, Last_name FROM users WHERE nic=?", user_id)
    doctor_name = {"fname": doctor_details[0]["first_name"], "lname": doctor_details[0]["Last_name"]}

    return render_template("inner-page.html", doctor_name=doctor_name)


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/viewPatient", methods=["GET", "POST"])
@login_required
def view_patient():
    if request.method == "GET":
        global patient_id
        patient_id = request.args.get("dbpatientID")
        if patient_id:
            row = db.execute("SELECT * FROM patientRegistration WHERE NIC=?", patient_id)
            if not row:
                return apology("Patient NIC not valid")
            else:
                notes = db.execute("SELECT date_time, note, patientRegistration.NIC, doctor_id,first_name FROM doctorsnote "
                                   "JOIN patientRegistration ON patientRegistration.NIC=doctorsnote.patient_id "
                                   "JOIN users ON users.nic=doctorsnote.doctor_id "
                                   "WHERE doctorsnote.patient_id=?  ORDER BY date_time DESC", patient_id)

                return render_template("viewPatient.html", row=row, notes=notes)
        else:
            return apology("Please enter a NIC")

@app.route("/add_note", methods=["GET", "POST"])
def noted():
    if request.method == "POST":
        if patient_id:
            doctor_id_ = session["user_id"]
            if request.form.get("doctorsnote"):
                notes = request.form.get("doctorsnote")
                date_time_ = datetime.datetime.now()
                try:
                    db.execute("INSERT INTO doctorsnote (patient_id, doctor_id, date_time, note) VALUES(?, ?, ?, ?)", patient_id, doctor_id_, date_time_, notes)
                except Exception as e:
                    apology(f"{e}")
                else:
                    flash("Your Note About Patient is Added.")
                    return redirect("/dashboard")
