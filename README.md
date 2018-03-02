# Scaife Digital Library Viewer

## Getting Started

Requirements:

* Python 3.6
  * pipenv
* Node 8.6
* PostgreSQL 9.6

First, set up a database to use for local development:

    createdb scaife-viewer

This assumes your local PostgreSQL is configured to allow your user to create databases. If this is not the case you might be able to create the user yourself:

    createuser --username=postgres --superuser $(whoami)

Install the Node and Python dependencies:

    npm install
    pipenv install --dev

To run commands in the Python environment, you can use `pipenv shell` and carry on, but I find it has some nasty side-affects. So, to activate the pipenv environment in your current shell:

    source "$(pipenv --venv)/bin/activate"

Setup the database:

    python manage.py migrate
    python manage.py loaddata sites

Seed the text inventory to speed up local development:

    curl -s "https://scaife-cts-dev.eldarion.com/api/cts?request=GetCapabilities" > ti.xml

You should now be set to run the development server:

    npm run dev

Browse to http://localhost:3000/.

Note that, although running Scaife locally, this is relying on the Nautilus server at https://scaife-cts-dev.eldarion.com to retrieve texts.


## Translations

Before you work with translations, you will need gettext installed.

macOS:

    brew install gettext
    export PATH="$PATH:$(brew --prefix gettext)/bin"

To prepare messages:

    python manage.py makemessages --all

If you need to add a language; add it to `LANGUAGES` in settings.py and run:

    python manage.py makemessages --locale <lang>
