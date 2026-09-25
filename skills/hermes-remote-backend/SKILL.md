---
name: hermes-remote-backend
description: "Use when Hermes runs on a remote VPS backend, not locally."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, remote, vps, ssh-backend, desktop, file-delivery, gateway, split-runtime]
---

# Hermes Remote Backend (VPS + remote desktop)

Operating Hermes with the **agent/gateway on a VPS** and a **desktop client (or SSH) on another machine**. This is the user's stable setup: Hermes runs on a VPS; the desktop app on a Mac connects remotely (typically over Tailscale).

The generic `hermes-agent` skill covers config/theming/spawning across all surfaces. This skill covers the *split-brain* concerns unique to a remote backend: where tools actually execute, and why file delivery sometimes fails.

## When to Use

- The user asks about a VPS-hosted Hermes + remote desktop/SSH topology, or "can the backend touch my local files?".
- A delivered file fails to download with `Couldn't fetch ... from the gateway`.
- You need to reason about *where* terminal/file tools execute in a remote setup.
- The user is installing or verifying a plugin that has both a Python backend and a Desktop widget (see the "Installing plugins" section).

## Mental model: two kinds of "connected" — do not conflate

| Concept | What it does | Where tools run |
|---|---|---|
| **Desktop → remote backend connection** | The Electron app streams the agent UI over a WebSocket (`/api/ws`) to the VPS gateway. UI only. | **On the backend (VPS).** Mac files are untouched. |
| **Tool execution location** | Set by `terminal.backend` on the machine running the agent. | Backend setting decides. |

Connecting the desktop to a remote backend does **not** give the agent access to local Mac files. `read_file`/`write_file`/`terminal`/`patch`/`search_files` all execute on whatever `terminal.backend` resolves to.

## "Remote brain, local hands" (split-runtime) is NOT implemented

The user repeatedly wants: VPS keeps skills/memory/reasoning, but terminal/file/browser tools run on the local Mac. This is **"split-runtime"** and it is **not yet natively supported**:

