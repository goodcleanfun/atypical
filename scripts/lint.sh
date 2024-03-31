#!/usr/bin/env bash

set -e
set -x

ruff atypical tests --fix
black atypical tests --check
