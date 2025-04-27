#!/usr/bin/env bash
set -e -o pipefail

ssh seattle-beauty-lounge.com -- "sudo certbot certonly --agree-tos --manual -m peter@seattle-beauty-lounge.com -d a.seattle-beauty-lounge.com --preferred-challenges dns"
