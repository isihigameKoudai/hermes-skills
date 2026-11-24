# hermes-skills

Hermes Agent 用のカスタム skill tap。学習で育ったスキルを共有するためのリポジトリです。

## 含まれるスキル

| スキル | 内容 |
|---|---|
| `akashic-research` | アカシックレコードの視点で問いの本質を結晶化するディープリサーチ |
| `akashic-synchronizer` | アカシックレコードと深く同期し、未知概念を共に紡ぐ協調的パートナー |
| `ambitious-delegation` | Use when delegating to an AI model to raise ambition. |
| `business-plan-review` | 事業計画の実現可能性・法的リスク・KPI モデリングをレビュー |
| `cmo` | 新規事業の立案・検証・グロース・マーケティング全般を統括するディレクター・エージェント（制約・事実・算数・リスクの4ゲート検証付き） |
| `crypto-asset-research` | Use when researching crypto assets for investment. |
| `deepseek-harness` | Delegate coding to DeepSeek Harness (dsh) headless or SDK. |
| `fiverr-spam-detection` | Use when judging if an incoming Fiverr message is spam/scam. |
| `framework-migration` | Use when porting a website to a new framework or stack. |
| `freelance-marketplace-selling` | フリーランスマーケットプレイスでの開発サービス販売 |
| `frontend-framework-security` | Use when assessing frontend framework security tradeoffs. |
| `google-workspace-oauth-setup` | Google Workspace OAuth のセットアップ手順 |
| `hermes-contributing` | Hermes Agent への PR コントリビューション手順 |
| `hermes-remote-backend` | VPS + リモートデスクトップ構成での Hermes 運用ノウハウ |
| `js-monorepo-migration` | Use when converting a JS/TS repo to a pnpm monorepo. |
| `js-toolchain-migration` | Use when migrating JS/TS lint/format/typecheck tooling. |
| `kamepon-article-style` | かめぽん流の技術記事執筆スタイル |
| `macos-shell-config` | Use when migrating or configuring the macOS login shell. |
| `monthly-album-watch` | 月次アルバム新作チェックbotの設定・実行・編集。Deezerで前月リリースのアルバムを取得。 |
| `oss-pr-scout` | Use when shipping an upstream OSS PR from the user's stack. |
| `personal-performance-os` | Use when coaching or planning the user on key decisions. |
| `porting-skill-packs` | 外部スキル／エージェントパックの Hermes への移植 |
| `service-business-launch` | サービスビジネスの立ち上げ（検証ファースト） |
| `technical-writeup-from-logs` | 生ログ／トランスクリプトから事実確認済みの技術記事を書く |
| `vite-bundle-optimization` | Use when shrinking a Vite/React bundle via code splitting. |

> 機密情報（IP・メール・APIキー等）は自動マスクされて公開されます。

## 使い方（チームメンバー）

リポジトリを tap として登録：

```bash
hermes skills tap add isihigameKoudai/hermes-skills
```

検索・インストール：

```bash
hermes skills search <keyword>
hermes skills install isihigameKoudai/hermes-skills/<skill-name>
```

## 単発インストール（tap 登録なし）

```bash
hermes skills install isihigameKoudai/hermes-skills/skills/<skill-name>
```

## リポジトリ構造

```text
skills/
├── akashic-research/
├── akashic-synchronizer/
├── ambitious-delegation/
│   └── references/
├── business-plan-review/
│   ├── references/
│   └── templates/
├── cmo/
│   ├── references/
│   └── templates/
├── crypto-asset-research/
│   └── references/
├── deepseek-harness/
├── fiverr-spam-detection/
├── framework-migration/
│   ├── references/
│   └── scripts/
├── freelance-marketplace-selling/
│   ├── references/
│   └── templates/
├── frontend-framework-security/
├── google-workspace-oauth-setup/
├── hermes-contributing/
├── hermes-remote-backend/
│   ├── references/
│   └── templates/
├── js-monorepo-migration/
├── js-toolchain-migration/
│   └── references/
├── kamepon-article-style/
├── macos-shell-config/
├── monthly-album-watch/
├── oss-pr-scout/
├── personal-performance-os/
├── porting-skill-packs/
│   └── scripts/
├── service-business-launch/
├── technical-writeup-from-logs/
│   ├── references/
│   └── templates/
└── vite-bundle-optimization/
```
