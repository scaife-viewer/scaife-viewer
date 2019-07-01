FROM node:11.7-alpine AS static-build
WORKDIR /opt/scaife-viewer/src/
COPY package.json package-lock.json ./
RUN npm ci
COPY webpack.config.js .babelrc .eslintrc.json ./
COPY ./static static
COPY ./test test
ARG FORCE_SCRIPT_NAME
RUN npm run lint
RUN npm run unit
RUN npm run build

FROM python:3.6-alpine3.7 AS python-build
WORKDIR /opt/scaife-viewer/src/
RUN pip --no-cache-dir --disable-pip-version-check install virtualenv
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"
COPY requirements.txt /opt/scaife-viewer/src/
RUN set -x \
    && virtualenv /opt/scaife-viewer \
    && apk --no-cache add \
        build-base curl git libxml2-dev libxslt-dev postgresql-dev linux-headers \
    && pip install -r requirements.txt
RUN pip install flake8 flake8-quotes isort

FROM python:3.6-alpine3.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /opt/scaife-viewer/src/
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"
ENV SECRET_KEY="foo"
WORKDIR /opt/scaife-viewer/src/
COPY --from=static-build /opt/scaife-viewer/src/static/dist /opt/scaife-viewer/src/static/dist
COPY --from=python-build /opt/scaife-viewer/ /opt/scaife-viewer/
RUN set -x \
    && runDeps="$( \
        scanelf --needed --nobanner --format '%n#p' --recursive /opt/scaife-viewer \
            | tr ',' '\n' \
            | sort -u \
            | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' \
        )" \
    && apk --no-cache add \
        $runDeps \
        curl
COPY . .
RUN flake8 scaife_viewer
RUN isort -c **/*.py
RUN python manage.py collectstatic --noinput
