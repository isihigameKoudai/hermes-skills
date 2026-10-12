---
name: crypto-asset-research
description: "Use when researching crypto assets for investment."
version: 1.0.0
author: Hermes Agent (curator)
tags: [crypto, investment, research, tokenomics, iso-20022, quantum-resistant]
platforms: [linux, macos, windows]
---

# Crypto Asset Investment Research

## When to Use

- User asks whether a crypto asset is a good investment, or wants a deep dive on a coin/token
- User asks why a coin's price surged or dumped, or about a specific project (QRL, XRP, ALGO, etc.)
- User asks about ISO 20022 compliance, quantum resistance, or a coin's tokenomics
- User asks about crypto payments infrastructure or enterprise-blockchain competitive positioning

User's standing analysis priority order (apply to every asset deep-dive):
1. Fundamentals — technology, team, adoption, partnerships (verify against official docs)
2. Market — price vs ATH, drawdown, market cap, volume, liquidity
3. Capital flows — whales, institutions, ETFs, validator/council stake concentration
4. Event consistency — has price historically reacted to this kind of catalyst, or is the market ignoring it?

## Procedure
1. Parallel `web_search` batches, one query per angle: (a) "<asset> news adoption partnerships <year>", (b) "<asset> tokenomics supply inflation unlock", (c) the specific event the user asked about (e.g. "why did X pump").
2. Cross-check price/valuation across at least two sources (CoinGecko, Forbes, CoinMarketCap). Sources disagree — especially analyst price targets, which can be wildly stale. Flag a divergent figure explicitly rather than averaging it silently.
3. For every bullish claim, name which layer the evidence actually supports (see the three-layer pitfall below). Never let price action substitute for token-demand evidence.
4. Score tokenomics before trusting the narrative (see references/tokenomics-checklist.md). A coin with a strong story and bad tokenomics is a trap.
5. End with an explicit verdict plus the single named risk that would invalidate it — not just a narrative summary.

## Pitfalls
- "ISO 20022 compliant" is NOT an official certification. ISO 20022 is a financial-messaging format; coins are "aligned" with it, never "certified". Do not present it as a regulatory stamp.
- "Quantum resistant" has three tiers — state the tier, never a blanket "quantum safe". Default-PQ (signatures post-quantum since genesis: QRL XMSS, Mochimo WOTS+, Abelian, Cellframe, SynX) / opt-in accounts (Algorand Falcon-1024, Nervos CKB — holders must migrate funds, consensus keys may stay classical) / announced-only (QANX is an ERC-20 token with no L1 mainnet — resistance not live).
- Decompose enterprise news into three layers: company validation / technology demand / TOKEN demand. A large institutional win (bank consortium selects the vendor) can rally price with zero stated token utility. Flag that gap; the key check is whether any party said banks must buy/stake/pay fees in the token.
- Treat vendor self-descriptions ("only production-grade", "only company capable") as marketing, not evidence. Verify the actual track record: pilot/PoC vs live production, and whether the network has even launched.
- Payment-infrastructure framing: SWIFT's moat is CROSS-BORDER correspondent messaging. Domestic rails (FedNow, RTP, CHIPS, TIPS, SEPA Instant) do not use SWIFT messages and settle a single currency only. A domestic win (e.g. a US clearing-house deal) is NOT "beating SWIFT" — don't conflate the two territories.
- Staking rewards funded by a foundation subsidy rather than fee revenue are a security cliff: when the subsidy runs out, validators leave unless fees have grown to replace it. Check who funds staking rewards and whether fee income is meaningful (not just whether a staking APY exists).
- Crypto price data decays fast: re-fetch prices for every new session instead of trusting numbers from prior conversations.
