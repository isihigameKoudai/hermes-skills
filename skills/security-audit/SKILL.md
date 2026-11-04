---
name: security-audit
description: "セキュリティ監査: 脅威モデル・探索・検証・報告を実行。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, audit, vulnerability, threat-model, pen-test]
    related_skills: [requesting-code-review, systematic-debugging]
---

# セキュリティ監査

2つのオープンソース参照実装を統合したセキュリティ監査ワークフロー。Cloudflare の `security-audit-skill`（カバレッジ主導のハンティング、敵対的な候補検証、機械検証可能なスキーマ付き構造化所見）と、Anthropic の `defending-code-reference-harness`（脅威モデル先行のスコープ設定、N票トリアージ、実行検証付き修正、検知・対応）。エージェントをセキュリティ監査人にする: 実際の信頼境界を越える脆弱性を見つけ、所有者にソース証拠・安全な再現手順・優先度・最小の有効な修正を渡す。

具体的な影響を受ける主体・資源・観測可能なセキュリティ結果を伴わない候補は、確定所見ではない。これは防御的でソース優先のワークフローであり、監査は修正を記述するだけで対象ソースを変更しない。

## いつ使うか

- コードベース・API・サービス・CLI・ライブラリ・デーモンの監査、ペネトレーションテスト、完全/包括的なセキュリティレビューを求められたとき。
- 脅威モデルの作成、セキュリティに焦点を当てたコードレビュー、他スキャナの所見のトリアージを求められたとき。
- 疑わしい脆弱性が報告され、ソースに基づく検証を求められたとき。
- 使わない場面: 一般的な「このコードは良いか」レビュー（`requesting-code-review`）、単一クラッシュのデバッグ（`systematic-debugging`）、セキュリティ境界に焦点のないコンプライアンス監査。

## 動作モード

- **ガイダンスモード（既定）** — セキュリティの質問、的を絞ったレビュー、方法論、特定所見のトリアージには、関連する参照ファイルだけを使う。全ワークフローを自動実行したり、出力ディレクトリを作ったり、監査成果物を書いたりしない。絞り込んだサブエージェントを起動してもよい（結果は現在のタスクへ返す）。
- **全監査モード** — コードベースの監査/ペネトレーションテスト、完全/包括的なセキュリティレビュー、または報告成果物の要求が明示されたとき、全ワークフローを実行し、下記のファイルを書く。

どちらのモードか曖昧な要求なら、ファイル作成や全ワークフロー開始の前に焦点を絞った質問を1つする。

## このスキルが検査するもの

2つの系統があり、すべて `references/` にある（末尾の索引を参照）。チェックリストが必要なときは `skill_view(name='security-audit', file_path='references/<file>')` で読み込む。

- **Cloudflare由来の攻撃クラス** — `ATTACK-CLASSES.md` と12のドメインファイル（`WEB-PROTOCOL-AND-AUTH.md`, `CLIENT-SIDE.md`, `CLOUD-AND-DEPLOYMENT.md`, `DATA-ISOLATION-AND-LIFECYCLE.md`, `DESKTOP-MOBILE-AND-LOCAL-IPC.md`, `MEMORY-SAFETY-AND-BINARY.md`, `PROTOCOLS-RPC-AND-MESSAGING.md`, `RESOURCE-EXHAUSTION-AND-AVAILABILITY.md`, `SUPPLY-CHAIN-AND-RELEASE.md`, `AI-AND-LLM.md`）: 約162の攻撃クラス。それぞれ、検証すべき具体的なシンク・設定キー・API・判別テスト付き。
- **Anthropic由来の方法論** — `threat-model.md`（STRIDE＋四問フレームワーク＋スキーマ）、`triage.md`（検証/重複排除/ランク付け/割り当て＋16の誤検知除外ルール）、`vuln-classes-and-harness.md`（メモリ安全性の分類＋クラッシュ品質階層＋サンドボックスモデル）、`detection-response.md`（既にログにいる攻撃者の捜索）。

## 核心原則

