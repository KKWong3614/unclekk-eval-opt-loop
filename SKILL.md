---
slug: unclekk-eval-opt-loop
name: unclekk-eval-opt-loop
displayName: UncleKK 自主优化验证闭环
version: 1.2.0
summary: >-
  通用 Agent 自主优化验证闭环：给定"可度量目标 + 独立验证器"，按"设目标 → 反馈引导搜索 → 独立验证门禁 → 局部指标全局复核"迭代，输出经独立验证的最终方案，并提供"局部指标不可信、须全局复核"的判据层。 | General eval-optimization loop: given a measurable objective + independent verifier, iterate set-objective → feedback-guided search → independent verification gate → global recheck of local metrics, providing the judgment layer that local metrics are untrustworthy without global recheck.
description: >-
  自主优化验证闭环技能。当需要对某方案做可验证的自主优化、或要判断局部指标是否在误导决策时使用：把 CompressionBench 的"terminal-task + 反馈搜索 + 独立验证 + 局部排名须全局复核"抽象成与目标域无关的闭环，核心卖点是"完整反馈可能推翻大量局部排名，局部指标不可信"。本技能提供判据层，不是优化执行器：不改技能、不沉淀经验、不做棘轮裁决（那些分别是 skill-optimizer/skill-evolver/self-improving-agent/unclekk-metacog-self-evolve 的职责）。不在本机压缩大模型（无 H200）。 | A verifiable self-optimization loop. Use when you need verifiable autonomous optimization of a solution, or want to judge whether a local metric is misleading. Abstracts CompressionBench's terminal-task + feedback search + independent verification + global recheck into a domain-agnostic loop; core value: full feedback can overturn many local rankings, so local metrics are untrustworthy. This is a judgment layer, NOT an optimization executor — it does not rewrite skills, accumulate experience, or ratchet (those are skill-optimizer/skill-evolver/self-improving-agent/unclekk-metacog-self-evolve). Does not compress LLMs locally (no H200).
license: MIT
---

# unclekk-eval-opt-loop（自主优化验证闭环）

## Overview
把 CompressionBench 的方法论抽象成与目标域无关的通用闭环：设目标 → 反馈引导搜索 → 独立验证门禁 → 局部指标全局复核。核心价值不是"跑优化"，而是提供**判据层**——论文实证"完整模型反馈推翻了 79 个局部排名中的 17 个"，说明局部指标会误导，必须全局复核。

Abstract CompressionBench into a domain-agnostic loop. Value is not running optimization but the **judgment layer**: full feedback overturned 17 of 79 local rankings, so local metrics mislead and must be globally rechecked.

## 何时使用（触发条件）| When to Use (Triggers)
- 有一个可度量优化目标 + 一个独立验证器，要迭代出经独立验证的方案
- 手上有基于局部指标/子集得分的排名，要判断是否可信、是否需要全局复核
- 想给某个优化器加一道"独立验证 + 全局复核"的验收判据

**实际调用示例（照着说就能触发）| Trigger examples**：
- 「我调了 3 版提示词，小样本上 A 最好，不确定要不要用它」→ 跑全局复核看 A 是否真最优
- 「帮我判断这个局部得分能不能信」→ 本技能核心就是"局部指标不可信"判据
- 「给这个优化器加一道独立验证门禁」→ 提供门禁清单接到优化器之后
- 端到端可跑示例见 `examples/minimal-example.md`（含真实命令与输出、通过/失败对照）；三类场景速查见 `examples/more-examples.md`（局部误导 / 越低越好取负 / 局部与全局一致）

🔴 **CHECKPOINT**: 开工前必须确认：① 目标可度量；② 验证器独立且可跑（与生成器上下文隔离）；③ 不依赖本机不具备的重算力（本技能不在本机压缩大模型）。缺任一 → 中止说明（fail-closed）。

**不适用 | Out of scope**: 不真去压缩大模型（本地无 H200/vLLM）；不是优化执行器（改技能→skill-optimizer/skill-evolver，记经验→self-improving-agent，棘轮裁决→unclekk-metacog-self-evolve）；不做告警后故障隔离（那是 unclekk-fault-isolation-guard）。

---

## 三铁律（忠实原著）| Three Iron Rules
1. **只评不改**：每条能力主张可溯源 CompressionBench 论文三份材料；论文没证明的写"待验证"。
2. **诚实披露**：压缩以约 2.2pp 下游精度换存储，非无损，是效率-能力折中；RSI 收益复利未证明（待验证）；低星新预印本，不写星标数字，不攀比人气。
3. **统一复验 + fail-closed**：验证器不独立、局部指标未复核、出现真压缩大模型需求、安全审计不过 → 停下报告。

---

## 四步闭环骨架 | Four-Step Loop

### Step 1：设目标（Set Objective）
定义 terminal-task 契约：源/checkpoint、预算 C、推理环境、时间预算 T（`templates/terminal-task-spec.md`）。抽象到目标域时，等价为"可度量目标 + 资源约束 + 截止时间"。

### Step 2：反馈引导搜索（Feedback-Guided Search）
用反馈信号（论文用 perplexity）引导方案搜索与迭代，记录每轮候选（`templates/opt-loop-log.md`）。

### Step 3：独立验证门禁（Independent Verification Gate）
最终方案由**独立验证器**一次终检；硬门禁不达标则 reward=0（`templates/verification-gate.md`，判定脚本 `scripts/gate_check.py`）。验证器须与生成器上下文隔离（借鉴 skill-optimizer 防泄漏复评思想，但不实现其闭环）。

