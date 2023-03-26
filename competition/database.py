# thank you flask documentation for all of this!
import sqlite3
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def init_db():
    db = get_db()
    with current_app.open_resource("schema.sqlite") as f:
        db.executescript(f.read().decode('utf8'))

# close database when application closes
def close_db(e=None):
    db = g.pop('db', None)
    if db != None:
        db.close()

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo("created database")

# called by __init__.py
def init_app(app):
    print("database module loaded")
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)