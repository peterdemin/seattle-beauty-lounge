#!/usr/bin/env bash

set -e -o pipefail

git archive --format=tar HEAD api -o caprover-api.tar
caprover deploy -t caprover-api.tar -a api -u staging.seattle-beauty-lounge.com -d
rm -rf caprover-api.tar
