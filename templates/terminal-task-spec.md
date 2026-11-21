# terminal-task 契约模板

> 对应 CompressionBench 论文："an agent receives a source checkpoint, storage limit, inference environment, and time budget, then constructs compressed weights and executable inference code"（三材料摘要一致）。
> 抽象到目标域：可度量目标 + 资源约束 + 环境 + 截止时间。

## 模板（压缩域原貌，供溯源对照）

```yaml
terminal_task:
  source_checkpoint: "<read-only 源模型/输入>"
  budget_C: "<存储上限：磁盘 + 显存双限>"
  environment: "<固定推理环境/运行时>"
  time_budget_T: "<截止时间>"
  deliverable: "<压缩权重 + 可执行推理代码 / 目标方案 + 可运行产物>"
  freedom: "agent 自选算法与实验；反馈引导搜索"
  final_check: "独立验证器一次终检"
```

## 抽象到通用域（本技能用法）

```yaml
terminal_task:
  objective: "<可度量优化目标，须有量化指标>"
  constraints: "<资源约束：预算/上限/硬门槛>"
  environment: "<固定环境/可复现条件>"
  deadline: "<时间预算 T>"
  deliverable: "<最终方案 + 可运行/可核验产物>"
  feedback_signal: "<引导搜索的反馈，如子集得分/代理指标>"
  verifier: "<独立验证器：与生成器上下文隔离>"
```

## 关键纪律
- **目标必须可度量**：否则 Step 3 门禁与 Step 4 复核都无法判定。
- **验证器必须独立**：与生成器上下文隔离（论文用独立容器 + 隐藏 Verifier）。
- **不在本机压缩大模型**：本技能不依赖 H200/vLLM；dogfood 用低风险小任务。
- 四要素缺一 → CHECKPOINT 停下（fail-closed）。
