#!/usr/bin/env bash

set -e -o pipefail

locust -f jigs/load-testing/locustfile.py
