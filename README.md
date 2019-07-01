# Scaife Viewer

The new reading environment for version 5.0 of the Perseus Digital Library.

The Scaife Viewer is the new reading environment for the Perseus Digital Library.

See [Ways to Contribute](https://github.com/scaife-viewer/scaife-viewer/wiki/Ways-to-Contribute).

## Getting Started with Local Development

Requirements:

* Python 3.6.x
* Node 11.7
* PostgreSQL 9.6
* Elasticsearch 6

First, install and run Elasticsearch on port 9200. If you're on a Mac, we recommend using brew for this:

    brew install elasticsearch
    brew services start elasticsearch

Then, set up a postgres database to use for local development:

    createdb scaife-viewer

This assumes your local PostgreSQL is configured to allow your user to create databases. If this is not the case you might be able to create the user yourself:

    createuser --username=postgres --superuser $(whoami)

Create a virtual environment. Then, install the Node and Python dependencies:

    npm install
    pip install -r requirements-dev.txt

Set up the database:

    python manage.py migrate
    python manage.py loaddata sites

Seed the text inventory to speed up local development:

    curl -s "https://scaife-cts-dev.perseus.org/api/cts?request=GetCapabilities" > ti.xml

You should now be set to run the static build pipeline and hot module reloading:

    npm start

In another terminal, collect the static files and then start runserver:

    python manage.py collectstatic --noinput
    python manage.py runserver

Browse to http://localhost:8000/.

Note that, although running Scaife locally, this is relying on the Nautilus server at https://scaife-cts-dev.perseus.org to retrieve texts.

## Tests

You can run the Vue unit tests, via:

    npm run unit

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

2. Make sure this is set prior to running `npm run build` as well as prior to and
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


## Deploying via Docker

A sample docker-compose configuration is available at `deploy/docker-compose.yml`.

Copy `.env.example` and customize environment variables for your deployment:

```
cp deploy/.env.example deploy/.env
```

To build the Docker image and bring up the `scaife-viewer`, `sv-postgres` and `sv-elasticsearch` services in the background:

```
docker-compose -f deploy/docker-compose.yml up --build -d
```

Tail logs via:

```
docker-compose -f deploy/docker-compose.yml logs --follow
```

To host the application off-root using docker-compose, you'll need to ensure that the `scaife-viewer` Docker image is built with the `FORCE_SCRIPT_NAME` build arg:

```
docker-compose -f deploy/docker-compose.yml build --build-arg FORCE_SCRIPT_NAME=/<your-off-root-path>
```

You'll also need to ensure that `FORCE_SCRIPT_NAME` exists in `deploy/.env`:

```
echo "FORCE_SCRIPT_NAME=/<your-off-root-path>" >> deploy/.env
```

Then, bring up all services:

```
docker-compose -f deploy/docker-compose.yml up -d
```

## Using Docker for development

The project also includes `Dockerfile-dev` and `Dockerfile-webpack` images which can be used with Docker Compose to facilitate development.

First, copy `.env.example` and customize environment variables for development:

```
cp deploy/.env.example deploy/.env
```

Then build the images and spin up the containers:

```
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up --build
```

To run only the `scaife-viewer`, `sv-webpack`, and `sv-postgres` services, set the `USE_ELASTICSEARCH_SERVICE` environment variable in `docker-compose.override.yml` to 0, and then run:

```
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml up --build scaife-viewer sv-webpack sv-postgres
```

To run the simple_indexer command:

```
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.override.yml exec scaife-viewer python manage.py simple_indexer
```


## API Library Cache

The client-side currently caches the results of `library/json/`. The cache is automatically invalidated every 24 hours. You can manually invalidate it by bumping the `LIBRARY_VIEW_API_VERSION` environment variable.
