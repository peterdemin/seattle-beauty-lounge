#!/bin/bash

set -exo pipefail

if ! id -u api; then
    adduser --system api
    sudo -u api python -m venv ~api/.venv
    sudo -u api ~api/.venv/bin/python -m pip install pip-tools==7.4.1
fi

rsync -a --delete api "~api/api"
chown -R api:api "~api/api"

pushd "~api/"
sudo -u api .venv/bin/python -m pip-sync api/requirements.txt
cp etc/systemd/system/api.service /etc/systemd/system/api.service
cp etc/nginx/sites-available/api /etc/nginx/sites-available/api
ln -fs /etc/nginx/sites-available/api /etc/nginx/sites-enabled/api
popd


certbot --nginx

systemctl daemon-reload
systemctl restart api.service
systemctl status api.service
systemctl reload nginx.service
