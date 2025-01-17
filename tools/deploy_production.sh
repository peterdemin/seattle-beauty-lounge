#!/usr/bin/env bash

set -e -o pipefail

make clean

HOST=seattle-beauty-lounge.com
ENV_SLUG=prod

scp .env.${ENV_SLUG} ${HOST}:
ssh ${HOST} "sudo ls /home/api >/dev/null 2>&1 && sudo mv .env.${ENV_SLUG} /home/api/.env && sudo chown api:api /home/api/.env || true"

rsync -a --delete lib ${HOST}:
rsync -a --delete api ${HOST}:
ssh ${HOST} "sudo api/deploy.sh"

make ${ENV_SLUG}
make compress  # Must be run separately to detect targets
rsync -a --delete public ${HOST}:
ssh ${HOST} "sudo rsync -a --delete public/ /var/www/html"
