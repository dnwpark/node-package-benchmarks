# Lockfile Test Corpus Index

58 real-world repositories cloned from GitHub as benchmark cases for parsing `package.json` and lockfiles. Organized by package manager and lockfile version, with varied complexity levels (minimal / medium / complex).

---

## Lockfile Version Reference

### npm — `package-lock.json`

| `lockfileVersion` | npm versions | Notes |
|---|---|---|
| 1 | npm 5–6 | Original format |
| 2 | npm 7–8 | Backwards-compatible superset of v1 |
| 3 | npm 9+ | Drops v1 compatibility data |

### pnpm — `pnpm-lock.yaml`

| `lockfileVersion` | pnpm versions | Format notes |
|---|---|---|
| 5.3 | pnpm 6.x | Unquoted YAML value: `lockfileVersion: 5.3` |
| 5.4 | pnpm 7.x | Unquoted YAML value: `lockfileVersion: 5.4` |
| 6.0 | pnpm 8.0–8.5 | Quoted YAML value: `lockfileVersion: '6.0'` |
| 6.1 | pnpm 8.6+ | Same structure as 6.0; adds `settings` block |
| 9.0 | pnpm 9.x, 10.x | pnpm 10 intentionally kept v9.0; no v10 lockfile version |

No lockfile versions v7 or v8 exist — the numbering jumped by design (v9+ aligns with pnpm major version).

### yarn — `yarn.lock`

| Type | Identifier in file | yarn tool version |
|---|---|---|
| v1 classic | Header: `# yarn lockfile v1`, no `__metadata` block | yarn 1.x |
| Berry (early v2) | `__metadata: { version: 4 }` | yarn 2.x early, yarn 3.0–3.1 |
| Berry v3 | `__metadata: { version: 6, cacheKey: 8 }` | yarn 3.2+ |
| Berry v4 | `__metadata: { version: 8, cacheKey: 10 }` | yarn 4.x |

> **Note:** yarn 2 and yarn 3 are not reliably distinguishable from the lockfile alone — both may show `version: 6`. Check `.yarnrc.yml` → `yarnPath` for the actual tool version. No yarn 2.x examples (metadata version 4) were found in active public repos.

### bun

| Type | Filename | Version field |
|---|---|---|
| Binary | `bun.lockb` | None (binary format, magic bytes only) |
| Text | `bun.lock` | `"lockfileVersion": 1` (JSONC format; introduced in bun 1.1.39, default in bun 1.2) |

### vlt — `vlt-lock.json`

JSON format. No `lockfileVersion` field. Versioned implicitly through the tool. Uses a `nodes` map with `§` as scope separator and `··` as path prefix.

---

## Repos

### npm

#### v1 — `"lockfileVersion": 1` (npm 5–6)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `npm-v1-rebrote-not-open` | https://github.com/fabitky/Rebrote-not-open | minimal | 5 |
| `npm-v1-stackcv` | https://github.com/cobluwu/StackCV | medium | 11 |
| `npm-v1-chanterelle-halogen-template` | https://github.com/f-o-a-m/chanterelle-halogen-template | medium | 14 |

#### v2 — `"lockfileVersion": 2` (npm 7–8)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `npm-v2-react-keys` | https://github.com/arunpraba/react-keys | minimal | 3 |
| `npm-v2-vitejs-vite-z4gujs` | https://github.com/Mayandev/vitejs-vite-z4gujs | minimal | 2 |
| `npm-v2-codedit-web` | https://github.com/satr14washere/codedit-web | medium | 11 |

#### v3 — `"lockfileVersion": 3` (npm 9+)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `npm-v3-projectf5-zootopia-frontend` | https://github.com/ZooDevelopers/ProjectF5-Zootopia-Frontend | medium | 11 |
| `npm-v3-auth` | https://github.com/Aryankumar12/auth | medium | 12 |
| `npm-v3-project-manager-sys` | https://github.com/rodlemus/project-manager-sys | complex | 18 |

---

### pnpm

#### v5.3 — `lockfileVersion: 5.3` (pnpm 6.x)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `pnpm-v5.3-sample-project` | https://github.com/pnpm/sample-project | minimal | 1 |
| `pnpm-v5.3-kit-prism-ssr-bug` | https://github.com/pngwn/kit-prism-ssr-bug | minimal | 7 |
| `pnpm-v5.3-authentication-expressJS` | https://github.com/GowriChelluri/authentication-expressJS | medium | 5 |
| `pnpm-v5.3-vue-alert` | https://github.com/damilaredevone/vue-alert | medium | 10 |
| `pnpm-v5.3-windicss-docs` | https://github.com/windicss/docs | complex | 43 |

