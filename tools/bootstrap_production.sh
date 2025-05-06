#!/usr/bin/env bash
set -e -o pipefail

scp alembic.minimal.ini tools/ubuntu_install.sh tools/init_production.sh seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com -- "chmod +x ubuntu_install.sh init_production.sh && sudo ./ubuntu_install.sh && sudo ./init_production.sh"
