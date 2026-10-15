# skill 真实开发可用性评估（2026-10）

> 评估对象：`dev-review-workflow`（通用版）与 `dev-review-workflow-omp`（omp 适配版），含 4 个 agent 定义、
> `config-snippet.yml` 与 `review-checklist-base.md`。
> 方法：**一手文档事实核验 + 端到端实测**（材料与证据见 `trial-2026-10/`）。
> 结论只代表本次核验到的版本，不构成"长期有效"的判断。

## 一、结论

**能用，而且核心机制是真的有效——但适用面比文档暗示的窄，且有 4 处会实际影响使用的问题需要修。**

1. **核心机制经实测有效。** 独立审核 + 证据重跑 + 分级门禁这三件事不是纸上纪律：一次 L1 实测里，
   第 3 步 reviewer 给出 10 项 blocking（含 2 项资金链路红线、1 项把 L2 自评拉回 L1），
   第 6 步 verifier 干净重跑否定了"全绿"申报、抓出越界文件，并自建 50 线程并发与边界输入用例。
2. **依赖项事实核验基本全绿。** omp 的 agents/skills 目录、frontmatter 字段（含 `read-summarize`、`output`）、
   `@task`/`@slow` 角色别名、`task.maxConcurrency`、`enabledModels` 替换语义、`omp agents unpack`、
   mattpocock/skills 的四个 skill 路径——**逐条有官方文档或仓库实证**。
3. **但有 4 个真实问题**：① omp 版前置检查只按 `name` 判定子代理，可能被同名 agent 静默替换；
   ② verifier 的 `output` schema 与派发模板不一致，实测被"绕过"；③ 模型配置指向已退役别名且锁死供应商；
   ④ headless/CI 场景未定义，4 个人工介入点无法履行。
   **①②③ 中的缺陷部分已在本分支修复（见第七节），④ 与供应商锁定属设计取舍，待你定。**
4. **成本必须配分级用。** 一次 L1 循环实测合计约 **47 万 input tokens / 26 轮子代理迭代**（三关）。
   用在 L1/L2 且可自动验收的变更上划算；小修小补原本没有便宜路径，**已在本分支补上 L0 直通**（1 次交互、0 子代理，见第七节）。

一句话建议：**保留并继续用，但先修 P1 的 4 条；把 L1/L2 当默认适用面，L3 之外不要强推。**

## 二、评估方法与证据强度

| 手段 | 覆盖 | 强度 |
|---|---|---|
| 一手文档核验（omp.sh/docs、DeepSeek API docs） | 所有外部依赖的事实 | 强（官方原文，含原文引用） |
| `gh api` 仓库核验 | mattpocock/skills 四个 skill 路径、安装命令 | 强（仓库实际内容） |
| 端到端实测（本环境子代理，按 SKILL.md 模板与 agents 正文派发） | 第 3/5/6 步的**机制有效性** | 中强（机制层，非 omp 实机） |

**明确的局限（影响结论强度，务必一并阅读）**

- 实测用的是本环境的通用子代理能力，**不是 omp 运行时**。`output` JSON Schema 没有被运行时强制校验，
  子代理是"自愿合规"——因此"schema 会被运行时拦下非法返回"这一条**未经验证**。
- token 数为本环境观测值，不是 omp 的计费口径，只能当**相对量级**看。
- 未实测：L2/L3 路径、多工单并行实现、`.review-workflow-state` 跨会话续跑、连续两轮未过的人工裁决。
- 环境无 `omp`，故"按 README 安装后能跑起来"属**文档级+机制级**证据，不是实机证据。

## 三、依赖事实核验（逐条）

