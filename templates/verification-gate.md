# 独立验证门禁清单（verification-gate）

> 对应 CompressionBench 项目 README（github.com/Infini-AI-Lab/Compression-Bench）的硬门禁原文："package size ≤ C, GPU-resident storage ≤ C, the compression is the submission's own, every stage completes, and a hidden correctness gate ... otherwise the reward is 0"。注：三份论文材料（raw/wiki/译稿）摘要层只说"independent verification checks the final model"，未出现 reward 字样；reward=0 的一票否决表述出自项目 README，故标注此来源差异。该 README 原文已于 2026-11-19 通过 GitHub 直接核验（含 "otherwise the reward is 0" 及包大小/显存/正确性门描述），作为三材料之外的旁证来源，不属论文摘要层。
> 抽象到目标域：所有硬门槛必须满足，否则 reward=0（一票否决）。

## 门禁清单模板

```markdown
# 独立验证门禁 — [任务名]

验证器：[描述]｜与生成器隔离方式：[独立容器 / 独立会话 / 纯静态]
终检方式：[一次终检，冻结提交]

## 硬门禁（任一不达标 → reward=0）
- [ ] 门槛 1：packagesize ≤ C（论文：包大小≤上限）
- [ ] 门槛 2：resident storage ≤ C（论文：显存≤上限）
- [ ] 门槛 3：方案为自身构造（论文：压缩必须是提交方自己的）
- [ ] 门槛 4：所有阶段完成（论文：每阶段须完成）
- [ ] 门槛 5：正确性 ≥ 阈值（论文：隐藏正确性门 ≥ BF16 均值 80%）

## 判定
- 结果：pass / reward=0
- 关键指标：[...]
- 证据范围：[本机验证 / 论文测试床，本机未复现]
```

## 判定脚本
用 `scripts/gate_check.py` 读验证结果 json，输出 pass / reward=0（纯本地判定，不执行生成代码）。

## 纪律
- **一票否决**：任一硬门槛不达标即 reward=0，不用其他指标补偿（论文原话 "otherwise the reward is 0"）。
- **独立隔离**：验证器与生成器上下文隔离，防止"自评自奖"。
- **一次性终检**：最终方案冻结后由独立验证器检查一次（论文："a hidden Verifier measures the final submission once"）。
- 论文指标（80% BF16 等）属压缩域，通用域须定义等价阈值并标注"自定义，待验证"。
