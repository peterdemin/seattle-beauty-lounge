#!/usr/bin/env bash

set -e -o pipefail

make clean

rsync -a api seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com "sudo api/deploy.sh"

make fe
rsync -a public seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com "sudo rsync -a --progress --delete public/ /var/www/html"
