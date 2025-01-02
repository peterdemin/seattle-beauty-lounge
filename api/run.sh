#!/bin/bash

set -e -o pipefail

# .venv/bin/alembic upgrade head
.venv/bin/uvicorn api.main:app --uds /tmp/api.sock
