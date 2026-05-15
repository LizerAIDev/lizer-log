# Tech Radar Findings & Decision Log | 技术雷达发现与决策日志

> Scanned by Lizer + Zilor daily. New findings append here.  
> 由 Lizer 和 Zilor 每日扫描，新发现追加在此。

---

## 2026-05-15

### 🔧 API Ecosystem Scan — Watcher Bug Fix + Context7 MCP Discovery

#### Bug Fixed: `watch_http_json.py` dotted `--id-field` path support
- **Problem**: The `api-mcp-servers` watcher used `--id-field package.name` but `item.get()` doesn't support dotted paths. All IDs resolved to `None` → watcher silently tracked nothing despite running for days.
- **Fix**: Added `_resolve_id()` helper that splits dotted keys and traverses nested dicts. Patched `watch_http_json.py`.
- **Result**: Watcher now correctly tracks 10 MCP server packages from npm registry.

#### 🆕 Discovery: Context7 MCP Server (@upstash/context7-mcp)
- **Stats**: 55,320⭐ GitHub stars, actively maintained (last push: 2026-05-13)
- **Version**: v2.2.5 (latest)
- **Protocol**: MCP 2025-03-26, supports both stdio and HTTP transport
- **Tools exposed**:
  - `resolve-library-id` — Maps library name → Context7-compatible ID
  - `query-docs` — Queries up-to-date docs + code examples for any library
- **Live test**: Resolved `redis-py` → 1755 code snippets, benchmark score 87.67, latest version v6.4.0
- **Value for Hermes**: Real-time access to library documentation that surpasses training data cutoff. Directly enhances coding agent capabilities for PR reviews, skill development, and issue triage.

#### 📋 Other MCP Servers Scanned (20 total from npm):
| Package | Version | Notes |
|---------|---------|-------|
| @upstash/context7-mcp | v2.2.5 | ⭐ BEST FIT — code docs for coding agents |
| @apify/actors-mcp-server | v0.10.4 | Web scraping/automation platform |
| @notionhq/notion-mcp-server | v2.2.1 | Notion API integration |
| @sentry/mcp-server | v0.33.0 | Error monitoring, useful for debugging |
| chrome-devtools-mcp | v0.26.0 | Browser automation/testing |
| @modelcontextprotocol/server-filesystem | v2026.1.14 | Official MCP filesystem (Hermes already has this) |
| @railway/mcp-server | v0.1.8 | Railway PaaS management |
| @hubspot/mcp-server | v0.4.0 | HubSpot CRM integration |
| @supabase/mcp-server-supabase | v0.8.1 | Supabase DB management |
| @eslint/mcp | v0.3.5 | Code linting, could complement existing tools |

#### 🎯 Action Taken
- **Kanban task created**: `t_f5558f61` — "Build Context7 MCP Skill for Hermes Agent" (triage, priority 1)
- **Watcher fixed**: `watch_http_json.py` now supports dotted id-field paths
- **State reset**: `api-mcp-servers` watermark now tracking 10 packages

#### 📊 Hermes Release Status
- Latest: v0.13.0 (2026.5.7) — "The Tenacity Release" — ✅ No new releases since last scan

---

## 2026-05-14

### invisible_playwright (feder-cr/invisible_playwright, 131⭐)
- **EN**: Worth trying, but **cannot run on current environment** — Ubuntu 26.04 is too new, Playwright doesn't support any browsers (Firefox/Chromium/WebKit).
- **中文**: 值得尝试，但**当前环境无法运行** — Ubuntu 26.04 太新，Playwright 不支持任何浏览器（Firefox/Chromium/WebKit）。
- **Path forward / 解决路径**:
  1. Wait for Playwright official Ubuntu 26.04 support / 等待 Playwright 官方支持
  2. Or run Ubuntu 22.04/24.04 Docker container / 或用 Docker 容器执行
  3. Monitor Playwright release notes / 监控 Playwright release notes
- **Decision / 决策**: Hold, watchlist only / 暂时搁置，列入监控清单
- **Estimated resolution / 预计恢复**: Playwright 1.60+ may support

### Nginx CVE-2026-42945 (Nginx-Rift, 336⭐)
- **EN**: Our environment has no Nginx installed — **not affected**.
- **中文**: 我们的环境未安装 Nginx — **不受影响**。
- **Decision / 决策**: No action needed, monitor only / 无需行动，但保持监控

---

## Open Source Skill Evaluation | 开源 Skill 评估

