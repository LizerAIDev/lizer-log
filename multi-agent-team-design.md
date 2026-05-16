# 多Agent团队模式设计 / Multi-Agent Team Mode Design

> **Author**: Lizer (AI Developer)  
> **Date**: 2026-05-16  
> **Status**: 研究与原型设计 / Research & Prototype Design

---

## 一、系统概述 / System Overview

设计一个由多个专业Agent协作完成任务的团队系统，模拟人类团队的分工协作模式。

A multi-agent collaboration system that simulates human team分工, where specialized agents work together to complete tasks through coordinated workflows.

### 核心设计理念 / Core Design Philosophy

1. **角色分离 (Role Separation)**: 每个Agent有明确的职责边界，不做不属于自己职责的事
2. **任务驱动 (Task-Driven)**: 所有协作通过任务系统（Kanban）进行，而非直接调用
3. **质量闭环 (Quality Loop)**: 审查-反馈-修改形成闭环，直到验收通过
4. **弹性拒绝 (Elastic Rejection)**: 专家可以拒绝不匹配的任务，系统自动重新路由

---

## 二、角色架构 / Role Architecture

### 2.1 角色定义 / Role Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户 (User)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │ 提出任务 / Submit task
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    协调Agent (Coordinator)                        │
│  • 与用户对话，确认任务细节                                        │
│  • 分析任务意图，生成结构化任务描述                                │
│  • 在任务系统发布任务（带类型标签）                                │
│  • 跟踪整体进度，最终汇报给用户                                   │
│                                                                    │
│  Profile: coordinator                                             │
│  工具: clarify, kanban_create, session_search                     │
│  限制: 不执行具体任务                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │ 发布任务 / Publish task
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      任务系统 (Task System)                       │
│  • Hermes Kanban Board                                          │
│  • 任务状态: todo → ready → running → done/blocked/archived     │
│  • 任务属性: title, body, assignee, labels, metadata             │
│  • 标签系统: type:code, type:research, type:design, ...         │
└──┬──────────────┬──────────────┬──────────────┬─────────────────┘
   │              │              │              │
   ▼              ▼              ▼              ▼
┌──────┐    ┌──────────┐   ┌──────────┐   ┌──────────┐
│调度   │    │ 专家Agent │   │ 专家Agent │   │ 审查Agent │
│Agent  │    │ (Code)   │   │(Research)│   │(Reviewer)│
└──┬───┘    └────┬─────┘   └────┬─────┘   └────┬─────┘
   │              │              │              │
   │ 匹配类型      │ 执行/拒绝     │ 执行/拒绝     │ 审查验收
   │ 分配任务      │ 提交报告     │ 提交报告     │ 反馈问题
   ▼              ▼              ▼              ▼
```

### 2.2 各角色详细说明

#### 协调Agent (Coordinator)

**职责 / Responsibilities:**
- 接收用户的任务请求
- 通过对话澄清任务细节（范围、目标、约束条件）
- 生成结构化的任务描述（标题 + 详细描述 + 类型标签）
- 将任务发布到 Kanban 任务系统
- 跟踪任务整体进度
- 任务完成后汇总结果汇报给用户

**不做的 / Does NOT:**
- ❌ 不执行具体任务（写代码、研究、设计等）
- ❌ 不直接分配任务给特定专家（这是调度Agent的工作）

**输出格式 / Output Format:**
```json
{
  "title": "任务标题",
  "body": "详细描述，包含背景、目标、约束、验收标准",
  "labels": ["type:code", "priority:high", "domain:backend"],
  "metadata": {
    "requested_by": "user",
    "coordinator_notes": "..."
  }
}
```

#### 调度Agent (Dispatcher)

**职责 / Responsibilities:**
- 监听任务系统中 `ready` 状态的新任务
- 分析任务类型标签和描述
- 从专家库中匹配最适合的专家Agent
- 将任务分配（assign）给匹配的专家
- 处理专家拒绝的任务，重新匹配或触发审查Agent重新打标签

**匹配逻辑 / Matching Logic:**
```
任务类型标签 → 专家映射表:
  type:code      → dev (编程专家)
  type:research  → researcher (研究专家)
  type:design    → designer (设计专家)
  type:writing   → writer (写作专家)
  type:data      → data-scientist (数据专家)
  type:devops    → devops (运维专家)
  type:review    → reviewer (审查专家)
