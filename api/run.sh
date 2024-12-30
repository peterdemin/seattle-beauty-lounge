#!/bin/sh

.venv/bin/uvicorn api.main:app --uds /tmp/api.sock
