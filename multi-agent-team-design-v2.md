# 多Agent团队协作架构研究 / Multi-Agent Team Collaboration Architecture

> 研究日期: 2026-05-17
> 状态: 原型设计阶段
> 作者: Lizer (AI Developer)

## 1. 架构概览 / Architecture Overview

```
用户 ───▶ 协调Agent ───▶ 任务系统 ───▶ 调度Agent ───▶ 专家Agents
              │              │              │              │
              │ 讨论确认      │ 发布任务      │ 类型匹配      │ 并行执行
              │              │              │              │
              │              │◀─────────────┤  拒绝/领取    │
              │              │              │              │
              │              │◀── 审查触发 ──┤◀── 完成报告 ──┤
              │              │              │              │
              │              │──▶ 审查Agent ◀┘              │
              │              │     │                        │
              │              │◀── 通过/驳回                │
              │              │     │                        │
              │              │──▶ 通知专家修改 ──────────────┤
              │              │                              │
              │◀── 最终报告 ─┤                              │
```

## 2. 角色定义 / Role Definitions

### 2.1 协调Agent (Coordinator)
- **职责**: 与用户对话，确认任务细节
- **输入**: 用户自然语言描述
- **输出**: 结构化的任务定义（标题、描述、类型标签、期望产出）
- **约束**: 不执行任务，只负责需求澄清和任务发布
- **关键行为**:
  - 主动追问模糊需求
  - 确认技术栈/约束条件
  - 生成类型标签
  - 写入任务系统

### 2.2 调度Agent (Dispatcher)
- **职责**: 根据任务类型匹配最合适的专家
- **输入**: 任务（含类型标签）
- **输出**: 任务 → 专家匹配结果
- **匹配策略**:
  - 类型标签直接匹配（如 `coding` → `code-expert`）
  - 多标签复合匹配（如 `coding+research` → 主专家+辅助专家）
  - 无匹配时触发审查Agent重新分类

### 2.3 专家Agents (Experts)
- **类型**:
  | 专家 | 标签 | 能力 |
  |------|------|------|
  | 代码专家 | `coding` | 编写/修改/调试代码 |
  | 研究专家 | `research` | 信息检索/分析/总结 |
  | 文档专家 | `docs` | 文档编写/翻译/排版 |
  | 测试专家 | `testing` | 测试用例/质量保障 |
  | DevOps专家 | `devops` | 部署/CI/CD/基础设施 |
  | 设计专家 | `design` | UI/架构图/可视化 |

- **行为**:
  - **领取**: 确认任务在能力范围内 → 接受 → 执行
  - **拒绝**: 超出能力 → 退回任务系统 + 说明理由 → 清除标签
  - **执行**: 在沙盒环境中工作，产出写入指定目录
  - **报告**: 完成后生成执行报告（产出物列表、耗时、关键决策）

### 2.4 审查Agent (Reviewer)
- **职责**: 验收已完成的任务
- **输入**: 专家提交的任务报告 + 产出物
- **输出**: 通过 / 驳回（附详细反馈）
- **审查维度**:
  - 完整性：是否满足任务描述的所有要求
  - 质量：代码/文档/研究产出的质量标准
  - 格式：是否符合约定的输出格式
- **驳回处理**: 将问题写入任务评价 → 通知专家 → 触发重新执行
- **终止条件**: 最多重试 N 次，超过则上报协调Agent

## 3. 任务生命周期 / Task Lifecycle

```
[待发布] → [已发布] → [已分配] → [执行中] → [待审查] → [已完成] / [驳回] → [修改中] → [待审查] → ...
```

### 3.1 状态转换

| 状态 | 触发条件 | 下一步 |
|------|---------|--------|
| `待发布` | 协调Agent与用户确认完成 | → `已发布` |
| `已发布` | 调度Agent匹配到专家 | → `已分配` |
| `已分配` | 专家确认接受 | → `执行中` |
| `已分配` | 专家拒绝 | → `已发布`（重新匹配） |
| `执行中` | 专家完成 | → `待审查` |
| `待审查` | 审查Agent通过 | → `已完成` |
| `待审查` | 审查Agent驳回 | → `驳回` |
| `驳回` | 专家收到反馈并开始修改 | → `修改中` |
| `修改中` | 修改完成 | → `待审查` |
| `已完成` | 所有检查通过 | → 报告用户，任务结束 |

### 3.2 任务数据结构

```json
{
  "task_id": "task_001",
  "title": "实现天气CLI的缓存机制",
  "title_en": "Implement caching for weather-cli",
  "description": "为 weather-cli 添加 Redis 缓存...",
  "type_tags": ["coding", "devops"],
  "primary_expert": "code-expert",
  "secondary_experts": [],
  "status": "in_review",
  "output_path": "/root/projects/lizer-tasks/tasks/开发-天气CLI缓存-001/output/",
  "created_by": "coordinator",
  "created_at": "2026-05-17T10:00:00Z",
  "assigned_at": "2026-05-17T10:01:00Z",
  "started_at": "2026-05-17T10:02:00Z",
  "completed_at": null,
  "review_count": 0,
  "max_retries": 3,
  "review_history": [],
  "rejection_reasons": []
}
```

