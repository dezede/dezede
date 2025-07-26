# Dezède

This site is available publicly at the URL: https://dezede.org

## Common to all installations

Preferred OS: Debian (latest stable release)

- Install Docker
- Add this in a new `/etc/docker/daemon.json` file, otherwise users with an IPv6
  will not get their IP forwarded to Django, due to a Docker limitation:

  ```json
  {
    "ip6tables": true,
    "experimental": true
  }
  ```
- Restart Docker with `systemctl restart docker`
- Limit the journalctl log size (it can take several GB after months) by editing `/etc/systemd/journalctl.conf` and set:

  ```
  [Journal]
  SystemMaxUse=250M
  ```
  then restart it with `systemctl restart systemd-journald`
- `sysctl -w vm.overcommit_memory=1 >> /etc/sysctl.conf` (see https://github.com/redis/docker-library-redis/issues/298#issuecomment-1749170920)
- `git submodule init`
- `git submodule update`

## Local development

- Follow “Common to all installations” above
- In the root project folder, run `docker compose up --build`
- Visit `http://dezede.localhost` on your browser.

## Production deployment

- Log as root to the server via SSH
- Follow “Common to all installations” above
- Clone the repository in `/srv/dezede`
- `docker compose -f docker-compose.prod.yaml build`
- `cp dezede.service /etc/systemd/system/`
- `systemctl daemon-reload`
- `systemctl start dezede.service`

# Copy remote data into the local Docker environment

**¡ This will delete your local database !**

```shell
pip install docker-website-backup==1.2.0
dwb --no-input clone dezede.org
```

# Localisation

1. Download the latest version of the Transifex client: https://github.com/transifex/cli/releases
2. Get the project token on https://transifex.com

## Push the source language to Transifex

```shell
tx --hostname https://rest.api.transifex.com --token [PROJECT_TOKEN] push -s
```

## Pull the latest translations from Transifex

1. `tx --hostname https://rest.api.transifex.com --token [PROJECT_TOKEN] pull -a`
2. `./manage.py compilemessages`