| # | skill/README 的声明 | 一手证据 | 判定 |
|---|---|---|---|
| 1 | 子代理定义放 `~/.omp/agent/agents/<name>.md` | omp 文档"Choose where it lives"表：User 作用域即此路径 | ✅ |
| 2 | skills 放 `~/.omp/agent/skills/<name>/SKILL.md` | omp 文档 Skills 页："A standalone skill is just a directory containing SKILL.md"，示例 `mkdir -p ~/.omp/agent/skills/postgres` | ✅（README 的 symlink 形式正确） |
| 3 | frontmatter 字段 `name`/`description`/`tools`/`model`/`thinking-level`/`read-summarize`/`output` | omp 文档 Frontmatter reference 逐字列出，且注明 camelCase/kebab-case 均可 | ✅ 全部存在 |
| 4 | `@task`/`@slow` 角色别名 | omp 内置角色表含 `task`（General subagent work）与 `slow`（Thorough reasoning）；文档："`@role` is canonical" | ✅ |
| 5 | `modelRoles` 键 `default/plan/task/slow/smol/tiny/commit` | omp 内置角色表含全部这些名字（另含 `vision`/`designer`/`advisor`） | ✅ |
| 6 | 模型串可带 `:high`/`:medium`/`:low` 思考等级后缀 | omp 文档："Thinking suffix … `openai-codex/gpt-5.3-codex:xhigh`" | ✅ |
| 7 | `task.maxConcurrency` 设 4 | omp 文档 Subagents 默认值表：`task.maxConcurrency` 默认 32，"0 is unlimited" | ✅ |
| 8 | 项目级 `.omp/config.yml` 的 `enabledModels` 会**替换**而非追加 | omp 文档 Settings 故障排查原文："an array in the project replaces the whole global array" | ✅（skill 的告警方向正确） |
| 9 | `omp agents unpack` 取官方 agent 副本 | omp 文档："run `omp agents unpack --project` or `omp agents unpack` for user scope" | ✅ |
| 10 | "omp 角色解析失败会静默回退，不报错" | 文档只说"角色/模型解析不到时去 `/models` 核对"，并未承诺"静默回退"；可确认的是未解析不会阻断定义发现 | ⚠️ 方向正确、措辞偏强 |
| 11 | mattpocock/skills 的 `skills/engineering/{tdd,grill-with-docs,to-spec,to-tickets}` | `gh api` 实测四个目录均存在（各含 `SKILL.md`，`tdd` 另含 `agents/`） | ✅ |
| 12 | `npx skills@latest add mattpocock/skills` | 该仓库 README 原文命令，且支持 `-a <agent>`（列表含 `pi`） | ✅ 可补 `-a pi` |
| 13 | `deepseek/deepseek-v4-pro`、`deepseek/deepseek-v4-flash` | DeepSeek 官方定价页：`deepseek-v4-pro` 有效；`deepseek-v4-flash` 已是 **legacy 名，模型已退役**，请求由 V4.1-Flash 承接（建议写 `deepseek-flash`） | ⚠️ pro 有效，flash 需更新 |
| 14 | 四个 agent 名字不会与 omp 内置冲突 | omp 内置 agent 列表**包含 `reviewer`**（@slow，"Evidence-backed correctness, quality, and security review"）；自定义同名可覆盖内置，但项目级 `.omp/agents/reviewer.md` 又会压过用户级 | ⚠️ 存在静默替换路径 |

## 四、端到端实测：三关的真实表现

**被测变更**：资金退款接口改造（L1）——线程池异步化 + 同 `request_id` 幂等 + 写账目落审计日志。
基线故意做成"方案自评 L2、验收清单要求幂等、实现里没有幂等"，并在第 6 步前植入两类失真：
**自报全绿但实际红**、**越界改了批准范围外的文件**。材料见 `trial-2026-10/`。

