#!/usr/bin/env bash

set -e -o pipefail

make clean

scp .env.prod seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com "sudo ls /home/api >/dev/null 2>&1 && sudo mv .env.prod /home/api/.env && sudo chown api:api /home/api/.env || true"

rsync -a api seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com "sudo api/deploy.sh"

make production
rsync -a public seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com "sudo rsync -a --delete public/ /var/www/html"
