---
name: fiverr-spam-detection
description: Use when judging if an incoming Fiverr message is spam/scam.
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [fiverr, spam, scam, phishing, freelance]
    related_skills: [freelance-marketplace-selling]
---

# Fiverr message spam detection

## When to Use
Use when the user pastes or forwards an incoming Fiverr buyer message and asks whether it is spam, or when reviewing messages for the vibe-rescue freelance business. Apply the checklist, return a clear spam/legit verdict with the specific red flags, and state the response (report + block).

## The one real signal
A message is ONLY a legitimate job if the Fiverr **"Orders with you"** panel (right sidebar of the chat) shows an actual active order. No order = treat as spam until proven otherwise.

## Red flags (any one = spam; several = certain scam)
- **Claims "I already placed the order" while "Orders with you" shows none** — lying to build trust.
- **External link in the first message** (not Google Drive / Dropbox / GitHub / Fiverr). Random domains like haoxing-sh.com, sdtone.com. Never click.
- **File attachment from a stranger** with "please check/review this" — malware delivery risk. Never download.
- **"On Fiverr since <current month/year>"** = brand-new throwaway account with zero completed orders & greyed-out rating stats.
- **Random username** (name + digits, e.g. grayme849824, gracekelly6555).
- **Generic template**: "everything is prepared", "when are you available to start", "reference materials below", "I've gathered all the materials", "I've already placed the order".
- **Off-platform asks**: WhatsApp / email / Telegram, "pay outside Fiverr", asking for your email.
- **"Translate to English" flag** on the message (foreign bot spam).

## Immediate action (do NOT negotiate)
1. Do NOT click links, download attachments, or reply.
2. Chat header ⋯ (top right, next to star/tag icons) → **Report** (choose spam/phishing) → **Block**.
3. Message-level ⋯ → Report also works for a single message.

## Legitimate pattern (rare)
- Active order visible in "Orders with you".
- Reference files arrive via Fiverr order requirements, or Google Drive / Dropbox / GitHub, AFTER the order is placed.
- Buyer has completed-orders / rating history (not greyed out).

## Notes
- New sellers get a coordinated scam wave for the first few days after publishing a gig, all using the same template. Block each; don't overthink.
- The scam wave targeting you is itself proof the gig is now indexed/visible — keep publishing.
