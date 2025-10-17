#!/usr/bin/env bash
set -e -o pipefail

IP=$1

scp tools/debian_install.sh tools/init_staging.sh "${IP}:"
ssh "${IP}" -- "chmod +x debian_install.sh init_staging.sh && sudo ./debian_install.sh && sudo ./init_staging.sh"
