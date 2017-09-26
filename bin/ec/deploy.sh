#!/bin/bash

set -eux

# Declare arg variables for clarity.
INSTANCE=$1

# @@@ set SHA after deployment succeeds
ec --log-http --instance="$INSTANCE" instances env SHA="$CIRCLE_SHA1"
ec --instance="$INSTANCE" deploy "$CIRCLE_SHA1"
ec --instance="$INSTANCE" run web -- python manage.py migrate --noinput
