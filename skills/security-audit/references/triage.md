# トリアージ（Anthropic の手法）

Anthropic `.claude/skills/triage/` から改作。所見の山（`/vuln-scan` 出力、パイプライン結果、`INCIDENTS.json`、他スキャナ）に対する4つの仕事: **検証**（敵対的、読み取り専用）、**重複排除**（実行/スキャナ横断）、**ランク付け**（スキャナの自称重大度ではなく導出した悪用可能性で）、**割り当て**（コンポーネント所有者へ）。出力は短く・ランク付き・所有者付きのリスト。

**厳格な制約:** 対象コードを実行しない。ネットワークに出ない（レジストリ/CVE/上流の照会をしない）。「PoCを書けなかった」は反証ではなく弱い証拠にすぎない。

## スコープ面談（既定は対話）

1. **環境と信頼境界** — インターネット向けWebサービス（HTTPは非信頼）／内部サービス（呼び出し元は認証済みピア）／ライブラリSDK（呼び出し元が境界）／CLIバッチ（オペレータ入力は信頼、ファイル入力は非信頼）／組み込みファームウェア（物理アクセスが範囲）。到達性はこれに対して判定。
2. **脅威モデル**（複数選択）— RCE／テナント間データ漏出／管理者への特権昇格／下流ユーザーへのサプライチェーン侵害／SLAに対するDoS／PII-PCI-PHIのコンプライアンス対象露出。ランク付けは、明示された脅威に当てはまる所見を引き上げる。
3. **スコア基準** — 導出 HIGH/MEDIUM/LOW（既定）／CVSS 3.1／CVSS 4.0／OWASP／組織バグバー。
4. **ノイズ耐性** — precision（票割れは捨てる）／recall（票割れは `needs_manual_test` で残す）／所見ごとに聞く。

自動既定: 環境＝「不明。外部到達の入口点は全て非信頼として扱い、境界前提を根拠に明記」、脅威モデル空、スコア＝導出、ノイズ耐性＝precision。

## 取り込みと正規化（フィールド別名）

正規名←別名: `file`←`path`/`location.file`/`filename`/ASAN最上位フレーム ・ `line`←`line_number`/`location.line`/`lineno` ・ `category`←`type`/`cwe`/`rule_id`/`crash_type`/`vulnerability_class` ・ `severity`←`severity_rating`/`level`/`priority`/`risk` ・ `title`←`name`/`summary`/`message` ・ `description`←`details`/`report`/`body` ・ `exploit_scenario`←`attack_scenario`/`poc`/`reproduction` ・ `preconditions`←`requirements`/`assumptions` ・ `recommendation`←`fix`/`remediation` ・ `scanner_confidence`←`confidence`/`score`/`certainty`（0.0–1.0へ正規化）。`file` が欠落/解決不能なら**位置不明**: 重複排除＋検証をスキップし、`verdict: false_positive`, `verify_verdict: needs_manual_test`, `confidence: 0`, `refute_reasons: ["doesnt_exist"]` で出力。

## 重複排除（検証の前）

- **決定的:** 同じ `file`（正規化）＋同じ `category`（大文字小文字/句読点無視）＋ `line` 差10以内。正典＝欠落フィールド最少（同数なら最小id）。他は `verdict: duplicate`, `duplicate_of`。
- **意味的**（サブエージェント1つ）: DUPLICATE＝「一方を直せば他方も直る」（同じ根本原因の言い換え、呼び出し元ごとに報告された共有ヘルパー、エンドポイントごとに報告された全体的保護の欠如）。DISTINCT＝同領域の別カテゴリ、同ファイル/カテゴリでも汚染変数が違えば別シンク、1つのヘルパーの独立した2バグ、修正が端点ごとに必要な2端点。

## 検証（敵対的N票 — 既定3票）

N人の独立した敵対的検証者がコードから主張を再導出する。姿勢は「これが間違っている理由を探せ」。各々は引用箇所のコードから始め（スキャナの説明ではなく）、他の検証者の推論を見ない。手順 — 各段階が特定の誤検知クラスを塞ぐ:

1. **引用箇所のコードを自分で読む。**
2. **シンクから後方に到達性を追う**（呼び出し元をgrep、importを追う。最初の呼び出し箇所を `file:line` で引用。到達不能コードは最大の誤検知源）。
3. **保護を探す**（上流の検証/無害化、フレームワーク自動エスケープ/パラメタ化クエリ、型制約、認証/認可ゲート、露出を制限する設定、死/テスト/フィクスチャコード）。
4. **各保護をストレステスト**（全経路に適用？符号化/境界/代替入口での迂回は？）。

### 除外ルール（技術的に正しくても FALSE_POSITIVE。ルール番号を引用）