| 关卡 | 派发对象 | 抓到的内容 | 成本 |
|---|---|---|---|
| 第 3 步 | `reviewer` | **10 blocking + 8 non-blocking**：幂等缺失、**L2 自评违规应为 L1**、无界队列触红线、写账目无审计触红线、fail-safe 未定义、并发共享状态无锁、边界输入未校验、"用 for 循环冒充并发验收"；全部附 `文件:行` | 4 轮 / 37k in |
| 第 5 步 | `core-dev` | 实现 + 自证边界（`git status` 证明未碰边界外文件）+ 主动申报 2 项偏差 + **1 项 `blocked`**：`ThreadPoolExecutor` 内部队列无界，与项目红线冲突，请架构师裁决 | 11 轮 / 258k in |
| 第 6 步 | `verifier` | **否定"全绿"申报**（两次独立重跑均 `EXIT_CODE=1`，附原始 traceback）、**抓出越界文件 `src/display.py`**（对照批准文件清单 + `git diff --name-only`）、自建 50 线程幂等与 200 次提交队列深度实测、自建边界输入用例、对"权限不足"判 `无法判定` 并说明缺什么、未给任何改进建议 | 11 轮 / 179k in |

合计 **26 轮子代理迭代、约 47 万 input tokens**（同一小变更、三个独立执行体）。

**值得记录的三个细节（说明门禁不是"走形式"）**

1. **verifier 没有被"看起来绿了"带偏**：植入的回归是"删掉幂等早退分支"，由于 `_REFUNDS` 以
   `request_id` 为键，记录数仍是 1 —— 幂等外观成立。verifier 准确地区分了
   "记录数=1（通过）"与"缺 `status=duplicate` 审计分支（未通过）"，把失败定位到规格输出项 3。
2. **双关交叉验证**：core-dev 的 `blocked`（无界队列与红线冲突）与第 3 步 reviewer 的 blocking
   是同一发现的**独立复现**——两个互不通气的执行体得出同一结论，这正是"并行审核"设计想要的信号。
3. **"申报"纪律被真实使用**：core-dev 把"方案写 `RefundService` 但仓库里没有类""方案要求不阻塞、
   规格卡要求等待返回"两处矛盾显式申报而非静默处理；主会话的 `files_changed` × `git diff` 机械核对
   因此是可行的（本次一致，2 个文件）。

## 五、真实开发中的适用性判断

| 场景 | 判断 | 理由 |
|---|---|---|
| L1 变更（资金/数据/权限/并发/核心链路） | ✅ **强烈建议用** | 实测收益最高：红线与分级误判都是"人容易放过、AI 逐条核对能抓住"的类型 |
| L2 变更（非核心模块、配置、依赖升级）且有自动化验收 | ✅ 用 | 单个 reviewer + 实现 + verifier，成本可接受，能防住夹带与假绿 |
| 无测试 / 验收无法自动化 | ⚠️ 勉强 | L1 强制 TDD 会先逼出测试（本次即如此）；但"人工项"占比高时，"全绿报告即放行"的核心凭证失效 |
| 小修小补、配置一行改动 | ❌ 不建议 | 三关成本远超改动本身，且 checklist 会把配置变更判成 L2 → 仍要三关 |
| 纯文档/注释 | ❌ | description 已明确排除（但与 L3 定义有轻微矛盾，见 P3-10） |
| headless / CI 无人值守 | ❌ **不可用** | 4 个人工介入点无法履行，skill 未定义降级行为（见 P2-5） |
| 非 omp 的工具 | 视情况 | omp 版会拒绝启动（设计如此）；通用版要求"能起独立 subagent"，本次实测证明只要工具有子代理能力即可跑通 |
| 多工单并行实现（L2 无阻塞） | ⚠️ 未实测 | 机制上可行（`task.maxConcurrency` 已确认存在），但"每工单独立 diff 独立验收"在单工作树里靠 `git diff` 收集会互相污染，需人工或隔离工作区配合 |

## 六、发现的问题（按影响排序）

### P1 · 会让流程跑偏或跑不起来

