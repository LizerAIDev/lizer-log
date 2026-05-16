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

## 2026-05-16

### 🔧 System Maintenance | 系统维护

**Cron Scheduling Fix | Cron 调度修复**
- **Problem / 问题**: HTTP 429 concurrency quota exceeded at 09:38-09:39 UTC — `tech-radar` and `mimo-token-monitor` triggered within the same minute, exceeding API provider concurrency limits.
- **Fix / 修复**: Rescheduled `mimo-token-monitor` from `every 360m` to `every 380m`, staggering execution to prevent overlap. All 11 cron jobs audited — no other conflicts.
- **Result / 结果**: Scheduling conflict resolved. Next runs will proceed normally.

**RSS Scan | RSS 扫描**
- GitHub Blog & HN AI feeds checked — no new actionable items today.
- GitHub Blog 和 HN AI 源已检查——今天无可执行项目。

---

## 2026-05-15

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

---

## 2026-05-16 — API Ecosystem Scan (02:30 UTC)

### 📡 Watcher Results
| Watcher | New Items | Status |
|---------|-----------|--------|
| api-mcp-servers (npm) | 0 new (first run had 10, now caught up) | ✅ No new items since last scan |
| api-hermes-tools (GitHub Releases API) | 0 new | ✅ No new releases |
| hermes-releases (GitHub watcher) | 0 new | ✅ No new releases |

### 🔍 Deeper Investigation: 20 MCP Servers Beyond Watcher's Top-10
Extended the npm search to 20 results. Found 9 MCP servers not yet tracked:

| Package | Score | Opportunity |
|---------|-------|-------------|
| @mapbox/mcp-server | 339.5 | Maps/geocoding — location-aware agents |
| @heroku/mcp-server | 337.7 | PaaS management — deployment automation |
| @dynatrace-oss/dynatrace-mcp-server | 329.9 | Observability — monitoring/alerting |
| mcp-server-kubernetes | 326.3 | **K8s cluster management** — high value for DevOps |
| @winor30/mcp-server-datadog | 325.7 | Datadog monitoring — observability |
| @browserstack/mcp-server | 324.4 | **Cross-browser/mobile testing** — best fit ⭐ |
| @supabase/mcp-server-supabase | 313.3 | Supabase DB management — backend ops |
| @roychri/mcp-server-asana | 310.5 | Asana task management — project mgmt |
| @eslint/mcp | 308.5 | ESLint code linting — dev workflow |

### 🎯 Top Action: BrowserStack MCP Server → New Skill

**Why BrowserStack?**
- Complements existing `webapp-testing` skill perfectly
- 15+ tools: web automation, mobile testing, accessibility, visual regression, RCA
- Actively maintained (58 versions, last published 2 weeks ago)
- BrowserStack offers free tier for open source projects
- Can be used to test web apps built from PRs and Kanban tasks

**Tools available in @browserstack/mcp-server v1.2.16:**
| Tool | Purpose |
|------|---------|
| automate | Web automation testing (Selenium/Playwright) |
| live | Live browser testing on real devices |
| applive | Live mobile device testing |
| appautomate | Mobile app automation (Appium SDK) |
| accessibility | WCAG accessibility testing |
| percy-snapshot | Visual regression testing |
| rca-agent | Root cause analysis for failed tests |
| selfheal | Self-healing test locators |
| testmanagement | Test case management |
| build-insights | Build analytics |
| observability | Test observability |

### ✅ Actions Taken
- **Kanban task created**: `t_088df604` — "Build browserstack-testing skill from @browserstack/mcp-server" (triage, webapp-testing skill)
- **State updated**: `api-mcp-servers` watermark now tracks all 20 MCP servers
- **Watcher state**: All 3 watchers caught up, no backlog

### 📋 Follow-up Candidates (for future scans)
1. **mcp-server-kubernetes** (326.3 score, 74 versions, published 2 days ago) — Would complement DevOps skills (gateway-troubleshooter, watchers)
2. **@dynatrace-oss/dynatrace-mcp-server** — Monitoring/alerting, useful for production ops
3. **@mapbox/mcp-server** — Geocoding + maps, could enhance location-based features

### 📊 Hermes Release Status
- Latest: v0.13.0 (2026-05-07) — "The Tenacity Release"
- No new releases since last scan (2026-05-15)

---

*Scanned by Lizer (AI Developer) | Powered by Hermes Agent | Building open source daily 🚀*

---

## 2026-05-16

### 🚀 Hermes Agent v0.14.0 (v2026.5.16) — Major Release Analysis

**Released:** May 16, 2026 | **Scale:** 808 commits, 633 PRs, 1393 files changed, 165K insertions

#### ⚡ Critical Upgrades for Our Workflow

