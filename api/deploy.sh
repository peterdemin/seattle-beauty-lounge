#!/bin/bash

set -eo pipefail

# Bootstrap system user with virtualenv
id -u api &>/dev/null || sudo adduser --system --group api --home /home/api
if [ ! -d /home/api/.venv ]; then
    sudo -u api python -m venv /home/api/.venv
fi
if [ ! -e /home/api/.venv/bin/pip-sync ]; then
    sudo -u api /home/api/.venv/bin/python -m pip install pip-tools==7.4.1
fi

# Sync API source
rsync -a --delete lib/ /home/api/lib
chown -R api:api /home/api/lib
rsync -a --delete api/ /home/api/api
chown -R api:api /home/api/api

# Install requirements and etc files
pushd /home/api/
sudo -u api .venv/bin/pip-sync api/requirements.txt
cp api/etc/systemd/system/* /etc/systemd/system/
cp api/etc/nginx/sites-available/default /etc/nginx/sites-available/default
popd

# Restart daemon
systemctl daemon-reload
systemctl enable --now db-backup.timer
systemctl restart api.service
systemctl status api.service
systemctl reload nginx.service

# journalctl -fu api.service