**P1-1 子代理前置检查只按 `name` 判定，存在静默替换路径。**
omp 的 agent 解析优先级是「最近的项目 `.omp/agents/` → 用户 agents 目录 → 扩展 → Claude 插件 → **omp 内置**」，
而 omp **内置 agent 里就有 `reviewer`**（@slow）。所以：① 任何仓库里放了 `.omp/agents/reviewer.md`，
本 skill 的 `reviewer` 会被静默顶掉；② 用户级文件缺失时，"按 name 能找到"也可能命中内置 reviewer
（无本 skill 要求的 `output` 契约）。前置检查"能按 name 找到"因此**会误判为通过**。
→ 已修（本分支）：前置检查第 4 条改为「`~/.omp/agent/agents/` 下四个文件必须存在」+「从项目根向上逐级检查 `.omp/agents/` 不得存在同名文件」，
两者不满足即停止并列出被哪个路径顶掉。用文件系统事实判定，不依赖人工去 `/agents` 里核对来源路径。

**P1-2 verifier 的 `output` schema 与派发模板不一致（实测被绕过）。**
模板要求"结论 + 各验收项结果 + **偏差与遗留清单**"，但 schema 是 `additionalProperties: false` 且只有
`slice/checks/overall`。实测 verifier 只能把"遗留/待裁决项"**包装成一条 `未通过` 的 check**——
遗留项 ≠ 验收失败，却参与 `overall` 判定，语义污染。
→ 已修（本分支）：`verifier.md` 的 schema 增 `deviations` / `leftovers`（string[]，列入 `required`，无则空数组），
正文补「偏差与遗留不是验收项，不得塞进 `checks`」与「`overall` 只由 `checks` 决定」；omp 版第 6 步同步补「缺这两个字段的返回视为无效，重派」，
第 7 步补「`leftovers` 非空 → 按有条件通过处理」（否则新字段收了没人接）。

**P1-3 `slice` 是 core-dev / implementer / verifier 三个 agent 的 required 字段，但派发模板从未提及。**
实测中 core-dev 与 verifier 各自猜了一个值（本次猜得合理，但这是运气；`reviewer.md` 的 schema 无该字段）。
→ 已修（本分支）：**不改模板文本**（两版模板继续保持逐字一致），改在 omp 版「subagent prompt 模板」节的**派发说明**里加一句
「各 agent 的 `output` 中 `slice` 是必填字段，派发时明确告知填规格卡编号或一句话标识」。

**P1-4 模型配置锁死供应商，且含已退役别名。**
`config-snippet.yml` 全量指向 `deepseek/*`，`core-dev.md` 直接写死 `deepseek/deepseek-v4-pro`；
其中 `deepseek-v4-flash` 在 DeepSeek 官方文档中已是 **legacy 名（模型已退役，按 `deepseek-flash`/V4.1-Flash 计费）**。
非 DeepSeek 用户必须同时改两个文件才能用。
→ 已修（本分支）：`deepseek-v4-flash` → `deepseek-flash`（task/smol/tiny/commit 四处），并在文件内加注释说明该名已退役。
→ **待你定（设计取舍）**：`core-dev.md` 仍写死 `deepseek/deepseek-v4-pro`。可选方案是新增 `core` 角色、frontmatter 写 `"@core"`——
仍是"显式指定"，但换供应商只改 `modelRoles` 一处；代价是多占一个角色位（omp 文档本身也建议"frontmatter 放角色别名、具体模型交给环境配置"）。

### P2 · 影响可用性与成本

**P2-5 headless / CI 场景未定义。** 4 个人工介入点（分级确认、L1 blocking 确认、遗留项过目、两轮未过裁决）
在 `omp -p`、CI、批处理里无法履行；skill 既没说"拒绝启动"，也没说"降级为只产出材料"。
→ 修法：补"非交互运行"一节：明确哪些介入点可预授权（如 `--approval-mode` 配合 L2 自动放行）、哪些必须停。

