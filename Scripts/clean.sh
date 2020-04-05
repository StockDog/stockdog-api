#!/usr/bin/env bash
RESTORE='\033[0m'
RED='\033[00;31m'
GREEN='\033[00;32m'
YELLOW='\033[00;33m'
BLUE='\033[00;34m'
CYAN='\033[00;36m'

echo -e "${CYAN}Attempting to clean repository${RESTORE}"
echo ""

# Move to the root directory
START_DIR="$(pwd)"
REPOSITORY_ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPOSITORY_ROOT_DIR" ]; then
   echo "Cannot determine StockDog root directory. Please run this script from within the repository."
   exit 1
fi
cd "$REPOSITORY_ROOT_DIR"

# Remove package-locks and node modules
echo "Removing Pipfile.lock"
find . -name "Pipfile.lock" -exec rm -rf '{}' +
