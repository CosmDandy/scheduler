# Шаблон для проектов с DevPod

Этот репозиторий является отправной точкой для всех моих проектов при работе с которыми я использую [DevPod](https://devpod.sh/)

Для создания проекта в DevPod я использую следующую команду:
```bash
devpod up . --id . --provider . --dotfiles https://github.com/CosmDandy/dotfiles-devpod.git
```

## [Docker in docker](https://github.com/devcontainers/features/tree/main/src/docker-in-docker)

```
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
```

## [Docker outside of docker](https://github.com/devcontainers/features/tree/main/src/docker-outside-of-docker)

```
  "mounts": [
    "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
  ],
  "features": {
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {}
  },
  "runArgs": [
    "--privileged",
    "--pid=host",
    "--network=host"
  ],
```