**P2-6 成本与分级不匹配，缺轻量通道。** 实测一次 L1 循环 ≈47 万 input tokens；而 checklist 把"配置变更、
依赖升级"判为 L2 → 也要"方案 + 分级 + reviewer + 实现 + verifier"五步。L3 只覆盖文档/展示，
**真实开发里最高频的"一行配置/小修"没有便宜路径**。
→ 已修（本分支）：两版 SKILL.md 新增**第 0 步 L0 直通**（微小改动：≤2 个文件且同属一个模块/目录 / ≤100 行 / 不新增公共接口 / 不命中 L1 与红线 / 有验收命令），
全程 1 次交互：直通卡确认 → 主会话直接改 → 贴验收原始输出 → 过目 diff；配套硬性升级条件（溢出第 3 个文件、超 100 行、第 2 个文件跨模块、命中红线、验收不绿、同一模块连续 2 次 → 立即停止并回到第 2 步）。
frontmatter description 同步收窄触发范围。omp 版把"主会话不产出 diff"的不变式改为"除 L0 外"。

**P2-7 omp 版 `name` 覆盖目录名。** `dev-review-workflow-omp/SKILL.md` 的 frontmatter 是
`name: dev-review-workflow`；omp 文档明确 `name` 会**覆盖目录名**用于匹配与 `/skill:<name>`。
所以按 README 装成 `dev-review-workflow-omp` 后，调用名其实是 `/skill:dev-review-workflow`；
若同一 omp 环境还能从 `~/.claude/skills/`、`~/.agent/skills/` 等**兼容目录**发现通用版，会出现同名两 skill。
→ 修法：omp 版设 `name: dev-review-workflow-omp`（或 README 注明"两版不要同时装在 omp 可见目录"）。

**P2-8 通用版没有"子代理怎么起"的可执行说明。** 通用版只说"起 subagent"，但目标环境的机制差异很大：
一类是**命名 agent 型**（如 omp：`agents/<name>.md` 预装定义 + 按 name 派发 + `output` schema 兜底），
另一类是**通用 task 型**（一次性的独立执行体，每次现场拼 prompt、无 schema 兜底）。通用版对两者都没写清，
第 3/6 步是否真的派发、派发到什么，不可控；而 omp 版反过来又是"缺一个就拒绝启动"。
→ 修法：通用版补"派发映射"表（命名 agent 型 / 通用 task 型各自怎么落），并明确
"若环境无法保证独立执行体，按无子代理降级处理并告知用户"。

### P3 · 文档一致性（低成本）

**P3-9** README 的 `npx skills@latest add mattpocock/skills` 可补 `-a pi`（官方 README 的 agent 列表含 `pi`，
即 oh-my-pi），避免 omp 用户交互式猜选项。
**P3-10** 通用版 description 写"Not for … doc-only edits"，但流程里 L3 明确覆盖"文档、注释" → 轻微自相矛盾，
建议统一措辞（例如"仅文档改动不进入流程"）。
**P3-11** `reviewer.md` 要求把"分级存疑观察"写进 `non_blocking`——可工作，但和第 P1-2 一起修更干净
（schema 加 `tier_concern`）。
**P3-12** `review-checklist-base.md` 声称"适用于任何项目"，但第 3 节是 Java 语境的条目
（"线程池显式创建、有界、命名、拒绝策略明确"）。本次实测在 Python 项目上仍然有效（`ThreadPoolExecutor`
的 `max_workers` 有界而内部队列无界，正好被这条抓住），但换成 Go/Node 项目时这条容易变成噪声。
→ 修法：把这节改写成与技术栈无关的表述（"并发执行体必须有界、可命名、拒绝策略明确"）。

## 七、处理状态

### 已修（本分支；只动 omp 适配版与配套文件，通用版逐字未改）