#### v5.4 — `lockfileVersion: 5.4` (pnpm 7.x)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `pnpm-v5.4-rules-cypress` | https://github.com/aspect-build/rules_cypress | minimal | 1 |
| `pnpm-v5.4-jest-global-setup-esm` | https://github.com/segevfiner/jest-global-setup-esm | minimal | 9 |
| `pnpm-v5.4-vue-dock-menu` | https://github.com/prabhuignoto/vue-dock-menu | medium | 26 |
| `pnpm-v5.4-dotocracy-frontend` | https://github.com/blockcoders/dotocracy-frontend | complex | 22 |

#### v6.0 — `lockfileVersion: '6.0'` (pnpm 8.0–8.5)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `pnpm-v6.0-gondolin` | https://github.com/earendil-works/gondolin | minimal | 3 |
| `pnpm-v6.0-submit-jokes-ms` | https://github.com/ThusharaX/submit-jokes-ms | medium | 22 |
| `pnpm-v6.0-blog` | https://github.com/phenix3443/blog | complex | 29 |
| `pnpm-v6.0-vue` | https://github.com/vuejs/vue | complex | 43 |
| `pnpm-v6.0-ice` | https://github.com/alibaba/ice | complex | 36 |

#### v6.1 — `lockfileVersion: '6.1'` (pnpm 8.6+)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `pnpm-v6.1-lambda-with-layer` | https://github.com/wiput1999/lambda-with-layer | minimal | 11 |
| `pnpm-v6.1-lazy-collections` | https://github.com/RobinMalfait/lazy-collections | minimal | 9 |
| `pnpm-v6.1-speechy` | https://github.com/admildo/speechy | complex | 30 |

#### v9.0 — `lockfileVersion: '9.0'` (pnpm 9.x, 10.x)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `pnpm-v9.0-vaul-vue-bakasura` | https://github.com/nikcosmos/vaul-vue-bakasura | minimal | 6 |
| `pnpm-v9.0-dashboard-vite-react` | https://github.com/HichemBenChaaben/dashboard-vite-typescript-react-rq | medium | 25 |
| `pnpm-v9.0-pnpm` | https://github.com/pnpm/pnpm | medium | 27 |
| `pnpm-v9.0-calybook` | https://github.com/alwaysfullybooked/calybook | complex | 78 |
| `pnpm-v9.0-nuxt` | https://github.com/nuxt/nuxt | complex | 69 |
| `pnpm-v9.0-typescript-eslint` | https://github.com/typescript-eslint/typescript-eslint | complex | 53 |

---

### yarn

#### v1 classic — `# yarn lockfile v1` header

| Directory | GitHub | Complexity | Total Deps | Notes |
|---|---|---|---|---|
| `yarn-v1-parse-yarn-lockfile` | https://github.com/VincentBailly/parse-yarn-lockfile | minimal | 3 | |
| `yarn-v1-s-template` | https://github.com/SebastianWesolowski/s-template | medium | 19 | scoped @commitlint, @semantic-release |
| `yarn-v1-nexea-frontend` | https://github.com/NxTech4021/nexea-frontend | medium | 82 | also has package-lock.json |
| `yarn-v1-vite-examples` | https://github.com/wx-chevalier/vite-examples | complex | — | workspace monorepo, ~1MB lockfile |

#### Berry v3 — `__metadata: { version: 6, cacheKey: 8 }` (yarn 3.2+)

> Berry v2 lockfiles (`version: 4`) were not found in active public repos.

| Directory | GitHub | Complexity | Total Deps | yarn tool |
|---|---|---|---|---|
| `yarn-berry-v3-react-container` | https://github.com/namannehra/react-container | minimal | 13 | 3.5.1 |
| `yarn-berry-v3-landscapeapp` | https://github.com/cncf/landscapeapp | medium | 33 | 3.2.1 |
| `yarn-berry-v3-imagine` | https://github.com/kwsong0113/imagine | medium | 51 | 3.5.0 |

#### Berry v4 — `__metadata: { version: 8, cacheKey: 10 }` (yarn 4.x)

