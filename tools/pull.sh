#!/usr/bin/env bash

set -eo pipefail

function pull {
    HOST=$1
    LOCAL_DIR=$2
    REMOTE_DIR=$3
    mkdir -p "${LOCAL_DIR}/${HOST}"
    rsync -a "${HOST}:${REMOTE_DIR}/" "${LOCAL_DIR}/${HOST}"
}

pull seattle-beauty-lounge.com logs /var/log/nginx
pull seattle-beauty-lounge.com backups /var/backups/postgresql
pull staging.seattle-beauty-lounge.com logs /var/log/nginx
pull staging.seattle-beauty-lounge.com backups /var/backups/postgresql
