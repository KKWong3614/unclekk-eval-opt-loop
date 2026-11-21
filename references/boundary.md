# 与已有自改进栈的边界

> 边界声明必须写进产出 SKILL 的"不适用 | Out of scope"段。本机实体已核对。

## 本机真实存在的相邻技能（已核对）

| 技能 | 定位 | 与本技能的关系 |
|---|---|---|
| `self-improving-agent` | 经验记录器：把 learnings/errors 记入 .learnings/*.md，配合 hook | **不同职责**。它沉淀经验；本技能不做经验沉淀 |
| `skill-optimizer` | 四步闭环编排器：基线评估→补丁修订→独立复评（防泄漏）→棘轮 | **优化执行器**。它真正改技能；本技能不改技能。"独立复评防泄漏"思想与本技能"独立验证"同源，可参考但不实现其闭环 |
| `skill-evolver` | 基于 SkillEvolver 论文：角色分离+策略多样化+补丁式修订+独立审计+棘轮 | **优化执行器**。同上，本技能不实现棘轮/角色分离 |
| `unclekk-metacog-self-evolve` | 五制品+三闸+双指标棘轮的规则演化引擎 | **优化执行器/演化引擎**。本技能不做棘轮裁决 |
| `unclekk-paper2skill` | 论文→三段式骨架元技能 | **上游**。本技能复用其骨架约定（指令/工具/验证 + 溯源表 + 局限段）|

## 边界总图（优化层）

```
经验沉淀：self-improving-agent（记 learnings）
优化执行：skill-optimizer / skill-evolver / unclekk-metacog-self-evolve（改技能、棘轮、角色分离）
        ↑ 可接入本技能作验收判据
本技能：判据层 —— "验证反直觉 / 局部指标不可信 / 独立验证门禁 / 全局复核"
        ↓ 不改技能、不记经验、不做棘轮
```

## 一句话边界声明（可直接粘进 SKILL）
> 本技能提供"验证反直觉 / 局部指标不可信"的判据层，可接到任何优化器之前或之后作为验收判据；本身不改技能（skill-optimizer/skill-evolver）、不沉淀经验（self-improving-agent）、不做棘轮裁决（unclekk-metacog-self-evolve）。"独立验证"与 skill-optimizer 的防泄漏复评同源，但不实现其基线→补丁→复评→棘轮闭环。

## 特别声明
- 本技能不压缩大模型：本机无 H200/vLLM，任何压缩需求应 fail-closed 停下并说明。
- dogfood 用低风险小任务（如提示词/参数优化），不碰模型权重。
