ARG ARTIFACTS_DOCKER_IMAGE="docker.io/scaife-viewer/scaife-viewer-artifacts:latest"
ARG WEBAPP_DOCKER_IMAGE="docker.io/scaife-viewer/scaife-viewer/webapp-base:latest"

FROM $ARTIFACTS_DOCKER_IMAGE AS artifacts

FROM $WEBAPP_DOCKER_IMAGE as data-prep
WORKDIR /opt/scaife-viewer/src/
COPY --from=artifacts /opt/scaife-viewer/src/data data

RUN mkdir -p atlas_data
RUN apk add bash
RUN ./bin/fetch_corpus_config
RUN ./bin/copy_corpus_repo_metadata

RUN python manage.py prepare_atlas_db --force

# https://stackoverflow.com/a/54245466
# https://docs.docker.com/engine/reference/builder/#onbuild

FROM $WEBAPP_DOCKER_IMAGE as final
WORKDIR /opt/scaife-viewer/src/

COPY --from=data-prep /opt/scaife-viewer/src/data data
COPY --from=data-prep /opt/scaife-viewer/src/atlas_data atlas_data
COPY --from=data-prep /opt/scaife-viewer/src/cts_resolver_cache cts_resolver_cache

