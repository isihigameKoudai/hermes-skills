# hermes-skills

Hermes Agent 用のカスタム skill tap。学習で育ったスキルを共有するためのリポジトリです。

## 含まれるスキル

| スキル | 内容 |
|---|---|
| `akashic-research` | アカシックレコードの視点で問いの本質を結晶化するディープリサーチ |
| `business-plan-review` | 事業計画の実現可能性・法的リスク・KPI モデリングをレビュー |
| `cmo` | 新規事業の立案・検証・グロース・マーケティング全般を統括するディレクター・エージェント（制約・事実・算数・リスクの4ゲート検証付き） |
| `freelance-marketplace-selling` | フリーランスマーケットプレイスでの開発サービス販売 |
| `google-workspace-oauth-setup` | Google Workspace OAuth のセットアップ手順 |
| `hermes-contributing` | Hermes Agent への PR コントリビューション手順 |
| `hermes-remote-backend` | VPS + リモートデスクトップ構成での Hermes 運用ノウハウ |
| `kamepon-article-style` | かめぽん流の技術記事執筆スタイル |
| `porting-skill-packs` | 外部スキル／エージェントパックの Hermes への移植 |
| `service-business-launch` | サービスビジネスの立ち上げ（検証ファースト） |
| `technical-writeup-from-logs` | 生ログ／トランスクリプトから事実確認済みの技術記事を書く |

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
├── business-plan-review/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
├── cmo/
│   ├── SKILL.md
│   └── references/
├── freelance-marketplace-selling/
│   ├── SKILL.md
│   └── references/
├── google-workspace-oauth-setup/
├── hermes-contributing/
├── hermes-remote-backend/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
├── kamepon-article-style/
├── porting-skill-packs/
├── service-business-launch/
└── technical-writeup-from-logs/
    ├── SKILL.md
    ├── references/
    └── templates/
```
