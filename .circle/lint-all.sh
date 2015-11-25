#!/bin/bash

set -x
set -e

# Flake the entire project using setup.cfg with specific settings.
flake8 --config=../setup.cfg --count celery_statsd/ tests/