1. **境界と結果を要求する** — 各候補について、低信頼の主体、受け入れる入力/操作、意図した制御、越える境界、影響を受ける主体/資源、具体的な観測済みまたは所有者観測可能な結果を名指す。ベストプラクティスの欠落、推測した配備挙動、一般的なパーサクラッシュ、自己影響は所見ではない。
2. **有界なローカル証拠を使う** — 静的解析がソース経路を確立し、サンドボックス化したローカルテストが挙動を確定する（最小ハーネス、単体テスト、小さなフィクスチャ、ダミーテナントの統合テスト、ローカルレンダリングした設定、隔離ループバックのクライアント）。最小の効果（誤った戻り値、不正なダミーレコード、サニタイザ発見、ポリシー差異）で止める。
3. **ソースの可視性を尊重する** — 配備制御、プロキシ挙動、プロバイダ設定、ブラウザヘッダ、識別ポリシー、ブローカーACL、パッケージング、トポロジは実在の制御。リポジトリに無い必須の事実は、どちらとも決めつけず `needs_validation` に正確な欠落事実を記録する。
4. **優先度と確実性を分ける** — 重大度を付けるのは `confirmed` だけ。尤度×影響は実証された条件を反映し、全体重大度は実証された影響を超えない。`needs_validation` はソースに根差した遮断された仮説であって、低確信の確定脆弱性ではない。重大度を持たない。
5. **最小の有効なソース修正を勧める** — コードが強制すべき不変条件と、最後の信頼できる判断点での最も狭い変更を特定する。汎用の強化助言より、リポジトリ相対の変更＋回帰テストを優先する。
6. **検証が要（Anthropic）** — 雑音の多い発見と敵対的検証を分ける: 所見を確認するエージェントは、それを見つけたエージェントでは決してない。エージェント評価の前に安価なプログラム的ゲート（サニタイザ信号、3/3再現）を挟む。文書による主張より実行可能な証拠を優先する。

### 重大度の基準（所見）

- **critical** — 非認証の攻撃者がコード実行、データストアへの完全アクセス、任意アカウントの乗っ取りを得る。
- **high** — 明示的なセキュリティ制御を実害を伴って完全に破る: 認証バイパス、クロステナントの読み書き、他ユーザーに影響する蓄積スクリプト実行、認証済みコード実行、共有サービスの非認証リモート停止。
- **medium** — 実在の境界違反だが影響範囲が限定的、前提が稀、または結果が狭い資源集合に限定。
- **low** — 非秘密の内部情報の開示、または最小の利得に継続的な労力を要する効果。
- **informational** — 確定したが影響が最小の観察。主に大きな所見の中の前提として有用。

high/medium の境界: 実証された結果が、実害のある操作に対する明示的な制御を「完全に破る」のか「弱めるだけ」か。具体的な損害を述べられなければ、重大度は感覚より低い。

`references/threat-model.md` は別の脅威レベルの尺度（影響: low…existential、尤度: very_rare…almost_certain）を定義しており、`THREAT_MODEL.md` の中でのみ使う。

## 実行の安全（両モード）

ソース検査は読み取り専用。対象が制御するビルド・テスト・プロセス・ブラウザ・エミュレータ・ファザー・フィクスチャ処理は、**OSが強制するサンドボックス内のみ**で実行する。それは以下を全て提供する: 外部ネットワークなし（ローカルのクライアント/サーバー通信が必要なチェックだけ隔離ループバック）、明示的な許可リストから作る空の環境、割り当てた `scratch/` ディレクトリにのみ書き込み可能な読み取り専用対象、明示的な低い CPU/メモリ/プロセス/ファイルサイズ/ディスク/壁時計の上限。

依存をインストールしたりビルドに取得させたりしない。対象コードにホストのホームディレクトリ・資格情報・ソケット・共有サービスを晒さない。ダミーの主体・フィクスチャ・秘密を使う。配備済み端点・外部サービス・本番識別・他ユーザーのデータ・稼働中の制御面を探査せず、有償API割当を消費せず、リリースを公開/変更しない。全制御を施行できないなら対象コードを実行せず、欠落する能力を `needs_validation` のブロッカーとして安全な検証計画とともに報告する。決定的な事実がソースやサンドボックス化フィクスチャの外なら `needs_validation` として記録する。

