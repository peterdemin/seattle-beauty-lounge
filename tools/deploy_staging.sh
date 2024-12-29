#!/usr/bin/env bash

set -e -o pipefail

git archive --format=tar HEAD api -o caprover-api.tar
caprover deploy -t caprover-api.tar -a api -u staging.seattle-beauty-lounge.com
rm -rf caprover-api.tar

make fe
tar cf caprover-static.tar public captain-definition Dockerfile
caprover deploy -t caprover-static.tar -a static -u staging.seattle-beauty-lounge.com
rm -rf caprover-static.tar
