#!/usr/bin/env bash
set -e -o pipefail

scp tools/init_staging.sh staging.seattle-beauty-lounge.com:
scp alembic.minimal.ini staging.seattle-beauty-lounge.com:
ssh staging.seattle-beauty-lounge.com -- "chmod +x init_staging.sh && sudo ./init_staging.sh"
