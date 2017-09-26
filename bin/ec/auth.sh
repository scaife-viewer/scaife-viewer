#!/bin/bash

set -e

echo "$EC_SERVICE_ACCOUNT_KEY" | base64 --decode > ${HOME}/ec-service-key.json

# setup and authenticate against Eldarion Cloud
sudo wget -q -O /usr/local/bin/ec "https://storage.googleapis.com/ec-cli/ec-v0.8.0_linux-amd64"
sudo chmod +x /usr/local/bin/ec
mkdir -p ~/.config/ec
ec login --from-file=${HOME}/ec-service-key.json --force
