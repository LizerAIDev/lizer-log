#!/usr/bin/env python3
"""
Reviewer Scanner — 混合扫描器（CLI + Python API）
用于 multi-agent-reviewer Cron Job

扫描逻辑:
1. CLI 快速扫描: done 任务 → 常规质量审查
2. Python 深度扫描: blocked 任务 → 分析 review-required / 专家拒绝 → 重路由
3. triage 任务 → 通知 Coordinator 需要细化

输出: 结构化的审查报告，供 Cron Agent 后续处理
"""

import json
import subprocess
import re
import sys
from datetime import datetime, timezone


def run_cmd(cmd: str) -> str:
    """执行 shell 命令并返回 stdout"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()


def parse_kanban_list() -> list[dict]:
    """解析 hermes kanban list 输出为结构化数据"""
    output = run_cmd("hermes kanban list 2>&1")
    tasks = []
    for line in output.splitlines():
        # Format: [icon] task_id  status  assignee  title
        # icon: ✓ (done), ? (triage), ⏳ (running), 🚫 (blocked), etc.
        match = re.match(r'^(.)\s+(t_\w+)\s+(\w+)\s+(.+?)\s{2,}(.+)$', line)
        if match:
            icon, task_id, status, assignee, title = match.groups()
            tasks.append({
                "icon": icon.strip(),
                "task_id": task_id,
                "status": status.strip(),
                "assignee": assignee.strip(),
                "title": title.strip(),
            })
    return tasks


def parse_kanban_stats() -> dict:
    """解析 hermes kanban stats 输出"""
    output = run_cmd("hermes kanban stats 2>&1")
    stats = {"by_status": {}, "by_assignee": {}}
    section = None
    for line in output.splitlines():
        if line.startswith("By status:"):
            section = "by_status"
        elif line.startswith("By assignee:"):
            section = "by_assignee"
        elif section and line.strip():
            parts = line.strip().split()
            if len(parts) >= 2:
                if section == "by_status":
                    # Format: "triage    1"
                    stats[section][parts[0]] = int(parts[-1])
                else:
                    # Format: "default               done=2"
                    # or "dev                   done=8"
                    assignee = parts[0]
                    if assignee not in stats[section]:
                        stats[section][assignee] = {}
                    for p in parts[1:]:
                        if "=" in p:
                            k, v = p.split("=", 1)
                            v_clean = v.rstrip(",;").strip()
                            if v_clean.isdigit():
                                stats[section][assignee][k] = int(v_clean)
    return stats


def get_task_detail(task_id: str) -> dict:
    """获取任务详情（含 events 和 comments）"""
    output = run_cmd(f"hermes kanban show {task_id} 2>&1")
    return {
        "task_id": task_id,
        "raw_output": output[:3000],  # 限制长度避免 token 爆炸
    }


def get_task_runs(task_id: str) -> list:
    """获取任务的执行历史"""
    output = run_cmd(f"hermes kanban runs {task_id} 2>&1")
    runs = []
    for line in output.splitlines():
        if "run #" in line.lower() or "run:" in line.lower():
            runs.append(line.strip())
    return runs


def analyze_blocked_tasks(tasks: list[dict]) -> list[dict]:
    """深度分析 blocked 任务，区分 review-required 和专家拒绝"""
    blocked_tasks = [t for t in tasks if t["status"] == "blocked"]
    results = []

    for task in blocked_tasks:
        detail = get_task_detail(task["task_id"])
        runs = get_task_runs(task["task_id"])

        # 分析 block 原因
        analysis = {
            "task_id": task["task_id"],
            "title": task["title"],
            "assignee": task["assignee"],
            "block_type": "unknown",
            "suggested_action": "",
            "detail_excerpt": detail["raw_output"][:500],
            "runs": runs,
        }

        raw = detail["raw_output"].lower()

        # 判断 block 类型
        if "review-required" in raw or "needs review" in raw or "needs eyes" in raw:
            analysis["block_type"] = "review-required"
            analysis["suggested_action"] = "reviewer_should_review_and_approve_or_request_changes"
        elif "not in my expertise" in raw or "not in my" in raw or "should be handled by" in raw:
            analysis["block_type"] = "expert-rejection"
            # 提取建议的专家
            match = re.search(r"handled by\s+(\w+)", raw)
            if match:
                analysis["suggested_expert"] = match.group(1)
            analysis["suggested_action"] = "reviewer_should_relabel_and_return_to_ready"
        elif "dependency" in raw or "waiting" in raw:
            analysis["block_type"] = "dependency-wait"
            analysis["suggested_action"] = "check_parent_task_status"
        else:
            analysis["block_type"] = "manual-block"
            analysis["suggested_action"] = "reviewer_should_investigate_and_decide"

        results.append(analysis)

    return results


def analyze_done_tasks(tasks: list[dict]) -> list[dict]:
    """快速扫描 done 任务，筛选需要审查的"""
    done_tasks = [t for t in tasks if t["status"] == "done"]
    results = []

    for task in done_tasks:
        detail = get_task_detail(task["task_id"])
        runs = get_task_runs(task["task_id"])

        analysis = {
            "task_id": task["task_id"],
            "title": task["title"],
            "assignee": task["assignee"],
            "review_status": "pending",  # pending / passed / needs_revision
            "detail_excerpt": detail["raw_output"][:500],
            "runs": runs,
        }

        # 检查是否已经有审查评论
        raw = detail["raw_output"].lower()
        if "审查通过" in raw or "review passed" in raw or "✅" in raw:
            analysis["review_status"] = "passed"
        elif "审查不通过" in raw or "review failed" in raw or "needs revision" in raw or "❌" in raw:
            analysis["review_status"] = "needs_revision"

        results.append(analysis)

    return results


def main():
    """主扫描流程"""
    print("=" * 60)
    print("REVIEW SCANNER — Multi-Agent Team Review Cycle")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Step 1: 获取全局统计
    print("\n📊 KANBAN STATS:")
    stats = parse_kanban_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # Step 2: 解析所有任务
    print("\n📋 ALL TASKS:")
    tasks = parse_kanban_list()
    print(f"Total tasks: {len(tasks)}")
    for t in tasks:
        print(f"  {t['icon']} {t['task_id']} [{t['status']}] {t['assignee']}: {t['title']}")

    # Step 3: 深度扫描 blocked 任务
    print("\n🔍 BLOCKED TASK ANALYSIS:")
    blocked_analysis = analyze_blocked_tasks(tasks)
    if blocked_analysis:
        print(f"Found {len(blocked_analysis)} blocked task(s):")
        for b in blocked_analysis:
            print(f"\n  🚫 {b['task_id']} ({b['block_type']})")
            print(f"     Assignee: {b['assignee']}")
            print(f"     Title: {b['title']}")
            print(f"     Action: {b['suggested_action']}")
            if "suggested_expert" in b:
                print(f"     Suggested Expert: {b['suggested_expert']}")
    else:
        print("  No blocked tasks.")

    # Step 4: 快速扫描 done 任务
    print("\n✅ DONE TASKS REVIEW STATUS:")
    done_analysis = analyze_done_tasks(tasks)
    if done_analysis:
        pending = [d for d in done_analysis if d["review_status"] == "pending"]
        passed = [d for d in done_analysis if d["review_status"] == "passed"]
        needs_revision = [d for d in done_analysis if d["review_status"] == "needs_revision"]
        print(f"  Pending review: {len(pending)}")
        print(f"  Already passed: {len(passed)}")
        print(f"  Needs revision: {len(needs_revision)}")

        if pending:
            print("\n  Tasks awaiting review:")
            for d in pending:
                print(f"    📝 {d['task_id']} ({d['assignee']}): {d['title']}")
    else:
        print("  No done tasks.")

    # Step 5: 扫描 triage 任务
    triage_tasks = [t for t in tasks if t["status"] == "triage"]
    if triage_tasks:
        print(f"\n⚠️ TRIAGE TASKS (need Coordinator attention):")
        for t in triage_tasks:
            print(f"  ? {t['task_id']}: {t['title']}")

    # Step 6: 输出 JSON 报告供 Cron Agent 处理
    print("\n📄 JSON REPORT:")
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "total_tasks": len(tasks),
        "blocked_analysis": blocked_analysis,
        "done_analysis": done_analysis,
        "triage_tasks": [{"task_id": t["task_id"], "title": t["title"]} for t in triage_tasks],
        "actions_needed": {
            "review_blocked": len(blocked_analysis),
            "review_done_pending": len([d for d in done_analysis if d["review_status"] == "pending"]),
            "triage_attention": len(triage_tasks),
        }
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return report


if __name__ == "__main__":
    main()