| 问题 | 改了什么 | 落在哪 |
|---|---|---|
| P1-1 | 前置检查第 4 条：按 name 找到 → **文件存在性 + 项目级遮蔽检测** | `dev-review-workflow-omp/SKILL.md` |
| P1-2 | verifier schema 增 `deviations` / `leftovers`（required，无则空数组）+ 正文两条纪律 + 第 6 步"缺字段重派" | `agents/verifier.md`、`SKILL.md` |
| P1-3 | 派发说明补 `slice` 必填提示（不动模板文本，两版模板保持逐字一致） | `SKILL.md` |
| P1-4a | `deepseek-v4-flash` → `deepseek-flash`（退役别名） | `config-snippet.yml` |
| P2-6 | 新增**第 0 步 L0 直通**（微小改动：1 次确认 / 0 子代理 / 无方案文档）+ description 收窄触发；omp 版不变式改为"除 L0 外" | 两版 `SKILL.md`、`dev-review-workflow-omp/README.md` |
| — | 差异边界第 5 类措辞同步（prompt 模板节现含派发说明） | `dev-review-workflow-omp/README.md` |

核验：四个 agent 的 frontmatter 与 `config-snippet.yml` 均通过 YAML 子集解析，且每个 `output.required`
里的字段都在 `properties` 中有定义（`additionalProperties: false` 下不会出现"必填但未定义"）。

### 待你定（设计取舍，未动）

- **P1-4b 供应商锁定**：`core-dev.md` 写死 `deepseek/deepseek-v4-pro`。建议新增 `core` 角色 + frontmatter 写 `"@core"`；
  不改也能用（该模型名当前有效）。
- **P2-5 headless/CI**：只有你要在 CI / `omp -p` 里跑这个流程才需要补"非交互运行"节；现在的"拒绝启动"是安全默认。
- **P2-7 `name` 覆盖目录名**：只有两个版本同时装进同一 omp 可见目录才会撞名；改动会动 frontmatter 差异类，收益小。
- **配套（已代改，请复核措辞）**：`review-checklist-base.md` 已补 L0 条目（分级表加一行 + 使用规则 6/7）。该文件自述"由人工维护，AI 不得自行修改"，
  本次是**用户明确授权后代改**，若措辞不合意请直接改回。项目级 `review-checklist.md` 由各项目自行同步（本仓库不含）。

### 建议不改（文案级打磨，随时可做，不值得单独开一轮）

- **P3-9** README 的 `npx skills@latest add mattpocock/skills` 补 `-a pi` —— **已作为 L0 直通样例顺手改掉**（1 次确认 + 1 条验收命令 + 0 子代理，见提交信息 "L0 fast path example"）
- **P3-10** 通用版 description 的"doc-only edits"与 L3 定义措辞统一
- **P3-12** `review-checklist-base.md` 第 3 节去 Java 语境（本次实测在 Python 上仍有效，改不改都不影响）

## 八、复现方式

```bash
cd evaluation/trial-2026-10/sample
git init -q && git add -A && git -c user.email=e@e -c user.name=e commit -qm baseline
python3 -m unittest discover -s tests -v      # 基线：1 红（幂等）1 绿
# 按 prompts/01-reviewer.md 派发 reviewer（期望 驳回 + 10 blocking）
# 按 prompts/02-core-dev.md 派发 core-dev（期望 全绿 + 申报偏差 + 1 blocked）
python3 ../plant_mutations.py                  # 植入回归 + 夹带
git --no-pager diff --stat                     # 3 个文件
# 按 prompts/03-verifier.md 派发 verifier（期望 overall=未通过 + 抓到 display.py）
```

三关的返回证据（含逐字原文与位置抽查）在 `trial-2026-10/evidence/`。

## 九、本次没有做的事

- 没有实机安装 omp 跑一遍（环境无 omp），因此"按 README 安装即可用"只有文档级证据。
- 没有验证 omp 运行时对 `output` schema 的**强制校验**行为（子代理是否会被拦下重派）。
- 除第七节列出的 P1 缺陷修复外，没有改动其他 skill / agent / checklist 内容；`review-checklist-base.md` 一字未动，
  通用版 `dev-review-workflow/SKILL.md` 也一字未动（修复只落在 omp 适配版与配套文件）。

