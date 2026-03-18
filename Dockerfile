FROM node:12.13-alpine AS static-build
WORKDIR /opt/scaife-viewer/src/
RUN apk add python2 make g++
RUN ln -sf python2 /usr/bin/python
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

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /opt/scaife-viewer/src/
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"

WORKDIR /opt/scaife-viewer/src/
COPY --from=static-build /opt/scaife-viewer/src/static /opt/scaife-viewer/src/static
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
RUN flake8 sv_pdl
RUN isort -c **/*.py

ENTRYPOINT ["entrypoint.sh"]

CMD ["gunicorn", "sv_pdl.wsgi:application"]