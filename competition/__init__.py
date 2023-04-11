import os
from random import randint
from flask import Flask, jsonify, request, flash, redirect, url_for, render_template
from . import database as db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # get the config, if it doesn't exist exit
    try:
        app.config.from_pyfile("config.py")
        app.config.update(
            DATABASE=os.path.join(app.instance_path, 'database.db')
        )
    except FileNotFoundError:
        print(f"config.py not found. create it in {app.instance_path}")
        exit(1)
    except Exception as e:
        print("an error occurred:", e)

    # let database.py set up any hooks
    db.init_app(app)

    def valid_name(name):
        return len(name) <= app.config['NAME_LIMIT'] and name.isalpha()

    def valid_team_name(name):
        return len(name) <= app.config['NAME_LIMIT'] and name.isalnum()

    @app.route("/")
    def homepage():
        return render_template("home.html")

    @app.post("/form/person")
    def form_person():
        """Handle the individual signup form and add people to the database."""
        first_name = request.form['first_name'].capitalize()
        last_name = request.form['last_name'].capitalize()
        team_code = request.form.get('team_code')
        team_id = None # used later in the query, stays None if no code given
        team_name = None # used in the person_success template if a team is joined
        con = db.get_db()

        print(first_name, last_name, type(team_code))

        # check name length
        if not valid_name(first_name) or not valid_name(last_name):
            flash(f"Names can't be longer than {app.config['NAME_LIMIT']} characters.")
            return redirect(url_for("form_person"))

        # if team code given, validate it
        if team_code == "":
            pass
        elif team_code.isnumeric() and len(team_code) == 6:
            team_code = int(team_code)
            # lookup team by the code given
            query = con.execute("SELECT name, id FROM teams WHERE code = ?", (team_code,))
            result = query.fetchone()
            if result is None: # if nonexistent team given, show an error
                flash("Team does not exist.")
                return redirect(url_for("form_person"))
            else: # if team exists, take id and name
                team_id = result['id']
                team_name = result['name']
                print(team_id, team_name)
        else: # if it's not a 6 digit code, show an error
            flash("Invalid team code. It should be 6 digits.")
            return redirect(url_for("form_person"))
            
        # add the competitor to the database
        query = con.execute("INSERT INTO individuals (first_name, last_name, team_id) VALUES(?,?,?)", (first_name,last_name,team_id))
        con.commit()
        return render_template("form/success/person.html", team_name=team_name, team_code=team_code, first_name=first_name)

    @app.get("/form/person")
    def render_form_person():
        return render_template("form/person.html")

    @app.post("/form/team")
    def form_team():
        """Handle the team signup form and add the team and its owner to the database."""
        # names should be capitalised
        first_name = request.form['first_name'].capitalize()
        last_name = request.form['last_name'].capitalize()
        team_name = request.form['team_name']
        con = db.get_db()

        print(first_name, last_name, team_name)

        # validate the names
        name_limit = app.config['NAME_LIMIT']
        if not valid_name(first_name) or not valid_name(last_name) or not valid_team_name(team_name):
            flash(f"Names can't be longer than {app.config['NAME_LIMIT']} characters, and can only have letters. Team names can have numbers.")
            return redirect(url_for("form_team"))

        # query the DB to see if the name is taken
        query = con.execute("SELECT * FROM teams WHERE name = ?", (team_name,))
        if query.fetchone() is not None:
            flash("This team already exists.")
            return redirect(url_for("form_team"))
        else:
            # generate a 6 digit code for others to join
            team_code = randint(100000, 999999)
            # add the competitor first
            query = con.execute("INSERT INTO individuals (first_name, last_name) VALUES(?,?)", (first_name, last_name))
            teamcreator = query.lastrowid # this is the competitor's id
            print("team creator id", teamcreator)
            # add the team next
            query = con.execute("INSERT INTO teams (name, creator, code) VALUES(?,?,?)", (team_name, teamcreator, team_code))
            team_id = query.lastrowid # team's id
            print("team id", team_id)
            # add the competitor to the team
            query = con.execute("UPDATE individuals SET team_id = ? WHERE id = ?", (team_id, teamcreator))
            con.commit()
            return render_template("form/success/team.html", team_name=team_name, team_code=team_code, first_name=first_name)

    @app.get("/form/team")
    def render_form_team():
        return render_template("form/team.html")

    @app.get("/events")
    def list_events():
        """TODO: make this a form lol"""
        con = db.get_db()
        # select the event id & event name from events and look up the event type name too (it will be the field `type`)
        query = con.execute("""
            SELECT events.id, events.name, events.team_event, event_type.name AS type
            FROM events INNER JOIN event_type
            GROUP BY events.id;
        """)
        events = query.fetchall()
        print([event['team_event'] == True for event in events])
        print(events)
        return render_template("form/event/list.html", events=events)


    @app.get("/flashtest")
    def flashtest():
        flash("this is a flashed message")
        return redirect(url_for("form_person"))

    return app
