---
name: ambitious-delegation
description: "Use when delegating to an AI model to raise ambition."
version: 0.1.0
author: Koudai Ishigame (isihigameKoudai)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, ambition, altitude, depth, range, outcome-ownership, ai-usage]
---

# Ambitious Delegation

## When to Use

- モデルにタスクを渡す際、デフォルトの「より速く」以上の野心を引き出したいとき。
- 「深い版」の手法、外部審判の用意、複数分野の動員、成果所有への転換を設計したいとき。
- 委任の抽象度（Altitude / Depth / Range）を意図的に上げたいとき。

モデルにタスクを渡すとき、デフォルトの「同じ仕事をより速く」(Speed) で満足してはならない。野心には4つの軸がある。Speed は確立済み・創造性不要でスキップせよ。残る3軸を上げるのが本スキルの目的。

## 4軸

- **Speed**: 同じ仕事を短時間で。経済価値の基本だが創造性を要さない。スキップ。
- **Altitude**: タスクではなく「成果」の抽象度で考える。
- **Depth**: タスクを分野の第一人者がやる方法でやる。タスクの層より一段下のデータ・道具・問題に触れる。
- **Range**: 表層が要求する分野だけでなく、複数の分野の知識・道具・技法を動員する。

## 成果所有 vs タスク所有（Altitude の核心）

タスクを所有するとは「作業の完了」に責任を持つこと。成果を所有するとは「目的の状態の持続」に責任を持つこと。この一点で「終わり」の定義が変わる。

- タスク所有: done = 納品物が渡った。リスクは依頼者に残る。
- 成果所有: done = 目的の状態が持続している。リスクを自分が引き受ける。支払いの対象は「不安の消滅」であり、時給で割れない。

**判別テスト**: 自分が去った後、何が持続しているかを問え。納品物だけ残るならタスク。監視と修復のループが回り続けるなら成果。

**Altitude の問い**: タスクを渡す前に「what do you want to happen next?」（タスクの先に何を起こしたいか）を問え。タスクの先の成果を所有せよ。成果を所有すれば、人間がタスクを渡し続けるループから抜け、耐久ワークフローになる。ただしこれにはモデルが計算機・データ・外部ツールにアクセスできる基盤が必要。

## Depth: 「深い版」を強制する

「大きい版」ではなく「深い版」を要求する。使う定型プロンプト:

> I want a deeper version of this task, not a bigger one. Before rewriting it: (1) say what a top professional in this field would do here that I'm not asking for; (2) name the rawest material they would start from instead of what has already been digested for me; (3) name the specific methods and tools they would use; (4) say what, other than you or me, would show the result is right. Then rewrite my prompt to ask for exactly that.

Depth の技法:
- 同じ道具を要求する。プロっぽく「振る舞う」よう指示すると語彙だけが変わり手法が変わらない。markdown 表を出したら DB と統計モデルを要求せよ。
- 無理な目標を「極めて妥当」と言い切れ。5s→10s の改善依頼なら 200ms を要求せよ。「不可能に見える」とモデルが言ったら「十分解ける、続けろ」と再主張せよ。
- 既知を敵対的に検証させる。生データへのアクセスを与え、仮定を再現させよ。
- 新しい知識を産ませる。データの奥まで入ったら盲点を探させよ。

## 外部審判の禁則

**モデルに自分自身を判定させてはならない。** 自己評価は必ず外部検証で置き換える（CI・実ビルド・テスト・実データ・別のツール）。理想はモデルが即座に実行してフィードバックを得られるツール。

## Range: 名詞を動詞に、乗員を召集

- **名詞を動詞に変換せよ**（The Art of Innovation の古い技法）。「四半期レビュー」は「デッキ」ではなく「多忙な人に因果の物語を信じさせ、不確実性の下で30分で決断させること」。動詞にすると、どの分野が独自の視点をもたらすかが分かる。
- **乗員を召集せよ**。例: 分析官・ジャーナリスト・編集者、発表ならモーション/音響デザイナー、敵対チームとして空売り屋と法廷会計士。多エージェント（subagents / orchestrator）で動員する。
- **ロールプレイに堕ちるな**。「空売り屋のように書け」ではなく「空売り屋が実際にやる調査」をやらせよ。分野と技法を見つけるためにこの方法を使え。

## 自己効力感（野心の前提）

人間は「可能と信じる範囲」に制約される。この制約はハックできる:

- **可能だと信じることで難しいことを成す**: Dantzig は未解決問題を宿題と誤認して解いた。
- **他人が成すのを見て成す**: 4分マイル。Bannister が破って46日後に追走者が続いた。2時間マラソンも同型。
- **失敗する許可を自分に与えることで成す**: Linux は「趣味だ、GNU みたいに大きくプロにならない」と宣言した者が作った。

具体的で難しい目標は「全力でやれ」という指示より高い成果を生む（Locke & Latham）。無謀な目標＋短い締切が実績を生む（Collison の Fast リスト）。

## 実践チェックリスト

1. タスクを渡す前に、その先の成果を問え（Altitude）。
2. 「深い版をくれ」プロンプトで分野第一人者の手法を引き出せ（Depth）。
3. 自己評価を禁じ、外部審判を用意しろ。
4. 名詞を動詞に変換し、未動員の分野を召集しろ（Range）。
5. Speed で満足するな。
