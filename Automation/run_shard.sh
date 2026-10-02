#!/usr/bin/env bash
# carbon-100 Groq retest: one emulator's worth of work.
#
# The android-emulator-runner action executes each YAML script LINE as its own
# `/usr/bin/sh -c "<line>"` call, so no if/fi or multi-line blocks can live in
# the workflow's `script:` block. All branching lives here instead; the
# workflow calls this file as ONE line.
set -euo pipefail
cd "$(dirname "$0")"

MODE="$1"          # smoke | wave
MODEL="$2"         # Groq model id
CASE="$3"          # smoke mode: 'category/folder'
CASES="$4"         # wave mode: comma-separated list (empty = all timeout cases)
SHARD="$5"         # wave mode: shard index

# Seed media (mirrors run.sh): galleries/players need pre-existing content.
# Skip with SKIP_SEED_MEDIA=1 if devices are already provisioned.
if [ "${SKIP_SEED_MEDIA:-0}" != "1" ]; then
  [ -d seed_media ] || python -u seed_media_gen.py
  python -u push_seed_media.py 5554
fi

if [ "$MODE" = "smoke" ]; then
  python -u run_retest_groq.py 5554 --model "$MODEL" --case "$CASE" --limit 1
elif [ -n "$CASES" ]; then
  python -u run_retest_groq.py 5554 --model "$MODEL" --cases "$CASES" --shard "$SHARD" --of 10
else
  python -u run_retest_groq.py 5554 --model "$MODEL" --shard "$SHARD" --of 10
fi
