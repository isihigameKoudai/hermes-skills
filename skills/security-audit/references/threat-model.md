# 脅威モデル（Anthropic の手法）

Anthropic `defending-code-reference-harness` の `.claude/skills/threat-model/` から改作。撃つ前に狙う: 脅威モデルは、特定のバグとは独立に「**このシステムで何が悪くなりうるか、誰がやるのか、それにどう対処するか**」に答える。これは*地図*であり、脆弱性発見は*金属探知機*である。

**試金石** — コードを1行直して項目が消えるなら、それは*脆弱性*であって*脅威*ではない。脅威（「信頼できないメディア解析によるRCE」）は既知バグを全て直しても残る。脆弱性（「`dr_wav.h:412` が `chunk_size` を境界検査しない」）は残らない。**脅威**を生み出すこと。脆弱性は、脅威の尤度を上げる**証拠**としてのみ現れる。

**安全の前置き（常に）** — 静的解析のみ。ソース・git履歴・提供された脆弱性レポートを読み、出力ファイル（`THREAT_MODEL.md`）を1つ書く。対象のビルド/実行/ファジング/変更はせず、対象インフラへの要求もしない。助言の照会は公開DB（NVD、GitHub Security Advisories、プロジェクトのトラッカー）のみで、実稼働は決して照会しない。エクスプロイト実行による検証を求められたら断り、サンドボックス化パイプラインへ回す。

## モード

| | `bootstrap` | `interview` |
|---|---|---|
| 必要なもの | ローカルチェックアウト、必要なら過去の脆弱性 | セッション内のアプリ所有者 |
| 手法 | 5段階の調査スウォーム→脆弱性の一般化→STRIDE穴埋め | 四問フレームワーク（Shostack） |
| 向く対象 | 継承されたシステム、サードパーティコード、OSS依存、CVE履歴 | 新規システム、設計レビュー、ビジネスロジックのリスク |

`bootstrap-then-interview`: bootstrap を最後まで回してから所有者と草案を歩く（所有者とコードベースが両方ある場合に推奨）。全モードが同じ `THREAT_MODEL.md` を出力する。

## 四問フレームワーク（interview）

1. **何に取り組んでいるのか？** → §1 文脈、§2 資産、§3 入口点と信頼境界。
2. **何が悪くなりうるか？** → §4 脅威行（STRIDE＋「データセット行へのIDOR」「長さフィールドの整数オーバーフロー」のような、修正後も残る粒度のドメイン固有クラス。「Web脆弱性」のような粒度ではだめ）。
3. **どう対処するのか？** → impact / likelihood / status / controls、§5 見送り、§8 緩和策。
4. **うまくやれたか？** → ランクとカバレッジの検証、§6 未解決の問い。

来歴の規律: 各事実に `[Code-verified]`（ソースを読んだ）か `[Owner-states]`（聞いただけで未検証）を付す。スコアに影響する `[Owner-states]` の事実は、必ず §6 に「検証すべきフォローアップ」として列挙する。

## bootstrap — 5段階

**入力:** `<target-dir>`（必須）、`--vulns <path>`（CVE ID／CSV `id,title,component,description`／markdownのペネトレポート／`id`+`description`を含むJSON配列）、`--depth recon|full`。

### 段階1 — 調査スウォーム（並行サブエージェント、1バッチ）

