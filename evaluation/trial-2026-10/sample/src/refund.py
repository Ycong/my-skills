"""退款服务：同步实现（改造前基线）。"""

_REFUNDS = []


def refund(request_id: str, amount_cents: int) -> dict:
    """按 request_id 提交退款，返回退款记录。"""
    record = {"request_id": request_id, "amount_cents": amount_cents}
    _REFUNDS.append(record)
    return record


def list_refunds() -> list:
    return list(_REFUNDS)


def reset_store() -> None:
    _REFUNDS.clear()
