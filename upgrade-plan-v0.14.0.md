# Hermes Agent v0.14.0 升级计划

> 生成时间: 2026-05-16 16:30 UTC
> 当前环境: Linux (alibaba-coding-plan / qwen3.6-plus)
> 分析来源: RELEASE_v0.14.0.md (Git commit a91a57fa5)
> 目标: 评估 15 个现有 cron jobs 的兼容性与升级路径

---

## 一、v0.14.0 Breaking Changes 总览

v0.14.0 "The Foundation Release" 是一次 **808 commits / 633 PRs** 的大版本更新。大多数变更是 **向后兼容** 的新增功能，但以下几项可能对现有 cron jobs 产生影响：

### 1.1 Provider 重命名

| 变更 | 旧配置 | 新配置 | 影响 |
|------|--------|--------|------|
| Alibaba Cloud → Qwen Cloud | `provider: alibaba-coding-plan` | `provider: alibaba-coding-plan` (兼容) | 配置 key 仍兼容，但 picker UI 已重命名 |

**结论**: 当前 config.yaml 中的 `provider: alibaba-coding-plan` 不受影响，release notes 明确说明 "Existing config keys still work."

### 1.2 工具签名变更

| 工具 | 变更内容 | 影响程度 |
|------|----------|----------|
| `vision_analyze` | 现在直接将像素传递给视觉模型（而非回退到文字描述） | 低 — 行为增强，签名不变 |
| `computer_use` | 后端切换至 `cua-driver`，支持非 Anthropic 提供商 | 低 — 无 cron job 使用此工具 |
| `video_generate` | 统一为可插拔 provider 后端 | 无影响 — 无 job 使用 |
| `x_search` | 新增工具，需要 OAuth/API key | 无影响 — 新增，非破坏性 |
| `write_file` / `patch` | 新增 LSP 语义诊断，自动报错 | **中** — 可能导致之前通过的编辑现在被标记错误 |

### 1.3 调度器 (Cron) 变更

| 变更 | 影响 |
|------|------|
| `deliver=all` 新增广播行为 | 无影响 — 当前所有 job 使用 `deliver: local` |
| 支持 name-based 查找 job | 无影响 — 新增功能 |
| 禁止 cron job 继承 `HERMES_SESSION_*` contextvars | **低** — 修复了 session 泄漏，理论上不影响 prompt/script |
| 提示注入检测覆盖 skill content | 无影响 — 现有 job 未使用 skills |

### 1.4 性能优化（非破坏性）

- 冷启动时间减少 ~19s
- `browser_console` 提速 180x
- `hermes tools` 从 14s → <1.5s
- Claude 跨会话 1h prefix 缓存

**结论**: 纯性能提升，不影响 cron job 行为。

### 1.5 安全加固

| 变更 | 影响 |
|------|------|
| sudo brute-force 阻断 | 可能影响依赖 sudo 的脚本 |
| `shell=True` 减少 | 可能影响需要 shell 展开的命令 |
| 凭据池 SSRF 防护 | 不影响现有 cron |

---

## 二、现有 Cron Jobs 逐项影响评估

共 **15 个 cron jobs**，逐项分析如下：

### 2.1 不受影响 (✅ 安全)

| Job ID | 名称 | 理由 |
|--------|------|------|
| e14ca326bb48 | lizer-daily-build | 纯 Python 脚本 + GitHub PR，不涉及变更的工具/配置 |
| 4f601ae9b735 | self-reflection | 纯文件读写操作，不涉及变更 |
| a5ff662b9989 | task-review | 使用 `hermes kanban` CLI，不涉及变更 |
| 44081eea22a9 | multi-agent-dispatcher | 使用 `hermes kanban` CLI，不涉及变更 |
| 2924afe2c30d | multi-agent-reviewer | 使用 `hermes kanban` CLI，不涉及变更 |
| b05fdd3190f3 | multi-agent-coordinator | 使用 `hermes kanban` CLI + git，不涉及变更 |
| 2843a83eeeca | task-deliverer | 使用 `send_message` + Python 脚本，不涉及变更 |

### 2.2 低风险 (⚠️ 需观察)

| Job ID | 名称 | 潜在风险 | 建议 |
|--------|------|----------|------|
| 4e05a5420f7d | kanban-auto-executor | 使用 `hermes kanban` CLI，CLI 行为可能有微调 | 升级后观察 1-2 个周期 |
| 87df9ffe55a6 | mimo-token-monitor | 使用 `gh api` + `curl`，不受影响；但当前已有 HTTP 429 错误 | 与 v0.14.0 无关，独立排查 |
| 6d83b97f07a3 | api-ecosystem | 使用 watchers 脚本 + GitHub API | 升级后观察 1 个周期 |

### 2.3 中等风险 (⚠️ 建议升级后测试)

