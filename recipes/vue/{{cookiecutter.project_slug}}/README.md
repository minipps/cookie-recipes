# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Run

```sh
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. See [frontend/README.md](frontend/README.md) for the full
toolchain, quality checks, codemods, and upgrade TODOs.

## Docker

```sh
docker compose up --build --detach --wait
docker compose down
```

Open http://127.0.0.1:8080. Set `FRONTEND_PORT` to change the host port.
The container runs without root and serves the static production build with SPA routing.

## CI and releases

GitHub CI checks formatting, linting, types, Vitest, Knip, the production build, and the
Docker image. Dependabot groups frontend runtime packages, development tools, images,
and GitHub Actions separately. TypeScript remains on 6 until Vue tooling supports 7.

To release, update the version and lockfile, commit, and push a matching tag:

```sh
npm version --prefix frontend --no-git-tag-version 0.2.0
git add frontend/package.json frontend/package-lock.json
git commit -m "Release 0.2.0"
git push
git tag v0.2.0
git push origin v0.2.0
```

The release workflow runs CI first and publishes to `ghcr.io/<owner>/<repository>`.
Tags must match `frontend/package.json`. Publishing an image does not deploy it to a server.