（Anthropic の参照実装はこれを具体的に強制する: 全エージェントは gVisor コンテナで動き、egress は CONNECT 許可リストのプロキシ経由でモデルAPIに限定され、エージェントを生成するコマンドはサンドボックス外での起動を拒否する。`references/vuln-classes-and-harness.md` 参照。）

## 全監査ワークフロー

全監査モードではフェーズを順に実行する。`delegate_task` でフェーズごとに孤立サブエージェントを生成する。ハンターと検証者は別でなければならず、検証者は別の検証者の結論を見てはならない。

0. **脅威モデル（推奨、小さな対象では省略可）** — `references/threat-model.md` で `THREAT_MODEL.md` を作る（資産、入口点/信頼境界、脅威（STRIDE＋過去CVEの一般化）、緩和策）。脅威モデルはスコープ設定と較正を導く。所見リストではない。全入口点が1つ以上の脅威行に対応したら完了。
1. **偵察** — ソース、信頼境界、ビルド経路、入口面、過去の証拠を `architecture.md`＋決定的な `coverage-ledger.json` に写像する（入口面×信頼境界×サブシステム×攻撃クラスごとに1ユニット）。過去の `coverage-ledger.json`/`findings.json` を読み、引き継ぎ/変更ソースのレコードを整合させる。`references/RECONNAISSANCE.md` 参照。台帳を種蒔きし `node scripts/validate-coverage-ledger.cjs coverage-ledger.json` が通ったら完了。
2. **カバレッジ主導のハンティング** — 台帳ユニットごとに孤立ハンターを1つ割り当てる。各ハンターは `references/ATTACK-CLASSES.md` と、その攻撃クラスのドメインファイル、`references/HUNTING.md` の候補ゲート＋構造化結果スキーマを使う。各波の後にカバレッジ批評を走らせて穴を見つける。批評がクリーンに通ったら完了。ユニットはハンターの構造化結果からのみ閉じる。
3. **候補検証** — 安定したフィンガープリントで候補を統合し、各 proposed `confirmed`/`needs_validation` を、ソース＋有界なローカル証拠から反証を試みる新規の敵対的検証者に渡す（`references/VALIDATION-AND-REPORTING.md` と `references/triage.md` の除外ルール参照）。フィンガープリントごとに最終レコードが1つできたら完了。
4. **構造化出力** — 最終 `confirmed`/`needs_validation`/`rejected` をフィンガープリント順に `findings.json` へ書く（スキーマ: `scripts/report-schema.json`）。`node scripts/validate-findings.cjs findings.json` が通ったら完了。
5. **独立レコード検証** — 保持する各レコードに新規検証者を1つ立て、全トレース/証拠のパス・行・スコープ・結果を再確認する。実質的な置換には別の独立検証者を充てる。`run_status: complete` になるか、未検証の全フィンガープリントを開示したら完了。
6. **報告** — 最終レコード＋台帳から `REPORT.md`, `FINDINGS-DETAIL.md`, `NEEDS-VALIDATION.md` を導出する（実運用探査の指示は含めない）。`references/VALIDATION-AND-REPORTING.md` 参照。
7. **修正（任意）** — 各 confirmed 所見について最小の修正＋回帰テストを生成し、`references/vuln-classes-and-harness.md` のラダーで検証する（T0 ビルド→T1 PoC停止→T2 テスト通過→T3 再攻撃）。差分は適用せず、人間のレビュー用に出力する。所有者が「適用してPRを」と明示した場合のみ `github-pr-workflow` に引き継いで差分を適用し、対象リポジトリ自身のツールチェーン（lint・型チェック・テスト・ビルド）を実実行してからコミットする。
8. **検知・対応（任意）** — 攻撃者が既にログにいる可能性があれば、`references/detection-response.md` の `dnr-hunt`→`dnr-respond` ループを回す。