| エージェント | 指示 | 返すもの |
|---|---|---|
| 文書リーダー | README*、SECURITY.md、CHANGELOG*、最上位docs/、ビルドマニフェストを読む | システムの散文説明＋自己文書化されたセキュリティ修正 |
| サーフェスマッパー | 下の表の入口シグネチャをgrepし、サーフェス・file:function・何を越えるかを記す（サプライチェーン面も含む）。`vendor/`/`node_modules/`/`third_party/`/生成コードは除外 | §3行 `{entry_point, description, trust_boundary, file_refs}` |
| インフラリーダー | `*.tf`、k8sマニフェスト、`Dockerfile*`、CIワークフロー、IAM/SA/ACLを読む。各々について (a) 実行する識別と到達先、(b) ツリー外で管理されるアクセス付与、(c) 移行/破棄を生き延びる資格情報/主体 | §3インフラ面＋§4行 |
| 資産ファインダー | 保護/生成する資産（敏感データ、プロセス整合性〔ネイティブでは常に〕、可用性、埋め込み側の資産）を特定 | §2行 `{asset, description, sensitivity}` |
| 履歴マイナー | 基本セット `CVE- security vuln fix exploit` に言語/ドメイン由来の6〜10語を加え、`git log --all -i --grep=<kw>` でヒットの全文+差分を読む。ツリー内 `issues/`/`bugs/` も | 脆弱性行 `{id(commit), title, component, class, vector}` |
| 助言フェッチャー | GitHubリモートがあれば `gh api /repos/{owner}/{repo}/security-advisories` | 脆弱性行 `{id(CVE/GHSA), title, component, class, vector}` |
| 脆弱性ファイルパーサー | `--vulns` 指定時のみ | 正規化した脆弱性行 |

**サーフェスマッパーのgrep対象**（種。言語の慣用句で拡張する）:

| サーフェス | 探すもの |
|---|---|
| ネットワーク | socket `listen`/`accept`/`bind`、HTTPルート定義（`@app.route`）、RPC/gRPC/GraphQLサービス定義 |
| ファイル/形式解析 | `open(`、マジックバイト検査、「parse」/「decode」/「load」/「unmarshal」関数 |
| CLI/環境 | argvパーサ（`argparse`）、env読み取り（`getenv`） |
| デシリアライズ | 外部データへのネイティブデシリアライザ（`pickle`、`ObjectInputStream`） |
| DB/クエリ | 生クエリ文字列構築、ORMの `.raw()`/`.query()` エスケープ |
| IPC/プラグイン | `dlopen`、サブプロセス起動、設定への `eval`/`exec`、動的import |
| サプライチェーン | 依存ロックファイル、ベンダー化ライブラリ、ビルドスクリプトの `curl \| sh` |
| インフラ/IAM | terraform `google_*_iam_*`/`aws_iam_*`、k8s `serviceAccountName`/WIF、データセット/テーブル `access{}`、秘密マウント |

### 段階2 — 合成（オーケストレータで）
- §1 システム文脈（1〜2段落）。§2 資産（重複排除、欠落補完—ネイティブコードには「ホストプロセス整合性」を追加）。§3 入口点と信頼境界（行ごとに境界を名指す: 「信頼できないファイル→プロセスメモリ」「非認証HTTP→アプリロジック」）。到達可能な§2資産を列挙。**カバレッジ不変条件: §3の全行は段階3/4で1つ以上の脅威を得る。**
- 脆弱性作業表: idで重複排除。各々がどの§3入口点を経由したか（ソースを読んで確認、§3に無ければ追加）。§4 `evidence` になる。

### 段階3 — 一般化: 脆弱性→脅威
- **3a クラスタ化** — `(入口点, バグクラス, 到達資産)` でまとめる。各クラスタ＝1つの候補脅威。試金石を適用。例: WAV/FLACパーサのヒープオーバーフロー3件＋整数オーバーフロー1件→「信頼できない音声ファイル解析によるRCE」1つの脅威、evidence＝4 ID。
- **3b 変種走査（尤度を上げる）** — 脆弱性リストに無い**兄弟**（同じ形状のコード経路）をgrep。悪用可能性の証明ではなく、パターンを共有する面の広さの見積もり。兄弟の `file:func` は作業メモに残し（§4 evidence には入れない。evidenceは確定済みの過去脆弱性のみ）。
- **3c スコア** — `actor` は入口点から（ファイル解析→誰がファイルを供給するか、ネットワーク→`remote_unauth`/`remote_auth`）。`impact` は資産＋バグクラスから。`likelihood`（同じ面に確定済み脆弱性≥1→最低`likely`、公開エクスプロイト→`almost_certain`、兄弟＋既知手法→`possible`、制御で下方修正）。`controls`（サイズ上限、入力検証、サンドボックス/seccomp、ASLR/スタック保護/CFI、パラメタ化クエリ、認証ミドルウェア、レート制限をgrep）。`status` は制御が完全に塞がない限り `unmitigated`。`recommended_mitigation` はクラスタごとに1つのクラスレベルの制御。

