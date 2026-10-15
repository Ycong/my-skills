# my-skills

个人开发审核流程的 skill 与模板仓库。跨机器分发统一走本仓库，禁止在安装位置手改。

## 仓库结构

```
my-skills/
├── dev-review-workflow/       # skill：开发审核流程编排（怎么转）· 通用版
│   └── SKILL.md
├── dev-review-workflow-omp/   # skill：同上 · oh-my-pi(omp) 适配版（自包含，含子代理与角色配置）
│   ├── SKILL.md
│   ├── agents/                # reviewer / core-dev / implementer / verifier
│   ├── config-snippet.yml     # modelRoles 片段（@task/@slow 解析来源）
│   └── README.md
├── review-checklist-base.md   # 审核标准母版（审什么的初始化源）
├── evaluation/                # 可用性评估（评估与建议，不改 skill 本体）
│   ├── 2026-10-skill-usability-report.md   # 结论：能用，但有 4 条 P1 需修
│   └── trial-2026-10/         # 实测材料：被测项目 + 派发 prompt + 三关证据
└── README.md
```

## 安装通用版 dev-review-workflow

将 `dev-review-workflow/` 目录放入对应产品的全局 skills 目录：

- Trae CN：`~/.trae-cn/skills/`
- Trae 国际版：`~/.trae/skills/`

```bash
# 复制方式
cp -r dev-review-workflow ~/.trae-cn/skills/

# 或 symlink 方式（本仓库 git pull 后自动同步）
ln -s "$(pwd)/dev-review-workflow" ~/.trae-cn/skills/dev-review-workflow
```

## 安装 omp 适配版 dev-review-workflow-omp

将 `dev-review-workflow-omp/` 目录放入 omp 的全局 skills 目录：

```bash
ln -s "$(pwd)/dev-review-workflow-omp" ~/.omp/agent/skills/dev-review-workflow-omp
```

**依赖四个命名子代理与角色配置，均已自包含在本目录**（适配版按 name 派发：第 3 步 `reviewer`、第 5 步 `core-dev`/`implementer`、第 6 步 `verifier`；缺任何一个 skill 拒绝启动，不降级为主会话亲自执行）：

```bash
# 1. skill
ln -s "$(pwd)/dev-review-workflow-omp" ~/.omp/agent/skills/dev-review-workflow-omp

# 2. 子代理定义：先确认官方目录约定，再放文件
omp agents unpack
cp dev-review-workflow-omp/agents/*.md <omp agents 目录>/

# 3. 角色配置：把 dev-review-workflow-omp/config-snippet.yml 的
#    modelRoles / task / enabledModels 段合并进 ~/.omp/agent/config.yml

# 4. /models 的 Roles 视图核对每个角色实际解析到的模型——
#    omp 角色解析失败会静默回退，不报错
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

## 可用性评估（2026-10）

见 `evaluation/2026-10-skill-usability-report.md`：逐条核验外部依赖（omp / Trae / mattpocock skills / 模型 ID），
并用一次 L1 变更（资金退款接口改造）实测第 3/5/6 步，植入"自报全绿""越界夹带"两类失真。
结论：核心门禁真实有效（抓到 10 项 blocking、否定假绿申报、抓出夹带），但有 4 条 P1 问题需修；
报告只给评估与建议，**不改动 skill 本体**。复现材料在 `evaluation/trial-2026-10/`。

## 维护纪律

- 通用版变更只改本仓库的 `dev-review-workflow/SKILL.md`，改完同步到各机器安装位置
- **omp 适配版跟随通用版同步**：先改通用版，再把差异移植到 `dev-review-workflow-omp/SKILL.md`（本版差异仅限"运行环境与角色分派"节、第 3/5/6 步的派发对象、prompt 模板的箭头标注，其余保持与通用版逐字一致，方便 diff）
- 通用审核条目只改 `review-checklist-base.md`，各项目版只维护自己的红线
- 各机器禁止手改安装位置的文件，统一从本仓库更新
