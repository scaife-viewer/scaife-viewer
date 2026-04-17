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

# We need to uninstall and reinstall urllib3 manually
# to avoid conflicts
RUN pip uninstall -y urllib3
RUN pip install urllib3==1.26.15
# Likewise, we install PyGithub here to avoid conflicts
RUN pip install PyGithub
RUN apk add --update make automake gcc g++ subversion
RUN pip install numpy
RUN pip install pandas

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

# Pre-bake ingestion sentinels when data already exists in the build context.
# Sentinels live inside atlas_data/ so they travel with the data (volume or image layer)
# rather than being lost on every container restart. The entrypoint skips expensive
# re-ingestion steps when the corresponding sentinel is present.
RUN mkdir -p atlas_data/sentinels && \
    if [ -d data/cts ] && [ "$(ls -A data/cts 2>/dev/null)" ]; then \
    sha256sum data/content-manifests/production.yaml 2>/dev/null | cut -d' ' -f1 \
    > atlas_data/sentinels/.manifest_hash; \
    touch atlas_data/sentinels/.text_repos_loaded; \
    fi && \
    if [ -f atlas_data/atlas.sqlite ]; then \
    touch atlas_data/sentinels/.atlas_db_prepared; \
    fi

# bash is needed for some of the ingestion
# scripts
RUN apk --no-cache add bash

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "sv_pdl.wsgi:application"]
