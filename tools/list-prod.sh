exec ssh seattle-beauty-lounge.com "sudo -u api /bin/bash -c 'cd && ./.venv/bin/python -m api.cli | tail -n 30'"