終了状態の規則: 全監査実行は、(a) 全報告成果物が書かれ検証器が通る、または (b) `run_status: "incomplete"` を正確な理由付きで記録しギャップを開示する、のどちらか一方に達するまで終了しない。フェーズの途中で止めない。`quick`/スコープ/部分実行は、部分カバレッジであることを明示する。

## サブエージェントの役割

| 役割 | エージェント | 書くもの | 読むもの |
|---|---|---|---|
| 偵察 | `research`（並行） | なし（事実を返す） | 対象ソース、ビルド/設定 |
| ハンター | `general`（台帳ユニットごとに1つ） | 自分の `agents/<id>/scratch/` | ソース＋その攻撃クラスの参照 |
| カバレッジ批評 | `research` | なし | 台帳＋ハンター結果 |
| 検証者（フェーズ3/5） | `general`/`research`（新規、ハンターでない） | なし | ソース＋候補＋スキーマ |
| 報告作成者 | 親（合成する） | 共有実行ファイル | 最終レコード＋台帳 |

各サブエージェントの `delegate_task` コンテキストには、正確な対象パス、割り当てられたスコープ/ユニット、関連する参照ファイルの内容、サンドボックス境界、レコードスキーマが必要。ハンター/検証者の独立性を保つ: 検証者の結論を別の検証者に渡さない。

## アンチパターン

1. チェックリストからの逸脱を脆弱性として提示する。
2. 到達可能な境界違反のない多層防御の助言。
3. 有界なローカル証拠では不十分な実運用/共有環境でのテスト。
4. ソースに無いプロバイダ/プロキシ/ブラウザ/識別/配備の挙動の推測。
5. 意図した同一主体の権限や自己影響を越境の結果として扱う。
6. 観測された効果より強いパーサ/実行時の効果を報告する。
7. 重複排除も検証もできない散文だけのハンター結果。
8. 引き継いだ同一ソースの過去 confirmed の再報告、またはそれを手掛かりにハントを固定する。
9. `needs_validation` レコードへの重大度の付与。
10. 独立検証前に報告を書く、または散文と JSON を食い違わせる。

## 参照索引

| ファイル | 内容 |
|---|---|
| `references/ATTACK-CLASSES.md` | 10の中核攻撃クラス（注入、アクセス制御、資源/ファイル、暗号、ビジネスロジック、機能悪用、連鎖、ワイルドカード、初歩）＋振り分け表 |
| `references/WEB-PROTOCOL-AND-AUTH.md` | HTTPフレーミング/デシンク、キャッシュポイズニング、CSRF、セッション固定、JWT/OAuth/SAML、MFA/パスキー、APIキー/mTLS |
| `references/CLIENT-SIDE.md` | DOM XSS、クロバリング、プロトタイプ汚染、postMessage/WebSocket/CORS、Service Worker、XS-Leaks、クリックジャッキング |
| `references/CLOUD-AND-DEPLOYMENT.md` | IAM/役割混同、入口/メッシュ迂回、コンテナ能力、秘密ライフサイクル、署名付きURL/イベント源混同 |
| `references/DATA-ISOLATION-AND-LIFECYCLE.md` | テナント/所有者強制、複合キー衝突、派生コピーのACLドリフト、エクスポート/インポート、論理削除/復元 |
| `references/DESKTOP-MOBILE-AND-LOCAL-IPC.md` | ディープリンク、WebViewブリッジ、IPCピア認証、特権ヘルパー、キーチェーン漏出 |
| `references/MEMORY-SAFETY-AND-BINARY.md` | 21クラス: 範囲外、整数オーバーフロー、UAF/二重解放、型混同、FFI/ABI、ローダ検索順、カーネルユーザーコピー |
| `references/PROTOCOLS-RPC-AND-MESSAGING.md` | フレーミング/正規化不一致、共用体/列挙混同、ブローカー/キュー隔離、再送/順序/冪等 |
| `references/RESOURCE-EXHAUSTION-AND-AVAILABILITY.md` | ReDoS/超線形、展開爆弾、無制限バッファリング、ハンドルリーク、割当/ワーカー飢餓、毒レコード |
| `references/SUPPLY-CHAIN-AND-RELEASE.md` | 依存混同、可変ビルド入力、CIワークフロー注入、成果物置換、署名/更新/プラグイン信頼 |
| `references/AI-AND-LLM.md` | プロンプト注入、コンテキスト混線、メモリ毒入れ、ツール引数注入、混同代理、MCP識別 |
| `references/HUNTING.md` | 優先順位、中核手法、サンドボックス制約、候補ゲート、構造化ハンター結果スキーマ、カバレッジ批評 |
| `references/RECONNAISSANCE.md` | フェーズ1の偵察エージェント、architecture.md、カバレッジ台帳の構造 |
| `references/VALIDATION-AND-REPORTING.md` | フェーズ3〜6: 検証者プロンプト、所見契約、報告内容 |
| `scripts/report-schema.json` | 3種の `findings.json` verdict の JSON スキーマ |
| `references/threat-model.md` | Anthropic の脅威モデリング: 四問フレームワーク、STRIDE、bootstrap スウォーム、THREAT_MODEL スキーマ |
| `references/triage.md` | Anthropic のトリアージ: 検証/重複排除/ランク/割り当て、16の除外ルール、所見＋verdict スキーマ |
| `references/vuln-classes-and-harness.md` | メモリ安全性の分類、クラッシュ品質階層、CVE例、ASANパイプライン＋サンドボックスモデル |
| `references/detection-response.md` | dnr-hunt / dnr-respond: ログ捜索チェックリスト、verdict ラダー、INCIDENTS/RESPONSE スキーマ |
| `scripts/validate-findings.cjs` | 依存ゼロの `findings.json` 検証器（Node.js） |
| `scripts/validate-coverage-ledger.cjs` | 依存ゼロの `coverage-ledger.json` 検証器（Node.js） |

