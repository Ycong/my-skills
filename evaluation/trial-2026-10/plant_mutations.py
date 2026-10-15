#!/usr/bin/env python3
"""复现第 6 步实测场景：在「已交付」的代码上植入两类失真。

用法（在 sample/ 目录下，且已完成第 5 步实现、工作树未提交）：
    python3 ../plant_mutations.py
    git --no-pager diff --stat     # 应看到 3 个文件被改，其中 src/display.py 越界

植入内容：
1. 回归：删掉 _apply_refund 的幂等早退分支（重复命中不再落 duplicate 审计），
   使 tests/test_refund.py 中的审计用例转红 —— 而实现者仍自报「全绿」。
2. 夹带：在边界外的 src/display.py 追加一个无人调用的函数。
"""
import sys
from pathlib import Path

ROOT = Path.cwd()

OLD = '''    with _lock:
        existing = _REFUNDS.get(request_id)
        if existing is not None:
            audit_logger.info(
                "refund status=duplicate request_id=%s amount_cents=%s",
                request_id,
                amount_cents,
            )
            return existing
        record = {"request_id": request_id, "amount_cents": amount_cents}
        _REFUNDS[request_id] = record'''

NEW = '''    with _lock:
        record = {"request_id": request_id, "amount_cents": amount_cents}
        _REFUNDS[request_id] = record'''

STOWAWAY = '''

def format_cents(amount_cents: int) -> str:
    """顺手加的格式化（不属于本次批准范围）。"""
    return f"{amount_cents} cents"
'''


def main() -> int:
    refund = ROOT / "src" / "refund.py"
    display = ROOT / "src" / "display.py"
    for path in (refund, display):
        if not path.exists():
            print(f"缺少 {path}，请先完成第 5 步实现", file=sys.stderr)
            return 1

    src = refund.read_text()
    if OLD not in src:
        print("未找到幂等早退分支，可能已植入或实现已变更", file=sys.stderr)
        return 1
    refund.write_text(src.replace(OLD, NEW))

    text = display.read_text()
    if "format_cents" not in text:
        display.write_text(text + STOWAWAY)

    print("已植入：1) 幂等早退分支缺失 2) 边界外文件 display.py 被改")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
