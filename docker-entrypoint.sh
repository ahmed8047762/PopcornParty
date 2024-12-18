#!/bin/bash

# Exit on error
set -e

# Execute the command passed to docker-entrypoint.sh
exec "$@"
