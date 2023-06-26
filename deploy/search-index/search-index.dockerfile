ARG WEBAPP_DEPLOY_DOCKER_IMAGE="docker.io/scaife-viewer/scaife-viewer/webapp-deploy:latest"
FROM $WEBAPP_DEPLOY_DOCKER_IMAGE as data-prep

ARG ANNOTATIONS_TARBALL="https://github.com/scaife-viewer/ogl-pdl-annotations/tarball/main"
RUN mkdir -p /opt/scaife-viewer/src/data/search-annotations
WORKDIR /opt/scaife-viewer/src/data/search-annotations
# TODO: Pipe this
RUN curl -L $ANNOTATIONS_TARBALL -o archive.tgz && \
    tar -xf archive.tgz --strip-components=1 && \
    rm archive.tgz

WORKDIR /opt/scaife-viewer/src/
ENV LEMMA_CONTENT=1
ENV TOKEN_ANNOTATIONS_PATH=/opt/scaife-viewer/src/data/search-annotations/data/token-annotations
