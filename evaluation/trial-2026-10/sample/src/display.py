"""订单展示辅助函数（与本次退款改造无关）。"""


def format_amount(amount_cents: int) -> str:
    return f"¥{amount_cents / 100:.2f}"
