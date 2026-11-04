# -*- coding: utf-8 -*-
"""Gate 2（算数ゲート）テンプレート: ファネル逆算 / 工数積み上げ / キャパシティ突き合わせ / 単位経済性。

使い方: 下の「入力」ブロックをヒアリング結果で書き換えて `python3 funnel_model.py` を実行する。
出力はそのまま成果物（`<project>/.local/research/<date>-<feature>/memory/` 配下に保存）にできる。

段階宣言（Gate 2-F）: 冒頭の STAGE を必ず明示する。Stage A = 仮定ベース（実績データ無し）、
Stage B = 根拠ベース（インタビュー等で支払意思・既存支出を確認済み）。仮定を予測として読ませない。
"""

STAGE = "Stage A（仮定ベース・実績データ無し）"  # or "Stage B（インタビュー根拠）"

# ============ 入力（ここを書き換える） ============
PRICE = {"Basic": 199, "Standard": 399, "Premium": 899}   # 商品ごとの価格
FEE = 0.20            # 決済・プラットフォーム手数料率（要検証。例: Fiverr新規20%）
DELIVER_H = {"Basic": 6, "Standard": 8, "Premium": 16}    # [Assumption] 納品工数
SALES_H = 0.5         # [Assumption] 営業工数（受注前後のやり取り）— 入れ忘れが最頻の欠陥
ADMIN = 0.15          # [Assumption] 管理工数
CAP_WEEK_LO, CAP_WEEK_HI = 2, 3                            # Gate 0 で確認した週あたり稼働上限
WEEKS = 4.33

TARGET_ORDERS_PER_MONTH = 1   # ファネル逆算の起点
CTR_CANDIDATES = (0.01, 0.02, 0.03)   # [Assumption] 表示→クリック
CVR_CANDIDATES = (0.01, 0.02, 0.03)   # [Assumption] クリック→成約
# =================================================


print(f"財務モデル段階: {STAGE}")

# ---- D. 単位経済性 ----
print("\n=== D. 単位経済性（実効時給）===")
eff = {}
for k in PRICE:
    net = PRICE[k] * (1 - FEE)
    h = (DELIVER_H[k] + SALES_H) * (1 + ADMIN)
    eff[k] = net / h
    print(f"  {k:9s} 価格 ${PRICE[k]:5d} -> 手数料後 ${net:7.1f} / 総工数 {h:5.1f}h -> 実効 ${eff[k]:6.1f}/h")

# ---- B/C. 工数積み上げとキャパシティ（＋天井） ----
avg_h = sum((DELIVER_H[k] + SALES_H) * (1 + ADMIN) for k in PRICE) / len(PRICE)
cap_lo, cap_hi = CAP_WEEK_LO * WEEKS, CAP_WEEK_HI * WEEKS
print("\n=== B/C. 工数積み上げとキャパシティ ===")
print(f"  1件あたり平均総工数: {avg_h:.1f}h")
print(f"  月の稼働上限: {cap_lo:.1f}h 〜 {cap_hi:.1f}h")
print(f"  -> 月に納品可能な件数: {cap_lo / avg_h:.1f} 〜 {cap_hi / avg_h:.1f} 件")
cheapest = min(PRICE, key=lambda k: eff[k])
print(f"  -> 月商上限（全件を最高単価 {max(PRICE)} で埋めた非現実的な最大）: "
      f"${cap_hi / ((DELIVER_H[max(PRICE)] + SALES_H) * (1 + ADMIN)) * max(PRICE):.0f}")

# ---- A. ファネル逆算 ----
print(f"\n=== A. ファネル逆算（月{TARGET_ORDERS_PER_MONTH}件の成約に必要な量）===")
print("  ※ CTR/CVR は [Assumption]。実測が取れたら差し替える。")
for ctr in CTR_CANDIDATES:
    for cvr in CVR_CANDIDATES:
        clicks = TARGET_ORDERS_PER_MONTH / cvr
        imps = clicks / ctr
        print(f"  CTR {ctr:4.0%} / CVR {cvr:4.0%}  ->  クリック {clicks:6.0f}  /  表示 {imps:9.0f}")

# ---- 感度分析 ----
base = eff[cheapest]
print("\n=== 感度分析（どのレバーが最も効くか）===")
print(f"  基準: {cheapest} の実効時給 ${base:.1f}/h")
half_h = max(DELIVER_H[cheapest] / 2, 0.5)
print(f"  (1) 納品工数を半減 -> ${PRICE[cheapest] * (1 - FEE) / ((half_h + SALES_H) * (1 + ADMIN)):.1f}/h")
print(f"  (2) 最高単価プランへ誘導 -> ${eff[max(PRICE, key=lambda k: eff[k])]:.1f}/h")
print(f"  (3) 価格を1.5倍 -> ${PRICE[cheapest] * 1.5 * (1 - FEE) / ((DELIVER_H[cheapest] + SALES_H) * (1 + ADMIN)):.1f}/h")
print(f"  (4) 手数料 {FEE:.0%} を直販0%に -> "
      f"${PRICE[cheapest] / ((DELIVER_H[cheapest] + SALES_H) * (1 + ADMIN)):.1f}/h")

# ---- 天井の判定（Gate 2-C の追加要件） ----
print("\n=== 天井の判定 ===")
max_orders = cap_hi / avg_h
if TARGET_ORDERS_PER_MONTH > max_orders:
    print(f"  NG: 目標 {TARGET_ORDERS_PER_MONTH} 件/月 は納品上限 {max_orders:.1f} 件/月 を超える。"
          "目標を下げるか前提を変えて再計算するまで出力してはならない。")
else:
    print(f"  OK（ただし天井が低い場合、流入施策の目的を「売上」ではなく"
          "「1件目の実績・レビュー取得」に書き換えること）")
