#!/usr/bin/env bash
# ReBL-dataset carbon test with Gemini (Vertex AI via ADC): one emulator's worth of work.
#
# The android-emulator-runner action executes each YAML script LINE as its own
# `/usr/bin/sh -c "<line>"` call, so no if/fi or multi-line blocks can live in
# the workflow's `script:` block. All branching lives here instead; the
# workflow calls this file as ONE line.
#
# Auth: the workflow passes the GCP_SA_JSON secret in the environment. We
# materialize it as a file and point GOOGLE_APPLICATION_CREDENTIALS at it;
# the raw secret is unset before any child process starts.
set -euo pipefail
cd "$(dirname "$0")"

if [ -z "${GCP_SA_JSON:-}" ]; then
  echo "FATAL: GCP_SA_JSON is empty. Set the GCP_SA_JSON repo secret (service-account JSON)." >&2
  exit 1
fi
printf '%s' "$GCP_SA_JSON" > "$HOME/gcp-sa.json"
chmod 600 "$HOME/gcp-sa.json"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/gcp-sa.json"
unset GCP_SA_JSON

MODE="$1"          # smoke | wave
MODEL="$2"         # Vertex AI model id (e.g. gemini-2.5-pro)
CASE="$3"          # smoke mode: 'category/folder' or 'folder'
CASES="$4"         # wave mode: comma-separated list (empty = all 95 ReBL cases)
SHARD="$5"         # wave mode: shard index

# Seed media (mirrors run.sh): galleries/players need pre-existing content.
# Skip with SKIP_SEED_MEDIA=1 if devices are already provisioned.
if [ "${SKIP_SEED_MEDIA:-0}" != "1" ]; then
  [ -d seed_media ] || python -u seed_media_gen.py
  python -u push_seed_media.py 5554
fi

if [ "$MODE" = "smoke" ]; then
  python -u run_rebl_gemini.py 5554 --model "$MODEL" --case "$CASE" --limit 1
elif [ -n "$CASES" ]; then
  python -u run_rebl_gemini.py 5554 --model "$MODEL" --cases "$CASES" --shard "$SHARD" --of 10
else
  python -u run_rebl_gemini.py 5554 --model "$MODEL" --shard "$SHARD" --of 10
fi
