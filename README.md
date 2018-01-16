# Scaife Viewer

The new reading environment for version 5.0 of the Perseus Digital Library.

The Scaife Viewer is the new reading environment for the Perseus Digital Library.

See [Ways to Contribute](https://github.com/scaife-viewer/scaife-viewer/wiki/Ways-to-Contribute).

## Getting Started

Requirements:

* Python 3.6.x
  * pipenv
* Node 10.7
* PostgreSQL 9.6
* Elasticsearch 6

First, set up a database to use for local development:

    createdb scaife-viewer

This assumes your local PostgreSQL is configured to allow your user to create databases. If this is not the case you might be able to create the user yourself:

    createuser --username=postgres --superuser $(whoami)

Install the Node and Python dependencies:

    npm install
    pipenv install --dev

Setup the database:

    pipenv run python manage.py migrate
    pipenv run python manage.py loaddata sites

Seed the text inventory, for the library view, to speed up local development:

    curl -s "https://scaife-cts-dev.perseus.org/api/cts?request=GetCapabilities" > ti.xml

Note that, this only grabs the title and name of the text, not the actual passage. For example:

```xml
<work urn="urn:cts:greekLit:tlg0062.tlg006" xml:lang="grc" groupUrn="urn:cts:greekLit:tlg0062">
  <title xml:lang="lat">Muscae encomium</title>
    <edition urn="urn:cts:greekLit:tlg0062.tlg006.1st1K-grc1" xml:lang="grc" workUrn="urn:cts:greekLit:tlg0062.tlg006">
    <label xml:lang="eng">The Fly</label>
    <description xml:lang="eng">Lucian of Samosata, The Fly, Lucian vol. 1, Harmon, Harvard, 1961</description>
    <online>
      <citationMapping>
        <citation xpath="/tei:div[@n='?']" scope="/tei:TEI/tei:text/tei:body/tei:div" label="section"></citation>
      </citationMapping>
    </online>
  </edition>
</work>
```

You should now be set to run the static build pipeline and hot module reloading:

    npm start

In another terminal, start runserver:

    pipenv run python manage.py runserver

Browse to http://localhost:8000/.

Note that, although running Scaife locally, this is relying on the Nautilus server at https://scaife-cts-dev.perseus.org to retrieve texts.


## Translations

Before you work with translations, you will need gettext installed.

macOS:

    brew install gettext
    export PATH="$PATH:$(brew --prefix gettext)/bin"

To prepare messages:

    python manage.py makemessages --all

If you need to add a language; add it to `LANGUAGES` in settings.py and run:

    python manage.py makemessages --locale <lang>


## Hosting Off-Root

If you need to host at a place other than root, for example, if you need to have
a proxy serve at some path off your domain like http://yourdomain.com/perseus/,
you'll need to do the following:

1. Set the environment variable, `FORCE_SCRIPT_NAME` to point to your script:

```
    export FORCE_SCRIPT_NAME=/perseus  # this front slash is important
```

2. Make sure this is set prior to runing `npm run build` as well as prior to and
   part of your wsgi startup environment.

3. Then, you just set your proxy to point to the location of where your wsgi
   server is running.  For example, if you are running wsgi on port 8000 you can
   have this snippet inside your nginx config for the server:

```
    location /perseus/ {
        proxy_pass        http://localhost:8000/;
    }
```

That should be all you need to do.

## Docker

Built with Docker Engine v18.09.2.

Run:

    docker-compose -f docker-compose-dev.yml up -d --build
    npm install
    npm start
