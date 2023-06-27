ARG CTS_TARBALL_URL=https://storage.googleapis.com/sv-ogl-pdl-deployments/heroku-dev/2022/07/22/homer.tgz

FROM alpine
RUN apk add bash curl

WORKDIR /opt/scaife-viewer/src

COPY ./bin bin
ARG CTS_TARBALL_URL
RUN ./bin/fetch_cts_tarball.sh
