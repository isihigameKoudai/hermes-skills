# Hermes Agent remote dashboard — verified knowledge bank

Condensed, citation-backed facts about running Hermes Agent headless on a VPS and
connecting Hermes Desktop from one or more Macs (or other clients) to it. Built from
the official docs at https://hermes-agent.nousresearch.com/docs/ and the Portal pricing
page, verified 2026-08. Use this when a source log is about installing Hermes Agent on
a remote host or wiring Desktop to it — so you do not re-derive the same corrections.

## Architecture (the shape that actually works)

```
Mac1 ──ssh -L 9119:127.0.0.1:9119──┐
Mac2 ──ssh -L 9119:127.0.0.1:9119──┼──▶ VPS: hermes dashboard (systemd, bind 127.0.0.1:9119)
Mac3 ──ssh -L 9119:127.0.0.1:9119──┘         └─▶ Nous Portal ─▶ LLMs
```

Desktop connects in **Remote gateway** mode to `http://127.0.0.1:9119` (the tunnel
exit). Each Mac runs its own independent SSH tunnel. State (memory, skills, sessions)
lives on the VPS in `~/.hermes/`, so every Mac shares one growing agent.

This shape is preferred because:
- Desktop's **Connect via SSH** mode is undocumented for remote backends; the docs'
  remote-connection section only describes **Remote gateway**.
- A non-loopback dashboard bind (`--host 0.0.0.0`) **always requires an auth provider**
  and the docs warn: never expose a password-protected dashboard to the open internet.
- SSH tunnels reuse the existing key auth and avoid opening a second firewall port.

## Service / unit names — get these right, they are the #1 time sink

| Wrong name (common guess) | Correct name | Notes |
|---|---|---|
| `hermes.service` | `hermes-gateway` | The messaging gateway. Profile-scoped: `hermes-gateway-<profile>`. |
| `hermes` (for `systemctl restart`) | `hermes-gateway` | `systemctl restart hermes` has never existed. |
| — | `hermes-dashboard` | Only if you create a **separate** unit for the dashboard. Not auto-registered. |

Install commands (these are the only supported paths):

```bash
sudo hermes gateway install --system   # Linux: boot-time system service
hermes gateway install                  # macOS: launchd user service (no sudo)
```

`hermes gateway migrate-legacy` removes leftover `hermes.service` units from pre-rename
installs; it never touches `hermes-gateway-<profile>` units.

Subcommand families of `hermes gateway`: `run` / `start` / `stop` / `restart` / `status`
/ `list` / `install` / `uninstall` / `setup` / `migrate-legacy` / `enroll`.

## Do NOT run `sudo hermes setup`

The setup wizard runs as the **regular user**. Prefixing it with `sudo` switches to
root's PATH and root's ownership, creating **root-owned files inside `/home/hermes/.hermes`**
that the `hermes` user can no longer write to — causing Permission denied later. If this
happens, repair with:

```bash
sudo chown -R hermes:hermes /home/hermes/.hermes
```

`/home/hermes` is the `hermes` user's own directory; this operation restores the correct
owner and does not lock root out (root can access anything regardless of owner).

For system-service registration, use **only** `sudo hermes gateway install --system`.
Everything else stays unprivileged.

## Config file facts

- Settings file: `~/.hermes/config.yaml` (**YAML**, not `.json`).
- Secrets file: `~/.hermes/.env` (API keys, bot tokens, dashboard auth, signing secrets).
- The terminal backend key is **`terminal.backend`**, value one of
  `local | docker | ssh | modal | daytona | vercel_sandbox | singularity` (7 backends).
- Do NOT hand-edit `config.yaml`. Use `hermes config set KEY VAL` — it routes secrets
  to `.env` and everything else to `config.yaml` automatically. A stray indent corrupts
  the file and can break the live gateway.

## Dashboard / Desktop remote connection — the deprecated and the current

### ❌ `HERMES_DASHBOARD_TUI` — removed

Commit `feat(dashboard): always enable embedded chat; remove dashboard --tui flag`
made the embedded chat pane (TUI over PTY/WebSocket) **always available**. The docs
now state: *"The Chat tab is part of every `hermes dashboard` launch — the embedded
browser chat pane (running the TUI over PTY/WebSocket) is always available, with no
extra flag required."* The env var is absent from the current env-var reference.

If a source log claims `HERMES_DASHBOARD_TUI=1` is required for WebSocket, that log is
out of date. Today, if `/api/ws` fails, suspect: missing `pty` extra (`ptyprocess`),
an inactive auth provider, or a CORS/origin mismatch — not a missing TUI flag.

### ❌ `HERMES_DASHBOARD_SESSION_TOKEN` — not a current env var

