# 最小完整示例：客服提示词优化（端到端，含真实运行结果）

> 这是一个**低风险、可自己跑**的示例，用提示词优化代替论文里的模型压缩（本机无 H200，不压缩大模型）。
> 下面每条命令和输出都是 2026-11-20 在本机**真实运行**的结果，不是编造。
> 目标：演示本技能的核心判据——**局部子集指标会误导，必须全局复核 + 独立门禁**。

---

## 0. 场景一句话

你有 3 个候选客服提示词，在 20 条子集上 A 得分最高（0.91）。要不要直接选 A？本技能说不——先看完整测试集，再过独立门禁。

---

## 1. 准备数据（可直接复制运行）

在本技能目录下建一个临时目录 `examples/_run/`（真实运行时用你自己的路径），放入 `candidates.json`：

```json
{
  "task": "客服机器人提示词优化（低风险示例，非模型压缩）",
  "metric": "任务成功率（0-1，越高越好）",
  "local_definition": "子集A（20条样本）上的成功率",
  "global_definition": "完整测试集（200条样本）上的成功率，由独立验证器给出",
  "candidates": [
    {"name": "prompt_A", "local": 0.91, "global": 0.78},
    {"name": "prompt_B", "local": 0.88, "global": 0.86},
    {"name": "prompt_C", "local": 0.87, "global": 0.85}
  ]
}
```

字段含义：`local` = 局部反馈（子集得分），`global` = 完整反馈（独立验证器在完整测试集上测得的得分）。

---

## 2. 跑局部指标全局复核（核心判据）

```bash
python scripts/recheck_compare.py --candidates <你放的目录>/candidates.json
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

**读数**：局部排第一的 A（0.91）在完整测试集只有 0.78，跌到末位；真正的全局最优是 B（0.86）。3/3 排名全被推翻——对应论文"完整反馈推翻 79 个局部排名中的 17 个"的判据（本例是我构造的低风险演示，不是论文数据）。

---

## 3. 独立验证门禁：通过路径

把全局最优 B 交给**独立验证器**（独立会话，不让它看到生成过程），得到 `verification.json`：

```json
{
  "task": "prompt_B 的独立验证结果",
  "verifier": "独立会话，未见生成过程",
  "gates": {
    "target_metric_reached": true,
    "within_budget": true,
    "solution_self_constructed": true,
    "all_stages_completed": true,
    "correctness_ge_threshold": true
  }
}
```

```bash
python scripts/gate_check.py --result <你放的目录>/verification.json
```

**真实输出（退出码 0）：**

```
=== 独立验证门禁（只读判定，不执行任何生成代码）===
  [PASS] target_metric_reached
  [PASS] within_budget
  [PASS] solution_self_constructed
  [PASS] all_stages_completed
  [PASS] correctness_ge_threshold
RESULT: pass（5 项硬门禁全过）
```

门禁项是你按任务定义的硬门槛（这里 5 项都要 true）。任一不达标 → 一票否决。

---

## 4. 失败情形对照：一票否决（reward=0）

换成局部最优 A 的验证结果 `verification_fail.json`——注意只有一项 `correctness_ge_threshold` 变成 `false`：

```json
{
  "task": "prompt_A 的独立验证结果（失败对照）",
  "verifier": "独立会话，未见生成过程",
  "gates": {
    "target_metric_reached": true,
    "within_budget": true,
    "solution_self_constructed": true,
    "all_stages_completed": true,
    "correctness_ge_threshold": false
  }
}
```

```bash
python scripts/gate_check.py --result <你放的目录>/verification_fail.json
```

**真实输出（退出码 1）：**

```
=== 独立验证门禁（只读判定，不执行任何生成代码）===
  [PASS] target_metric_reached
  [PASS] within_budget
  [PASS] solution_self_constructed
  [PASS] all_stages_completed
  [FAIL] correctness_ge_threshold
RESULT: reward=0（未过门禁: correctness_ge_threshold）
```

**读数**：哪怕目标指标达到了，只要一项硬门槛没过，就是 reward=0，不用其他指标补偿——对应论文 "otherwise the reward is 0" 的硬门禁纪律。

---

## 5. 填迭代记录（把上面结果落表）

按 `templates/opt-loop-log.md` 填，本示例的关键行：

| 轮次 | 候选 | 局部得分 | 全局得分 | 门禁结果 | 备注 |
|---|---|---|---|---|---|
| 1 | prompt_A | 0.91（局部第1）| 0.78（全局第3）| reward=0（correctness 未过）| 局部最优被推翻 |
| 2 | prompt_B | 0.88（局部第2）| 0.86（全局第1）| pass | 全局最优，选中 |

---

## 6. 结论

- **别信局部**：A 子集分最高，完整测试集垫底，且门禁没过——选它是错的。
- **全局复核 + 独立门禁缺一不可**：B 子集分不是最高，但全局最优且过全部门禁，才是正确答案。
- 这就是本技能的全部价值：`templates/global-recheck.md` + `templates/verification-gate.md` 两个判据。

## 7. 迁移到你自己的任务

1. 把 `candidates.json` 里的候选换成你的方案，`local`/`global` 换成你的局部/完整指标（越大越好）。
2. 把 `verification.json` 的 `gates` 换成你的硬门槛（全部 true 才算 pass）。
3. 换数据请自己跑，本示例的数字仅为演示机制，不代表真实优化效果。
