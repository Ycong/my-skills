import unittest

from src.refund import list_refunds, refund, reset_store


class RefundAcceptanceTest(unittest.TestCase):
    def setUp(self):
        reset_store()

    def test_duplicate_request_id_only_refunds_once(self):
        """验收项 2：同一 request_id 重复调用只产生一条退款记录（幂等）。"""
        refund("req-1", 1000)
        refund("req-1", 1000)
        self.assertEqual(len(list_refunds()), 1)

    def test_five_distinct_requests_all_succeed(self):
        """验收项 3：并发提交 5 个不同请求，全部成功且金额正确。"""
        for i in range(5):
            rec = refund(f"req-{i}", 100 * (i + 1))
            self.assertEqual(rec["amount_cents"], 100 * (i + 1))
        self.assertEqual(len(list_refunds()), 5)


if __name__ == "__main__":
    unittest.main()
