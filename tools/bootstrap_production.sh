#!/usr/bin/env bash
set -e -o pipefail

scp tools/init_production.sh seattle-beauty-lounge.com:
ssh seattle-beauty-lounge.com -- "chmod +x init_production.sh && sudo ./init_production.sh"
