#!/usr/bin/env bash

set -e -o pipefail

make clean

scp .env.prod seattle-beauty-lounge.com:.env.prod
ssh seattle-beauty-lounge.com "sudo mv .env.prod /home/api/.env && sudo chown api:api /home/api/.env"

rsync -a api seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com "sudo api/deploy.sh"

make fe
rsync -a public seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com "sudo rsync -a --delete public/ /var/www/html"
