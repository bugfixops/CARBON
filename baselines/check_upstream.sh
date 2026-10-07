#!/usr/bin/env bash
# Show every difference between baselines/AdbGPT, baselines/ReActDroid and the
# upstream commits they were copied from. Files marked [CARBON-RETEST] are the
# only intended changes; UPSTREAM.md explains each one.
set -euo pipefail
cd "$(dirname "$0")"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fetch() {  # name url commit
  git clone -q "$2" "$tmp/$1"
  git -C "$tmp/$1" checkout -q "$3"
}
fetch AdbGPT https://github.com/sidongfeng/AdbGPT ec29b4bd71f0f6469f35ad4f81b429075fb4266b
fetch ReActDroid https://github.com/wuchiuwong/ReActDroid 6bde9cdb3bed89a826c6cccde89ad7c19ef4b340

for tool in AdbGPT ReActDroid; do
  echo "=================== $tool vs upstream ==================="
  diff -ru -x .git -x __pycache__ -x test -x Data "$tmp/$tool" "$tool" || true
done
