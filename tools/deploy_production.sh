#!/usr/bin/env bash

set -e -o pipefail

# git archive --format=tar HEAD api -o caprover-api.tar
# caprover deploy -t caprover-api.tar -a api -u staging.seattle-beauty-lounge.com
# rm -rf caprover-api.tar

make clean fe
rsync public seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com "sudo rsync -a --progress --delete public/ /var/www/html"
