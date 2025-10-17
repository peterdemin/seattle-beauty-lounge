#!/usr/bin/env bash

set -e -o pipefail

HOST=${1:-staging.seattle-beauty-lounge.com}

scp ~/.gcp/service-account.json ${HOST}:
ssh ${HOST} -- "sudo mkdir -p ~api/.gcp && sudo mv service-account.json ~api/.gcp/ && sudo chown -R api:api ~api/.gcp"
