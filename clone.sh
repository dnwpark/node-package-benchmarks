#!/usr/bin/env bash
set -euo pipefail

REPOS_DIR="$(cd "$(dirname "$0")" && pwd)/repos"
mkdir -p "$REPOS_DIR"

clone() {
  local name="$1"
  local url="$2"
  if [ -d "$REPOS_DIR/$name/.git" ]; then
    echo "skip  $name"
  else
    echo "clone $name"
    git clone --depth=1 "$url" "$REPOS_DIR/$name"
  fi
}

# ── npm ──────────────────────────────────────────────────────────────────────

# v1
clone "npm-v1-rebrote-not-open"            "https://github.com/fabitky/Rebrote-not-open"
clone "npm-v1-stackcv"                     "https://github.com/cobluwu/StackCV"
clone "npm-v1-chanterelle-halogen-template" "https://github.com/f-o-a-m/chanterelle-halogen-template"

# v2
clone "npm-v2-react-keys"                  "https://github.com/arunpraba/react-keys"
clone "npm-v2-vitejs-vite-z4gujs"          "https://github.com/Mayandev/vitejs-vite-z4gujs"
clone "npm-v2-codedit-web"                 "https://github.com/satr14washere/codedit-web"

# v3
clone "npm-v3-projectf5-zootopia-frontend" "https://github.com/ZooDevelopers/ProjectF5-Zootopia-Frontend"
clone "npm-v3-auth"                        "https://github.com/Aryankumar12/auth"
clone "npm-v3-project-manager-sys"         "https://github.com/rodlemus/project-manager-sys"

# ── pnpm ─────────────────────────────────────────────────────────────────────

# v5.3
clone "pnpm-v5.3-sample-project"           "https://github.com/pnpm/sample-project"
clone "pnpm-v5.3-kit-prism-ssr-bug"        "https://github.com/pngwn/kit-prism-ssr-bug"
clone "pnpm-v5.3-authentication-expressJS" "https://github.com/GowriChelluri/authentication-expressJS"
clone "pnpm-v5.3-vue-alert"               "https://github.com/damilaredevone/vue-alert"
clone "pnpm-v5.3-windicss-docs"           "https://github.com/windicss/docs"

# v5.4
clone "pnpm-v5.4-rules-cypress"           "https://github.com/aspect-build/rules_cypress"
clone "pnpm-v5.4-jest-global-setup-esm"   "https://github.com/segevfiner/jest-global-setup-esm"
clone "pnpm-v5.4-vue-dock-menu"           "https://github.com/prabhuignoto/vue-dock-menu"
clone "pnpm-v5.4-dotocracy-frontend"      "https://github.com/blockcoders/dotocracy-frontend"

# v6.0
clone "pnpm-v6.0-gondolin"                "https://github.com/earendil-works/gondolin"
clone "pnpm-v6.0-submit-jokes-ms"         "https://github.com/ThusharaX/submit-jokes-ms"
clone "pnpm-v6.0-blog"                    "https://github.com/phenix3443/blog"
clone "pnpm-v6.0-vue"                     "https://github.com/vuejs/vue"
clone "pnpm-v6.0-ice"                     "https://github.com/alibaba/ice"

# v6.1
clone "pnpm-v6.1-lambda-with-layer"       "https://github.com/wiput1999/lambda-with-layer"
clone "pnpm-v6.1-lazy-collections"        "https://github.com/RobinMalfait/lazy-collections"
clone "pnpm-v6.1-speechy"                 "https://github.com/admildo/speechy"

# v9.0
clone "pnpm-v9.0-vaul-vue-bakasura"       "https://github.com/nikcosmos/vaul-vue-bakasura"
clone "pnpm-v9.0-dashboard-vite-react"    "https://github.com/HichemBenChaaben/dashboard-vite-typescript-react-rq"
clone "pnpm-v9.0-pnpm"                    "https://github.com/pnpm/pnpm"
clone "pnpm-v9.0-calybook"                "https://github.com/alwaysfullybooked/calybook"
clone "pnpm-v9.0-nuxt"                    "https://github.com/nuxt/nuxt"
clone "pnpm-v9.0-typescript-eslint"       "https://github.com/typescript-eslint/typescript-eslint"

# ── yarn ─────────────────────────────────────────────────────────────────────

# v1 classic
clone "yarn-v1-parse-yarn-lockfile"        "https://github.com/VincentBailly/parse-yarn-lockfile"
clone "yarn-v1-s-template"                 "https://github.com/SebastianWesolowski/s-template"
clone "yarn-v1-nexea-frontend"             "https://github.com/NxTech4021/nexea-frontend"
clone "yarn-v1-vite-examples"              "https://github.com/wx-chevalier/vite-examples"

# berry v3 (__metadata version: 6, cacheKey: 8)
clone "yarn-berry-v3-react-container"      "https://github.com/namannehra/react-container"
clone "yarn-berry-v3-landscapeapp"         "https://github.com/cncf/landscapeapp"
clone "yarn-berry-v3-imagine"              "https://github.com/kwsong0113/imagine"

# berry v4 (__metadata version: 8, cacheKey: 10)
clone "yarn-berry-v4-json-origami"         "https://github.com/hacomono-lib/json-origami"
clone "yarn-berry-v4-otto-app"             "https://github.com/Joarell/otto-app"
clone "yarn-berry-v4-open-mercato"         "https://github.com/open-mercato/open-mercato"
clone "yarn-berry-v4-backstage"            "https://github.com/backstage/backstage"

# ── bun ──────────────────────────────────────────────────────────────────────

# binary (bun.lockb)
clone "bun-binary-how-did-i-get-here"      "https://github.com/hackclub/how-did-i-get-here"
clone "bun-binary-ai-pricing"              "https://github.com/nuxdie/ai-pricing"
clone "bun-binary-ptimer-web"              "https://github.com/pocka/ptimer-web"
clone "bun-binary-rocket"                  "https://github.com/Rahuletto/rocket"
clone "bun-binary-bullmq-proxy"            "https://github.com/taskforcesh/bullmq-proxy"
clone "bun-binary-clapper"                 "https://github.com/jbilcke-hf/clapper"

# text (bun.lock, lockfileVersion: 1)
clone "bun-text-postgres-language-server"  "https://github.com/supabase-community/postgres-language-server"
clone "bun-text-elysia"                    "https://github.com/elysiajs/elysia"
clone "bun-text-idonthavespotify"          "https://github.com/sjdonado/idonthavespotify"
clone "bun-text-javascript-cheatsheet"     "https://github.com/wilfredinni/javascript-cheatsheet"
clone "bun-text-hono"                      "https://github.com/honojs/hono"
clone "bun-text-todo-giga-potato"          "https://github.com/lassestilvang/todo-giga-potato"

# ── vlt ──────────────────────────────────────────────────────────────────────

clone "vlt-vlt-monorepo"                   "https://github.com/hamlim/vlt-monorepo"
clone "vlt-nodeconfeu-2024-workshop"       "https://github.com/vltpkg/nodeconfeu-2024-workshop"
clone "vlt-vltpkg"                         "https://github.com/vltpkg/vltpkg"

echo "done"
