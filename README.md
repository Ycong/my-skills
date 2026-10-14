# my-skills

个人开发审核流程的 skill 与模板仓库。跨机器分发统一走本仓库，禁止在安装位置手改。

## 仓库结构

```
my-skills/
├── dev-review-workflow/       # skill：开发审核流程编排（怎么转）
│   └── SKILL.md
├── review-checklist-base.md   # 审核标准母版（审什么的初始化源）
└── README.md
```

## 安装 dev-review-workflow

将 `dev-review-workflow/` 目录放入对应产品的全局 skills 目录：

- Trae CN：`~/.trae-cn/skills/`
- Trae 国际版：`~/.trae/skills/`

```bash
# 复制方式
cp -r dev-review-workflow ~/.trae-cn/skills/

# 或 symlink 方式（本仓库 git pull 后自动同步）
ln -s "$(pwd)/dev-review-workflow" ~/.trae-cn/skills/dev-review-workflow
```

## 新项目初始化审核标准

1. 复制 `review-checklist-base.md` 到项目根目录，重命名为 `review-checklist.md`
2. 填写第四节"项目扩展区"红线（一行一条"禁止/必须什么"）
3. 之后直接向 agent 提出开发需求即可，skill 自动按 7 步循环走，审核标准读取当前项目的 `review-checklist.md`

`review-checklist.md` 属于项目，随项目仓库走，不放入本仓库。

## 可选外部 skill（来自 mattpocock/skills 源仓库）

以下 skill 由 [mattpocock/skills](https://github.com/mattpocock/skills) 维护，**不放入本仓库**，按需从源仓库安装：

| skill | 在流程中的作用 | 未安装时 |
|---|---|---|
| `tdd` | L1 强制 TDD 循环（red-green-refactor） | 按 SKILL.md 内联 TDD 规则执行 |
| `grill-with-docs` | 方案产出前澄清模糊需求，沉淀术语表 | 直接产出方案 |
| `to-spec` | 澄清后将结论标准化成文 | 由 AI 直接撰写方案文档 |
| `to-tickets` | 大需求拆分为带阻塞关系的工单 | 不拆分，整需求走流程 |

安装方式（任选其一）：

```bash
# 官方安装器（交互式选择 skill 与 agent）
npx skills@latest add mattpocock/skills

# 或手动下载对应目录后复制到全局 skills 目录
# https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd
# https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs
# https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec
# https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets
```

注意：四者均为可选依赖，dev-review-workflow 未检测到它们时按内联规则降级执行，不阻塞流程。

## 融合边界（与 mattpocock 编排链的关系）

dev-review-workflow 的 7 步门禁骨架不变，外部 skill 只作为步骤内的可选执行器接入：

- 已接入：澄清（grill-with-docs）→ 成文（to-spec）→ 拆票（to-tickets）→ TDD（tdd）
- 不接入：code-review 审核链（语义冲突——无 checklist 绑定、无红线、无 blocking 门禁，替换即丢失人工介入点）
- 并行实现仅限 L2 无阻塞工单（每工单独立 diff、独立验收）；L1 永远串行 TDD

## 维护纪律

- 流程变更只改本仓库的 `dev-review-workflow/SKILL.md`，改完同步到各机器安装位置
- 通用审核条目只改 `review-checklist-base.md`，各项目版只维护自己的红线
- 各机器禁止手改安装位置的文件，统一从本仓库更新
