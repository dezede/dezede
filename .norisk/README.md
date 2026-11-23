# Deployment (added by Norisk)

See the workflow for what runs; `remote.sh` is the only part that runs on the server.

## One-time setup

This repository is public, so these files name neither the server nor this application: Norisk gives each environment's settings to GitHub as the secret `NORISK_DEPLOY_SETTINGS` when a deploy starts. What to set up on the server once (the user, the checkout, how it is reached) is on its page in Norisk.

**Secrets**, where a branch or a pull request cannot read them:
- **GitHub**: Settings, Environments, create `production`, restrict each one's *Deployment branches* to its branch. `NORISK_DEPLOY_TOKEN` and `NORISK_SSH` (the deploy key and the server's host key) are **environment secrets** set by Norisk itself.

**Starting a deploy**: Actions, *Deploy*, Run workflow; or the *Deploy now* button in Norisk, which does the same.
A failed health check puts the previous commit back and fails the run. Nothing is recorded as deployed unless it succeeded.