Absent from the current env-var reference. The current model is: sign in through an
auth provider, and Desktop reuses the resulting session for the WebSocket
automatically — *"there is no token to copy or paste."* If Desktop asks for a session
token instead of showing a Sign-in button, the auth provider is not active
(`/api/status` won't list it in `auth_providers`).

### ✅ Current auth providers (pick one for a non-loopback bind)

| Provider | Env vars / config | When to use |
|---|---|---|
| Username/password (basic) | `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `_PASSWORD` (or `_PASSWORD_HASH`) + `HERMES_DASHBOARD_BASIC_AUTH_SECRET` (stable signing key) | Trusted LAN / VPN only. Not for direct public exposure. |
| OAuth (Nous Portal) | `HERMES_DASHBOARD_OAUTH_CLIENT_ID` via `hermes dashboard register` | Internet-facing. Desktop shows "Sign in with Nous Research". |
| Self-hosted OIDC | `HERMES_DASHBOARD_OIDC_ISSUER` + `_CLIENT_ID` (+ optional `_SCOPES`) | Your own IdP (e.g. Keycloak). |

`HERMES_DASHBOARD_BASIC_AUTH_SECRET` must be a stable value (e.g.
`openssl rand -base64 32`); if blank, the signing key regenerates per boot and every
restart logs you out.

`--insecure` is **deprecated / no-op** — a public bind always requires an auth provider
and fails closed without one.

### ✅ Server-side systemd unit (dashboard, remote access)

```ini
[Unit]
Description=Hermes Dashboard
After=network.target

[Service]
Type=simple
User=hermes
WorkingDirectory=/home/hermes/.hermes
EnvironmentFile=/home/hermes/.hermes/.env
ExecStart=/home/hermes/.local/bin/hermes dashboard --no-open
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

`EnvironmentFile=` keeps secrets out of the unit file. For SSH-tunnel use, leave
`--host` at the default `127.0.0.1` (the auth gate does not engage, but the port is
unreachable from outside). For Tailscale, bind `--host <tailscale-ip>` to restrict to
the tailnet.

### ✅ Client-side (each Mac)

launchd agent at `~/Library/LaunchAgents/com.hermes.tunnel.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.hermes.tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>ssh</string><string>-L</string>
        <string>9119:127.0.0.1:9119</string>
        <string>-N</string><string>hermes@xserver</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardErrorPath</key><string>/tmp/hermes-tunnel.err</string>
    <key>StandardOutPath</key><string>/tmp/hermes-tunnel.out</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.hermes.tunnel.plist
launchctl list | grep hermes
```

Desktop settings: **Settings → Gateway → Remote gateway**, Remote URL
`http://127.0.0.1:9119`, then Sign in. `HERMES_DESKTOP_REMOTE_URL` env var overrides the
in-app URL (panel shows an "env override" badge). CORS allows localhost origins
(`:9119` / `:3000` / `:5173`); a custom port is auto-added. The SSH-tunnel-to-127.0.0.1
shape fits this constraint cleanly.

## Slack gateway — the scopes and events people forget

Hermes uses **Socket Mode** (WebSocket, no public URL). Generate the manifest with
the current Agent view (new apps require it):

```bash
hermes slack manifest --agent-view --write   # writes ~/.hermes/slack-manifest.json
```

Then paste at https://api.slack.com/apps → Create New App → From an app manifest.

**Required Bot Token Scopes** (the manifest covers all, but verify if hand-pasted):

`chat:write`, `app_mentions:read`, `channels:history`, `channels:read`,
`groups:history`, `im:history`, `im:read`, `im:write`, `mpim:history`, `mpim:read`,
`users:read`, `files:read`, `files:write`.

**Required event subscriptions**: `message.im`, `message.mpim`, `message.channels`,
`message.groups`, `app_mention`.

Two setup steps that silently break Slack if missed:
1. **Features → App Home → Show Tabs → Messages Tab ON** + check "Allow users to send
   Slash commands and messages from the messages tab". Without it, DMs are blocked
   entirely — this is a Slack platform requirement, not a Hermes bug.
2. **Bot must be invited to each channel** (`/invite @Hermes Agent`). Auto-join is off.

Classic Slack apps (RTM API) were deprecated March 2025. Old apps must be recreated.

`.env` entries:

```bash
SLACK_BOT_TOKEN=***       # xoxb-...
SLACK_APP_TOKEN=***       # xapp-...  (App-Level Token, scope connections:write)
SLACK_ALLOWED_USERS=...   # comma-separated Slack Member IDs (U... format)
SLACK_HOME_CHANNEL=...    # C... format, for cron/notifications
```

Common failure mode: **"works in DM, silent in channels"** = `message.channels`
event missing or `channels:history` scope missing.

## Nous Portal — pricing and what's bundled

Verified against https://portal.nousresearch.com/manage-subscription (2026-08):

| Plan | Monthly | Credits | Rollover cap |
|---|---|---|---|
| Free | $0 | $0 | — |
| Plus | $20 | $22 (+10%) | $10 |
| Super | $100 | $110 (+10%) | $50 |
| Ultra | $200 | $220 (+10%) | $100 |

Rollover is **capped per plan**, not unlimited. Credits can be topped up when exhausted.

One OAuth (`hermes setup --portal`) covers:
- 300+ models (Anthropic Claude, OpenAI GPT, Google Gemini, DeepSeek, Qwen, Kimi,
  GLM, MiniMax, xAI Grok, NVIDIA Nemotron, Tencent Hunyuan, Xiaomi MiMo, StepFun,
  Hermes-4, and 280+ more).
- **Tool Gateway** — 5 backends via one subscription: web search/extract (Firecrawl),
  image generation (FAL, 9 models), TTS (OpenAI), cloud browser automation (Browser
  Use), cloud terminal sandbox (Modal, optional add-on).
- No long-lived API keys in `.env` — the refresh token at `~/.hermes/auth.json` is the
  only credential; per-request JWTs are minted from it.

Per-tool routing can mix Nous Subscription and your own backends via `hermes tools`.

Headless/SSH OAuth: forward the loopback callback port from the Mac
(`ssh -L 8787:127.0.0.1:8787 hermes@xserver`), then run `hermes setup --portal` on the
VPS and open the displayed URL in the Mac's browser.

## Counts and platform surface (current)

- Bundled skills: ~90. Optional installable skills: ~60. Built-in tools: 60+.
- Messaging platforms: 21+ (19 native to the gateway + IRC and Microsoft Teams via
  plugins). Includes Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost,
  Email, SMS, Home Assistant, DingTalk, Feishu, WeCom, QQ Bot, LINE, Google Chat, etc.
- Terminal backends: 7 (`local`, `docker`, `ssh`, `modal`, `daytona`,
  `vercel_sandbox`, `singularity`).

## VPS sizing

Hermes does not run the model locally — it calls cloud APIs. CPU is light; RAM matters
more.

| Use | Recommended |
|---|---|
| Chat + messaging gateway | 1–2 vCPU / 2 GB RAM |
| Usual (skills + cron) | 2 vCPU / 2–4 GB RAM / 40 GB SSD |
| Heavy browser automation | 2 vCPU / 4 GB RAM+ |

Browser tooling and parallel subagents are the main RAM consumers.

## Common SSH/VPS setup notes (Xserver VPS specific, but generalizable)

- Xserver's **packet filter** blocks SSH(22) by default. Allow it in the control panel
  before connecting. Whitelist your IP for tighter security (note: consumer ISP IPs
  rotate; if SSH suddenly fails, suspect IP rotation first).
- Xserver auto-generates an SSH key at OS-install time; the private `.pem` downloads
  **once** via the browser. The management panel's "SSH Key registration" and "Public
  key view" do **not** re-issue the private key. If lost and the VPS is empty, the
  fastest fix is OS reinstall with "SSH Key: auto-generate".
- After OS reinstall, the host key changes → `ssh-keygen -R <IP>` clears the stale
  `known_hosts` entry, then reconnect and accept the new fingerprint.
- Xserver's key is registered to **root** only. To log in as a regular `hermes` user,
  copy `authorized_keys` and fix ownership/perms:

  ```bash
  adduser hermes && usermod -aG sudo hermes
  sudo mkdir -p /home/hermes/.ssh
  sudo cp /root/.ssh/authorized_keys /home/hermes/.ssh/
  sudo chown -R hermes:hermes /home/hermes/.ssh
  sudo chmod 700 /home/hermes/.ssh
  sudo chmod 600 /home/hermes/.ssh/authorized_keys
  ```

- `~/.ssh/config` alias on the Mac makes both terminal SSH and Desktop's SSH mode
  resolve the key automatically:

  ```text
  Host xserver
    HostName <VPS-IP>
    User hermes
    IdentityFile ~/.ssh/hermes-ssh.pem
  ```

## Troubleshooting quick reference (remote dashboard)

| Symptom | Likely cause | Fix |
|---|---|---|
| `Unit hermes.service not found` | Wrong unit name | Use `hermes-gateway` (or `hermes-dashboard` if you run a separate unit) |
| `sudo: hermes: command not found` | `sudo` drops user PATH | Don't `sudo hermes`. For service install use `sudo hermes gateway install --system` |
| Permission denied on `~/.hermes` files | `sudo hermes setup` left root-owned files | `sudo chown -R hermes:hermes ~/.hermes` |
| Desktop asks for session token, no Sign-in button | Auth provider inactive | Set BASIC_AUTH_USERNAME + PASSWORD (or HASH) in `.env`, confirm `/api/status` lists `"basic"` |
| Logged out after every restart | `HERMES_DASHBOARD_BASIC_AUTH_SECRET` blank | Set a stable `openssl rand -base64 32` value |
| WebSocket `/api/ws` fails, HTTP OK | `pty` extra missing, or auth provider inactive | `uv pip install -e ".[web,pty]"`; verify auth provider |
| `Could not reach this gateway` | URL port wrong or dashboard bound to 127.0.0.1 | Use full `http://127.0.0.1:9119` via SSH tunnel; or bind `--host 0.0.0.0` with auth |
| `Connection refused` / timeout | Firewall / 127.0.0.1 bind | Open SSH tunnel, or bind reachable address (with auth) |
| Slack bot silent in channels | `message.channels` event or `channels:history` scope missing | Re-paste full manifest or add them manually, then reinstall app |
| Slack DMs blocked | Messages Tab not enabled | App Home → Show Tabs → Messages Tab ON + slash/messages checkbox |
