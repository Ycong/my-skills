# 第 6 步派发材料（→ verifier）

## system prompt
取自 `dev-review-workflow-omp/agents/verifier.md` 正文（去掉 frontmatter），末尾追加该文件 `output` 字段的 JSON Schema 要求。

## task prompt（SKILL.md「执行验收」模板填入 + 待复核的申报）
```
你是独立验收人，与执行者无共享上下文。
材料：diff（sample 工作树相对基线提交的 git diff，含 3 个文件）、验收清单（docs/refund-plan.md
第二节「可执行验收清单」）、审核标准（sample/review-checklist.md）。
逐条执行验收：可自动化项必须实际运行测试/脚本并附输出；人工项给出核对证据。
同时核对：diff 无夹带、blocking 项代码层复核、偏差全部披露。
输出：结论 + 各验收项结果 + 偏差与遗留清单。

补充材料：
- 规格卡验收命令：cd sample && python3 -m unittest discover -s tests -v
- 本次批准的可改文件清单：src/refund.py, tests/test_refund.py
- 实现者申报（待你复核，不要直接采信）：files_changed = [src/refund.py, tests/test_refund.py]；
  其自报验收命令 exit_code=0，"Ran 5 tests ... OK 全绿"。
- 实现者申报的偏差（原文摘要）："2) 「异步」语义偏窄：方案文档写『不阻塞主请求』，规格卡要求
  等待结果返回以保持向后兼容，两者不可同时成立——我按规格卡实现（阻塞在 future.result()）。"
```

## 这一步是本次实测的关键
派发前人为把「已交付且自报全绿」的代码改坏，并越界改了一个文件——模拟真实开发中最常见的
两类失真：**申报与实况不符**、**夹带改动**。verifier 必须靠干净重跑与 diff 对照自己发现，
不能依赖任何一方自述。