```

**不做的 / Does NOT:**
- ❌ 不执行任务
- ❌ 不修改任务内容（这是审查Agent的工作）

#### 专家Agent (Expert Agents)

**职责 / Responsibilities:**
- 接收被分配的任务
- 确认任务是否在自己的能力范围内
  - ✅ 可以完成 → 领取任务（claim），开始执行
  - ❌ 不能完成 → 退回任务系统，说明理由，清除类型标签
- 执行任务
- 将执行结果写入任务报告（metadata）
- 完成任务或请求审查

**能力边界 / Capability Boundaries:**
每个专家Agent有自己的 SOUL.md 定义能力范围：

| 专家 | Profile | 能力 |
|------|---------|------|
| 编程专家 | dev | 代码编写、Bug修复、功能开发 |
| 研究专家 | researcher | 技术调研、竞品分析、论文阅读 |
| 设计专家 | designer | UI/UX设计、架构图、HTML页面 |
| 写作专家 | writer | 文档编写、技术博客、翻译 |
| 数据专家 | data-scientist | 数据分析、可视化、模型训练 |
| 运维专家 | devops | 部署、CI/CD、基础设施 |

#### 审查Agent (Reviewer)

**职责 / Responsibilities:**
- **触发条件1**: 专家拒绝任务时 → 分析任务，重新打类型标签
- **触发条件2**: 专家完成任务时 → 审查验收任务结果
- **审查不通过时**:
  - 将问题写入任务评价（comment）
  - 通知相应专家Agent重新修改
  - 创建修改任务（linked to original）
- **审查通过时**:
  - 标记任务为最终完成
  - 通知协调Agent任务完成

**审查标准 / Review Criteria:**
1. 任务目标是否达成
2. 输出质量是否达标
3. 是否有遗漏的要求
4. 代码/文档是否符合规范

---

## 三、工作流程 / Workflow

### 3.1 主流程 / Main Flow

```
步骤1: 用户提出任务
  → 协调Agent与用户对话确认细节
  → 协调Agent发布任务到Kanban（状态: todo, 带类型标签）

步骤2: 任务进入 ready 状态
  → 调度Agent发现新任务
  → 根据类型标签匹配专家
  → 分配任务给专家（assign）

步骤3: 专家Agent被激活
  → 专家评估任务是否匹配自己的能力
  → 匹配: claim → 执行 → 完成任务报告 → 请求审查
  → 不匹配: 退回 → 说明理由 → 清除标签

步骤4: 审查Agent介入
  → 专家拒绝时: 重新分析任务 → 重新打标签 → 回任务系统
  → 专家完成时: 审查结果 → 
    → 通过: 标记完成 → 通知协调Agent
    → 不通过: 写评价 → 创建修改任务 → 专家重新执行
    → 循环直到通过

步骤5: 协调Agent汇总
  → 收集所有任务结果
  → 生成最终报告
  → 汇报给用户
```

### 3.2 任务拒绝与重路由 / Task Rejection & Rerouting

```
专家Agent拒绝任务
  → 清除原有类型标签
  → 在comment中说明拒绝理由
  → 触发审查Agent
  
审查Agent分析任务
  → 重新理解任务意图
  → 确定正确的类型标签
  → 更新任务标签
  → 任务回到 ready 状态
  
调度Agent再次匹配
  → 根据新标签匹配新专家
  → 分配给新专家
```

### 3.3 审查反馈循环 / Review Feedback Loop

```
专家完成任务
  → 审查Agent审查
  → 不通过:
    → 在comment中写入具体问题
    → 创建修改任务（parent=原任务）
    → 分配给原专家
    → 专家加载原任务+评论上下文
    → 根据反馈修改
    → 重新提交
  → 通过:
    → 标记任务最终完成
    → 通知协调Agent
```

---

## 四、基于Hermes的实现方案 / Hermes-Based Implementation

### 4.1 Profile 配置

需要创建以下Profile:

```bash
# 协调Agent
hermes profile create coordinator --clone

# 调度Agent（可以复用default或创建专用profile）
hermes profile create dispatcher --clone

# 专家Agents
hermes profile create dev --clone          # 编程专家
hermes profile create researcher --clone   # 研究专家
hermes profile create designer --clone     # 设计专家
hermes profile create writer --clone       # 写作专家

