#!/usr/bin/env bash

set -e
set -x

ruff check atypical tests --fix
black atypical tests --check
