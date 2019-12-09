#!/usr/bin/env bash

set -e

# usage: slack-notify <ec-instance-name>

# check for instance mapping
INSTANCE="$1"

SHA_SHORT="${CIRCLE_SHA1:0:7}"

AUTHOR_NAME="$(git show -s --format='%an' $SHA_SHORT)"
if [[ "$CIRCLE_BRANCH" == "master" ]]; then
    INSTANCE_URL="https://scaife.perseus.org/"
else
    INSTANCE_URL="https://scaife-dev.perseus.org/"
fi

# prepare Slack message payload
MESSAGE="${AUTHOR_NAME} deployed \`<https://github.com/scaife-viewer/scaife-viewer/commit/${SHA_SHORT}|${SHA_SHORT}>\` to <${INSTANCE_URL}|${INSTANCE}>."
PAYLOAD_DATA="payload={\"channel\": \"#dev-feed\", \"username\": \"Heroku Deployments\", \"text\": \"${MESSAGE}\", \"icon_emoji\": \":white_check_mark:\"}"

# post to Slack
echo "Sending Slack notification..."
echo $PAYLOAD_DATA
curl -XPOST "$EC_DEPLOY_WEBHOOK_URL" --data-urlencode "$PAYLOAD_DATA"
