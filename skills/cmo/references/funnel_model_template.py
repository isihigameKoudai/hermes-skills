"""
Gate 2（算数ゲート）用 ファネル逆算・単位経済性検証テンプレート

使い方:
1. INPUTS を、Gate 0（制約ヒアリング）とリサーチ結果に基づいて実際の値に書き換える。
2. `python funnel_model_template.py` として必ずコード実行し、結果を確認する。
   - 暗算での逆算は禁止。このスクリプトを実行して得られた数値のみを本文に転記すること。
3. 出力される `capacity_check` が False の場合、計画を出力してはならない。
   価格・転換率・工数のいずれかを変更し、True になるまで再計算すること。
4. 実行結果（標準出力）はそのまま `.local/research/<folder>/memory/funnel_model_result.md` 等に
   コピーして成果物として保存する。

このファイルは fix_plan.md の Gate 2（算数ゲート）チェックリストに対応する:
  A. ファネル逆算（トップダウン）
  B. 工数の積み上げ（ボトムアップ）
  C. 突き合わせ判定（キャパシティ検証）
  D. 単位経済性
  E. 用語の正確性（粗利 vs 営業利益）
"""

from dataclasses import dataclass, field


# =========================================================
# INPUTS — ここを実際の値に書き換えてから実行する
# =========================================================


@dataclass
class Inputs:
    # --- ゴール ---
    monthly_revenue_goal_usd: float = 13285.0

    # --- 単価・オファー ---
    price_per_deal_usd: float = 500.0  # 1成約あたりの平均単価
    payment_fee_rate: float = (
        0.03  # 決済手数料率（例: Stripe 2.9%+$0.30 相当なら概算で入れる）
    )
    payment_fee_fixed_usd: float = 0.30  # 決済手数料の固定分（1決済あたり）

    # --- ファネル転換率（[検証済]/[公称]/[推定] のいずれかをラベリングして本文に転記すること）---
    # 例: lead -> contact -> meeting -> deal
    contact_to_lead_rate: float = 0.05  # 接触 → リード化率 [推定]
    lead_to_meeting_rate: float = 0.30  # リード → 商談化率 [推定]
    meeting_to_deal_rate: float = 0.25  # 商談 → 成約率 [推定]

    # --- 工数（1件あたり／時間） ---
    delivery_hours_per_deal: float = 3.0  # 納品工数（1成約あたり）
    sales_hours_per_lead: float = 0.5  # 営業工数（1リードあたりの接客・提案工数）
    management_overhead_rate: float = 0.15  # 管理工数（総稼働に対する割合。15%目安）

    # --- 制約（Gate 0 のヒアリング結果を必ず反映） ---
    weekly_capacity_hours: float = 20.0  # 事業者が実際に使える週あたり稼働時間の上限


@dataclass
class Results:
    required_deals: float = 0.0
    required_meetings: float = 0.0
    required_leads: float = 0.0
    required_contacts: float = 0.0

    total_delivery_hours: float = 0.0
    total_sales_hours: float = 0.0
    subtotal_hours: float = 0.0
    management_hours: float = 0.0
    total_monthly_hours: float = 0.0
    weekly_hours_required: float = 0.0

    capacity_check_passed: bool = False
    capacity_gap_hours_per_week: float = 0.0

    effective_hourly_rate_usd: float = 0.0
    gross_margin_rate: float = 0.0

    notes: list = field(default_factory=list)


