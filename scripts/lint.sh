#!/usr/bin/env bash

set -e
set -x

#ruff atypical tests
black atypical tests --check
