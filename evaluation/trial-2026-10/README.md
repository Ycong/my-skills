# trial-2026-10 · skill 可用性实测材料

对 `dev-review-workflow` / `dev-review-workflow-omp` 的一次端到端实测：用**资金链路退款接口改造**
（L1）当被测变更，按 SKILL.md 的第 3 / 5 / 6 步派发子代理，并人为植入两类最常见的失真，看门禁是否真的挡得住。

评估报告见 `../2026-10-skill-usability-report.md`。

## 目录

```
trial-2026-10/
├── sample/                       # 被测项目（基线，可直接跑）
│   ├── docs/refund-plan.md       # 方案文档（第 1 步产出，自评 L2、缺回滚方案等）
│   ├── src/refund.py             # 同步基线实现（无幂等、无审计、无锁）
│   ├── src/display.py            # 边界外文件（夹带检测用）
│   ├── tests/test_refund.py      # 验收用例（基线 1 红 1 绿）
│   └── review-checklist.md       # 审核标准（母版 + 两条项目红线）
├── prompts/                      # 三步派发材料（system prompt 来源 + task prompt 模板）
├── plant_mutations.py            # 植入回归 + 夹带的脚本
└── evidence/                     # 三关返回的关键证据（逐字引用 + 位置抽查）
```

## 复现步骤

```bash
cd sample
git init -q && git add -A && git -c user.email=e@e -c user.name=e commit -qm baseline

# 基线：应 1 红（幂等用例）1 绿
python3 -m unittest discover -s tests -v

# 第 3 步：按 prompts/01-reviewer.md 派发 reviewer → 期望 驳回 + 10 项 blocking
# 第 5 步：按 prompts/02-core-dev.md 派发 core-dev  → 期望 全绿 + 申报偏差 + 1 项 blocked
python3 ../plant_mutations.py        # 植入：幂等分支缺失 + 越界改 display.py
git --no-pager diff --stat           # 应 3 个文件

# 第 6 步：按 prompts/03-verifier.md 派发 verifier
# 期望：overall=未通过；否定"全绿"申报；抓到 display.py 夹带
```

## 关键设计点

- **基线就是红的**：方案自评 L2、验收清单却要求幂等，而基线实现没有幂等 → 第 3 步的审核有真实抓手，
  第 5 步的 TDD 也有天然的红。
- **植入的两类失真**正是真实开发中最常见的：① 申报与实况不符（自报全绿）；② 夹带越界改动。
  两者都无法靠"读申报"发现，只能靠干净重跑 + diff 机械比对。
- **派发材料全部照抄 SKILL.md 的模板与 agents/*.md 的正文**，只把 `output` JSON Schema 写在
  system prompt 末尾（本环境无 omp 的运行时 schema 校验，见报告的局限声明）。
