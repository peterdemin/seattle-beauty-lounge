#!/usr/bin/env bash

DOMAIN=seattle-beauty-lounge.com

scp -rC tools/provision_bugsink.sh "${DOMAIN}:"
ssh -t $DOMAIN -- "chmod +x provision_bugsink.sh && sudo ./provision_bugsink.sh && rm provision_bugsink.sh"
