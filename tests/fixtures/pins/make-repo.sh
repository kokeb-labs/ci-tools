#!/usr/bin/env bash
# A scratch repository whose one gitlink pins a real driver at its release-candidate tag, for the live test of
# tools/pins/pins.py in ci-pin-hygiene.yml. Usage: make-repo.sh DIR
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dir="$1"
rm -rf "$dir"
mkdir -p "$dir/drivers" "$dir/cmake"
cd "$dir"
git init -q
git config user.email "ci@example.invalid"
git config user.name "ci"
printf '[submodule "drivers/driver-ws2812-rmt"]\n\tpath = drivers/driver-ws2812-rmt\n\turl = https://github.com/kokeb-labs-drivers/driver-ws2812-rmt.git\n' > .gitmodules
cp "$here/stale.lock.yml" drivers/drivers.lock.yml
cp "$here/gates.cmake" cmake/gates.cmake
cp "$here/version.cmake" cmake/version.cmake
git add .gitmodules drivers/drivers.lock.yml cmake
git update-index --add --cacheinfo 160000,2790be043fce5c620281aafa5b2bc2e0880af829,drivers/driver-ws2812-rmt
git commit -q -m "pins"