- GitHub issue [#18715](https://github.com/NousResearch/hermes-agent/issues/18715) "Support remote Hermes agent with local tool execution".
- PR #21223 only *documented* server-side execution; the actual split-runtime PR [#63966](https://github.com/NousResearch/hermes-agent/pull/63966) is still open.

Do not claim it's supported. Do not promise a config that makes it work natively.

### Workaround: SSH terminal backend in *reverse* direction

`terminal.backend: ssh` is designed as "agent local, commands remote", but pointing it *back* at the Mac gives VPS-brain + Mac-hands:

```yaml
terminal:
  backend: ssh
  ssh_host: <Mac Tailscale IP>
  ssh_user: <mac username>
  ssh_port: 22
  ssh_key: /root/.ssh/id_ed25519
  cwd: /Users/<macuser>/workspace   # path ON the Mac
  persistent_shell: true
```

Requirements: Mac **Remote Login** enabled (System Settings → General → Sharing → Remote Login), passwordless SSH key auth, and reachability (use **Tailscale**/WireGuard, not public exposure). Env-var form also works: `TERMINAL_SSH_HOST`, `TERMINAL_SSH_USER`.

**Caveat:** the SSH backend treats the remote as a sandbox and pushes `~/.hermes/` state (credentials, skills, cache) into it during the session ("Remote-to-Host State Sync on Teardown"). In reverse direction this can copy VPS credentials onto the Mac — verify with a read-only command first, and mind what you expose.

**Verify, don't assume:** `terminal` definitely routes over SSH; confirm `read_file`/`write_file`/`patch` follow the same backend with a `pwd` + small-file write test before trusting it for a real job.

## Installing plugins that have a backend + desktop widget (split-runtime)

Most plugins ship two halves: a Python backend under `<HERMES_HOME>/plugins/<name>/` (loaded by the gateway at process start) and a Desktop widget under `<HERMES_HOME>/desktop-plugins/<name>/plugin.js` (read by Electron on the app machine). A plugin's `./install.sh` installs **both halves onto the machine it runs on** — it has no notion of the split.

In split-runtime (VPS gateway + Mac desktop):
- Run the installer **on the VPS** (via SSH) — that lands the backend beside the gateway, which is correct. But it also strands the widget on the VPS.
- Then **scp the widget half to the Mac**, because Electron reads it there, not from the VPS:
  `mkdir -p ~/.hermes/desktop-plugins/<name> && scp hermes@<vps>:/home/hermes/.hermes/desktop-plugins/<name>/plugin.js ~/.hermes/desktop-plugins/<name>/plugin.js`
  (copy `version.json` too if the plugin writes one — it drives the widget's update self-check).
- Restart **both halves independently**. Restarting the desktop app reloads only the widget; the Python backend mounts at gateway process start, so the VPS gateway must be restarted separately (systemd / however it's managed). A Mac app restart alone does NOT restart the VPS gateway.
- Verify on the gateway, never the sandbox: `ssh hermes@<vps> 'hermes plugins doctor <name> && hermes <plugin-subcommand>'`. The sandbox has no `hermes` CLI and its `plugins/`/`desktop-plugins/` are NOT bind-mounted (only attachments/skills/images/cache are), so you can neither run the plugin commands nor inspect the installed plugin from there — confirm install state over SSH instead.

## Gateway file delivery — the non-media download bug

**Symptom:** clicking a delivered file link shows
`Couldn't fetch {filename} from the gateway (missing, unreadable, or too large).`

**Root cause (verified, GitHub [#89713](https://github.com/NousResearch/hermes-agent/issues/89713)):** when the gateway has `auth_required: true`, non-media files (`.zip` `.docx` `.pdf` `.csv` `.xlsx` …) fail to download. The Electron app sends `X-Hermes-Session-Token`, but `gated_auth_middleware` ignores that header (only checks `Authorization` bearer / cookies) → 401 → this generic error. Media files (image/audio/video) use a different fetch path and work fine.

**The message is misleading — "missing/unreadable/too large" is a 401, not the file's fault.** Always verify the file is actually intact before blaming it:

```bash
find / -name '<filename>' 2>/dev/null
stat -c '%s bytes' <path>
unzip -l <path>          # for zips
```

Fixes, in order:
1. **Immediate (no code change):** the file exists on the backend. `scp <user>@<vps_ip>:<path> ~/Downloads/` from the Mac. Confirm the host-visible path — inside the terminal backend the file may be at `/workspace/...`; the host may differ, so `find` on the host if the scp 404s.
2. **Root cause:** run `hermes update` on the host — PR [#89013](https://github.com/NousResearch/hermes-agent/pull/89013) ("authenticate gated file downloads for password remotes") may already fix it.
3. **Patch:** add `X-Hermes-Session-Token` recognition to `gated_auth_middleware` (see `references/gateway-file-delivery.md`).
4. **Stopgap:** `auth_required: false` — only if the gateway is NOT internet-exposed (Tailscale-only is fine).

## Pitfalls

- **The terminal backend is a Docker sandbox *inside* the VPS; the gateway/agent runs on the VPS *host*, outside it.** From the sandbox you can find/diagnose files but cannot run `hermes update` or patch the host gateway — that must happen on the host. Don't claim you applied a fix you only verified from the sandbox.
- **The Docker sandbox does NOT inherit `~/.hermes/.env`** (verified: only ~16 env vars, none of the host's API keys). To pass a secret to `terminal`/`execute_code`, either list it in `terminal.docker_forward_env` (resolves from `.env`, value never enters config) or declare `required_environment_variables:` in the skill frontmatter (auto-merged). The forward is applied at container creation, so a gateway restart + new session is needed after adding a key.
- **Re-sending `MEDIA:` won't dodge the download bug** — it hits the same 401 for non-media files. Give the `scp` path instead.
- **A `@folder:` reference to a Mac path never reaches the sandbox.** The desktop app expands it locally; when the path is outside the configured allowed workspace you get only a `path is outside the allowed workspace` context warning with no file contents. Don't stall or ask immediately — previous sessions often left a working mirror of the same material on the VPS (`/workspace/`, `/root/`, or a project subdir). `ls` those first; if you find the mirror, say plainly you worked from the VPS mirror and list which files, then ask the user to flag anything missing.
- The user's standing preference (see memory): when file delivery silently fails, resolve the **concrete path** (find + scp), never a "copy from chat" workaround.

## Verified sandbox↔host mapping (this user's VPS)

Confirmed via `/proc/self/mountinfo` from inside the terminal backend. Files the agent writes to `/workspace/...` are host-visible at the exact path below — no `find` guessing needed:

| Inside sandbox | On the VPS host |
|---|---|
| `/workspace` | `/home/hermes/.hermes/sandboxes/docker/default/workspace` |
| `/root` | `/home/hermes/.hermes/sandboxes/docker/default/home` |

- SSH key auth for the `hermes` user is configured; `scp hermes@<vps-ip>:/home/hermes/.hermes/sandboxes/docker/default/workspace/... ~/Downloads/` works from the Mac.
- From inside the sandbox you CANNOT reach `/home/hermes/.ssh` (no mount, no docker.sock), so adding SSH keys / editing host `authorized_keys` must happen from an existing host session (root console or a working SSH user).
- **Skills tree is `ro` in the sandbox.** `/root/.hermes/skills` is a read-only bind mount of the host's `/home/hermes/.hermes/skills/` (verify: `grep -E '/root|/skills' /proc/self/mountinfo`). The agent reads skills but cannot write them from the sandbox; `skill_manage` writes happen host-side.
- **`~/.hermes/scripts/` is NOT mounted into the sandbox.** Cron `script` paths resolve under the HOST `$HERMES_HOME/scripts/`; a sandbox write to `/root/.hermes/scripts/` lands elsewhere and the cron creation fails its script-existence check ("Script file not found"). To place a script on the host: write it to `/workspace/` (rw), then have the user `cp` it over SSH. Full recipe: `references/skill-sharing-and-backup.md`.
- **No `hermes` CLI, no docker.sock, no SSH keys inside the sandbox** — cannot run `hermes …` against the host backend or reach `/home/hermes/.ssh`. Host-side work needs the user's SSH session.
- When `MEDIA:`/gateway download fails, the fastest working fallback is uploading from the sandbox to tmpfiles.org (`curl -F file=@x https://tmpfiles.org/api/v1/upload`, then extract the `/dl/...` href from the returned HTML page). Prefer scp — tmpfiles links expire.
- To answer "what did past sessions change in my skills", read the curator audit trail under `/root/.hermes/skills/` — see `references/skill-change-history.md` for the three sources (ledger / usage telemetry / backups) and the backfill caveats.

### Read-only skills mount + cron script placement

- `/root/.hermes/skills` is a **read-only (`ro`) bind mount** of the real `/home/hermes/.hermes/skills` (verify with `grep '/root' /proc/self/mountinfo`). From the sandbox you can read skills but NOT write them — `git init`/edits to skills must happen on the host (via a cron job or the user's SSH), never from the sandbox terminal.
- The sandbox's `/root/.hermes/scripts` is NOT bind-mounted — it is a different tree from the host's `~/.hermes/scripts/`. A `write_file` under `/root/.hermes/scripts/` does NOT reach where cron looks.
- Cron **scripts run on the host** (the gateway/scheduler side). `cronjob` `script:` resolves under the cron process's `$HERMES_HOME/scripts/` (= `/home/hermes/.hermes/scripts/`), and `action='create'` FAILS if that file doesn't already exist there.
- To place a host file from the sandbox: `write_file` it under `/workspace` (rw mount → host `/home/hermes/.hermes/sandboxes/docker/default/workspace/`), then have the user copy it into place: `ssh hermes@<vps-ip> 'mkdir -p ~/.hermes/scripts && cp /home/hermes/.hermes/sandboxes/docker/default/workspace/<file> ~/.hermes/scripts/ && chmod +x ~/.hermes/scripts/<file>'`.
- `no_agent: true` cron jobs make **zero LLM/API calls** (verified: `API calls: 0`) — use them for pure-shell recurring work (e.g. a `git init && git commit` autocommit of the skills tree) to avoid Nous Portal credit spend. A proven self-initialising autocommit script is in `templates/git-autocommit-skills.sh`; create it with `deliver: local` so no notification fires, and keep the script silent (empty stdout) when nothing changed.
- Reading the host-owned `.git` from the sandbox (as root) fails with `fatal: detected dubious ownership in repository` — inspect it with `git -c safe.directory='*' log` (or `-C <dir> -c safe.directory='*'`). The skills repo lives at the real `/home/hermes/.hermes/skills/.git`, visible read-only under `/root/.hermes/skills/.git`. The git owner is the host user, not sandbox root — hence the ownership guard.
