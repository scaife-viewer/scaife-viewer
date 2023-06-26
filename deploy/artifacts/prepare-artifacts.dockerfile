ARG WEBAPP_DOCKER_IMAGE="docker.io/scaife-viewer/scaife-viewer/webapp-base:latest"

FROM $WEBAPP_DOCKER_IMAGE as artifacts
WORKDIR /opt/scaife-viewer/src/
RUN python manage.py load_text_repos \
    && python manage.py slim_text_repos \
    && python manage.py shell -c 'from scaife_viewer.core.cts import text_inventory; text_inventory();'
