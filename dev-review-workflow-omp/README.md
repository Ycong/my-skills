# dev-review-workflow-omp

`../dev-review-workflow`（通用版）的 **oh-my-pi（omp）适配版**，含其运行所需的全部配套产出。原版 skill 不动，两版并行维护。

## 目录结构

```
dev-review-workflow-omp/
├── SKILL.md            # 流程编排：四角色分派版（第 3/5/6 步按 name 派发子代理）
├── agents/             # 四个命名子代理定义（skill 的硬依赖）
│   ├── reviewer.md     # 方案审核 · @slow · 只读 · output=verdict+blocking/non_blocking
│   ├── core-dev.md     # L1 核心实现 · 显式强模型 · TDD · contract_deviations 申报
│   ├── implementer.md  # L2/L3 常规实现 · @task · 结构化返回
│   └── verifier.md     # 独立验收 · @slow · 干净重跑 · 结论只有三种
├── config-snippet.yml  # modelRoles 片段（@task/@slow 的解析来源），合并进 ~/.omp/agent/config.yml
└── README.md           # 本文件
```

## 安装

```bash
# 1. skill（symlink，git pull 后自动同步）
ln -s "$(pwd)/dev-review-workflow-omp" ~/.omp/agent/skills/dev-review-workflow-omp

# 2. 子代理定义：先确认官方目录约定，再放文件
omp agents unpack
cp agents/*.md <omp agents 目录>/

# 3. 角色配置：把 config-snippet.yml 的 modelRoles / task / enabledModels 段
#    合并进 ~/.omp/agent/config.yml（手动合并，勿整文件覆盖）

# 4. 核对（缺一不可）
#    - /models 的 Roles 视图：每个角色解析到的模型逐个确认（解析失败静默回退不报错）
#    - 发起需求时 skill 前置检查会检测四个子代理是否可按 name 找到
```

## 与通用版的差异边界

SKILL.md 相对 `../dev-review-workflow/SKILL.md` 的差异**全部属于以下五类**，其余逐字一致（可 diff 验证）：

1. frontmatter description（标注 omp 适配）
2. 头部注释 + "运行环境与角色分派"节（omp 专属）
3. 前置检查新增第 4 条（检测四个子代理是否已安装）
4. 第 1/2/4/7 步：标题与正文的主语从"AI"改为"主会话"，第 1 步新增"方案文档写入 `docs/`，主会话只写文档不写代码"；第 3/5/6 步：执行主体改为命名子代理（reviewer / core-dev+implementer / verifier），第 5 步整段重写为按分级派发
5. prompt 模板节（箭头标注 `→ reviewer` 等、新增的"实现派发"模板、以及模板前的派发说明——含 `slice` 为必填的提示）

通用变更同步流程：先改通用版，再把差异移植到本目录的 SKILL.md。

## 审核标准

同通用版：项目根目录 `review-checklist.md`（母版 `../review-checklist-base.md`），本目录不携带、不维护审核标准。
