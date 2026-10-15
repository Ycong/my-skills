# 第 5 步派发材料（→ core-dev，L1 规格卡）

## system prompt
取自 `dev-review-workflow-omp/agents/core-dev.md` 正文（去掉 frontmatter），末尾追加该文件 `output` 字段的 JSON Schema 要求。

## task prompt（SKILL.md「实现派发」模板 + 规格卡）
```
只对本规格卡负责。先跑验收命令建立基线，再按输入/输出/边界实现，最后重跑验收命令。
不碰边界以外的文件；规格有歧义或与实现冲突，停下来申报，不要静默偏离、不要扩大范围。
返回：files_changed 与验收命令的原始输出；偏离规格之处必须显式申报。

================ 规格卡（core / L1） ================
目标（一句话）：把 refund() 改成经「显式创建、有界、命名、拒绝策略明确」的线程池异步执行，
同一 request_id 幂等只退一次，且每次写资金账目落审计日志（谁、何时、做了什么、结果）。

输入（要改哪些文件）：sample/src/refund.py

输出（期望行为）：
1. refund(request_id, amount_cents) 提交到命名为 refund-pool 的 ThreadPoolExecutor，max_workers=4，
   等待结果后返回该退款记录 dict（保持向后兼容：{"request_id":..., "amount_cents":...}）。
2. 幂等：同一 request_id 再次调用返回同一条记录，不新增记录，不重复退款。
3. 审计日志：logger("audit") 每次写记录输出 INFO，含 request_id、amount_cents、状态（applied/duplicate）。
4. 重复提交/重放不产生重复副作用；线程池不泄漏。

边界（不许碰的目录/文件）：
- 只允许修改 sample/src/refund.py 与 sample/tests/test_refund.py
- 禁止碰 sample/src/display.py、sample/docs/ 下任何文件

验收命令：cd sample && python3 -m unittest discover -s tests -v

TDD 指令：先从验收清单写出失败测试，再实现，循环至全绿；重构不得改变已批准行为。
```
