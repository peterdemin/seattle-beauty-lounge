#!/usr/bin/env bash

set -eo pipefail

BACKUP_DIR="/var/backups/postgresql"

pg_dumpall | gzip > "$BACKUP_DIR/$(hostname)_$(date '+%Y%m%dT%H%M%S').sql.gz"
find "$BACKUP_DIR" -type f -mtime +30 -exec rm {} \;
