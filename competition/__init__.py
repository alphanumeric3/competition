import os
from random import randint
from flask import Flask, jsonify, request, flash, redirect, url_for, render_template, session
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
        name = name.replace(' ', '')
        return len(name) <= app.config['NAME_LIMIT'] and name.isalnum()

    @app.route("/")
    def homepage():
        return render_template("home.html")

    @app.post("/person/create")
    def create_person():
        """Add a person."""
        # capitalise the name
        print(request.form)
        first_name = request.form['first_name'].capitalize()
        last_name = request.form['last_name'].capitalize()
        team_id = request.form.get('team')
        print(first_name, last_name, team_id)
        con = db.get_db()
        # validate the name, if it's invalid return an error
        if not valid_name(first_name) or not valid_name(last_name):
            flash(f"Names are required, and can't be longer than {app.config['NAME_LIMIT']} characters.")
            return redirect(url_for("create_person"))
        
        # check that the team exists
        query = con.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
        if query.fetchone is None:
            flash("That team doesn't exist.")
            return redirect(url_for("create_person"))

        # add the person to the database
        query = con.execute(
            "INSERT INTO individuals (first_name, last_name, team_id) VALUES(?,?,?)",
            (first_name,last_name,team_id)
        )
        con.commit()
        return render_template("form/success/person.html", first_name=first_name, last_name=last_name)

    @app.get("/person/create")
    def render_create_person():
        """Render the form for adding a person."""
        con = db.get_db()
        query = con.execute("SELECT id, name FROM teams")
        return render_template("form/person.html", teams=query)

    @app.post("/team/create")
    def create_team():
        """
        Create a team.
        """
        team_name = request.form['team_name']
        con = db.get_db()
        # validate the team name
        print(team_name)
        name_limit = app.config['NAME_LIMIT']
        if not valid_team_name(team_name):
            flash(f"Team names can't be longer than {app.config['NAME_LIMIT']} characters and can't have special characters.")
            return redirect(url_for("create_team"))

        # query the DB to see if the name is taken
        query = con.execute("SELECT name FROM teams WHERE name = ?", (team_name,))
        if query.fetchone() is not None:
            flash("This team already exists.")
            return redirect(url_for("create_team"))

        else:
            # add the team
            query = con.execute("INSERT INTO teams (name) VALUES(?)", (team_name,))
            team_id = query.lastrowid # team's id
            print("team id", team_id)
            # add the competitor to the team
            # query = con.execute("UPDATE individuals SET team_id = ? WHERE id = ?", (team_id, person_id))
            con.commit()
            return render_template("form/success/team.html", team_name=team_name)

    @app.get("/team/create")
    def render_create_team():
        return render_template("form/team.html")

    @app.post("/event/create")
    def create_event():
        name = request.form['name']
        # this should be 1 or 0, which gets converted
        event_type = bool(request.form['type'])
        category = request.form['category']
        con = db.get_db()
        query = con.execute(
            "INSERT INTO events (name, team_event, category) VALUES (?,?,?)",
            (name,event_type,category)
        ) # TODO: FIX WORDING!!!
        con.commit()
        return "response"

    @app.get("/event/create") # TODO: TODO: TODO: TODO: THIS THIS THIS!!!!!!
    def render_create_event():
        con = db.get_db()
        query = con.execute("SELECT * FROM categories")
        categories = query.fetchall()
        return render_template("form/event.html", categories=categories)
        

    @app.get("/events")
    def list_events():
        """
        List the events.
        """
        con = db.get_db()
        # select the event id & event name from events and look up the event type name too 
        # (it will be the field `type`)
        query = con.execute("""
            SELECT events.id, events.name, events.team_event, event_category.name AS type
            FROM events INNER JOIN event_category
            GROUP BY events.id;
        """)
        events = query.fetchall()
        print([event['team_event'] == True for event in events])
        print(events)
        return render_template("form/event/list.html", events=events)

    @app.post("/events")
    def register_events():
        """
        Add the user to events based on the form from list_events().
        TODO: remove this, adding people to events should be under /person/<...>
        """
        con = db.get_db()
        if session.get("individual_id") and not session.get("team_creator"):
            for event in request.form:
                print(request.form[event])
                individual_id = int(session["individual_id"])
                event = int(event)
                data = (event, 0, individual_id)
                query = con.execute("""
                    INSERT INTO entries (event_id, entry_type, individual_id)
                    VALUES (?,?,?)
                """, data)
                con.commit()
            return "okie!"

    @app.get("/flashtest")
    def flashtest():
        flash("this is a flashed message")
        return redirect(url_for("create_person"))

    return app
