# Lighthouse before/after for a migration

Run Lighthouse to produce a defensible performance delta, and to catch third-party costs that raw resource timing misses.

## Headless setup (no system Chrome)

- `npx --yes @puppeteer/browsers install chrome@stable --path <dir>` → binary at `<dir>/chrome/linux-*/chrome-linux64/chrome`.
- Lighthouse reads the `CHROME_PATH` env var, not a `--chrome-path` flag. Export it before running.
- Command: `CHROME_PATH=<chrome> npx --yes lighthouse <url> --chrome-flags="--headless --no-sandbox --disable-gpu --disable-dev-shm-usage" --output=json --output-path=report.json --only-categories=performance --quiet`.
- Mobile is the default (4x CPU + slow-4G simulation) and is where heavy third-party JS and slow image decode bite — treat it as the official CWV view. `--preset=desktop` is the unthrottled reference.

## Read TBT first

- Total Blocking Time is network-independent, so it isolates JS parse/eval cost from TTFB/latency. It is the cleanest before/after signal for removing scripts.
- FCP/LCP/TTI mix in network latency; compare them only when both sides are measured from the same host.

## What inflates LCP vs SI

- A CSS opacity fade-in on the hero (`.appear { opacity: 0 }` + a keyframe) inflates Speed Index (the page LOOKS empty for the animation duration) but often does NOT move LCP — Lighthouse counts an opacity-0 image as painted. "Remove the fade-in to fix LCP" is usually wrong; it fixes SI.
- The thing that actually inflates LCP is main-thread JS (a heavy third-party script) delaying the first paint of the LCP image. Remove the script first.

## Deprecated analytics is dead weight

- A Universal Analytics tag (`UA-xxxxx`) stopped collecting in July 2023 but still loads `gtag.js` (~125KB) plus a second `analytics.js` (~21KB) — enough to push mobile TBT into the seconds. If the only tag is `UA-`, deleting it is a pure win. GA4 (`G-xxx`) is a single ~50KB script with no second fetch.

## Network-matched before/after

- Production-vs-localhost is not a fair comparison (localhost TTFB ≈ 0). To isolate a code change, build BOTH versions and serve each with `python3 -m http.server <port> --directory dist` (launch with background=true), then Lighthouse each localhost port.
- A build-time-injected third-party script (analytics) only appears if its env var is set at build time. Reproduce production's "before" by rebuilding the old commit with the var set (e.g. `GA=UA-xxx <build>`); otherwise the "before" silently lacks the very script being removed and the comparison shows nothing.
