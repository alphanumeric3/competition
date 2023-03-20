import os
import time
from random import randint
from flask import Flask, jsonify, request, render_template

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    try:
        app.config.from_pyfile("config.py")
    except:
        app.config.from_mapping(
            DATABASE=os.path.join(app.instance_path, "database.db"),
            NAME_LIMIT=20
        )

    @app.post("/form/person")
    def form_person():
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        teamcode = request.form.get('teamcode')

        print(firstname, lastname, teamcode)

        # check name length
        if len(firstname) <= app.config['NAME_LIMIT'] and len(lastname) <= app.config['NAME_LIMIT']:
            pass
        else:
            return f"something is too long, the limit is {app.config['NAME_LIMIT']} characters\n", 400

        # check if there is a team involved
        # for future reference: this conditional block shouldn't end the
        # request in the final version UNLESS the code is invalid or nonexistent
        # if we look up the team and it exists, we add it to the sqlite tuple
        # thing and let the rest of the function execute
        if teamcode == None: # there is no team code
            print("no team code, not checking")
        # TODO: is this foolproof?
        elif teamcode.isnumeric() and len(teamcode) == 6:
            print("checking team code")
            teamcode = int(teamcode)
        else: # if it doesn't fit 6 digit code format
            return "that's not a valid team code\n", 400
            
        # continue processing
        print("user is joining a team")
        return f"welcome. you are in a team ({teamcode != None})\n"

    @app.get("/form/person")
    def render_form_person():
        # this function will render the form template. um... TODO.
        pass

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
        else:
            return f"something is too long, the limit is {app.config['NAME_LIMIT']} characters", 400

        # query the DB to see if the name is taken
        # x = db.fetchone() or something
        name_taken = ...
        if name_taken:
            return "the team name is already in use", 400
        else:
            # insert the team into the db, including a 6 digit code
            # add_competitor_stuff()
            # add_team_stuff(reference the competitor in the query)
            return "hooray you are now a team leader. code 123456"

    return app
