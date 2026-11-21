#!/usr/bin/env python3
"""
gate_check.py — 独立验证门禁判定（unclekk-eval-opt-loop）

用途：读取一个验证结果 json（各硬门槛的达标情况），输出 pass / reward=0。
一票否决：任一硬门槛不达标 → reward=0（对应论文 "otherwise the reward is 0"）。

安全契约（对应 skills-security-check 审计）：
  - 只读一个本地验证结果 json；只向 stdout 打印判定，不写文件
  - 不 eval/exec、不 subprocess 执行生成代码、不 pip install、不联网
  - 纯数据判定工具，不执行任何被验证的方案本身

用法：
  python gate_check.py --result <result.json>
  result.json 形如 {"gates": {"gate1": true, "gate2": false, ...}}
退出码：0=pass；1=reward=0（有门禁未过）；2=文件/格式错误
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="独立验证门禁判定（只读，不执行生成代码）")
    ap.add_argument("--result", required=True, help="验证结果 json 文件")
    args = ap.parse_args()

    path = Path(args.result)
    if not path.is_file():
        print(f"ERROR: 验证结果文件读不到: {path}", file=sys.stderr)
        return 2
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        print(f"ERROR: 结果解析失败: {e}", file=sys.stderr)
        return 2

    gates = data.get("gates")
    if not isinstance(gates, dict) or not gates:
        print("ERROR: result.json 缺少非空 'gates' 对象", file=sys.stderr)
        return 2

    print("=== 独立验证门禁（只读判定，不执行任何生成代码）===")
    all_ok = True
    for name, passed in gates.items():
        ok = passed is True
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            all_ok = False

    if all_ok:
        print(f"RESULT: pass（{len(gates)} 项硬门禁全过）")
        return 0
    failed = [n for n, v in gates.items() if v is not True]
    print(f"RESULT: reward=0（未过门禁: {', '.join(failed)}）")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
