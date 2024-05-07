import string

from cs50 import SQL
from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from math import ceil
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import lookup, login_required, lookup_by_id, update_table

app = Flask(__name__)

# From Finance pset, confiugre session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///plants.db")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Check if username given and unique
        username = request.form.get("registerUsername")
        if not username:
            return render_template("error.html", error="Username required.")
        elif username in [
            row["username"] for row in db.execute("SELECT username FROM users;")
        ]:
            return render_template("error.html", error="Username unavailable.")

        # Check if password exists and matches confirmation password
        password = request.form.get("registerPassword")
        confirmation = request.form.get("registerPasswordConfirm")
        if not password and not confirmation:
            return render_template("error.html", error="Password fields required.")
        elif password != confirmation:
            return render_template("error.html", error="Passwords do not match.")

        # Check if password is long enough
        if len(password) <= 8:
            return render_template(
                "error.html", error="Password must be at least 8 characters."
            )

        # Check if password contains one of following using string attributes
        password_checks = [
            {
                "criteria": string.ascii_lowercase,
                "error message": "Password missing lowercase letter.",
            },
            {
                "criteria": string.ascii_uppercase,
                "error message": "Passwords missing uppercase letter.",
            },
            {"criteria": string.digits, "error message": "Password missing digit."},
            {
                "criteria": string.punctuation,
                "error message": "Password missing symbol.",
            },
        ]

        for check in password_checks:
            for char in password:
                if char in check["criteria"]:
                    break
            else:
                return render_template("error.html", error=check["error message"])

        # Update database
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?);",
            username,
            generate_password_hash(password),
        )

        flash("Registration successful! Login to begin journaling!")
        return redirect("/")
    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    session.clear()

    # makes sure both fields were given
    if not request.form.get("username"):
        return render_template("error.html", error="Username required.")
    elif not request.form.get("password"):
        return render_template("error.html", error="Password required.")

    # validates username and password
    rows = db.execute(
        "SELECT * FROM users WHERE username = ?", request.form.get("username")
    )

    if len(rows) != 1 or not check_password_hash(
        rows[0]["hash"], request.form.get("password")
    ):
        return render_template("error.html", error="Invalid username and/or password.")

    # Remembers which user is logged into session
    session["user_id"] = rows[0]["id"]

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    """Retreives user's inventory and displays each plant with date of latest update"""

    # Return with default values if not logged in
    user_id = session.get("user_id")
    if not user_id:
        return render_template(
            "index.html", inventory=None, latest_updates=None, username=None
        )

    # Get username for author section
    username = db.execute("SELECT username FROM users WHERE id=?;", user_id)[0][
        "username"
    ]

    # Get that user's info from database
    user_plant_inventory = db.execute(
        "SELECT * FROM intake_details WHERE owner_id=?;", user_id
    )
    latest_updates = {}

    if not user_plant_inventory:
        inventory = None
        latest_dates = None
    else:
        inventory = user_plant_inventory
        for plant in user_plant_inventory:
            plant_alias = plant["alias"]
            # get the datetime of latest update for each plant
            latest_update = db.execute(
                "SELECT entry_date FROM event_history WHERE owner_id=? AND plant_alias= ? ORDER BY entry_date DESC LIMIT 1;",
                user_id,
                plant_alias,
            )[0]["entry_date"]

            # convert to datetime for date arithmetic
            latest_update = datetime.strptime(latest_update, "%Y-%m-%d %H:%M:%S")
            now_datetime = datetime.today()
            time_delta = now_datetime - latest_update

            # check if latest_update was in the past
            if time_delta.microseconds < 0:
                raise ValueError ("Timestamp later than current datetime.")

            # convert the date arithmetic to strings
            if time_delta < timedelta(days=1):
                latest_updates[plant_alias] = "Last updated today"
            elif timedelta(days=30) > time_delta > timedelta(days=1):
                latest_updates[plant_alias] = f"Last updated {time_delta.days} days ago"
            elif timedelta(days=365) >= time_delta >= timedelta(days=30):
                latest_updates[
                    plant_alias
                ] = f"Last updated {time_delta.days // 30} month/s ago"
            else:
                latest_updates[
                    plant_alias
                ] = f"Last updated {time_delta.days // 365} year/s ago"

    return render_template(
        "index.html",
        inventory=inventory,
        latest_updates=latest_updates,
        username=username,
    )