## 実行方法

- **質問/的を絞ったレビュー** — 関連する参照ファイルを読んで答える。成果物は作らない。
- **全監査** — 出力ディレクトリを決め（既定 `~/security-audit/<repo>/run-<N>`）、フェーズ0〜8を `delegate_task` で進める。`terminal(command="node scripts/validate-findings.cjs findings.json")` で検証する（パスはスキルディレクトリ相対。`skill_view` で位置を確認できる）。

## 注意点

- 検証器は形式＋台帳の整合性だけを証明する。所見が本物かどうかは検証しない。独立した人間/エージェントの検証が証拠の基準。
- 1回の実行で対象を網羅しきれない（参照実行では、繰り返し実行の合計のおよそ半分しか見つからなかった）。カバレッジ文でそう述べる。
- `needs_validation` は推測の駐車場ではない。正確な未解決事実と、安全なローカルまたは所有者観測の計画を名指す。
- ReDoS/アルゴリズム複雑度/無制限再帰は報告すべき DoS。量だけのレート制限欠落は違う（インフラの問題）。
- メモリ安全言語のメモリ安全性は `unsafe`/FFI 内のみ報告可。React/Angular/Vue の XSS は素通し口（`dangerouslySetInnerHTML` 等）経由のみ。
- クライアントSPAへのヘッダ/CSP追加の修正では、ソースを grep して全外部オリジン（WASM/CDNモデル/API端点）を列挙し `connect-src`/`script-src` に含める。オリジンを漏らすと機能が壊れる。nosniff・frame-ancestors・Referrer-Policy 等の基盤ヘッダは無リスクなので先に付ける。
- 所見スキーマ・検証器・チェックリストは MIT/Apache-2.0 のソースから改作したもの。下記の出典参照。

## 出典

ワークフロー、カバレッジ台帳、攻撃クラス参照、`report-schema.json`、検証器は Cloudflare の `security-audit-skill`（MIT, © Cloudflare）から改作。脅威モデリング、トリアージ、修正ラダー、ハーネスの分類、検知・対応は Anthropic の `defending-code-reference-harness`（Apache-2.0, © Anthropic PBC）から改作。
