FROM node:8.10-alpine AS static
WORKDIR /opt/scaife-viewer/src/
COPY package.json package-lock.json .babelrc .postcssrc.js ./
RUN npm install
COPY ./static static
RUN npm run build:prod

FROM python:3.6-alpine3.7 AS build
WORKDIR /opt/scaife-viewer/src/
RUN pip --no-cache-dir --disable-pip-version-check install pipenv
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"
COPY Pipfile Pipfile.lock /opt/scaife-viewer/src/
RUN set -x \
    && virtualenv /opt/scaife-viewer \
    && apk --no-cache add \
        build-base curl git libxml2-dev libxslt-dev postgresql-dev linux-headers \
    && pipenv install --deploy

FROM python:3.6-alpine3.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /opt/scaife-viewer/src/
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"
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
    && apk --no-cache add \
        $runDeps \
        curl
COPY . /opt/scaife-viewer/src/
RUN python manage.py collectstatic --noinput
