#!/usr/bin/env bash

set -e -o pipefail

PYTHON_VERSION="3.12"
NODE_VERSION="18"
PYTHON="python${PYTHON_VERSION}"
VENV_DIR=~/.virtualenvs/S

brew install "python@${PYTHON_VERSION}"

# Ensure virtualenv is created and active
if [ -z "$VIRTUAL_ENV" ]; then
    mkdir -p ~/.virtualenvs/
    if [ ! -f "${VENV_DIR}/bin/activate" ]; then
        $PYTHON -m venv ${VENV_DIR}
    fi
    . ${VENV_DIR}/bin/activate
fi

$PYTHON -m pip install -r requirements/prereq.txt
pip-sync requirements/dev.txt

tools/nvm.sh

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

nvm install "${NODE_VERSION}"
nvm use "${NODE_VERSION}"
npm install

pre-commit install
pre-commit autoupdate

# https://cloud.google.com/sdk/docs/install
curl -s -L https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-darwin-arm.tar.gz | tar xz - -C ~/
(cd ~/google-cloud-sdk/ && ./install.sh && bin/gcloud init)