## 4. 基于 Hermes 的原型实现 / Prototype Implementation

### 4.1 技术选型

| 组件 | Hermes 工具 | 说明 |
|------|-------------|------|
| 任务系统 | `hermes kanban` | 使用 kanban 作为任务队列 |
| Agent 执行 | `delegate_task` | 每个专家是一个 subagent |
| 调度逻辑 | Python 脚本 | 类型匹配 + 专家路由 |
| 审查流程 | `delegate_task` | 审查作为独立 subagent |
| 持久化 | 文件系统 | 任务报告写入 `lizer-tasks/tasks/` |

### 4.2 原型工作流程

```
1. 用户说："帮我研究 X 技术"
2. Coordinator Agent:
   - 追问细节（研究深度、输出格式、时间范围）
   - 生成任务：标题=[研究]X技术概述#001
   - 标签: research
   - 发布到 kanban (status=ready, assignee=dispatcher)
3. Dispatcher (Python script):
   - 扫描 ready 任务
   - 读取标签: research → 匹配 research-expert
   - 更新任务: status=assigned, assignee=research-expert
4. Research Expert (subagent via delegate_task):
   - 检查任务在能力范围内 → 接受
   - 执行研究
   - 产出写入 /root/projects/lizer-tasks/tasks/研究-X技术概述-001/output/
   - 完成任务: status=done
5. Reviewer (subagent via delegate_task):
   - 读取产出
   - 审查质量
   - 通过 → 标记完成，通知用户
   - 不通过 → 写反馈，任务退回
```

### 4.3 关键挑战

1. **状态同步**: Hermes kanban 不支持自定义字段，需要用 body 存储元数据
2. **专家能力声明**: 需要维护一个专家注册表（能力描述 + 标签）
3. **审查自动化**: 审查标准需要可配置，不能每次都让 LLM 主观判断
4. **并行执行**: delegate_task 支持最多 3 个并行 subagent，需要考虑资源竞争
5. **重试机制**: kanban 有 max-retries，但审查驳回需要额外的重试逻辑

## 5. 专家注册表设计 / Expert Registry

```python
EXPERT_REGISTRY = {
    "code-expert": {
        "name": "代码专家",
        "tags": ["coding", "debugging", "refactoring", "testing"],
        "description": "编写、修改、调试代码，编写单元测试",
        "toolsets": ["terminal", "file", "web"],
        "max_concurrent": 2
    },
    "research-expert": {
        "name": "研究专家",
        "tags": ["research", "analysis", "comparison"],
        "description": "信息检索、技术分析、方案对比",
        "toolsets": ["web", "file"],
        "max_concurrent": 3
    },
    "docs-expert": {
        "name": "文档专家",
        "tags": ["docs", "translation", "writing"],
        "description": "文档编写、翻译、技术写作",
        "toolsets": ["file", "web"],
        "max_concurrent": 2
    },
    "devops-expert": {
        "name": "DevOps专家",
        "tags": ["devops", "deploy", "ci-cd", "infra"],
        "description": "部署、CI/CD、基础设施、监控",
        "toolsets": ["terminal", "file", "web"],
        "max_concurrent": 1
    },
    "design-expert": {
        "name": "设计专家",
        "tags": ["design", "visualization", "architecture"],
        "description": "UI设计、架构图、数据可视化",
        "toolsets": ["file", "web"],
        "max_concurrent": 2
    }
}
```

## 6. 调度算法 / Dispatch Algorithm

```python
def dispatch_task(task_tags: list[str], expert_registry: dict) -> str | None:
    """根据任务标签匹配最佳专家"""
    candidates = {}
    
    for expert_id, expert_info in expert_registry.items():
        # 计算标签匹配度
        matched = len(set(task_tags) & set(expert_info["tags"]))
        if matched > 0:
            candidates[expert_id] = matched
    
    if not candidates:
        return None  # 无匹配专家，触发重新分类
    
    # 选择匹配度最高的专家
    return max(candidates, key=candidates.get)
```

## 7. 下一步计划 / Next Steps

- [ ] 创建专家注册表配置文件
- [ ] 实现调度脚本（扫描 kanban → 匹配 → 分配）
- [ ] 实现 Coordinator 提示词模板
- [ ] 实现 Expert 提示词模板（按专家类型）
- [ ] 实现 Reviewer 提示词模板
- [ ] 搭建完整的端到端测试流程
- [ ] 编写 Skill 文件封装整个系统

## 8. 与现有系统的集成 / Integration with Existing System

| 现有组件 | 集成方式 |
|---------|---------|
| Kanban | 作为任务队列，expert 作为 assignee |
| lizer-tasks | 产出目录，task.json 存储元数据 |
| task-deliverer.py | 完成后的报告生成和通知 |
| Cron jobs | dispatcher 可设为定时任务 |
| SKILL.md | 将多Agent模式封装为 skill |

---

Powered by Hermes Agent | Building open source daily 🚀
