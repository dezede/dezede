#!/usr/bin/env bash
# Runs on the CI machine (already on the tailnet): starts remote.sh detached on the server over Tailscale SSH (directly, when this
# machine is the server), follows it to its end, then tells Norisk. The deploy does not depend on this job: cancelled, timed
# out or cut off, it goes on on the server by itself (reconnections follow it again).
# The server's host key is accepted the first time (accept-new): the tailnet already authenticates the machine, and a later change still fails.
set -euo pipefail
# A public repository holds no name of the server or of this application: Norisk gives them in this one secret.
if [ -n "${NORISK_DEPLOY_SETTINGS:-}" ]; then
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    export "$line"
    if [ -n "${GITHUB_ACTIONS:-}" ]; then
      case "${line%%=*}" in DEPLOY_HOST|DEPLOY_DIR|DEPLOY_BUILD|DEPLOY_HEALTH_URL|NORISK_DEPLOY_URL) echo "::add-mask::${line#*=}" ;; esac
    fi
  done <<<"$(printf '%s' "$NORISK_DEPLOY_SETTINGS" | base64 -d)"
fi
: "${DEPLOY_HOST:?}" "${DEPLOY_USER:?}" "${DEPLOY_DIR:?}" "${DEPLOY_BRANCH:?}"
here="$(cd "$(dirname "$0")" && pwd)"
# Tells Norisk how it went and says what it answered. Never makes the deploy itself fail.
# The response body is not shown: an HTML page from some other server on the way would only hide that the report did not arrive.
report() {
  [ -n "${NORISK_DEPLOY_URL:-}" ] && [ -n "${NORISK_DEPLOY_TOKEN:-}" ] || return 0
  local code
  code="$(curl -sS --retry 3 -L --post301 --post302 --post303 -X POST -H "Authorization: Bearer $NORISK_DEPLOY_TOKEN" "$@" \
    -o /dev/null -w '%{http_code}' "$NORISK_DEPLOY_URL")" || { echo "WARNING: could not reach Norisk at $NORISK_DEPLOY_URL" >&2; return 0; }
  case "$code" in
    2??) echo "Told Norisk (HTTP $code)" ;;
    *) echo "WARNING: Norisk at $NORISK_DEPLOY_URL answered HTTP $code: the result was not recorded" >&2 ;;
  esac
}
log="$(mktemp)"
trap 'code=$?; rm -rf "$log" "${ssh_dir:-$log}"; if [ "$code" -ne 0 ]; then report -d status=failed -d "code=$code"; fi' EXIT
# The CI machine is the server itself (a self-hosted runner next to what it deploys): Tailscale SSH does not take a machine's
# connections to itself, so run remote.sh here, as the deploy user, with no SSH.
is_local() {
  local name address mine
  for name in localhost "$(hostname)" "$(hostname -s 2>/dev/null || true)" "$(hostname -f 2>/dev/null || true)"; do
    [ -n "$name" ] && [ "${DEPLOY_HOST%.}" = "$name" ] && return 0
  done
  # Any other name of this machine (its Tailscale name, an alias): it resolves to one of this machine's own addresses.
  mine=" $(hostname -I 2>/dev/null || true) 127.0.0.1 ::1 "
  for address in $(getent ahosts "$DEPLOY_HOST" 2>/dev/null | awk '{print $1}' | sort -u); do
    case "$mine" in *" $address "*) return 0 ;; esac
  done
  return 1
}
if is_local; then
  echo "$DEPLOY_HOST is this machine: deploying here as $DEPLOY_USER, without SSH"
  if [ "$(id -un)" = "$DEPLOY_USER" ]; then runner=(bash -s); else runner=(sudo -n -u "$DEPLOY_USER" bash -s); fi
