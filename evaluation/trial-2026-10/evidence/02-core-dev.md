第 5 步 core-dev 的关键字段摘录（决定性内容逐字引用，长 stdout 已略，原文见会话记录）。

## 结构性返回（合规）

```
files_changed: ["/tmp/omp-eval/sample/src/refund.py", "/tmp/omp-eval/sample/tests/test_refund.py"]
commands:
  1) cd sample && python3 -m unittest discover -s tests -v      exit_code=1   ← 基线（红，符合 TDD 预期）
  2) 补测试后重跑同一命令                                        exit_code=1   ← TDD 红：新用例全红
  3) 实现后重跑同一命令                                          exit_code=0   ← 全绿（5 tests OK）
  4) 并发压测（24 线程同 id + 12 线程不同 id）                     exit_code=0
  5) git diff --stat / git status --porcelain / 越界文件核对       exit_code=0
```

第 5 条命令的原始输出（节选）：

```
 src/refund.py        | 92 +++++++++++++++++++++++++++++++++++++++++++++++-----
 tests/test_refund.py | 29 +++++++++++++++++
 2 files changed, 113 insertions(+), 8 deletions(-)
--- untracked/modified ---
 M src/refund.py
 M tests/test_refund.py
?? src/__pycache__/
?? tests/__pycache__/
--- confirm forbidden files untouched ---
0
```

## 主动申报的偏差（`contract_deviations`）

- 方案文档写 `RefundService.refund()`（类方法），仓库里从无任何类；按规格卡实现模块级函数，**未新增类**，并请架构师确认文档是否笔误（该文件它无权改）。
- 方案写「不阻塞主请求」，规格卡要求「等待结果后返回」；两者不可同时成立，按规格卡实现（`return future.result()`），**未擅自改成 fire-and-forget**。

## `blocked`（停下来问，未自行扩大范围）

> review-checklist.md 第四节红线「禁止在请求路径上使用无界队列或无界线程池」，与规格卡「ThreadPoolExecutor，max_workers=4」冲突——`max_workers` 有界，但其内部工作队列（SimpleQueue）容量无界，而 `refund()` 正是请求路径入口。我没有擅自添加有界队列/信号量/自定义拒绝策略（那属于架构决策）。请架构师二选一：(a) 确认接受现状…；(b) 批准改为显式有界…，我按新契约重做。

## `notes`（未擅自改动的顺手发现）

边界输入未校验、审计缺「谁」字段（拿不到鉴权上下文，未臆造）、audit logger 显式 setLevel 防止被 root logger 吞掉、懒加载单例 + atexit shutdown 及「池已 shutdown 后 submit 抛 RuntimeError」的拒绝策略、测试访问私有属性 `_max_workers` 属实现耦合、方案自评 L2 与规格卡 L1 不一致（仅记录）、环境未安装 `tdd` skill 故按内联 TDD 执行。

## 对流程纪律的实测结论

- 边界遵守：`git status` 与越界核对命令自证未碰 `src/display.py` 与 `docs/`。
- 结构化返回：`files_changed` 与 `git diff` 实际一致（2 个文件），主会话的机械核对可通过。
- 越界与偏离均走「申报」而非「静默」，符合 SKILL.md 第 5 步的纪律设计。
