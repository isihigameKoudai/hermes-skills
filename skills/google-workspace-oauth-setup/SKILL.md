---
name: google-workspace-oauth-setup
description: "Set up Google Workspace OAuth on Hermes."
version: 1.0.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Google, OAuth, authentication, setup, Sheets, Drive, Docker]
    related_skills: [google-workspace]
---

# Google Workspace OAuth Setup

Use when setting up Google Workspace (Sheets, Drive, Gmail, Calendar) access in Hermes for the first time, or when OAuth auth fails.

## Key Insight

**If Hermes runs in Docker, OAuth setup MUST complete on the host machine.** The Docker container and host filesystem are separate; tokens generated inside Docker won't persist. Always run `setup.py` commands (Steps 1-5 below) on your Mac/Linux host, not inside `hermes chat` or the Docker terminal.

## Procedure — First-Time Setup

### Step 1: Create OAuth 2.0 Credentials

On your host machine:

1. Go to https://console.cloud.google.com/projectselector2/home/dashboard
2. Create a new project or select existing
3. Enable APIs in Library:
   - **Google Sheets API**
   - **Google Drive API**
   - (Add others if needed: Gmail API, Calendar API, etc.)
4. Go to Credentials: https://console.cloud.google.com/apis/credentials
5. Create OAuth 2.0 Client ID:
   - **Application type: MUST be "Desktop app"** (not "Web application")
   - Click Create
6. Download the JSON file → save to `~/.hermes/client_secret_XXXXX.json`

### Step 2: Authorize the Client Secret

On your **host machine** (Mac/Linux):

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --client-secret ~/.hermes/client_secret_XXXXX.json
```

Output: `OK: Client secret saved to ~/.hermes/google_client_secret.json`

### Step 3: Add Test User (if app in Testing mode)

If you see "Unverified app" or "access_denied" errors:

1. Go to OAuth consent screen: https://console.cloud.google.com/auth/audience
2. Click "Test users"
3. Add your Gmail address exactly as you'll use it
4. Save

### Step 4: Get Authorization URL

On your **host machine**:

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --auth-url
```

Copy the output URL (starts with `https://accounts.google.com/o/oauth2/auth?...`)

### Step 5: Complete Authorization Flow

1. Paste the URL into your browser
2. Log in with your Gmail account
3. Select scopes (Sheets + Drive minimum; see table below)
4. After approval, browser shows error page — this is normal
5. Copy the **entire URL from the address bar** (e.g., `http://localhost:1/?code=4/0A...&scope=...`)

On your **host machine**:

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --auth-code "PASTE_THE_URL_HERE"
```

Output: `OK: Authorization successful`

### Step 6: Verify

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --check
```

Should print: `AUTHENTICATED`

Token is now at `~/.hermes/google_token.json` on the host and will auto-sync to Docker on next Hermes run.

## Scope Selection (Step 5)

When the browser prompts you to select scopes, check only what you need:

| Use Case | Scopes to Enable |
|----------|-----------------|
| **Sheets + Drive (typical)** | Google Sheets API, Google Drive API |
| Sheets + Drive + Gmail | Add Gmail API |
| Full Workspace | Gmail, Calendar, Drive, Sheets, Docs, Contacts |

For Sheets-only portfolio tracking, select **Sheets + Drive only**.

## Troubleshooting

### "Invalid application type" or "redirect_uri_mismatch"

**Cause**: OAuth client is "Web application" instead of "Desktop app".

**Fix**:
1. Delete the old credentials in Google Cloud Console
2. Create NEW OAuth 2.0 Client ID with **Application type = Desktop app**
3. Download new JSON
4. Re-run Step 2 with the new file

### "Error 403: access_denied" or "Unverified app"

**Cause**: OAuth app is in Testing mode and your email is not a test user.

**Fix**: Complete Step 3 above (add yourself as test user), then retry.

### "No token at /root/.hermes/google_token.json" in Docker

**Cause**: You tried to run `setup.py` inside Docker. Token must be generated on the host.

**Fix**: Run Steps 1-6 on your Mac/Linux host machine, not inside `hermes chat`. Token auto-syncs to Docker.

### "AUTHENTICATED (partial)" or scopes missing

**Cause**: Auth didn't grant all scopes you need.

**Fix**:
```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --revoke
# Then redo Steps 4-6 above
```

### "Client secret not found" in Docker after setup on host

**Cause**: Docker sees a stale filesystem snapshot. Restart Hermes.

**Fix**:
```bash
hermes doctor
# If needed:
hermes --force-restart
```

Then verify: `$GSETUP --check` (in Docker) should print `AUTHENTICATED`.

## Pitfalls

- ❌ Don't run `setup.py` inside Docker (`hermes chat -q "...setup.py..."`). Run it on the host.
- ❌ Don't use "Web application" type. Must be "Desktop app".
- ❌ Don't skip adding test users if the app is in Testing mode.
- ❌ Don't paste just the auth URL into the browser address bar as-is — the first run generates it, you open it, then paste the **result** URL back to `--auth-code`.

## Next Steps

Once `setup.py --check` returns `AUTHENTICATED`:

```bash
# Verify Sheet access from Docker
GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI sheets get "YOUR_SHEET_ID" "Sheet1!A1:D10"
```

If that works, you're ready to use the `google-workspace` skill in cronjobs and agent tasks.
