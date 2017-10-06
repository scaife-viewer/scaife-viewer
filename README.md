# Scaife Digital Library Viewer

## Getting Started

Requirements:

* Python 3.6
  * pipenv
* Node 8.6
* PostgreSQL 9.6

To setup the project for local development:

```
createdb scaife-viewer
npm install
pipenv install --dev
```

To run commands in the Python environment, you can use `pipenv shell` and carry on, but I find it has some nasty side-affects. So, to activate the pipenv environment in your current shell:

```
source "$(pipenv --venv)/bin/activate"
```

Setup the database:

```
python manage.py migrate
python manage.py loaddata sites
```

You should now be set to run the development server:

```
npm run dev
```

Browse to http://localhost:3000/.
