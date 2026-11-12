---
name: monthly-album-watch
version: 1.0.0
description: 月次アルバム新作チェックbotの設定・実行・編集。Deezerで前月リリースのアルバムを取得。
---

# 月次アルバム新作チェック Bot

指定したアーティストの「前月(または指定月)にリリースされたアルバム」を Deezer API から自動取得して報告する。カレンダー/ライブラリ管理用。

## 動きの全体像

```
cron (毎月1日 09:00, no_agent)
  → ~/.hermes/scripts/monthly_albums.py を実行
  → monthly_data/target_artists.txt に列挙されたアーティストだけを調べる
  → 前月にリリース日があり、保有済みでない album/ep を抽出
  → stdout を cron がチャットへ配信
```

## ディレクトリ構成(ホスト ~/.hermes/scripts/ 配下)

```
monthly_albums.py
monthly_data/
  artists.txt          # 全961名のマスタ(変更しない)
  target_artists.txt   # ★ここに1行1アーティストで対象を記入
  owned_albums.json    # 保有アルバム(除外対象) {アーティスト: [アルバム名,...]}
monthly_report/
  albums_YYYY-MM.txt   # 実行ログ(記録として保存)
```

## 対象アーティストの指定方法(最重要)

`monthly_data/target_artists.txt` を1行1アーティストで編集する。**ここに書いたアーティストだけを調べる**(他はスキップ)。

```
# 例
米津玄師
BAND-MAID
Blackpink
EVANESSCENCE
```

- `#` で始まる行はコメント(無視)
- 指定しない(空)場合は全961名にフォールバック → **処理に数分 + クレジット増**。普段は必ず絞る。
- アーティスト名は Deezer でヒットする表記を推奨。表記ゆれ(例: 「B'z」/「B’z」/「B'Z」)は正規化して同アーティスト扱いになる。
- アプリや別プロセスからも編集可。次回cron実行時に反映される。

### 絶対知っておくべき: サンドボックスとホストは別のツリー

cron は**ホスト** `~/.hermes/scripts/monthly_data/target_artists.txt` を読む。サンドボックス内の `/root/.hermes/scripts/...` や `/workspace/monthly_data/...` はホストと**別物**で、cron から参照されない。サンドボックスで `target_artists.txt` をいくら編集しても cron には反映されない。

- 反映するにはホスト側のファイルを書き換える → ユーザーに `ssh hermes@<vps> ` で編集してもらう、またはホスト置換コマンドを組み立てて渡す。
- サンドボックスで編集した新コピーは、`/workspace`(読み書き可→ホスト実体 default_ws_<hash>/workspace)に置き、ユーザーに `cp` してもらうと確実。
- スクリプト本体も同様: cron の `script: monthly_albums.py` は相対パスでホスト `~/.hermes/scripts/` に無いと作成/実行が失敗する(絶対パス・home相対パスは一切受け付けない)。

## 実行コマンド

ホストの `~/.hermes/scripts/` で:

```bash
# 前月分(推奨)
python3 monthly_albums.py
# 指定月
python3 monthly_albums.py 2026-10
# 対象をCLIで直接指定(ファイルを月収) / 全961名
python3 monthly_albums.py 2026-10 "米津玄師" "BAND-MAID"
python3 monthly_albums.py --all 2026-10
```

手動テストは対象を絞って(5名以下・数秒)行うこと。

### CLI引数の罠

- 月指定は必ず `YYYY-MM` の7文字(例 `2025-10`)。`2025` のような裸の年号は月と判定されず、**アーティスト名として検索対象に加わってしまう**(全961名に誤って混入し、その分呼び出しが増える)。
- 対象アーティスト未指定(空)だと全961名にフォールバックし数分～8分かかる。手動テストの前に対象を絞るか、`/tmp`にコピーした縮小 `target_artists.txt` を一時参照しない限り、すぐに全件走る。

## cron 設定

`cronjob_manage` で作成済み。毎月1日 09:00。`script=monthly_albums.py` + `no_agent=true`(LLM不使用・クレジット0)。

- 作成済み job 名: 「毎月アルバム新作チェック」
- 対象は target_artists.txt 次第。空なら全961名。
- 配信先: 作成元チャット(origin)。

## 出力フォーマット

```
アーティスト名
アルバム名 (YYYY-MM-DD)
https://www.deezer.com/album/ID
(空行)
```

## Pitfalls / 限界

- **Deezer が情報源**。Amazon/楽天/Spotify の商品URLは出さず、DeezerアルバムページURL。
- **旧音源の再配信を除去しきれない**: リマスター/リイシュー/デラックス/アニバーサリー版はキーワードで除外するが例外あり。重要アーティストは目視確認を推奨。
- **シングルは除外**(record_type=single)。EP・ミニアルバムは含む。
- **ラジオ番組シリーズ**(例: A State of Trance)やクラシック旧録はキーワード除外。
- 保有アルバム除外は「正規化した同名」で判定(英数字+空白+記号除去・大文字化)。
- Deezer はレート制限あり。961名だと search(0.25s)+アルバム一覧(0.2s)の呼び出しになり数分～8分。cronでは対象を絞ること。
