import os
from random import randint
from flask import Flask, jsonify, request, flash, redirect, url_for, render_template

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    try:
        app.config.from_pyfile("config.py")
        app.config.update(
            DATABASE=os.path.join(app.instance_path, 'database.db')
        )
    except Exception as e:
        print("where is the config?", e)
        exit(1)

    # app.secret_key = app.config['SECRET_KEY']

    @app.route("/")
    def homepage():
        return app.send_static_file("index.html")
    
    @app.post("/form/person")
    def form_person():
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        teamcode = request.form.get('teamcode')

        print(firstname, lastname, type(teamcode))

        # check name length
        if len(firstname) <= app.config['NAME_LIMIT'] and len(lastname) <= app.config['NAME_LIMIT']:
            pass
        else: # if any name is too long, show an error
            flash(f"The limit for names is {app.config['NAME_LIMIT']} characters.")
            return redirect(url_for("form_person"))

        # check if there is a team involved
        # for future reference: this conditional block shouldn't end the
        # request in the final version UNLESS the code is invalid or nonexistent.
        # if we look up the team and it exists, we add it to the sqlite tuple
        # thing and let the rest of the function execute
        if teamcode == "": # there is no team code
            print("no team code, not checking")
        # TODO: is this foolproof?
        elif teamcode.isnumeric() and len(teamcode) == 6:
            print("checking team code")
            teamcode = int(teamcode)
        else: # if it's not a 6 digit code, show an error
            flash("Invalid team code. It should be 6 digits.")
            return redirect(url_for("form_person"))
            
        # continue processing
        print("user is joining a team")
        return f"welcome. are you in a team?: ({teamcode != ''})\n"

    @app.get("/form/person")
    def render_form_person():
        return render_template("form/person.html")

    @app.post("/form/team")
    def form_team():
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        teamname = request.form['teamname']

        print(firstname, lastname, teamname)

        # validate the names
        # this conditional looks unwieldy to me, can i make it more concise?
        if len(firstname) <= app.config['NAME_LIMIT'] and len(lastname) <= app.config['NAME_LIMIT'] and len(teamname) <= app.config['NAME_LIMIT']:
            pass
        else: # if any name is too long, show an error
            flash(f"The limit for names is {app.config['NAME_LIMIT']} characters.")
            return redirect(url_for("form_team"))

        # query the DB to see if the name is taken
        # x = db.fetchone() or something
        name_taken = ...
        if name_taken:
            flash("this team already exists")
            return redirect(url_for("form_team"))
        else:
            # insert the team into the db, including a 6 digit code
            # add_competitor_stuff()
            # add_team_stuff(reference the competitor in the query)
            return "hooray you are now a team leader. code 123456"

    @app.get("/form/team")
    def render_form_team():
        return render_template("form/team.html")

    @app.get("/flashtest")
    def flashtest():
        flash("this is a flashed message")
        return redirect(url_for("form_person"))
        
    return app
