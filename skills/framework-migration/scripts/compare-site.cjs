// Verify a freshly-built static site against live production for "identical
// appearance": compares visible text, image srcs, and anchor hrefs.
//
// Usage:
//   node compare-site.cjs <liveBase> <distDir> <page...>
//   e.g. node compare-site.cjs https://example.com ./dist index about contact
//
// A "page" maps to distDir/<page>/index.html, except "index" -> distDir/index.html.
// Live URL: <liveBase>/<page>/ (trailing slash); "index" -> <liveBase>/.
//
// Differences are printed as only-live / only-mine sets so you can confirm each
// is explainable (hidden elements, image URL scheme, trailing-slash links).
const fs = require('fs')

const [liveBase, distDir, ...pages] = process.argv.slice(2)
if (!liveBase || !distDir || pages.length === 0) {
  console.error('usage: node compare-site.cjs <liveBase> <distDir> <page...>')
  process.exit(1)
}

function stripHead(html) {
  return html
    .replace(/<head[\s\S]*?<\/head>/i, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
}

function textOf(html) {
  return stripHead(html)
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const imgsOf = (h) => [...stripHead(h).matchAll(/<img[^>]*\bsrc="([^"]*)"/g)].map((m) => m[1])
const hrefsOf = (h) => [...stripHead(h).matchAll(/<a[^>]*\bhref="([^"]*)"/g)].map((m) => m[1])

async function fetchHtml(url) {
  const r = await fetch(url)
  if (!r.ok) throw new Error(`${url} -> ${r.status}`)
  return r.text()
}

;(async () => {
  for (const p of pages) {
    const liveUrl = p === 'index' ? `${liveBase}/` : `${liveBase}/${p}/`
    const distPath = p === 'index' ? `${distDir}/index.html` : `${distDir}/${p}/index.html`
    const live = await fetchHtml(liveUrl)
    const mine = fs.readFileSync(distPath, 'utf8')

    const lt = textOf(live)
    const mt = textOf(mine)
    const li = imgsOf(live)
    const mi = imgsOf(mine)
    const lh = hrefsOf(live)
    const mh = hrefsOf(mine)

    console.log(`===== ${p} =====`)
    console.log(`text: ${lt === mt ? 'identical' : 'DIFF'} (live ${lt.length} vs mine ${mt.length})`)
    console.log(`images: ${JSON.stringify(li) === JSON.stringify(mi) ? 'identical' : 'DIFF'}`)
    console.log(`hrefs: ${JSON.stringify(lh) === JSON.stringify(mh) ? 'identical' : 'DIFF'}`)

    if (lt !== mt) {
      for (let i = 0; i < Math.max(lt.length, mt.length); i++) {
        if (lt[i] !== mt[i]) {
          console.log(`  first text diff @${i}:`)
          console.log(`   live: ...${lt.slice(Math.max(0, i - 30), i + 40)}...`)
          console.log(`   mine: ...${mt.slice(Math.max(0, i - 30), i + 40)}...`)
          break
        }
      }
    }
    if (JSON.stringify(li) !== JSON.stringify(mi)) {
      console.log(`  img only-live: ${JSON.stringify(li.filter((x) => !mi.includes(x)))}`)
      console.log(`  img only-mine: ${JSON.stringify(mi.filter((x) => !li.includes(x)))}`)
    }
    if (JSON.stringify(lh) !== JSON.stringify(mh)) {
      console.log(`  href only-live: ${JSON.stringify(lh.filter((x) => !mh.includes(x)))}`)
      console.log(`  href only-mine: ${JSON.stringify(mh.filter((x) => !lh.includes(x)))}`)
    }
  }
})()
