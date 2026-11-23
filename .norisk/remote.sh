#!/usr/bin/env bash
# Runs on the server as the deploy user, detached from the SSH session that started it (run.sh): a cancelled or timed-out CI job, or a
# network cut, never leaves the server half deployed; it goes on to its end, going back to the previous version if anything fails.
# Everything is inside main() so that no command can swallow the rest of the script from stdin.
main() {
  set -euo pipefail
  cd "$DEPLOY_DIR"
  # Its lock, log and result are in .git, the deploy user's own (a fixed name in /tmp could be anyone's).
  state="$(git rev-parse --absolute-git-dir)/norisk"
  mkdir -p "$state"
  exec 9>>"$state/lock"
  flock -n 9 || { echo "Another deploy is already running" >&2; exit 3; }
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Uncommitted changes in $DEPLOY_DIR: not deploying over them" >&2
    exit 4
  fi
  # What runs now, read before anything moves: after a rollback from Norisk it is an older commit (detached), and the branch
  # still names the version that was rolled back. The new commit is fetched before the files change: a fetch that fails changes nothing.
  previous="$(git rev-parse HEAD)"
  git fetch --quiet origin "$DEPLOY_BRANCH"
  target="$(git rev-parse "origin/$DEPLOY_BRANCH")"
  if ! git merge-base --is-ancestor "$previous" "$target"; then
    echo "$DEPLOY_DIR is on $previous, which $DEPLOY_BRANCH on origin does not contain (commits made on the server, or a rewritten" \
      "branch): not deploying over it" >&2
    exit 7
  fi

  restarted=0
  restart() {
    restarted=1
    if [ -n "${DEPLOY_UNIT:-}" ]; then
      if [ "$(id -u)" = 0 ]; then systemctl restart "$DEPLOY_UNIT"; else sudo -n systemctl restart "$DEPLOY_UNIT"; fi
    elif [ -n "${DEPLOY_COMPOSE_FILE:-}" ]; then COMPOSE_FILE="$DEPLOY_COMPOSE_FILE" docker compose up -d
    else docker compose up -d; fi
  }
  # `&&` chains, not `set -e`: errexit is off inside a function called from an `if`. The branch is moved, never reset: a file of the
  # server that is not in git stops it instead of being overwritten.
  apply() {
    git checkout --quiet -B "$DEPLOY_BRANCH" "$1" && git submodule update --init --recursive --quiet \
      && bash -c "${DEPLOY_BUILD:-}" && restart
  }
  healthy() {
    [ -n "${DEPLOY_HEALTH_URL:-}" ] || return 0
    for _ in $(seq 1 "${DEPLOY_HEALTH_TRIES:-30}"); do
      curl -fsSL -o /dev/null --max-time 10 "$DEPLOY_HEALTH_URL" && return 0  # -L: a redirect is not an answer, where it leads is
      sleep "${DEPLOY_HEALTH_WAIT:-10}"
    done
    return 1
  }

  if apply "$target" && healthy; then
    echo "DEPLOYED $target"
    return 0
  fi
  failed_before_restart="$((1 - restarted))"
  echo "Deploying $target failed: going back to $previous" >&2
  if ! apply "$previous"; then
    if [ "$failed_before_restart" = 1 ] && [ "$restarted" = 0 ]; then
      echo "Building $previous failed too (an outside cause?): nothing was restarted, the version that ran still runs, but" \
        "$DEPLOY_DIR may be half built" >&2
      exit 9
    fi
    echo "ROLLBACK FAILED: $DEPLOY_DIR needs a person" >&2
    exit 6
  fi
  healthy || { echo "The previous version does not pass the health check either" >&2; exit 8; }
  exit 5
}
main </dev/null
