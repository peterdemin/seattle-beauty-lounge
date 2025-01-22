#!/bin/bash

set -exo pipefail

# Replace nginx config by staging alternative
mv -f api/etc/nginx/sites-available/staging api/etc/nginx/sites-available/default
