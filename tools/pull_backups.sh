#!/usr/bin/env bash

set -eo pipefail

HOST=$1
if [ -z "${HOST}" ]; then
    echo "Pass hostname as an argument"
    exit 1
fi

# This section must be in sync with db-backup.service
BACKUP_DIR="/var/backups/postgresql"

mkdir -p "backups/${HOST}"
rsync -a "${HOST}:${BACKUP_DIR}/" "backups/${HOST}"
