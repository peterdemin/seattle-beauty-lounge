#!/usr/bin/env bash
set -e -o pipefail

scp tools/init_ubuntu.sh staging.seattle-beauty-lounge.com:
ssh staging.seattle-beauty-lounge.com -- "chmod +x init_ubuntu.sh && sudo ./init_ubuntu.sh"

cat <<EOF
Replicate this CapRover server setup (Password in the password manager):

? have you already started CapRover container on your server? Yes
? IP address of your server: 35.185.245.45
? CapRover server root domain: staging.seattle-beauty-lounge.com
? new CapRover password (min 8 characters): [hidden]
? enter new CapRover password again: [hidden]
? "valid" email address to get certificate and enable HTTPS: peter@seattle-beauty-lounge.com
? CapRover machine name, with whom the login credentials are stored locally: staging

CapRover server setup completed: it is available as staging at https://captain.staging.seattle-beauty-lounge.com
EOF

caprover serversetup
