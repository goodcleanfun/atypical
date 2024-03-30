#!/usr/bin/env bash

set -e
set -x

export PYTHONPATH=.
coverage run -m pytest tests ${@}