def compute(inputs: Inputs) -> Results:
    r = Results()

    # --- A. ファネル逆算（トップダウン） ---
    r.required_deals = inputs.monthly_revenue_goal_usd / inputs.price_per_deal_usd
    r.required_meetings = r.required_deals / inputs.meeting_to_deal_rate
    r.required_leads = r.required_meetings / inputs.lead_to_meeting_rate
    r.required_contacts = r.required_leads / inputs.contact_to_lead_rate

    # --- B. 工数の積み上げ（ボトムアップ） ---
    r.total_delivery_hours = r.required_deals * inputs.delivery_hours_per_deal
    r.total_sales_hours = r.required_leads * inputs.sales_hours_per_lead
    r.subtotal_hours = r.total_delivery_hours + r.total_sales_hours
    r.management_hours = r.subtotal_hours * inputs.management_overhead_rate
    r.total_monthly_hours = r.subtotal_hours + r.management_hours
    r.weekly_hours_required = r.total_monthly_hours / 4.33

    # --- C. 突き合わせ判定 ---
    r.capacity_check_passed = r.weekly_hours_required <= inputs.weekly_capacity_hours
    r.capacity_gap_hours_per_week = (
        r.weekly_hours_required - inputs.weekly_capacity_hours
    )

    # --- D. 単位経済性 ---
    fee_per_deal = (
        inputs.price_per_deal_usd * inputs.payment_fee_rate
        + inputs.payment_fee_fixed_usd
    )
    net_price_per_deal = inputs.price_per_deal_usd - fee_per_deal
    hours_per_deal_fully_loaded = (
        inputs.delivery_hours_per_deal
        + inputs.sales_hours_per_lead
        / inputs.lead_to_meeting_rate
        / inputs.meeting_to_deal_rate
    )
    r.effective_hourly_rate_usd = net_price_per_deal / hours_per_deal_fully_loaded

    # --- E. 用語の正確性 ---
    # 自己労働費・税を計上していないため、これは「粗利率」であり「営業利益率」ではない。
    r.gross_margin_rate = net_price_per_deal / inputs.price_per_deal_usd

    if not r.capacity_check_passed:
        r.notes.append(
            f"[NG] 週あたり必要稼働 {r.weekly_hours_required:.1f}h が上限 "
            f"{inputs.weekly_capacity_hours:.1f}h を {r.capacity_gap_hours_per_week:.1f}h 超過している。"
            "価格・転換率・工数のいずれかを見直し、再計算するまでこの計画を出力してはならない。"
        )
    else:
        r.notes.append("[OK] 週あたり必要稼働は上限内に収まっている。")

    r.notes.append(
        "この結果に含まれる転換率・工数はすべて [推定] である場合、"
        "本文には必ず「仮説であり実測が必要」と明記すること。"
    )
    r.notes.append(
        "gross_margin_rate は自己労働費・税を含まない粗利率である。"
        "「営業利益率」という語を使う場合は自己労働費・税を別途計上すること。"
    )

    return r


def print_report(inputs: Inputs, r: Results) -> None:
    print("=" * 60)
    print("Gate 2: 算数ゲート 計算結果")
    print("=" * 60)
    print("\n--- A. ファネル逆算（トップダウン） ---")
    print(f"目標月商: ${inputs.monthly_revenue_goal_usd:,.0f}")
    print(f"必要成約数/月: {r.required_deals:.1f} 件")
    print(f"必要商談数/月: {r.required_meetings:.1f} 件")
    print(f"必要リード数/月: {r.required_leads:.1f} 件")
    print(f"必要接触数/月: {r.required_contacts:.1f} 件")

    print("\n--- B. 工数の積み上げ（ボトムアップ） ---")
    print(f"納品工数合計: {r.total_delivery_hours:.1f} h/月")
    print(f"営業工数合計: {r.total_sales_hours:.1f} h/月")
    print(f"小計: {r.subtotal_hours:.1f} h/月")
    print(
        f"管理工数（{inputs.management_overhead_rate * 100:.0f}%）: {r.management_hours:.1f} h/月"
    )
    print(f"総稼働時間: {r.total_monthly_hours:.1f} h/月")
    print(f"週あたり必要稼働: {r.weekly_hours_required:.1f} h/週")

    print("\n--- C. 突き合わせ判定 ---")
    print(
        f"週あたり稼働上限（Gate 0 ヒアリング結果）: {inputs.weekly_capacity_hours:.1f} h/週"
    )
    print(
        f"判定: {'PASS' if r.capacity_check_passed else 'FAIL（出力禁止・再計算が必要）'}"
    )

    print("\n--- D. 単位経済性 ---")
    print(f"実効時給: ${r.effective_hourly_rate_usd:.2f}/h")

    print("\n--- E. 用語の正確性 ---")
    print(f"粗利率（自己労働費・税未計上）: {r.gross_margin_rate * 100:.1f}%")

    print("\n--- Notes ---")
    for n in r.notes:
        print(f"- {n}")
    print("=" * 60)


if __name__ == "__main__":
    inputs = Inputs()
    results = compute(inputs)
    print_report(inputs, results)
