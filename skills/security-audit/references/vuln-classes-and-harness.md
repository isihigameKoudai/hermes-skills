# 脆弱性クラスと自律ハーネス（Anthropic）

Anthropic `harness/`（`vuln-pipeline`）とその対象コーパスから改作。これは実行検証側である: エージェントが入力を細工し、サンドボックス内でASAN計装の対象を実行し、検出器が発火し、第二のエージェントが検証し、第三が悪用可能性を分析し、第四が修正する。参照対象はC/C++だが、*形状*は汎用的（検出器・PoCの形・ビルドを差し替える）。

## クラッシュ品質階層（findエージェントの採点）

- **高価値:** `heap-buffer-overflow`（特にWRITE）、`heap-use-after-free`／`double-free`、`stack-buffer-overflow`、`global-buffer-overflow`、攻撃者が影響する非nullアドレスでのSEGV。
- **低価値:** 表明失敗（`assert`/`CHECK`/`DCHECK`）、無制限再帰によるスタックオーバーフロー（DoSのみ）、0x0や0x8のような小さなオフセットでのSEGV。
- **範囲外:** OOM、タイムアウト/ハング、正常終了、テスト/ビルドコードでのクラッシュ、デバッグ専用フラグのクラッシュ。（オプトイン `--accept-dos` はDoSクラス—`allocation-size-too-big`、スタック枯渇、割当起因のnull参照—を許容。heap-overflow-WRITEより下位。）

整数オーバーフローは単独の所見になることは稀で、ワイルドmalloc／過小割当／heap-OOB-write を生む**根本原因**（dr_flac、BGZF）。

## 実際に狩る具体的クラス（参照コーパス）

| 対象 | クラス | 根本原因 |
|---|---|---|
| canary（合成） | heap-buffer-overflow WRITE | 入力の長さフィールドを信頼し、8バイトのヒープバッファへコピー |
| canary | stack-buffer-overflow WRITE | 16バイトのスタックバッファへ無制限 `memcpy` |
| canary | heap-use-after-free WRITE | 番兵で早期 `free` し、垂れ下がったポインタ経由で書き込む |
| drlibs (dr_wav) | heap OOB write（36B、攻撃者制御） | 2パス `smpl` チャンク解析のデシンク—件数パスは検証、読み取りパスは無条件書き込み |
| drlibs (dr_flac) | 整数オーバーフロー→ワイルドmalloc（DoS） | STREAMINFO由来の `totalPCMFrameCount` をオーバーフロー検査なしで乗算 |
| htslib (BGZF) | intオーバーフロー→`malloc(0)` 経由のheap OOB write | `.gzi` の8バイト件数ヘッダ |
| htslib (CRAM ×9) | コーデックディスパッチ横断のheap overflow、OOB read/write、NULL参照 | XPACK／huffman／byte-array-stop／byte-array-len |
| alsa (topology) | heap OOB write（CWE-129） | `.tplg` バイナリ由来の `num_channels` を信頼し、固定 `SND_TPLG_MAX_CHAN` 配列を越えてループ |

## パイプライン段階（recon → find → grade → judge → report → patch）

1. **ビルド** — `-O1 -g -fsanitize=address -fno-omit-frame-pointer` でコンパイル（O0は遅すぎ、O2+はバグを最適化で消しうる）。1イメージを全エージェントで再利用。
2. **偵察** — 軽量エージェントが5〜15の焦点領域（「個別に攻撃する価値のある入力解析サブシステム」）を提案し、並行findエージェントが1つのバグに収束しないようにする。
3. **find** — エージェントがソースを読み、境界入力（極大/ゼロ/負/最大intサイズ、切り詰めヘッダ、不正長フィールド）を細工し、入力が**3/3回**クラッシュするまで実行（非OOM/タイムアウト）。PoCを最小化し、重複でない理由の `<dup_check>` を必ず出す。
4. **grade/検証** — **同じイメージからの新規コンテナ**が再検証。越境するのはPoCバイトのみ。5基準のルーブリック: PoC有効・再現（3回、<2/3で失敗）・非OOM/タイムアウト（137=OOM、124=タイムアウト）・プロジェクトコード内のクラッシュ・実行横断でクラッシュクラスが一貫。
5. **judge**（ストリーミング）— 過去のバグに対して NEW／DUP_BETTER／DUP_SKIP を、クラッシュクラスではなく**根本原因**を鍵に判定。
6. **report** — 6セクションの悪用可能性分析: `<primitive>`（書き込み/読み取りバイト、オフセット、制御）・`<reachability>`（実攻撃面かハーネス由来か）・`<heap_layout>`・`<escalation_path>`・`<constraints>`（stack-protector/RELRO/PIE—バイナリを確認）・`<escalation_attempt>`。加えて `<novelty>`（FIXED/UNFIXED/UNKNOWN）と `<severity>`。別の評価エージェントが各セクションを意味的に採点。
7. **patch**（別コマンド）— 下のラダー参照。

