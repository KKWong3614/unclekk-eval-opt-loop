#!/usr/bin/env python3
"""
recheck_compare.py — 局部排名 vs 完整反馈比对（unclekk-eval-opt-loop）

用途：输入每个候选的局部得分与完整（全局）得分，输出排名对比与被推翻的局部排名。
依据论文："complete-model feedback reverses 17 of 79 prior local rankings"。

安全契约（对应 skills-security-check 审计）：
  - 只读一个本地候选 json；只向 stdout 打印结果，不写文件
  - 不 eval/exec、不 subprocess、不联网
  - 纯计算工具

用法：
  python recheck_compare.py --candidates <candidates.json>
  candidates.json 形如：
    {"candidates":[{"name":"A","local":0.91,"global":0.78}, ...]}
退出码：0=成功；1=未指定候选；2=文件/格式错误
"""

import argparse
import json
import sys
from pathlib import Path


def rank(candidates, key):
    """返回按 key 降序排序的 (name, value) 列表与名次映射。"""
    ordered = sorted(candidates, key=lambda c: c[key], reverse=True)
    ranks = {}
    for i, c in enumerate(ordered, 1):
        ranks[c["name"]] = (i, c[key])
    return ranks


def main() -> int:
    ap = argparse.ArgumentParser(description="局部指标全局复核比对（只读）")
    ap.add_argument("--candidates", required=True, help="候选 json 文件")
    args = ap.parse_args()

    path = Path(args.candidates)
    if not path.is_file():
        print(f"ERROR: 候选文件读不到: {path}", file=sys.stderr)
        return 2
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        print(f"ERROR: 解析失败: {e}", file=sys.stderr)
        return 2

    cands = data.get("candidates", [])
    if not cands:
        print("ERROR: 无候选数据", file=sys.stderr)
        return 2
    for c in cands:
        if "name" not in c or "local" not in c or "global" not in c:
            print("ERROR: 每个候选需含 name / local / global", file=sys.stderr)
            return 2

    local_rank = rank(cands, "local")
    global_rank = rank(cands, "global")
    print("=== 局部指标全局复核（只读比对）===")
    print(f"{'候选':<12}{'局部分':>10}{'局部名次':>10}{'全局分':>10}{'全局名次':>10}  推翻?")
    overturned = 0
    for c in sorted(cands, key=lambda x: local_rank[x["name"]][0]):
        name = c["name"]
        lr, lv = local_rank[name]
        gr, gv = global_rank[name]
        flipped = lr != gr
        if flipped:
            overturned += 1
        print(f"{name:<12}{lv:>10.3f}{lr:>10}{gv:>10.3f}{gr:>10}  {'是' if flipped else '否'}")

    print(f"被推翻的局部排名: {overturned} / {len(cands)}")
    best_global = min(global_rank, key=lambda n: global_rank[n][0])
    best_local = min(local_rank, key=lambda n: local_rank[n][0])
    print(f"局部最优={best_local} | 全局最优={best_global}")
    if best_local != best_global:
        print("结论: 局部最优被全局复核推翻 —— 以全局为准，勿信局部指标")
    else:
        print("结论: 本例局部最优与全局一致（论文仍警示多数场景局部会误导）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
