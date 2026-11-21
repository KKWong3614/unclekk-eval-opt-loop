# 更多可直接照用案例（三类场景，真实运行输出）

> 针对 SkillHub TRACE 测评（4.8/5）"部分示例细节不一致、跨场景需较多人工准备、场景可更丰富"补齐。
> 全部命令与输出为 2026-11-20 在本机**真实运行**，非编造；数据与脚本随包，可直接复制跑。
> 三个案例覆盖脚本的三种输出分支：① 局部误导（被推翻）；② 越低越好指标（取负转换）；③ 局部与全局一致（不被推翻）。

输出表头统一为：`候选 / 局部分 / 局部名次 / 全局分 / 全局名次 / 推翻?`。

---

## 案例一：局部最优被推翻（主案例的简版速查）

数据：`examples/data/candidates.json`（客服提示词优化）。

```bash
python scripts/recheck_compare.py --candidates <技能目录>/examples/data/candidates.json
```

**真实输出（退出码 0）：**

```
=== 局部指标全局复核（只读比对）===
候选                 局部分      局部名次       全局分      全局名次  推翻?
prompt_A         0.910         1     0.780         3  是
prompt_B         0.880         2     0.860         1  是
prompt_C         0.870         3     0.850         2  是
被推翻的局部排名: 3 / 3
局部最优=prompt_A | 全局最优=prompt_B
结论: 局部最优被全局复核推翻 —— 以全局为准，勿信局部指标
```

**注意**：本表数字（B=0.88/0.86、C=0.87/0.85，3/3 全被推翻）与 `templates/global-recheck.md`、`examples/minimal-example.md` 完全一致。此前模板曾写成 B=0.89/0.85、C 标"否"，属笔误，已修正。

---

## 案例二：指标越低越好（延迟/成本/错误率）——取负转换后直接用

**场景**：API 网关配置调优，指标是 P95 延迟（ms，**越低越好**）。脚本按"越高越好"排序，所以先把延迟取负：`score = -延迟`（-80 表示 80ms，-150 表示 150ms，值越大延迟越低）。

**原始数据（供你理解换算，不用喂给脚本）：**

| 配置 | 局部 P95（100 请求） | 全局 P95（全量回放） | 转换后 local | 转换后 global |
|---|---|---|---|---|
| cfg_fast | 80ms | 150ms | -80 | -150 |
| cfg_balanced | 95ms | 92ms | -95 | -92 |
| cfg_safe | 110ms | 100ms | -110 | -100 |

喂给脚本的是转换后的负值，已存好：`examples/data/latency-candidates.json`。

```bash
python scripts/recheck_compare.py --candidates <技能目录>/examples/data/latency-candidates.json
```

**真实输出（退出码 0）：**

```
=== 局部指标全局复核（只读比对）===
候选                 局部分      局部名次       全局分      全局名次  推翻?
cfg_fast       -80.000         1  -150.000         3  是
cfg_balanced   -95.000         2   -92.000         1  是
cfg_safe      -110.000         3  -100.000         2  是
被推翻的局部排名: 3 / 3
局部最优=cfg_fast | 全局最优=cfg_balanced
结论: 局部最优被全局复核推翻 —— 以全局为准，勿信局部指标
```

**读数**：局部小样本里最快的是 cfg_fast（80ms），但完整流量回放下它最慢（150ms）；真正最优是 cfg_balanced。又一次印证"局部会骗人"。

**迁移到你的越低越好指标**：`score = -原值`（或 `1/原值`，只要保证越大越好且 local/global 同口径），再按案例一的方式填 json。

---

## 案例三：局部最优与全局一致（脚本的另一种输出分支）

**场景**：文档检索参数（top-k）选择，召回率越高越好。这批数据里局部与全局排名恰好一致。

数据：`examples/data/retrieval-candidates.json`。

```bash
python scripts/recheck_compare.py --candidates <技能目录>/examples/data/retrieval-candidates.json
```

**真实输出（退出码 0）：**

```
=== 局部指标全局复核（只读比对）===
候选                 局部分      局部名次       全局分      全局名次  推翻?
k10_localbest     0.930         1     0.900         1  否
k20              0.910         2     0.890         2  否
k5               0.880         3     0.870         3  否
被推翻的局部排名: 0 / 3
局部最优=k10_localbest | 全局最优=k10_localbest
结论: 本例局部最优与全局一致（论文仍警示多数场景局部会误导）
```

**读数**：0/3 被推翻，退出码 0，**不会被误判成失败**。但一致只说明这批数据没翻转，不代表局部指标普遍可信——论文 17/79 的警示仍成立，复核步骤不能因此省掉。

---

## 案例四：独立验证门禁（通过 + 一票否决失败）

复用 `minimal-example.md` 的两份验证结果，命令与输出在此速查。

```bash
# 通过：5 项全 true
python scripts/gate_check.py --result <技能目录>/examples/data/verification-pass.json
# 失败：correctness_ge_threshold=false
python scripts/gate_check.py --result <技能目录>/examples/data/verification-fail.json
```

**通过（退出码 0）：**

```
=== 独立验证门禁（只读判定，不执行任何生成代码）===
  [PASS] target_metric_reached
  [PASS] within_budget
  [PASS] solution_self_constructed
  [PASS] all_stages_completed
  [PASS] correctness_ge_threshold
RESULT: pass（5 项硬门禁全过）
```

**失败（退出码 1）：**

```
=== 独立验证门禁（只读判定，不执行任何生成代码）===
  [PASS] target_metric_reached
  [PASS] within_budget
  [PASS] solution_self_constructed
  [PASS] all_stages_completed
  [FAIL] correctness_ge_threshold
RESULT: reward=0（未过门禁: correctness_ge_threshold）
```

---

## 快速迁移清单（换你自己的数据）

1. 复制 `examples/data/` 下最接近你场景的 json，改 `candidates` 数组（`name`/`local`/`global` 三个字段必须有，数值用数字别用字符串）。
2. 指标越高越好直接用；越低越好先取负（`score=-值`），local/global 同口径。
3. `local` = 你的局部/子集/代理指标；`global` = 独立验证器在完整目标上测得的指标。
4. 用 `C:/...` 原生路径（Git Bash 下 `/tmp` 会被当 `C:\tmp`）。
5. 看输出"被推翻"列 + 结论行做决策；再过 `gate_check.py` 独立门禁。
6. 数字仅为机制演示，非论文实验结果；论文真实数字见 `references/metrics.md`（本机未复现）。
