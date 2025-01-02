#!/usr/bin/env bash

set -e -o pipefail

make clean

scp .env.staging staging.seattle-beauty-lounge.com:
ssh staging.seattle-beauty-lounge.com "sudo ls /home/api >/dev/null 2>&1 && sudo mv .env.staging /home/api/.env && sudo chown api:api /home/api/.env || true"

rsync -a --delete api staging.seattle-beauty-lounge.com:
ssh staging.seattle-beauty-lounge.com "api/adapt_to_staging.sh"
ssh staging.seattle-beauty-lounge.com "sudo api/deploy.sh"

make staging
make compress  # Must be run separately to detect targets
rsync -a --delete public staging.seattle-beauty-lounge.com:
ssh staging.seattle-beauty-lounge.com "sudo rsync -a --delete public/ /var/www/html"
