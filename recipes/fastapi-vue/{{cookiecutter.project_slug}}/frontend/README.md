# Vue frontend

Use Node 26.10.0 or newer. Start the FastAPI backend and apply migrations using the root
README, then run:

```sh
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. Vite proxies `/api` and `/health` to FastAPI on port 8000.
The example form uses Pinia to create an item in the backend, Vue Router for navigation,
and Vue I18n for English and Spanish messages. Browser requests use native `fetch`.

## Checks and cleanup

```sh
npm run format:check
npm run lint
npm run type-check
npm test
npm run knip
npm run build
```

CI runs these checks with the committed `package-lock.json`. Oxlint loads the recommended
[e18e rules](https://github.com/e18e/eslint-plugin) through its JavaScript plugin support.
`npm run format` formats files with Oxfmt; `npm run lint -- --fix` applies safe lint fixes.
`npm run knip:fix` removes unused dependencies and exports; review its changes before committing.

The [e18e CLI](https://github.com/e18e/cli) provides dependency analysis and replacement codemods:

```sh
npm run e18e
npm run codemod -- --help
npm run codemod -- --all --dry-run --include 'src/**/*.ts'
# Apply the suggested dependency replacements:
npm run codemod -- --all --include 'src/**/*.ts'
```

Codemods are an explicit maintenance command, since they modify source files. Review the diff
and run checks afterward. Oxlint also auto-fixes modern web syntax through the e18e rules.

## Docker and releases

From the project root, `docker compose up --build --detach --wait` builds both images.
Open http://127.0.0.1:8080 (`FRONTEND_PORT` changes the host port). Nginx runs without root,
serves the production build, supports Vue Router history paths, and proxies `/api` and `/health`
to the API container. No Node process or development dependencies ship in the frontend image.

The release workflow publishes the backend as `ghcr.io/<owner>/<repository>` and the frontend
as `ghcr.io/<owner>/<repository>-frontend`, after both CI jobs and Docker checks pass.
Both use the version in the root `pyproject.toml`. Dependabot groups frontend runtime and
development dependencies separately and applies a seven-day cooldown.

## Upgrade TODOs

- TODO: replace Vue `3.6.0-rc.9` with the stable 3.6 release when available.
- TODO: replace Vue I18n `12.0.0-alpha.4` with an RC when published, then with stable 12.
  No version 12 RC was published on npm when this recipe was created (2026-09-30).
- TODO: upgrade TypeScript 6 to TypeScript 7 once Vue language tools / `vue-tsc` support it;
  remove the TypeScript 7 Dependabot ignore at the same time.
- The npm overrides keep Vue and its SFC compiler on the same prerelease and allow packages
  whose Vue peer range only names stable releases. Remove them when using stable Vue.