@app.route("/add-plant", methods=["GET", "POST"])
@login_required
def add_plant():
    if request.method == "POST":
        """Adds a plant to the database"""

        # Get and populate intake_data dict
        intake_data = {}
        user_id = session.get("user_id")
        intake_data["owner_id"] = user_id

        # Check that api_id given and exists in api
        api_id = request.form.get("api_id")
        if not api_id:
            return render_template("error.html", error="Plant API ID missing.")

        plant_info = lookup_by_id(api_id)
        if not (plant_info):
            return render_template("error.html", error="Invalid Plant ID.")

        latin_name = plant_info["Latin name"]

        # Get the rest of data from form
        components = [
            "alias",
            "date_acquired",
            "acquire_method",
            "acquire_from",
            "notes",
        ]
        for component in components:
            result = request.form.get(component)
            if result:
                intake_data[component] = result
            else:
                intake_data[component] = None

        # Verify all necessary data was entered into form
        if not intake_data["date_acquired"]:
            return render_template("error.html", error="Event date missing.")
        if not intake_data["alias"]:
            return render_template("error.html", error="Alias missing.")

        # check if alias is unique in user's inventory
        used_aliases = db.execute(
            "SELECT alias FROM intake_details WHERE owner_id=?;", user_id
        )
        if used_aliases and intake_data["alias"] in [
            alias["alias"] for alias in used_aliases
        ]:
            return render_template(
                "error.html", error="Alias must be unique in your plant inventory!"
            )

        # check if plant_id is valid and adds if it is new to database
        if lookup_by_id(api_id) is None:
            return render_template("error.html", error="Plant ID invalid")
        elif api_id in [
            row["api_id"] for row in db.execute("SELECT api_id FROM plants;")
        ]:
            pass  # plant_id not unique in table
        else:
            db.execute(
                "INSERT INTO plants (latin_name, api_id) VALUES (?, ?);",
                latin_name,
                api_id,
            )

        # Get and insert plant_id foreign key
        plant_id = db.execute("SELECT id FROM plants WHERE api_id = ?", api_id)[0]["id"]
        intake_data["plant_id"] = plant_id

        # update the intake_details table
        update_table(db, intake_data, "intake_details")

        # update the event_history table with acquire event
        event_data = {
            "owner_id": user_id,
            "plant_alias": intake_data["alias"],
            "event_type": 1,
            "event_date": intake_data["date_acquired"],
            "additional_details": [],
        }

        # If additional optional info entered, put them into additional_details in an ordered way
        additional_details = [
            {
                "optional input field": "acquire_method",
                "prepend string": "Acquired:",
            },
            {
                "optional input field": "acquire_from",
                "prepend string": "From:",
            },
            {
                "optional input field": "notes",
                "prepend string": "Notes:",
            },
        ]

        for additional_detail in additional_details:
            optional_input = additional_detail["optional input field"]
            prepend_string = additional_detail["prepend string"]
            if intake_data[optional_input]:
                event_data["additional_details"].append(
                    f"{prepend_string} {intake_data[optional_input]}"
                )

        # join the strings into one for writing to database
        if event_data["additional_details"]:
            event_data["additional_details"] = " | ".join(
                event_data["additional_details"]
            )

        update_table(db, event_data, "event_history")
        return redirect("/")
    return redirect("/lookup")


@app.route("/lookup", methods=["GET"])
@login_required
def look_up():
    return render_template("lookup.html")


