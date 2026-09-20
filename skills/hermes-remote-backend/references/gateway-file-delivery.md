# Gateway file delivery bug — detailed reproduction & fix

Symptom string (exact): `Couldn't fetch {filename} from the gateway (missing, unreadable, or too large).`

Verified against GitHub issue [#89713](https://github.com/NousResearch/hermes-agent/issues/89713) — "Desktop app cannot download non-media files (.docx, .pdf, etc.) from gateway — X-Hermes-Session-Token header ignored when auth_required=true".

## Root cause

Two download endpoints and two auth middlewares disagree on which auth header to accept:

| Endpoint | Used by | Size limit | Accepts `?token=` |
|---|---|---|---|
| `/api/files/download` (older) | `mediaExternalUrl()` — browser/OS link | 100 MB | yes |
| `/api/fs/download` (newer) | `saveGatewayFile()` — Electron download dialog | none (streaming) | no |
| `/api/fs/read-data-url` (fallback) | `saveGatewayFileViaDataUrl()` | 16 MB | no |

Two middlewares:

1. `auth_middleware` (`web_server.py:819`) — checks `X-Hermes-Session-Token`. **But when `auth_required` is true it returns early (~line 830-831) without the check**, delegating to the gated middleware.
2. `gated_auth_middleware` (`dashboard_auth/middleware.py:323`) — checks `Authorization` bearer and session cookies. **Does not check `X-Hermes-Session-Token`.**

The Electron client (`downloadViaTokenToFile`, `apps/desktop/electron/main.ts`) sends the token as `X-Hermes-Session-Token`. So under `auth_required: true`, the header is ignored by *both* middlewares → 401 → the generic error.

## Reproduction

1. Gateway configured with `auth_required: true` (basic or OAuth).
2. Agent delivers a non-media file via `MEDIA:/path/to/file.zip`.
3. Click the download link in desktop chat → error.

Media files (image/audio/video) are unaffected because they fetch through a different path.

## Manual fix (patch to `hermes_cli/dashboard_auth/middleware.py`)

In `gated_auth_middleware`, after the public-path check and before the bearer check:

```python
session_header = request.headers.get("X-Hermes-Session-Token", "")
if session_header:
    import hmac
    from hermes_cli.web_server import _SESSION_TOKEN
    if hmac.compare_digest(session_header.encode(), _SESSION_TOKEN.encode()):
        return await call_next(request)
```

## Verification matrix (from the issue author)

| Test | Before | After |
|---|---|---|
| No auth header | 401 | 401 (still blocked) |
| `X-Hermes-Session-Token` (valid) | 401 | **200 OK** (file served) |
| `X-Hermes-Session-Token` (wrong) | 401 | 401 (still blocked) |
| `/api/fs/read-data-url` (valid) | 401 | **200 OK** |

Note: an overlapping PR, [#89013](https://github.com/NousResearch/hermes-agent/pull/89013) ("authenticate gated file downloads for password remotes"), may supersede this manual patch — check whether `hermes update` already ships it before hand-editing.

## Secondary inconsistency

`_QUERY_TOKEN_API_PATHS` only contains the older `/api/files/download`. The newer `/api/fs/download` and `/api/fs/read-data-url` do not accept `?token=` query auth. Not required to fix the reported bug, but relevant if you harden the download path further.