### 段階4 — 穴埋め（STRIDE）
§4行の無い各§3入口点について STRIDE を歩く — 攻撃者は**なりすまし**（信頼元を装う）、**改ざん**（転送中/保存中のデータを変える）、**否認**（帰属可能なログなしに行動）、**情報開示**（読むべきでないものを読む）、**DoS**（資源を枯渇させる）、**昇格**（開始時より高い特権を得る）ができるか。既に§4行のある入口点も再確認。インフラ/IAMの入口点は代わりに **過大付与**、**横断的識別**、**ドリフト**（ツリー外管理の付与）、**残存アクセス**、**列露出**、**スコープ強制** を歩く。**§4は evidence が空の行を1つ以上含む**必要がある（そうでなければ段階4は走っていない）。§5に「検討して除外したSTRIDEカテゴリ＋理由」を書く。

### 段階5 — 出力
カバレッジ検査: 各§3入口点が1つ以上の§4 `surface` セルに名指しされる。§4を（impact降順, likelihood降順）で整列し `id` を `T1, T2, …`。§6 未解決の問い（配備文脈、意図したアクター、検証不能な制御、リスク選好）。§8 クラスレベル緩和策ごとに1行。

## THREAT_MODEL.md スキーマ（契約 — 見出しと列順は厳守）

必須セクションを順に: `# Threat Model: <name>`, `## 1. System context`（散文）, `## 2. Assets`, `## 3. Entry points & trust boundaries`, `## 4. Threats`, `## 5. Deprioritized`, `## 6. Open questions`, `## 7. Provenance`, `## 8. Recommended mitigations`（任意）。

- **§2 Assets** — `| asset | description | sensitivity |`。`sensitivity ∈ {low, medium, high, critical}`。
- **§3 Entry points & trust boundaries** — `| entry_point | description | trust_boundary | reachable_assets |`（資産はカンマ区切り）。
- **§4 Threats** — `| id | threat | actor | surface | asset | impact | likelihood | status | controls | evidence |`
  - `actor ∈ {remote_unauth, remote_auth, adjacent_network, local_user, local_admin, supply_chain, insider}`
  - `impact ∈ {low, medium, high, critical, existential}`
  - `likelihood ∈ {very_rare, rare, possible, likely, almost_certain}`
  - `status ∈ {unmitigated, partially_mitigated, mitigated, risk_accepted}`
  - `evidence` = CVE/issue/commit ID。空でもよい。**evidence は尤度を上げるもので、脅威そのものではない。**
  - `id` は安定（`T1,T2,…`）。削除時に振り直さない。impact, likelihood 降順で整列。
- **§5 Deprioritized** — `| threat | reason |`。
- **§6 Open questions** — 箇条書き（所有者の主張／コードで検証不能な事実）。
- **§7 Provenance** — `mode: interview|bootstrap|bootstrap-then-interview`, `date`, `target @ <commit>`, `inputs`, `owner`。
- **§8 Recommended mitigations** — `| mitigation | threat_ids | closes_class | effort |`。`closes_class: yes|partial`、`effort: S|M|L`。

**Impact:** low = 迷惑・データ/可用性の喪失なし ／ medium = 一部ユーザーの限定的なデータ露出や可用性低下 ／ high = 重大な露出・整合性喪失・完全な可用性喪失 ／ critical = 主資産の完全な侵害（RCE、認証バイパス、大規模データ持ち出し）／ existential = 組織の継続的な運営を脅かす。

**Likelihood:** very_rare = 国家級の資源か極めて稀な前提連鎖が必要 ／ rare = 高度な技能＋非既定設定が必要 ／ possible = 動機ある攻撃者が公開ツールで現実的に実行可能 ／ likely = 面が到達可能で手法が周知、本/類似システムに前例 ／ almost_certain = 実地で活発に悪用、または既定設定で自明に自動化可能。evidence は尤度を**上げ**、controls は**下げる**。現行制御後の**残余**尤度を評価する。
