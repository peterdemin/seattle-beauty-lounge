#!/usr/bin/env bash
set -e -o pipefail

scp tools/init_staging.sh staging.seattle-beauty-lounge.com:
ssh staging.seattle-beauty-lounge.com -- "chmod +x init_staging.sh && sudo ./init_staging.sh"

caprover setup -y \
    -r staging.seattle-beauty-lounge.com \
    -e peter@seattle-beauty-lounge.com \
    -p captain42 \
    -w "${CAPROVER_PASSWORD}" \
    -n staging
