#!/usr/bin/env bash

set -e -o pipefail

apt-get update
apt-get install -y ca-certificates curl nginx rsync
if [ ! -e /usr/bin/certbot ]; then
    snap install --classic certbot
    ln -s /snap/bin/certbot /usr/bin/certbot
fi
certbot --nginx
