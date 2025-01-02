#!/bin/bash

set -exo pipefail

# Fix host in nginx config:
# https://stackoverflow.com/a/15432888/135079
sed -i 's/seattle-beauty-lounge.com/staging.seattle-beauty-lounge.com/' api/etc/nginx/sites-available/default
