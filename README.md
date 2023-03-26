# comeptition
an app written in flask to manage a competition.

## setup
```
# clone the project and enter the directory.
# make your venv
python3 -m venv venv
source venv/bin/activate

# create the config and generate a secret key
cp config.example.py instance/config.py
sed -i s/verysecretkey/`openssl rand -hex 30`/ instance/config.py

# create the DB (in instance/database.db)
flask --app competition init-db

# start the app (no production yet)
flask --debug --app competition run
```