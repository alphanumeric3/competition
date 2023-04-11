# comeptition
an app written in flask to manage a competition.

## setup
```shell
# clone the project and enter the directory.
# make your venv
python3 -m venv venv
source venv/bin/activate

# create the config and generate a secret key
cp config.example.py instance/config.py
sed -i s/verysecretkey/`openssl rand -hex 30`/ instance/config.py

# makes flask commands shorter
export FLASK_APP=competition

# create the DB (in instance/database.db)
flask init-db

# start the app (no production yet)
flask --debug run
```