### Step 4：局部指标全局复核（Global Recheck of Local Metrics）—— 核心判据
把基于局部指标/子集的排名，用完整反馈重新评估；标记被推翻的局部排名（`templates/global-recheck.md`，比对脚本 `scripts/recheck_compare.py`）。论文证据：完整模型反馈推翻 79 个局部排名中的 17 个。

---

## 输出契约
1. 迭代记录（opt-loop-log）
2. 经独立验证门禁的最终方案 + 门禁结果（gate_check）
3. 局部排名 vs 完整反馈的复核表（recheck_compare），标出被推翻项
4. 诚实披露段：效率-能力折中、待验证项、证据范围（本机未复现论文压缩指标）

---

## 能力主张溯源（摘要，详见 references/metrics.md / key-finding.md）

| 能力主张 | 论文出处 | 状态 |
|---|---|---|
| terminal-task 四要素契约 | 三材料摘要一致 | 已证明（压缩域）|
| 反馈引导搜索 + 独立容器验证终检 | 三材料摘要一致 | 已证明（压缩域）|
| 独立验证器一次终检 | 三材料摘要一致（"independent verification checks the final model"）| 已证明（压缩域）|
| 硬门禁 reward=0 | 项目 README（infini-ai-lab/Compression-Bench）"otherwise the reward is 0"；三材料摘要层只说"独立验证"，未载 reward 字样 | 已证明（论文项目文档，非三材料摘要层）|
| 完整反馈推翻 79 个局部排名中的 17 个 → 须全局复核 | 三材料摘要/关键结果一致 | 已证明（该论文域）；**泛化其他域待验证** |
| 29/36 通过、PPL+3.4%、77.33 vs 79.56 | 三材料摘要一致 | 已证明（论文测试床，本机未复现）|
| RSI 收益复利 | 材料定位为概念，未证明 | **待验证/不宣称** |
| 压缩无损 | 材料明确约 2.2pp 精度折中 | 否，写效率-能力折中 |

## 局限与边界 | Limitations
单列成段，不藏：约 2.2pp 精度换存储非无损；评测只覆盖 3 个模型尺寸；RSI 复利未证明；"局部指标不可信"判据在压缩域已证、外推待验证；本机未复现论文压缩指标。详见 references/metrics.md。

## 边界声明 | Boundary
`self-improving-agent` 是经验记录器；`skill-optimizer`/`skill-evolver`/`unclekk-metacog-self-evolve` 是优化执行器/规则演化引擎。本技能只提供"验证反直觉 / 局部指标不可信"的**判据层**：可接到任何优化器前后作验收判据，本身不改技能、不沉淀经验、不做棘轮裁决。"独立验证"与 skill-optimizer 防泄漏复评同源，但不实现其基线→补丁→复评→棘轮闭环。详见 references/boundary.md。

## 安全说明 | Security Note
`scripts/` 纯本地读写：只读验证结果 json、输出判定；不 `eval/exec` 生成代码、不 subprocess 执行生成代码、不自动 pip install、不联网。凡"agent 自建方案/自主执行"均声明验证在独立容器或纯静态完成，本机不执行未知代码。

## 资源 | Resources
- `templates/terminal-task-spec.md` / `opt-loop-log.md` / `verification-gate.md` / `global-recheck.md`
- `scripts/gate_check.py` / `recheck_compare.py`
- `references/method.md` / `key-finding.md` / `metrics.md` / `boundary.md` / `faq.md`（常见错误清单、失败情形、反模式、FAQ）
- `examples/minimal-example.md`（端到端最小示例：真实命令 + 真实输出 + 通过/失败对照）
- `examples/more-examples.md`（三类可照用场景 + 快速迁移清单：局部误导 / 越低越好取负 / 局部与全局一致 / 门禁通过+否决）
- `examples/data/candidates.json` / `verification-pass.json` / `verification-fail.json` / `latency-candidates.json` / `retrieval-candidates.json`（示例随包数据，可直接复制跑）

## 变更记录 | Changelog
- 1.2.0 (2026-11-20)：应对 SkillHub TRACE 测评（4.8/5）"部分示例数字不一致、跨场景需较多人工准备、场景可更丰富"——① 修正 `templates/global-recheck.md` 判据表数字（原 B=0.89/0.85、C 标"否"与真实数据/运行输出冲突，改为 B=0.88/0.86、C=0.87/0.85、3/3 全推翻）；② 修 `references/faq.md` 两个脚本报错文案混用；③ 修 `recheck_compare.py` 负数分数列黏连（列宽 8→10/12）；④ 新增 `examples/more-examples.md` 三类可照用场景 + `examples/data/latency-candidates.json`（越低越好取负）、`retrieval-candidates.json`（局部与全局一致）；同步 `minimal-example.md` 输出表头。全部输出已用随包数据真实复现。
- 1.1.0 (2026-11-20)：应对 SkillHub TRACE 测评"实际案例和真实运行验证偏少、反模式与FAQ 3.8/5、触发方式缺实际示例"——新增 `examples/minimal-example.md`（端到端示例 + 真实命令/输出 + 一票否决失败对照）、`examples/data/*.json`（随包可跑数据）、`references/faq.md`（常见错误清单 + 失败情形 + 反模式 + 触发示例 + FAQ）；SKILL.md 触发段补实际调用示例，Resources 接入上述资源。示例输出已用随包数据真实复现，非编造。
- 1.0.0 (2026-11-19)：初版，源自 CompressionBench 论文（arXiv:2611.06858），复用 unclekk-paper2skill 三段式骨架约定。
