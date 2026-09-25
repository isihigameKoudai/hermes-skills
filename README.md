# hermes-skills

Hermes Agent 用のカスタム skill tap。学習で育ったスキルを共有するためのリポジトリです。

## 含まれるスキル

| スキル | 内容 |
|---|---|
| `cmo` | 新規事業の立案・検証・グロース・マーケティング全般を統括するディレクター・エージェント（制約・事実・算数・リスクの4ゲート検証付き） |
| `technical-writeup-from-logs` | 生ログ／トランスクリプトから事実確認済みの技術記事を書く |
| `business-plan-review` | 事業計画の実現可能性・法的リスク・KPI モデリングをレビュー |
| `hermes-remote-backend` | VPS + リモートデスクトップ構成での Hermes 運用ノウハウ |
| `google-workspace-oauth-setup` | Google Workspace OAuth のセットアップ手順 |
| `kamepon-article-style` | かめぽん流の技術記事執筆スタイル |

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
├── cmo/
│   ├── SKILL.md
│   └── references/
├── technical-writeup-from-logs/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
├── business-plan-review/
├── hermes-remote-backend/
├── google-workspace-oauth-setup/
└── kamepon-article-style/
```
