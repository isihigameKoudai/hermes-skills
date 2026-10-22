#!/usr/bin/env node
// Normalized text/img/href diff of a built static site against live production HTML.
//
// Usage: node compare-site.cjs <live-dir> <dist-dir> [pages...]
//   <live-dir>  directory containing live-<page>.html files
//   <dist-dir>  built site (Astro dist/, or any static output)
//   pages       page names; default: index profile portfolio plan contact
//
// Fetch live pages first:
//   for p in profile portfolio plan contact; do \
//     curl -sL "https://example.com/$p/" -o "$LIVE_DIR/live-$p.html"; done
//   curl -sL "https://example.com/" -o "$LIVE_DIR/live-index.html"
//
// Every reported diff must be EXPLAINABLE before you claim "identical":
//   - text:    hidden/conditional elements (v-if / display:none) present in one but not the other
//   - images:  URL-scheme change only (hashed /_nuxt/img vs plain /portfolio/...) — same files
//   - hrefs:   trailing-slash normalization (/contact vs /contact/) — same destination

const fs = require('fs')
const path = require('path')

const [liveDir, distDir, ...rest] = process.argv.slice(2)
const pages = rest.length ? rest : ['index', 'profile', 'portfolio', 'plan', 'contact']
if (!liveDir || !distDir) {
  console.error('usage: node compare-site.cjs <live-dir> <dist-dir> [pages...]')
  process.exit(2)
}

function strip(html) {
  return html
    .replace(/<head[\s\S]*?<\/head>/i, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
}

function textOf(html) {
  return strip(html)
    .replace(/<[^>]+>/g, ' ')
    .replace(/&(amp|lt|gt|#39|quot|nbsp);/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function attrOf(html, tag, attr) {
  const re = new RegExp(`<${tag}[^>]*\\b${attr}="([^"]*)"`, 'g')
  return [...strip(html).matchAll(re)].map((m) => m[1])
}

function firstTextDiff(a, b) {
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    if (a[i] !== b[i]) {
      return `@${i}:\n   live: …${a.slice(Math.max(0, i - 40), i + 60)}…\n   mine: …${b.slice(Math.max(0, i - 40), i + 60)}…`
    }
  }
  return ''
}

let fail = false
for (const p of pages) {
  const liveFile = path.join(liveDir, `live-${p}.html`)
  const mineFile = p === 'index' ? path.join(distDir, 'index.html') : path.join(distDir, p, 'index.html')
  if (!fs.existsSync(liveFile) || !fs.existsSync(mineFile)) {
    console.log(`\n${p}: SKIP (missing ${!fs.existsSync(liveFile) ? liveFile : mineFile})`)
    fail = true
    continue
  }
  const live = fs.readFileSync(liveFile, 'utf8')
  const mine = fs.readFileSync(mineFile, 'utf8')

  const lt = textOf(live)
  const mt = textOf(mine)
  const li = attrOf(live, 'img', 'src')
  const mi = attrOf(mine, 'img', 'src')
  const lh = attrOf(live, 'a', 'href')
  const mh = attrOf(mine, 'a', 'href')

  const textSame = lt === mt
  const imgOnlyLive = li.filter((x) => !mi.includes(x))
  const imgOnlyMine = mi.filter((x) => !li.includes(x))
  const hrefOnlyLive = lh.filter((x) => !mh.includes(x))
  const hrefOnlyMine = mh.filter((x) => !lh.includes(x))
  const imgSame = imgOnlyLive.length === 0 && imgOnlyMine.length === 0
  const hrefSame = hrefOnlyLive.length === 0 && hrefOnlyMine.length === 0

  console.log(`\n${p}: text=${textSame ? 'OK' : 'DIFF'} images=${imgSame ? 'OK' : 'DIFF'} hrefs=${hrefSame ? 'OK' : 'DIFF'}`)
  if (!textSame) {
    fail = true
    console.log(`  text ${firstTextDiff(lt, mt)}`)
  }
  if (!imgSame) {
    fail = true
    console.log(`  images only-live: ${JSON.stringify(imgOnlyLive)}`)
    console.log(`  images only-mine: ${JSON.stringify(imgOnlyMine)}`)
  }
  if (!hrefSame) {
    fail = true
    console.log(`  hrefs only-live: ${JSON.stringify(hrefOnlyLive)}`)
    console.log(`  hrefs only-mine: ${JSON.stringify(hrefOnlyMine)}`)
  }
}

console.log(fail ? '\nDIFFERENCES FOUND — verify each is explainable (see header).' : '\nAll pages: text/images/hrefs match.')
process.exit(fail ? 1 : 0)
