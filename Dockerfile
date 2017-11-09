FROM node:8.9-alpine AS static
WORKDIR /opt/scaife-viewer/src/
COPY package.json package-lock.json .babelrc webpack.config.js ./
RUN npm install
COPY ./static static
RUN npm run build:prod

FROM python:3.6-alpine3.6 AS build
WORKDIR /opt/scaife-viewer/src/
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"
RUN pip --no-cache-dir --disable-pip-version-check install --upgrade pip setuptools wheel pipenv
COPY Pipfile Pipfile.lock /opt/scaife-viewer/src/
RUN set -x \
    && python -m venv /opt/scaife-viewer \
    && apk --no-cache add \
        build-base curl git libxml2-dev libxslt-dev postgresql-dev \
    && pipenv install --deploy

FROM python:3.6-alpine3.6
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /opt/scaife-viewer/src/
ENV PATH="/opt/scaife-viewer/bin:${PATH}"
WORKDIR /opt/scaife-viewer/src/
COPY --from=static /opt/scaife-viewer/src/static/dist /opt/scaife-viewer/src/static/dist
COPY --from=build /opt/scaife-viewer/ /opt/scaife-viewer/
RUN set -x \
    && runDeps="$( \
        scanelf --needed --nobanner --format '%n#p' --recursive /opt/scaife-viewer \
            | tr ',' '\n' \
            | sort -u \
            | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' \
        )" \
    && apk --no-cache add $runDeps
COPY . /opt/scaife-viewer/src/
