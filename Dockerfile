FROM node:12.13-alpine AS static-build
RUN apk --no-cache add \
    g++ make python
WORKDIR /opt/scaife-viewer/src/
COPY package.json package-lock.json ./
RUN npm ci
COPY webpack.config.js babel.config.js .eslintrc.json ./
COPY ./static static
COPY ./test test

ARG FORCE_SCRIPT_NAME
RUN npm run lint
RUN npm run unit
RUN npm run build

FROM python:3.8-alpine AS python-build
WORKDIR /opt/scaife-viewer/src/
RUN pip --no-cache-dir --disable-pip-version-check install virtualenv
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"
COPY requirements.txt /opt/scaife-viewer/src/
RUN set -x \
    && virtualenv /opt/scaife-viewer \
    && apk --no-cache add \
        build-base curl git libgcc libxml2-dev libxslt-dev postgresql-dev linux-headers python3-dev libffi-dev \
    && pip install -r requirements.txt
RUN pip install flake8 flake8-quotes isort PyGithub

FROM python:3.8-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/scaife-viewer/src/
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"

WORKDIR /opt/scaife-viewer/src/

COPY --from=python-build /opt/scaife-viewer/ /opt/scaife-viewer/
RUN set -x \
    && runDeps="$( \
        scanelf --needed --nobanner --format '%n#p' --recursive /opt/scaife-viewer \
            | tr ',' '\n' \
            | sort -u \
            | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' \
            | grep -v 'libgcc_s-' \
        )" \
    && apk --no-cache add \
        $runDeps \
        libgcc \
        curl

COPY . .

# static files must be copied after COPY . . — otherwise the latter command overwrites
# the Docker-built files with whatever exists from the last local build.
COPY --from=static-build /opt/scaife-viewer/src/static/dist /opt/scaife-viewer/src/static/dist
COPY --from=static-build /opt/scaife-viewer/src/static/stats /opt/scaife-viewer/src/static/stats

RUN flake8 sv_pdl
RUN isort -c **/*.py
RUN python manage.py collectstatic --noinput

ENV CTS_LOCAL_DATA_PATH=data/cts

RUN mkdir -p ${CTS_LOCAL_DATA_PATH}

RUN python manage.py loaddata sites
RUN python manage.py makemigrations
RUN python manage.py migrate sites
RUN python manage.py migrate

RUN python manage.py load_text_repos
RUN python manage.py slim_text_repos

RUN mkdir -p atlas_data
RUN python manage.py prepare_atlas_db --force

ENV SV_ELASTICSEARCH_HOST=localhost
ENV SV_ELASTICSEARCH_PORT=9200

RUN curl -O https://gist.githubusercontent.com/jacobwegner/68e538edf66539feb25786cc3c9cc6c6/raw/252e01a4c7e633b4663777a7e12dcb81119131e1/scaife-viewer-tmp.json
RUN curl -X PUT "http://${SV_ELASTICSEARCH_HOST}:${SV_ELASTICSEARCH_PORT}/_template/scaife-viewer?pretty" -H 'Content-Type: application/json' -d "$(cat scaife-viewer-tmp.json)"
RUN python manage.py indexer --max-workers=1 --limit=1000

RUN rm scaife-viewer-tmp.json

CMD ["gunicorn", "sv_pdl.wsgi:application"]