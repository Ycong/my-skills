# 第 3 步派发材料（→ reviewer）

## system prompt
取自 `dev-review-workflow-omp/agents/reviewer.md` 正文（去掉 frontmatter），末尾追加该文件 `output` 字段的 JSON Schema 要求。

## task prompt（SKILL.md「方案审核」模板填入）
```
你是独立审核人，与方案作者无共享上下文，不得迁就方案的自评结论。
材料：方案文档 sample/docs/refund-plan.md、审核标准 sample/review-checklist.md、相关代码 sample/src/refund.py、sample/tests/test_refund.py。
逐条核对 checklist 各节；以代码与配置实况为准，不信任方案描述。
输出：结论（通过/有条件通过/驳回）+ blocking 列表 + non-blocking 列表，
每条附代码位置或方案章节。
```