else
  command -v ssh >/dev/null || { echo "ssh is not installed on this CI machine: install the OpenSSH client (openssh-client)" >&2; exit 1; }
  ssh_options=(-o BatchMode=yes -o ConnectTimeout=30 -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
  if [ -n "${NORISK_SSH:-}" ]; then
    # The deploy key and the host key Norisk stored, in files that go when the job ends. No host key yet: the first connection trusts it.
    ssh_dir="$(mktemp -d)"
    printf '%s' "${NORISK_SSH%%.*}" | base64 -d >"$ssh_dir/key"
    printf '%s' "${NORISK_SSH#*.}" | base64 -d >"$ssh_dir/known_hosts"
    chmod 600 "$ssh_dir/key"
    ssh_options+=(-i "$ssh_dir/key" -o IdentitiesOnly=yes -p "${DEPLOY_PORT:-22}" -o UserKnownHostsFile="$ssh_dir/known_hosts"
                  -o StrictHostKeyChecking="$([ -s "$ssh_dir/known_hosts" ] && echo yes || echo accept-new)")
  else
    ssh_options+=(-o StrictHostKeyChecking=accept-new)
  fi
  runner=(ssh "${ssh_options[@]}" "$DEPLOY_USER@$DEPLOY_HOST" bash -s)
fi
exports=""
for name in DEPLOY_DIR DEPLOY_BRANCH DEPLOY_UNIT DEPLOY_BUILD DEPLOY_COMPOSE_FILE DEPLOY_HEALTH_URL; do
  exports+="$(printf 'export %s=%q' "$name" "${!name-}")"$'\n'
done
# The job: the variables and remote.sh, written on the server by `start` (base64: any text goes through) and run there detached.
job="$(printf '%s' "$exports"; cat "$here/remote.sh")"
start='main() {
  set -euo pipefail
  git_dir="$(git -C "$DEPLOY_DIR" rev-parse --absolute-git-dir)"
  dir="$git_dir/norisk"
  mkdir -p "$dir"
  pid="$(cat "$dir/pid" 2>/dev/null || true)"
  if [ -n "$pid" ] && [ -r "/proc/$pid/cmdline" ] && grep -qaF "$dir" "/proc/$pid/cmdline"; then
    echo "Another deploy is already running (pid $pid)" >&2
    exit 3
  fi
  rm -f "$dir/state" "$dir/log" "$dir/pid"
  printf "%s" "$NORISK_JOB" | base64 -d >"$dir/deploy.sh"
  setsid bash -c '"'"'echo $$ >"$1/pid"; bash "$1/deploy.sh" >"$1/log" 2>&1; echo "code=$?" >"$1/state.tmp"; mv "$1/state.tmp" "$1/state"'"'"' \
    norisk-deploy "$dir" </dev/null >/dev/null 2>&1 &
  # Its pid is written once it runs in a session of its own: from then on nothing that happens to this job can stop it.
  for _ in $(seq 1 100); do [ -s "$dir/pid" ] && break; sleep 0.1; done
  [ -s "$dir/pid" ] || { echo "The deploy could not be started on the server" >&2; exit 1; }
  echo "Deploy started on the server: it goes on there whatever happens to this job"
}
main </dev/null
'
# Prints the deploy's log as it grows, then exits with its exit code. Run again after a cut connection, it starts from the top.
follow='main() {
  set -uo pipefail
  dir="$(git -C "$DEPLOY_DIR" rev-parse --absolute-git-dir)/norisk"
  offset=0
  n=0
  flush() {
    [ -f "$dir/log" ] || return 0
    size="$(wc -c < "$dir/log")"
    if [ "$size" -gt "$offset" ]; then tail -c +"$((offset + 1))" "$dir/log" | head -c "$((size - offset))"; offset="$size"; fi
  }
  while [ ! -e "$dir/state" ]; do
    flush
    pid="$(cat "$dir/pid" 2>/dev/null || true)"
    if [ -z "$pid" ] || [ ! -r "/proc/$pid/cmdline" ] || ! grep -qaF "$dir" "/proc/$pid/cmdline"; then
      n=$((n + 1))
      if [ "$n" -gt 5 ]; then flush; echo "The deploy stopped without a result (the server may have restarted)" >&2; exit 10; fi
    else
      n=0
    fi
    sleep "${NORISK_POLL:-2}"
  done
  flush
  code="$(sed -n "s/^code=//p" "$dir/state")"
  exit "${code:-10}"
}
main </dev/null
'
{ printf '%s' "$exports"; printf 'export NORISK_JOB=%q\n' "$(printf '%s' "$job" | base64 | tr -d '\n')"; printf '%s' "$start"; } | "${runner[@]}"
code=255
for attempt in $(seq 1 20); do
  set +e
  { printf '%s' "$exports"; printf '%s' "$follow"; } | "${runner[@]}" | tee -a "$log"
  code="${PIPESTATUS[1]}"
  set -e
  [ "$code" -eq 255 ] || break  # 255: ssh lost the connection, not the deploy's own code: it goes on, follow it again
  echo "The connection to $DEPLOY_HOST was lost (attempt $attempt): following the deploy again in 15 s" >&2
  sleep "${NORISK_RECONNECT_WAIT:-15}"
done
[ "$code" -eq 0 ] || exit "$code"
sha="$(sed -n 's/^DEPLOYED //p' "$log" | tail -n 1)"
[ -n "$sha" ] || { echo "The server did not report a deployed commit" >&2; exit 1; }
report -d "commit=$sha"
