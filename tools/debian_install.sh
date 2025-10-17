#!/usr/bin/env bash

set -e -o pipefail

apt-get remove -y google-cloud-cli google-cloud-cli-anthoscli google-guest-agent google-osconfig-agent

curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list

apt-get update
apt-get upgrade -y
apt-get install -y \
    ca-certificates \
    curl \
    nginx \
    rsync \
    python3 \
    python3-venv \
    python-is-python3 \
    postgresql \
    postgresql-contrib \
    tailscale

if [ ! -e /usr/bin/certbot ]; then
    python3 -m venv /opt/certbot/
    /opt/certbot/bin/pip install certbot certbot-nginx
    ln -s /opt/certbot/bin/certbot /usr/bin/certbot
fi
