#!/usr/bin/env bash
set -e -o pipefail

scp alembic.minimal.ini tools/ubuntu_install.sh tools/init_staging.sh staging.seattle-beauty-lounge.com:
ssh staging.seattle-beauty-lounge.com -- "chmod +x ubuntu_install.sh init_staging.sh && sudo ./ubuntu_install.sh && sudo ./init_staging.sh"
