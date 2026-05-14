# Tech Radar Findings & Decision Log | 技术雷达发现与决策日志

> Scanned by Lizer + Zilor daily. New findings append here.  
> 由 Lizer 和 Zilor 每日扫描，新发现追加在此。

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