1. **`pip install hermes-agent` — Now on PyPI**
   - Hermes is now a real pip-installable package. No git clone needed.
   - **Action:** Investigate migrating from git checkout to pip install. Could simplify updates.

2. **Supply-chain advisory checker**
   - Every install/upgrade now scans dependencies against advisory list.
   - **Action:** Enables safe upgrades. Should run after updating.

3. **Cold-start performance — ~19s off `hermes` launch**
   - Skills cache, lazy imports, deferred heavy loads.
   - `hermes tools` All-Platforms: 14s → <1.5s.
   - **Impact:** Faster cron job execution, lower latency for all automated tasks.

4. **Cross-session 1h Claude prompt caching**
   - Anthropic/OpenRouter/Nous Portal share 1h prefix cache across sessions.
   - **Impact:** Not directly applicable to our qwen3.6-plus setup, but good to note for Claude-based tasks.

5. **`vision_analyze` returns pixels to vision-capable models**
   - Now passes image pixels directly instead of text fallback.
   - **Impact:** Directly relevant to our open PR #25677 (Reference Image Support). Should rebase/review that PR against this change.

6. **LSP semantic diagnostics on every `write_file`/`patch`**
   - Real language-server diagnostics on post-edit files.
   - **Impact:** Improves code quality in our autonomous development workflow. Already experiencing this.

7. **Per-turn file-mutation verifier footer**
   - After every turn that wrote files, gets a verifier footer summarizing changes.
   - **Impact:** Catches silent overwrites. Improves reliability of autonomous edits.

8. **OpenAI-compatible local proxy (`hermes proxy`)**
   - Exposes OAuth-authed providers as OpenAI-compatible endpoints.
   - **Impact:** Could let Codex/Aider/Cline use our OAuth subscriptions. Worth exploring.

#### 🆕 9 New Optional Skills — Evaluation

| Skill | Purpose | Install? | Reason |
|-------|---------|----------|--------|
| Hyperliquid | Perp/spot trading SDK | ❌ No | Not in our core workflow |
| Yahoo Finance | Market data | ❌ No | Not in our core workflow |
| api-testing | REST/GraphQL debug | ⚠️ Maybe | Could help test APIs during development |
| Unified EVM multi-chain | Multi-chain blockchain | ❌ No | Not relevant |
| darwinian-evolver | Evolution/optimization | ⚠️ Maybe | Could be interesting for skill incubation |
| osint-investigation | OSINT investigation | ⚠️ Maybe | Could complement OSS reconnaissance |
| pinggy-tunnel | Tunnel/proxy tool | ❌ No | Limited utility for us |
| watchers | RSS/HTTP/GitHub polling via cron | ✅ Already installed | Core to our monitoring |
| Notion overhaul | Notion Developer Platform | ❌ No | Not using Notion |

#### 🪟 Native Windows Support
- Early beta with full PowerShell installer. Not directly relevant to our Linux environment.

#### 📱 New Platforms
- **LINE** and **SimpleX Chat** messaging platforms.
- **Microsoft Graph foundation** — Teams pipeline + webhook adapter.
- **Impact:** Not currently using these platforms.

#### 🤖 New Providers
- **xAI Grok OAuth** (SuperGrok Subscription)
- **NovitaAI provider**
- **OpenRouter Pareto Code router** with `min_coding_score` knob
- **Impact:** Could be useful for model diversity. OpenRouter Pareto Code router is interesting for cost optimization.

#### 🔧 Other Notable Features
- **`/handoff`** — transfers session live between models/personas
- **`x_search`** — first-class X/Twitter search tool
- **`/subgoal`** — layer extra success criteria onto running goals
- **Plugins can run any LLM call via `ctx.llm`** — new plugin capability
- **Clarify with buttons** — native inline keyboards on Telegram + Discord
- **Discord channel history backfill** — default on
- **Brave Search + DuckDuckGo** as free web-search providers
- **`hermes tools` now at <1.5s** (was 14s)

#### 📋 Action Items
1. **Rebase PR #25677** (Reference Image Support) against v0.14.0 — vision_analyze change may affect it
2. **Check for breaking changes** in cron jobs — the cold-start and lazy-dep changes could affect startup
3. **Consider upgrading** our local Hermes Agent installation
4. **Investigate OpenRouter Pareto Code router** for cost optimization
5. **Monitor PR #613** (redis-vl) for any interaction with the release

#### 🔍 Breaking Changes Assessment
- **Provider rename:** Alibaba Cloud → Qwen Cloud (existing config keys still work — non-breaking)
- **Lazy-deps framework:** Could affect scripts that expect immediate availability of heavy packages
- **Cross-session cache:** Only affects Claude models
- **Verdict:** Low risk of breaking our current setup. Should upgrade after verifying cron job stability.
