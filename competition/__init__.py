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
        events = request.form.getlist('events')
        print(events)
        print(first_name, last_name, team_id)
        con = db.get_db()

        ## form validation starts here
        # validate the name, if it's invalid return an error
        if not valid_name(first_name) or not valid_name(last_name):
            flash(
                f"Names are required, and can't be longer than {app.config['NAME_LIMIT']} characters and can't have special characters.",
                category="error"
            )
            return redirect(url_for("create_person"))
        
        # check that the team exists
        query = con.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
        if query.fetchone is None:
            flash("That team doesn't exist.", category="error")
            return redirect(url_for("create_person"))

        # check there are 5 or less events checked
        if len(events) >= 5 or len(events) == 0:
            flash("Please select between 1 and 5 events.", category="error")
            return redirect(url_for("create_person"))

        ## database modification starts here
        # add the person to the database
        query = con.execute(
            "INSERT INTO individuals (first_name, last_name, team_id) VALUES(?,?,?)",
            (first_name,last_name,team_id)
        )
        individual_id = query.lastrowid

        # add the person to each event
        for event in events:
            event = int(event)
            print("handling event id", event)
            query = con.execute(
                "INSERT INTO individual_entries (event_id,individual_id) VALUES (?,?)",
                (event, individual_id)
            )

        con.commit()
        return render_template("form/success.html", text=f"{first_name} {last_name}")

    @app.get("/person/create")
    def render_create_person():
        """Render the form for adding a person."""
        con = db.get_db()
        # get teams to choose from
        teams = con.execute("SELECT id, name FROM teams")
        # get events to choose from
        events = con.execute("SELECT id, name FROM events WHERE team_event = false")
        return render_template("form/person.html", teams=teams, events=events)

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
            flash(
                f"Team names can't be longer than {app.config['NAME_LIMIT']} characters and can't have special characters.",
                category="error"
            )
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
            return render_template("form/success.html", text=team_name)

    @app.get("/team/create")
    def render_create_team():
        con = db.get_db()
        # get team events to choose from
        events = con.execute("SELECT id, name FROM events WHERE team_event = true")
        return render_template("form/team.html", events=events)

    @app.post("/event/create")
    def create_event():
        name = request.form['name']
        # this should be 1 or 0, which gets converted
        event_type = bool(int(request.form['type']))
        category = request.form['category']
        con = db.get_db()
        query = con.execute(
            "INSERT INTO events (name, team_event, category) VALUES (?,?,?)",
            (name, event_type, category)
        )
        con.commit()
        return render_template("form/success.html", text=name)

    @app.get("/event/create")
    def render_create_event():
        """Return the form for adding an event."""
        con = db.get_db()
        query = con.execute("SELECT * FROM categories")
        categories = query.fetchall()
        return render_template("form/event.html", categories=categories)
        

    @app.get("/event/list")
    def list_events():
        """List the events."""
        con = db.get_db()
        # select all events and their categories
        query = con.execute("""
            SELECT events.id, events.name, events.team_event, categories.name AS type
            FROM events INNER JOIN categories
            ON categories.id = events.category
            GROUP BY events.id;
        """)
        events = query.fetchall()
        print([event['team_event'] == True for event in events])
        print(events)
        return render_template("form/event/list.html", events=events)

    @app.get("/event/view/<int:event_id>")
    def view_event(event_id):
        """View a specific event and who is participating in it."""
        con = db.get_db()
        # find the event, get its name, and determine if team or individual
        query = con.execute("SELECT name, team_event FROM events WHERE id = ?", (event_id,))
        results = query.fetchone()
        event_name = results['name']
        team_event = bool(int(results['team_event']))
        
        # if team, get info from team_entries
        if team_event:
            # select the id, name and place/points for the event
            query = con.execute("""
            SELECT team_id as id, name, score
            FROM team_entries INNER JOIN teams on team_id = teams.id
            WHERE event_id = ?
            GROUP BY team_id
            """, (event_id,))
            results = query.fetchall()
        # else, get info from individual_entries
        else:
            # select the id, name and place/points for the event
            query = con.execute("""
            SELECT individual_id as id, first_name || " " || last_name as name, score
            FROM individual_entries INNER JOIN individuals on individual_id = individuals.id
            WHERE event_id = ?
            GROUP BY individual_id
            """, (event_id,))
            results = query.fetchall()
            print(results)

        # render the final page 
        return render_template(
            "form/event/view.html",
            entries=results,
            event_name=event_name,
            event_id=event_id
        )

    @app.post("/event/update/<int:event_id>")
    def update_event(event_id):
        """
        Update a competitor's score for an event. The only parameters
        are `id` and `score`.
        """
        con = db.get_db()
        # determine if the event is team or individual
        query = con.execute("SELECT team_event FROM events WHERE id = ?", (event_id,))
        results = query.fetchone()
        team_event = bool(int(results['team_event']))
        
        # check request parameters
        competitor_id = int(request.form['id']) # team/person
        score = int(request.form['score']) # their score

        # decide what table to use
        if team_event:
            query = con.execute(
                "UPDATE team_entries SET score = ? WHERE event_id = ? AND team_id = ?",
                (score, event_id, competitor_id)
            )
        else:
            query = con.execute(
                "UPDATE individual_entries SET score = ? WHERE event_id = ? AND individual_id = ?",
                (score, event_id, competitor_id)
            )

        con.commit()
        flash("Updated score.", category="success")
        return redirect(url_for('view_event', event_id=event_id))


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