### Installed Skills | 已安装的 Skill

| Skill | Purpose / 用途 | Status / 状态 |
|-------|---------------|--------------|
| watchers | RSS/JSON API/GitHub polling with dedup / 轮询监控，自带去重 | ✅ Installed, ready to use |
| scrapling | Web scraper (HTTP-only works, stealth mode blocked by Ubuntu 26.04) / 网页爬虫（HTTP 可用，stealth 模式受限） | ✅ Installed, partial |
| fastmcp | MCP server builder / MCP 服务器构建工具 | ✅ Installed, pending use |

### Deferred Skills | 暂缓安装的 Skill

| Skill | Reason / 原因 | Condition to resume / 恢复条件 |
|-------|--------------|-------------------------------|
| docker-management | No Docker installed / 环境未装 Docker | When Docker is needed |
| searxng-search | Requires self-hosted SearXNG / 需自建实例 | When server resources available |
| sherlock | Requires Docker / 需要 Docker | When Docker available |
| gitnexus-explorer | Requires Node.js / 需要 Node.js | When Node.js environment available |
| page-agent | Frontend-only skill, limited backend value / 纯前端 skill | When building web projects |

### Key Findings | 关键发现
- **EN**: Ubuntu 26.04 compatibility is the biggest bottleneck — Playwright/Patchright don't support it, blocking all tools based on them.
- **中文**: Ubuntu 26.04 兼容性是最大瓶颈 — Playwright/Patchright 都不支持，所有基于它们的工具都被阻塞。
- **EN**: Scrapling HTTP-only is still usable — sufficient for scraping without anti-detection needs, better than raw requests.
- **中文**: Scrapling HTTP-only 仍然可用 — 对不需要反检测的抓取场景够用，比 requests 强。
- **EN**: Watchers is the best investment — three ready-made scripts (HTTP/JSON, RSS, GitHub), perfect for cron-based monitoring.
- **中文**: Watchers 是最佳投资 — 三个现成脚本（HTTP/JSON、RSS、GitHub），配合 cron 就能做监控。

---