1. 量だけのDoSやレート制限欠落（インフラ層）— ただし ReDoS／アルゴリズム複雑度／無制限再帰は有効。
2. テスト専用/死/例示/フィクスチャコード、またはセキュリティ影響のないクラッシュ。
3. 意図した設計（圧縮ミドルウェア、強いアルゴリズムと並ぶ後方互換の弱いアルゴリズム）。
4. メモリ安全言語のメモリ安全性（`unsafe`/FFI の外）。
5. 攻撃者がホスト/プロトコルでなくパスだけ制御する SSRF。
6. AI/LLM プロンプトへ流れるユーザー入力（プロンプト注入はそれ自体ではコード脆弱性ではない）。
7. `../` が信頼境界を越えないオブジェクトストレージ（S3/GCS）のパストラバーサル。
8. 信頼入力（オペレータ設定の環境変数、CLIフラグ）をベクタとする（環境が非信頼と明示する場合を除く）。
9. サーバー側クラスで指摘されたクライアント側コード。
10. 古い依存バージョン。
11. 非セキュリティ用途の弱い乱数。
12. 影響の小さい迷惑（ログ偽装、ログアウトCSRF、自己XSS、タブナビング、オープンリダイレクト、正規表現注入）。
13. 具体的な悪用経路のない強化/ベストプラクティスの欠落。
14. 既定で自動エスケープするフレームワーク（React/Angular/Vue/Jinja2）のXSS（素通し口 `dangerouslySetInnerHTML`/`bypassSecurityTrustHtml`/`v-html`/`|safe` を除く）。
15. 構成的に推測不能な識別子（UUIDv4、128ビット以上の乱数トークン）を「予測可能」とした指摘。
16. 理論上のレース/TOCTOU。

（＋組織固有 `--fp-rules`。）

**verdictブロック:** `VERDICT: TRUE_POSITIVE|FALSE_POSITIVE|CANNOT_VERIFY` ・ `CONFIDENCE: 0-10` ・ `REFUTE_REASON: doesnt_exist|already_handled|implausible_trigger|intentional_behavior|misread_code|duplicate|not_actionable|n/a` ・ `EXCLUSION_RULE: 1-16|org|none` ・ `FIRST_LINK: file:line|none found` ・ `RATIONALE: 2-5文、file:line付き`。
TRUE_POSITIVE は全て必要: 環境上非信頼入力から到達可能、保護が不十分/迂回可能、現実的な悪用が可能。FALSE_POSITIVE はどれか1つ: 到達不能、全経路で十分に保護、読み誤り、除外ルール該当。CANNOT_VERIFY は静的推論の限界（控えめに。既定にしない）。

**集計:** 過半数TP→`true_positive`、過半数FP→`false_positive`、過半数なし→precisionは捨てる（「票割れ」を付記）／recallは `needs_manual_test` で残す／聞く。

## 悪用可能性でランク付け（confirmed のみ）

全前提条件＋最小アクセスレベルを列挙し、重大度を導出 — 各列を独立に評価し、**低い方**を取る:

| 前提条件 | 必要アクセス | 重大度 |
|---|---|---|
| 0 | 非認証リモート | HIGH |
| 1〜2 | 認証済み | MEDIUM |
| 3+ | ローカルのみ／実演経路なし | LOW |

脅威モデル一致は1段階だけ引き上げ可（2段階は不可）。スキャナの自称重大度を判定（`severity_alignment` −5..+5）。`verify_verdict ∈ {exploitable, mitigated, needs_manual_test}`。**CVSSをモデルに計算させない** — 電卓ツールを渡すか後処理で計算（モデルは生のCVSS計算のかなりの割合を間違える）。

## 割り当て

所有者は (1) `CODEOWNERS`/`OWNERS`/`.github/CODEOWNERS` のパターン一致（最後の一致が勝つ）、(2) `git log --format='%an' -n 50 -- <file>` の最上位コミッター、(3) モジュール代替（最上位ディレクトリ）。`owner_hint` にその出所を明記。

## 出力 — TRIAGE.json の所見スキーマ

`id, source, title, file, line, category, claimed_severity, verdict (true_positive|false_positive|duplicate), verify_verdict (exploitable|mitigated|needs_manual_test|null), confidence, severity (HIGH|MEDIUM|LOW|null), severity_label, severity_alignment, preconditions[], access_level, threat_match, rationale, vote_breakdown {true_positive,false_positive,cannot_verify}, refute_reasons[], exclusion_rule, first_links[], duplicate_of, absorbed[], owner_hint, missing_fields[]`。最上位: `triage_completed`, `triage_context`, `summary`。全入力所見がちょうど1回現れる — 黙って捨てない。

## カナリア／スモークテスト

既知の所見の小さなフィクスチャ（本物2、重複1、誤検知2）を同梱し、実際の入力に信頼する前に期待する verdict を出すことを確認する: f001＋f003 は確認、f002 は f001 の重複、f004 は `misread_code` で棄却、f005 は `already_handled` で棄却。実所見からテスト/フィクスチャ/デモコード（ルール2）を除外する。