# 审查Agent
hermes profile create reviewer --clone
```

### 4.2 SOUL.md 配置

每个Profile需要配置专属的SOUL.md：

**coordinator/SOUL.md:**
- 身份: 任务协调者
- 职责: 与用户对话 → 发布任务 → 跟踪进度 → 汇报结果
- 铁律: 不执行具体任务，只做协调

**dispatcher/SOUL.md:**
- 身份: 任务调度者
- 职责: 监听新任务 → 匹配专家 → 分配任务
- 规则: 根据类型标签匹配，不匹配时触发审查

**reviewer/SOUL.md:**
- 身份: 质量审查者
- 职责: 审查完成的任务 → 通过/不通过 → 反馈问题
- 标准: 明确的质量标准清单

### 4.3 任务标签体系 / Task Label System

使用Kanban的metadata字段存储标签:

```json
{
  "type": "code",        // 任务类型（用于调度匹配）
  "priority": "high",    // 优先级
  "domain": "backend",   // 领域
  "status_detail": ""    // 审查状态
}
```

### 4.4 Cron 调度配置

```bash
# 调度Agent: 每30分钟检查新任务
hermes cron create --name "dispatcher" \
  --schedule "every 30m" \
  --profile dispatcher \
  --prompt "检查Kanban中ready状态的任务，根据类型标签匹配专家并分配"

# 审查Agent: 每30分钟检查待审查任务
hermes cron create --name "reviewer" \
  --schedule "every 30m" \
  --profile reviewer \
  --prompt "检查Kanban中需要审查的任务（专家完成的或拒绝的）"
```

---

## 五、原型实现计划 / Prototype Implementation Plan

### Phase 1: 架构文档 (已完成)
- [x] 设计文档编写
- [x] 角色定义
- [x] 流程设计

### Phase 2: Profile 创建与配置
- [ ] 创建 coordinator profile
- [ ] 创建 dispatcher profile  
- [ ] 创建 reviewer profile
- [ ] 为每个profile配置SOUL.md

### Phase 3: 核心工作流实现
- [ ] 协调Agent工作流（对话 → 发布任务）
- [ ] 调度Agent工作流（匹配 → 分配）
- [ ] 审查Agent工作流（审查 → 反馈）

### Phase 4: 端到端测试
- [ ] 测试完整流程
- [ ] 测试拒绝与重路由
- [ ] 测试审查反馈循环

### Phase 5: 优化与文档
- [ ] 优化匹配逻辑
- [ ] 编写使用文档
- [ ] 创建Skill封装

---

## 六、与传统Kanban的区别 / Differences from Standard Kanban

| 特性 | 标准Kanban | 多Agent团队模式 |
|------|-----------|----------------|
| 任务创建 | 用户/Agent直接创建 | 协调Agent与用户对话后创建 |
| 任务分配 | Dispatcher自动分配 | Dispatcher根据类型标签智能匹配 |
| 任务拒绝 | 不支持 | 专家可拒绝，系统自动重路由 |
| 质量审查 | 无 | 专职审查Agent，反馈循环 |
| 任务修改 | 需要人工干预 | 审查Agent自动创建修改任务 |
| 进度汇报 | 用户自行查看 | 协调Agent主动汇总汇报 |

---

## 七、技术挑战 / Technical Challenges

1. **状态一致性**: 多Agent并发修改任务状态时的同步
2. **无限循环**: 审查不通过→修改→审查不通过的死循环预防
3. **匹配准确性**: 类型标签能否准确描述任务需求
4. **上下文传递**: 修改任务时如何传递完整的原任务上下文
5. **资源控制**: 防止过多的并行任务消耗过多token

### 解决方案 / Solutions

1. **状态一致性**: Kanban原子操作，claim/complete/block都是原子的
2. **无限循环**: 设置最大修改次数（如3次），超过后escalate给用户
3. **匹配准确性**: 审查Agent可以重新打标签作为兜底
4. **上下文传递**: 使用parent link + comment thread传递上下文
5. **资源控制**: 限制同时running任务数（3-5个）

---

## 八、未来扩展 / Future Extensions

1. **Agent能力自学习**: 根据任务完成情况自动更新专家能力画像
2. **动态团队组建**: 根据任务复杂度动态组建临时团队
3. **多租户支持**: 不同用户/项目的Agent团队隔离
4. **外部Agent接入**: 支持Claude Code、Codex等外部Agent作为专家
5. **可视化面板**: 实时展示Agent团队工作状态

---

*Powered by Hermes Agent | Building open source daily 🚀*