## 修正検証ラダー（T0–T3、実行オラクル — モデルの判断で失敗しない）

| 段 | 問い | オラクル |
|---|---|---|
| T0 ビルド | 修正ツリーはコンパイルできるか | `git apply`＋ビルド終了コード |
| T1 PoC停止 | 元のクラッシュは消えたか | 終了0 かつ出力に `AddressSanitizer:` なし |
| T2 テスト通過 | 既存挙動を壊していないか | テストコマンド終了コード |
| T3 再攻撃 | 根本原因が消えたか、この入力だけか | 新規50ターンのfindエージェントが修正バイナリを攻撃 |
| style | メンテナは受け入れるか | LLM判定0–10、助言のみ |

修正は T0・T1・T2（またはテストなし）・T3 が全てクリーンで合格。**なぜ再攻撃か:** モデル修正の約60%はビルド＋再現を通過するが、ファジング/差分テストを生き残るのは15%未満。支配的な失敗は「クラッシュ箇所の境界検査だけで、悪い値が少し異なる入力から到達可能なまま」というもの。再攻撃がそれを防ぐ。

## 重複排除／新規性／judge（3層）

1. **実行時** — `found_bugs.jsonl`（`known_bugs` で種蒔き）。エージェントはASANシグネチャを意味的に比較。`<dup_check>` 必須（無い提出はパイプラインが拒否）。`known_bugs` は**関数名**で照合（行番号ではない）。
2. **judge** — 根本原因を鍵にしたLLM重複排除（NEW／DUP_BETTER／DUP_SKIP）、ロック下で直列化。
3. **新規性**（オプトイン、ホスト側のみ）— `git log <commit>..HEAD -- <crash_file>` で FIXED/UNFIXED を述べる。GitHubに触るのはオーケストレータだけ。reportコンテナのegressは制限されたまま。

## サンドボックスと信頼モデル（なぜ重要か）

制約は**プロンプトではなくコード**で強制する。全エージェントは gVisor コンテナ（`runsc`）で動き、ネットワークegressは `--internal` ネットワーク上のHTTP CONNECT許可リストプロキシ経由でモデルAPIに限定。エージェントを生成するコマンドはサンドボックス外での起動を拒否（`--dangerously-no-sandbox`＝使い捨てVMのみ）。2コンテナの信頼境界: findとgradeは同じイメージから作った別コンテナで動き、越境するのはPoCバイトのみ。資格情報は環境変数のみ（`AWS_PROFILE`/`~/.aws`/IMDSは転送しない—`169.254.169.254` への経路なし）。セットアップ段階（`docker build` の外向きネット）は攻撃段階（egressをモデルAPIに固定）から分離。

**別スタックへの移植**は次に答えること: *何が所見の信号か？*（ASANクラッシュ→例外/カナリアファイル/DNSコールバック）・*PoCはどんな形か？*（クラッシュ入力→HTTP要求列/トランザクション列/テストハーネス）・*対象のビルドと実行方法は？*（Docker+clang+ASAN→その言語のコンテナ内ビルド）。脆弱性クラスの軸: メモリ安全 ／ Web-API（SQLi、XSS、SSRF、XXE、パストラバーサル、IDOR）／ デシリアライズRCE ／ ロジック-レース（TOCTOU、特権昇格）／ 暗号（弱いRNG、タイミング、nonce再利用）／ DoS（ReDoS、ハッシュフラッディング）／ スマートコントラクト（リエントランシ、アクセス制御）／ ML-AI（プロンプト注入、脱獄、抽出）／ プロトコル解析。
