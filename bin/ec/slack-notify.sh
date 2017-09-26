#!/usr/bin/env bash

set -e

# usage: slack-notify <ec-instance-name>

# check for instance mapping
INSTANCE="$1"

SHA_SHORT="${CIRCLE_SHA1:0:7}"

# prepare Slack message payload
MESSAGE="@${CIRCLE_USERNAME} deployed \`${SHA_SHORT}\` to ${INSTANCE}."
PAYLOAD_DATA="payload={\"channel\": \"#dev-feed\", \"username\": \"EC Deployments\", \"text\": \"${MESSAGE}\", \"icon_emoji\": \":lightning_cloud:\"}"

# post to Slack
echo "Sending Slack notification..."
echo $PAYLOAD_DATA
curl -XPOST "$EC_DEPLOY_WEBHOOK_URL" --data-urlencode "$PAYLOAD_DATA"