| Directory | GitHub | Complexity | Total Deps | yarn tool |
|---|---|---|---|---|
| `yarn-berry-v4-json-origami` | https://github.com/hacomono-lib/json-origami | minimal | 14 | 4.2.2 |
| `yarn-berry-v4-otto-app` | https://github.com/Joarell/otto-app | minimal | 8 | — |
| `yarn-berry-v4-open-mercato` | https://github.com/open-mercato/open-mercato | complex | 60 | 4.12.0 |
| `yarn-berry-v4-backstage` | https://github.com/backstage/backstage | complex | — | 4.x, monorepo |

---

### bun

#### Binary — `bun.lockb`

| Directory | GitHub | Complexity | Notes |
|---|---|---|---|
| `bun-binary-how-did-i-get-here` | https://github.com/hackclub/how-did-i-get-here | minimal | 15 deps, express/ejs/dotenv |
| `bun-binary-ai-pricing` | https://github.com/nuxdie/ai-pricing | minimal | React/Vite/Tailwind/shadcn |
| `bun-binary-ptimer-web` | https://github.com/pocka/ptimer-web | minimal | 16 deps |
| `bun-binary-rocket` | https://github.com/Rahuletto/rocket | medium | 21 deps |
| `bun-binary-bullmq-proxy` | https://github.com/taskforcesh/bullmq-proxy | medium | scoped @bullmq/* packages |
| `bun-binary-clapper` | https://github.com/jbilcke-hf/clapper | complex | monorepo, 9 workspaces |

#### Text — `bun.lock` (`"lockfileVersion": 1`)

| Directory | GitHub | Complexity | Total Deps |
|---|---|---|---|
| `bun-text-postgres-language-server` | https://github.com/supabase-community/postgres-language-server | minimal | 3 |
| `bun-text-elysia` | https://github.com/elysiajs/elysia | minimal | 23 |
| `bun-text-idonthavespotify` | https://github.com/sjdonado/idonthavespotify | medium | 32 |
| `bun-text-javascript-cheatsheet` | https://github.com/wilfredinni/javascript-cheatsheet | medium | 48 |
| `bun-text-hono` | https://github.com/honojs/hono | complex | 25+ devDeps, scoped @hono/* |
| `bun-text-todo-giga-potato` | https://github.com/lassestilvang/todo-giga-potato | complex | 58 |

---

### vlt

#### `vlt-lock.json`

| Directory | GitHub | Complexity | Notes |
|---|---|---|---|
| `vlt-vlt-monorepo` | https://github.com/hamlim/vlt-monorepo | minimal | 5 devDeps, turborepo monorepo |
| `vlt-nodeconfeu-2024-workshop` | https://github.com/vltpkg/nodeconfeu-2024-workshop | medium | many @astrojs/* scoped packages |
| `vlt-vltpkg` | https://github.com/vltpkg/vltpkg | complex | vlt itself, 5179-line lockfile |

---

## Coverage Summary

| Package Manager | Lockfile Version | Count | Complexity spread |
|---|---|---|---|
| npm | v1 | 3 | minimal / medium / medium |
| npm | v2 | 3 | minimal / minimal / medium |
| npm | v3 | 3 | medium / medium / complex |
| pnpm | v5.3 | 5 | minimal / minimal / medium / medium / complex |
| pnpm | v5.4 | 4 | minimal / minimal / medium / complex |
| pnpm | v6.0 | 5 | minimal / medium / complex / complex / complex |
| pnpm | v6.1 | 3 | minimal / minimal / complex |
| pnpm | v9.0 | 6 | minimal / medium / medium / complex / complex / complex |
| yarn | v1 classic | 4 | minimal / medium / medium / complex |
| yarn | berry v3 | 3 | minimal / medium / medium |
| yarn | berry v4 | 4 | minimal / minimal / complex / complex |
| bun | binary (bun.lockb) | 6 | minimal / minimal / minimal / medium / medium / complex |
| bun | text (bun.lock) | 6 | minimal / minimal / medium / medium / complex / complex |
| vlt | vlt-lock.json | 3 | minimal / medium / complex |
| **Total** | | **58** | |

### Not found / not collected
- **yarn berry v2** (`__metadata.version: 4`): No active public repos found; yarn 2.x lockfiles in the wild almost always show v6 (upgraded to 3.x behavior).
- **npm v4**: Does not exist as of April 2026.
- **pnpm v7/v8 lockfile**: These version numbers were never used; the scheme jumped from v6.1 to v9.0.
