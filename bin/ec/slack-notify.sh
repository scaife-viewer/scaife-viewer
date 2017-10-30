#!/usr/bin/env bash

set -e

# usage: slack-notify <ec-instance-name>

# check for instance mapping
INSTANCE="$1"

SHA_SHORT="${CIRCLE_SHA1:0:7}"

AUTHOR_NAME="$(git show -s --format='%an' $SHA_SHORT)"
if [[ "$CIRCLE_BRANCH" == "master" ]]; then
    EC_INSTANCE_URL="https://lk353.eu1.eldarioncloud.com/"
else
    EC_INSTANCE_URL="https://ho905.eu1.eldarioncloud.com/"
fi

# prepare Slack message payload
MESSAGE="${AUTHOR_NAME} deployed \`<https://github.com/eldarion-client/scaife-viewer/commit/${SHA_SHORT}|${SHA_SHORT}>\` to <${EC_INSTANCE_URL}|${INSTANCE}>."
PAYLOAD_DATA="payload={\"channel\": \"#dev-feed\", \"username\": \"EC Deployments\", \"text\": \"${MESSAGE}\", \"icon_emoji\": \":lightning_cloud:\"}"

# post to Slack
echo "Sending Slack notification..."
echo $PAYLOAD_DATA
curl -XPOST "$EC_DEPLOY_WEBHOOK_URL" --data-urlencode "$PAYLOAD_DATA"
