# competition
an app written in flask to manage a competition.

## info 
I wrote this web application for my course. We weren't required to use Python or Git, I just
didn't think Microsoft Access was right for me.

It uses Flask, Jinja2 templates and an SQLite3 database.

'competition' isn't incredibly secure, you would need HTTP Basic Authentication to protect it.

## setup
you will need a linux installation with python and flask.
(if you are on windows, use `setup.sh` to set it up by hand)
```shell
./setup.sh
```

## navigating the project
everything important is in the `competition` directory:
- static: static files like the CSS
- templates: Jinja2 templates
  - `home.html`: the homepage
  - `base.html`: every template uses this
  - `form/event/`: event-related pages. they're not really forms, i'll move them soon. 
  - `success.html`: when a form has no errors, this is used

and there are other files at the top level:
- `__init__.py` handles all web requests
- `database.py` is used by `__init__.py` to access the database. 
it closes the database after each web request finishes, and also handles the CLI command `init-db`.
- `schema.sqlite` is the database schema