| Job ID | 名称 | 潜在风险 | 建议 |
|--------|------|----------|------|
| c02639740a4f | pr-monitor | 使用 `watch_github.py` 脚本，路径 `~/.hermes/skills/devops/watchers/scripts/` — 该 skill 是 v0.14.0 新增的 (#21881) | **确认脚本路径是否变化**；如果技能安装路径变了，job 会失败 |
| 73004ee703b6 | tech-radar | 同上 — 依赖 `watch_rss.py` / `watch_http_json.py` 等脚本 | 同上 |
| 66b32db28fa9 | oss-recon | 同上 — 依赖 `watch_http_json.py` | 同上 |
| b46c23bde933 | repo-activity | 同上 — 依赖 `watch_github.py` | 同上 |
| aee78855b961 | skill-incubator | 使用 `skills` toolset；v0.14.0 新增了 `skill_view` 冲突拒绝逻辑 | 低风险，但建议验证 skills_list 是否正常 |

### 2.4 LSP 诊断影响评估

v0.14.0 的 `write_file` / `patch` 现在运行 LSP 语义诊断。影响：

- **影响范围**: 所有使用 `write_file` 或 `patch` 工具的 cron jobs
- **正面效果**: 会在编辑后立即发现语法错误，避免写入无效文件
- **潜在问题**: 如果某些 job 的 prompt 依赖"静默写入无效文件"的行为，现在会被拦截
- **实际风险**: 极低 — 这些 job 写入的都是 Markdown/Python，LSP 诊断会提升质量

---

## 三、已知问题（与 v0.14.0 无关）

升级前已存在的问题，需在升级后继续排查：

| Job | 问题 | 错误信息 |
|-----|------|----------|
| mimo-token-monitor | HTTP 429 并发限制 | `concurrency allocated quota exceeded` |
| tech-radar | HTTP 429 并发限制 | `concurrency allocated quota exceeded` |

这两个 job 的失败原因是 **API 并发配额超限**，与 v0.14.0 无关。建议：
- 增加间隔时间（从 380m / 60m 调整）
- 或调整 `enabled_toolsets` 减少并发

---

## 四、升级步骤

### 阶段 1: 升级前准备 (5 分钟)

```bash
# 1. 备份当前配置
cp /root/.hermes/config.yaml /root/.hermes/config.yaml.bak.$(date +%Y%m%d)

# 2. 备份 cron jobs 配置
hermes kanban list 2>/dev/null  # 或用 cronjob tool export
cp /root/.hermes/cron/jobs.json /root/.hermes/cron/jobs.json.bak.$(date +%Y%m%d)

# 3. 记录当前版本号
cat /root/.hermes/version 2>/dev/null || echo "unknown"
```

### 阶段 2: 执行升级 (10-15 分钟)

```bash
# 方案 A: 如果通过 pip 安装
pip install --upgrade hermes-agent

# 方案 B: 如果使用 git 部署
cd /usr/local/lib/hermes-agent
git pull origin main

# 升级后验证
hermes version
hermes doctor  # 检查所有连接正常
```

### 阶段 3: 升级后验证 (10 分钟)

```bash
# 1. 验证 provider 配置仍有效
hermes tools --list 2>/dev/null

# 2. 验证 cron jobs 状态
hermes kanban list 2>/dev/null

# 3. 验证 watchers 脚本路径
ls ~/.hermes/skills/devops/watchers/scripts/watch_github.py
ls ~/.hermes/skills/devops/watchers/scripts/watch_rss.py
ls ~/.hermes/skills/devops/watchers/scripts/watch_http_json.py

# 4. 测试 write_file LSP 诊断（确认行为变化）
echo "确认 LSP 诊断正常工作"
```

### 阶段 4: 观察期 (24-48 小时)

- 观察所有 cron jobs 的 `last_status` 是否保持 `ok`
- 特别关注使用 watchers 脚本的 4 个 jobs
- 如果 `write_file` / `patch` 开始报 LSP 错误，检查是否因依赖缺失导致

### 阶段 5: 回滚方案

```bash
# 如果升级后出现问题
cd /usr/local/lib/hermes-agent
git log --oneline -20  # 找到升级前的 commit
git reset --hard <previous-commit>

# 恢复配置（如需要）
cp /root/.hermes/config.yaml.bak.YYYYMMDD /root/.hermes/config.yaml
cp /root/.hermes/cron/jobs.json.bak.YYYYMMDD /root/.hermes/cron/jobs.json
```

---

## 五、v0.14.0 可利用的新特性

升级后可以立即利用的功能：

| 特性 | 适用 Job | 收益 |
|------|----------|------|
| Claude 跨会话 1h prefix 缓存 | 所有使用 Claude 模型的 jobs | 降低 token 成本，加快响应 |
| 冷启动 ~19s 优化 | 所有 cron jobs | 每次运行减少等待时间 |
| `deliver=all` | task-deliverer | 可同时推送 Telegram + Discord 等多平台 |
| Brave Search / DDGS 免费搜索 | tech-radar, oss-recon | 新增免费搜索后端，减少对付费 API 的依赖 |
| 平台断路器 | 所有 jobs | 单个平台故障不影响其他平台 |

---

## 六、决策建议

| 项目 | 建议 |
|------|------|
| **是否立即升级** | ✅ 推荐 — Breaking changes 极少，config key 兼容 |
| **升级窗口** | 今晚 22:00 UTC 之后（避开白天高频 job 运行） |
| **升级前必须做** | 备份 config.yaml + jobs.json |
| **升级后必须做** | 验证 watchers 脚本路径 |
| **需要修改的 jobs** | 0 个 — 所有 jobs 的 prompt/script 无需调整 |
| **风险等级** | 低 |

---

*文档生成: Lizer Research Agent*
*Powered by Hermes Agent | Building open source daily 🚀*
