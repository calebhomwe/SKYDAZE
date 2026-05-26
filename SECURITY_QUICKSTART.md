# FTC Security Quickstart — Where Secrets Live

> **TL;DR:** *Never raw on GitHub.* Three safe homes for keys. Pick by use case.
>
> If you ever paste a key into a chat, a commit, or a screenshot — rotate it
> on the provider dashboard within 10 minutes. Cheaper than a breach.

---

## The three safe places

### 1. Local `.env` (for dev on your laptop)

```bash
cp .env.example .env
# open .env, paste your keys, save
```

`.env` is already in `.gitignore` — git refuses to track it. Python reads it
via `python-dotenv`. This is the right home for `make scrape-real`,
`make test-real`, `python generate_collection.py`, `python workers/render_worker.py`.

### 2. GitHub Encrypted Secrets (for CI / Actions)

`Repo → Settings → Secrets and variables → Actions → New repository secret`

Add each key by name (same names as in `.env.example`): `FAL_KEY`,
`OPENROUTER_API_KEY`, etc. They are encrypted at rest by GitHub, only
decrypted inside a workflow run, and **never visible to anyone with read
access to the repo** — including reviewers and forks.

Reference them in workflows like this:

```yaml
- run: python workers/render_worker.py
  env:
    FAL_KEY: ${{ secrets.FAL_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 3. Claude Code on the Web — Environment env vars (for this sandbox)

The same browser session you're using now has an **Environment Settings**
page. Add your keys there and every future session in this environment
auto-receives them as env vars — meaning `python scraper.py` will hit real
Firecrawl without you ever pasting a key into chat.

Docs: <https://code.claude.com/docs/en/claude-code-on-the-web>

---

## NEVER, under any circumstance

- Commit `.env` to GitHub. (gitignored on purpose; do not `git add -f` it.)
- Paste a key into a public chat, screenshot, or Loom video.
- Hardcode a key into Python / YAML / JSON.
- Email or DM keys.
- Share an n8n encryption key between machines.

## If a key leaks

1. Open the provider dashboard (Fal, OpenRouter, Anthropic, Shopify, etc.).
2. Revoke the key. Generate a new one.
3. Update `.env` (and GitHub Secrets, and n8n .env) with the new value.
4. Check `git log` and run `git rev-list --all | xargs git grep -l <prefix>`
   to confirm no historical leak.
5. If exposed in a public commit, force-rotate **everything** the leaked key
   could touch.

## For hosted n8n / production

Use platform secret stores:

- **Hetzner / VPS:** systemd `EnvironmentFile=/etc/ftc/env` (`chmod 600`)
- **Railway / Render:** dashboard env vars (encrypted, scoped to project)
- **Fly.io:** `fly secrets set FAL_KEY=...`
- **Cloudflare / Vercel:** project env vars (encrypted)

Mirror the same names as `.env.example` so code never changes between
environments.

## What FTC enforces automatically

- `security-sentinel` (FTC-005) scans every artifact for credential patterns
  before any push.
- `forbidden-term-detector` (FTC-059) blocks secrets that accidentally land
  in prompts.
- Pre-commit hook (optional, recommended): install `pre-commit` +
  `detect-secrets` for a final guard.

```bash
pip install pre-commit detect-secrets
pre-commit install
```
