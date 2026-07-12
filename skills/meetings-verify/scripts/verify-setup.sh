#!/usr/bin/env bash
# meeting-transcribe pipeline health check.
# Checks binaries, models, package venv, watcher, and folders.

PASS="PASS"; FAIL="FAIL"; WARN="WARN"
errors=0

check() {
  local label="$1" status="$2" detail="${3:-}"
  printf "  %-26s %s" "$label" "$status"
  [ -n "$detail" ] && printf "  — %s" "$detail"
  printf "\n"
  [ "$status" = "$FAIL" ] && errors=$((errors + 1))
  return 0
}

PKG="$HOME/Task-Management/packages/meeting-transcribe"
MODELS="$HOME/.config/meeting-transcribe/models"
INBOX="/Volumes/SSD/Dropbox/Apps/meetings-inbox"

echo "meeting-transcribe health check"
echo "================================"

# Binaries
for bin in whisper-cli ffmpeg uv; do
  if command -v "$bin" >/dev/null 2>&1; then
    check "binary: $bin" "$PASS" "$(command -v "$bin")"
  else
    check "binary: $bin" "$FAIL" "not on PATH"
  fi
done

# Models — large-v3 is required; turbo is optional (only needed for --fast).
for m in "ggml-large-v3.bin" "ggml-silero-v6.2.0.bin" \
         "diarization/segmentation.onnx" "diarization/embedding.onnx"; do
  if [ -f "$MODELS/$m" ]; then
    check "model: $m" "$PASS"
  else
    check "model: $m" "$FAIL" "missing at $MODELS/$m"
  fi
done
if [ -f "$MODELS/ggml-large-v3-turbo.bin" ]; then
  check "model: turbo (--fast)" "$PASS"
else
  check "model: turbo (--fast)" "$WARN" "not installed (--fast disabled; large-v3 still works)"
fi

# Package venv + imports
if [ -d "$PKG" ]; then
  if (cd "$PKG" && uv run python -c "import meeting_transcribe, sherpa_onnx, soundfile" >/dev/null 2>&1); then
    check "package venv + imports" "$PASS"
  else
    check "package venv + imports" "$FAIL" "uv run import failed in $PKG"
  fi
else
  check "package dir" "$FAIL" "missing: $PKG"
fi

# Watcher launchd job
if launchctl list 2>/dev/null | grep -q com.user.meeting-transcribe; then
  check "watcher (launchd)" "$PASS" "com.user.meeting-transcribe loaded"
else
  check "watcher (launchd)" "$WARN" "not loaded (manual CLI still works)"
fi

# Folders
[ -d "$INBOX" ] && check "inbox folder" "$PASS" "$INBOX" \
                || check "inbox folder" "$WARN" "missing: $INBOX"
[ -d "$HOME/vault/meetings" ] && check "meetings output dir" "$PASS" \
                        || check "meetings output dir" "$WARN" "missing: ~/vault/meetings"

echo "================================"
if [ "$errors" -eq 0 ]; then
  echo "All critical checks passed."
else
  echo "$errors critical check(s) FAILED."
fi
exit "$errors"
