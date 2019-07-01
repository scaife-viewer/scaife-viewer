FROM python:3.6-alpine3.7 AS build
WORKDIR /opt/scaife-viewer/src/
RUN pip --no-cache-dir --disable-pip-version-check install virtualenv
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"
COPY requirements-dev.txt requirements.txt /opt/scaife-viewer/src/
RUN set -x \
    && virtualenv /opt/scaife-viewer \
    && apk --no-cache add \
        build-base curl git libxml2-dev libxslt-dev postgresql-dev linux-headers \
    && pip install -r requirements-dev.txt

FROM python:3.6-alpine3.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH /opt/scaife-viewer/src/
ENV PATH="/opt/scaife-viewer/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-viewer"
WORKDIR /opt/scaife-viewer/src/
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
COPY . .