@app.route("/search-results", methods=["GET"])
@login_required
def results():
    # Verify search terms were given
    search_terms = request.args.get("name")
    if not search_terms:
        return redirect("/lookup")

    # Verify page is given and a number, else default of first page
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    info = lookup(search_terms)

    # Set page and pages to none if nothing returned from api query
    if not info:
        page = None
        pages = None
        number_of_results = 0
    else:
        number_of_results = len(info)
        pages = ceil(len(info) / 10)

        # check if page is out of range
        if page not in range(1, pages + 1):
            return render_template("error.html", error="404 page not found")

        # divide up info to only 10 search result per page
        start_range = (page - 1) * 10
        end_range = start_range + 10
        info = info[start_range:end_range]

    return render_template(
        "add-plant.html",
        info=info,
        pages=pages,
        page=page,
        search_terms=search_terms,
        number_of_results=number_of_results,
    )


@app.route("/plant-page/<plant_alias>", methods=["GET"])
@login_required
def plant_page(plant_alias):
    """Gets information about user_id + plant_alias from database"""

    user_id = session.get("user_id")
    plant_info = db.execute(
        "SELECT * FROM intake_details WHERE owner_id = ? AND alias = ?;",
        user_id,
        plant_alias,
    )[0]
    latin_name = db.execute(
        "SELECT latin_name FROM plants JOIN intake_details ON plants.id = intake_details.plant_id WHERE intake_details.owner_id = ? AND intake_details.alias=?;",
        user_id,
        plant_alias,
    )[0]["latin_name"]

    journal_entries = db.execute(
        "SELECT * FROM event_history WHERE owner_id = ? AND plant_alias = ?;",
        user_id,
        plant_alias,
    )

    # Splits the strings from additional_details
    for entry in journal_entries:
        if entry["additional_details"]:
            entry["additional_details"] = entry["additional_details"].split(" | ")

    # Dict for event_type, its emoji, and name of event_type
    event_strings = {
        1: ["&#128035", "Acquired"],
        2: ["&#x1f4a7;", "Watered"],
        3: ["&#x1F331;", "Fertilized"],
        4: ["&#128030", "Treatment"],
        5: ["&#x1F3FA;", "Repotted"],
        6: ["&#128128;", "Death"],
    }
    return render_template(
        "plant-page.html",
        event_strings=event_strings,
        plant_info=plant_info,
        journal_entries=journal_entries,
        latin_name=latin_name,
    )


@app.route("/add-journal-entry", methods=["POST"])
@login_required
def add_event():
    """Lets user add new journal entry/event in database"""

    event_info = {}
    user_id = session.get("user_id")
    event_info["owner_id"] = user_id
    event_type = request.form.get("event_type")

    # Checks if event_type is valid and returns if true
    if not event_type:
        return render_template("error.html", error="Event type missing.")
    elif int(event_type) not in [
        type["id"] for type in db.execute("SELECT id FROM event_type")
    ]:
        return render_template("error.html", error="Bad event type!")
    else:
        event_info["event_type"] = int(event_type)

    # validate plant_alias was given and valid for that user
    plant_alias = request.form.get("plant_alias")
    if not plant_alias:
        return render_template("error.html", error="Missing plant alias.")

    valid_aliases = db.execute(
        "SELECT alias FROM intake_details WHERE owner_id=?;", user_id
    )
    if valid_aliases and plant_alias in [alias["alias"] for alias in valid_aliases]:
        event_info["plant_alias"] = plant_alias
    else:
        return render_template(
            "error.html", error="Plant alias doesn't exist in your journal."
        )

    # validate event_date was given
    event_date = request.form.get("event_date")
    if not event_date:
        return render_template("error.html", error="Event date missing.")
    else:
        event_info["event_date"] = event_date

    additional_details = request.form.get("notes")
    if additional_details:
        event_info["additional_details"] = f"Notes: {additional_details}"

    update_table(db, event_info, "event_history")

    # Refreshes the page or default of index if no return page found
    return redirect(request.referrer or "/")