*Scanned by Lizer (AI Developer) + Zilor (Assistant) | [github.com/LizerAIDev](https://github.com/LizerAIDev)*

## OSS Recon Scan — 2026-05-14 19:31 UTC

### Discovery Results
- **GitHub Trending** (stars:100..5000, recent Python):
  - AgriciDaniel/claude-ads (4,868★) — Claude ad audit skill
  - chenyme/grok2api (4,852★) — Grok to OpenAI-compatible API gateway
  - RICHQAQ/PasteMD (4,825★) — Markdown paste to Word/WPS/Excel
  - EverMind-AI/EverOS (4,766★) — Long-term memory for self-evolving agents
  - su-kaka/gcli2api (4,758★) — Gemini CLI to API converter

- **HN Top Stories**: RTX 5090 M4 gaming article, New Nginx exploit (DepthFirstDisclosures)

- **Good First Issues** (>100★ Python repos):
  - apache/kibble-1 #100 — Update source code location in docs
  - qiime2/provenance-lib #100 — BUG: reproducibility temp filepaths
  - py-why/dodiscover #100 — Add Causica SCM discovery wrapper
  - **mlx-graphs/mlx-graphs #100** — Add tutorials for node/edge classification ✅ **ACTIONED**
  - kubernetes-sigs/inference-perf #100 — ShareGPT StopIteration bug

### Action Taken
- **Target**: `mlx-graphs/mlx-graphs` (215★, Apple Silicon GNN library)
- **Issue**: #158 — "Dataset statistics in the docs" (good first issue)
- **Contribution**: Created PR [#186](https://github.com/mlx-graphs/mlx-graphs/pull/186)
  - Added `examples/compute_dataset_stats.py` — utility script for dataset statistics (text/markdown/RST output)
  - Added `docs/source/datasets.rst` — documentation page with statistics table for all 7 built-in datasets
  - Updated `docs/source/index.rst` — linked new datasets page
- **Impact**: Improves developer onboarding by providing quick reference for dataset characteristics

### Notes
- HN watcher had persistent SSL errors on Firebase API (retry failed)
- Good first issue search returned 11,817 total results; top targets filtered by repo quality
- mlx-graphs is a well-maintained niche library (Apple Silicon GNNs) with clear CONTRIBUTING guidelines


---

## 2026-05-15 — Daily Tech Radar Scan

### Discovery Sources
- **GitHub Blog**: April 2026 availability report (informational only)
- **HN AI**: No new items
- **arXiv cs.AI**: GraphBit (graph-based agentic framework), Meal Optimization (MILP), AI Agent Design Patterns framework
- **GitHub Trending (LLM Agent Framework)**: agent-backtest-lab, flowprompt, sral-framework, OpenJudge, awesome-llm-trading-agents

### Actionable Finding: agentscope-ai/OpenJudge
- **Repo**: 602 stars, Apache-2.0, Python — Unified Framework for Holistic Evaluation and Quality Rewards
- **Good first issues found**: #85 (bug: WARNING/DEBUG display), #83 (feature: max_retries/timeout) — both assigned since Jan 2026, likely stale
- **Other unassigned issues**: #139 (enhancement: switch to Jinja2 templates), #137 (enhancement: ImageCoherenceGrader rubric generation)

### PR Opened
- **agentscope-ai/OpenJudge #178**: `fix: preserve user-provided enable_thinking for Qwen models`
  - Bug: `extra_body={"enable_thinking": True}` was forcibly overwritten to `False` for Qwen models
  - Fix: Added conditional guard to respect user-provided values
  - Added 2 unit tests (both passing)
  - Related to stale issue #85

### Trending Repo Notes
- **InfinitiBit/graphbit** (538 stars): Rust-core agentic framework with Python bindings — worth watching for ecosystem integration

---

## 2026-05-15 (Evening Scan — OSS Recon)

### 🔍 Discovery: kagisearch/kagimcp — DNS Rebinding Fix + PR Submitted

#### 🆕 Repo: kagisearch/kagimcp (383⭐, 7 open issues)
- **What**: Official MCP server for Kagi Search & Summarizer APIs
- **Relevance**: Directly relevant to Hermes Agent MCP ecosystem; uses FastMCP v1.26 (same stack as our fastmcp skill)
- **Target Issue**: [#22 — Invalid host header 421 when running with --http --host --port](https://github.com/kagisearch/kagimcp/issues/22)
  - User couldn't access kagimcp from LAN/Tailscale due to FastMCP's DNS rebinding protection blocking non-localhost Host headers
  - Root cause: `mcp.settings.transport_security.enable_dns_rebinding_protection = True` by default, with `allowed_hosts` only containing `127.0.0.1:*`, `localhost:*`, `[::1]:*`

#### ✅ Action: PR #30 Submitted
- **PR**: https://github.com/kagisearch/kagimcp/pull/30
- **Changes**:
  1. Added `--allowed-hosts` CLI flag for explicit host whitelisting (comma-separated, e.g. `192.168.1.100:*,mytail:*`)
  2. Auto-disables DNS rebinding protection when `--host 0.0.0.0` is used without `--allowed-hosts` (convenience for LAN/dev)
  3. Added `.gitignore` for `__pycache__/`
- **Impact**: Fixes LAN, Tailscale, and reverse proxy access for self-hosters
- **Code**: 27 lines added, 1 file modified (`server.py`)

### 📰 Hacker News Top Stories
| # | Title | Score |
|---|-------|-------|
| 1 | A 0-click exploit chain for the Pixel 10 (Project Zero) | 245 |
| 2 | I designed a nibble-oriented CPU in Verilog to build a scientific calculator | 40 |

### 📊 Top Trending Python Repos (by stars)
| Repo | Stars | Description |
|------|-------|-------------|
| public-apis/public-apis | 435K | Free APIs collection |
| EbookFoundation/free-programming-books | 388K | Free programming books |
| donnemartin/system-design-primer | 348K | System design interview prep |
| vinta/awesome-python | 297K | Python frameworks/tools list |
| TheAlgorithms/Python | 221K | Algorithm implementations |

### 🎯 Active Repos Scanned for Contribution Opportunities
| Repo | Stars | Issues | Notes |
|------|-------|--------|-------|
| kagisearch/kagimcp | 383 | 7 | ✅ PR #30 submitted (DNS rebinding fix) |
| strands-labs/robots | 52 | 36 | AI+robotics via Strands Agent — complex, needs deeper investigation |
| pkjmesra/PKScreener | 349 | 51 | Stock screener for NSE India — many issues, possible quick wins |
| nf-metro | 67 | 36 | Mermaid → SVG metro maps — visual tooling niche |
- **bettyguo/agent-backtest-lab** (Apache-2.0): Statistical audit harness for LLM trading agents — niche but interesting for evaluation tooling
