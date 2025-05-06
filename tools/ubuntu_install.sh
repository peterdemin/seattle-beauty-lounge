#!/usr/bin/env bash

set -e -o pipefail

curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list

apt-get update
apt-get upgrade -y
apt-get install -y \
    ca-certificates \
    curl \
    nginx \
    rsync \
    python3 \
    python3.12-venv \
    python-is-python3 \
    postgresql \
    postgresql-contrib \
    tailscale
