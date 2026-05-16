#!/usr/bin/env python3
"""
Dispatch Scanner — 智能调度扫描器（负载均衡 + 优先级 + 依赖管理）
用于 multi-agent-dispatcher Cron Job

核心能力:
1. 负载均衡: 根据专家当前工作负载分配任务（running 任务少的优先）
2. 任务优先级: 高优先级任务优先调度，同优先级按创建时间 FIFO
3. 依赖管理: 检查任务依赖链，未满足依赖的任务延迟调度

输出: 结构化的调度建议报告
"""

import json
import subprocess
import re
import sys
from datetime import datetime, timezone
from collections import defaultdict


def run_cmd(cmd: str) -> str:
    """执行 shell 命令并返回 stdout"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()


def parse_kanban_list() -> list[dict]:
    """解析 hermes kanban list 输出"""
    output = run_cmd("hermes kanban list 2>&1")
    tasks = []
    for line in output.splitlines():
        match = re.match(r'^(.)\s+(t_\w+)\s+(\w+)\s+(.+?)\s{2,}(.+)$', line)
        if match:
            icon, task_id, status, assignee, title = match.groups()
            tasks.append({
                "icon": icon.strip(),
                "task_id": task_id,
                "status": status.strip(),
                "assignee": assignee.strip().rstrip(),
                "title": title.strip(),
            })
    return tasks


def parse_assignees() -> dict:
    """解析专家列表和当前状态"""
    output = run_cmd("hermes kanban assignees 2>&1")
    assignees = {}
    for line in output.splitlines():
        # Format: "NAME                  ON DISK   COUNTS"
        #         "dev                   yes       done=8"
        #         "coordinator           yes       (idle)"
        match = re.match(r'^(\S+)\s+(yes|no)\s+(.+)$', line)
        if match:
            name, on_disk, counts = match.groups()
            if on_disk == "yes" and name not in ("default", "monitor"):
                status = counts.strip()
                # Parse counts like "done=8" or "(idle)" or "running=2 done=5"
                count_dict = {}
                for pair in re.findall(r'(\w+)=(\d+)', status):
                    count_dict[pair[0]] = int(pair[1])
                assignees[name] = {
                    "on_disk": True,
                    "counts": count_dict,
                    "running_count": count_dict.get("running", 0),
                    "total_done": count_dict.get("done", 0),
                    "is_idle": "idle" in status.lower(),
                }
    return assignees


def get_task_detail(task_id: str) -> str:
    """获取任务详情"""
    return run_cmd(f"hermes kanban show {task_id} 2>&1")


def get_task_runs(task_id: str) -> str:
    """获取任务执行历史"""
    return run_cmd(f"hermes kanban runs {task_id} 2>&1")


def extract_type_label(title: str, body: str) -> str:
    """从标题或正文中提取类型标签"""
    # Title prefix: [code], [research], [design], etc.
    match = re.match(r'^\[(\w+)\]\s', title)
    if match:
        return match.group(1).lower()

    # Body: type: code, type: research, etc.
    match = re.search(r'type:\s*(\w+)', body, re.IGNORECASE)
    if match:
        return match.group(1).lower()

    return "unknown"


def extract_priority(body: str) -> str:
    """从正文中提取优先级"""
    match = re.search(r'priority:\s*(high|medium|low)', body, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return "medium"  # Default


def extract_dependencies(detail: str) -> list[str]:
    """从任务详情中提取父任务依赖"""
    parents = []
    # In task header: "parents:   t_abc123"
    match = re.search(r'parents:\s*(.+)', detail)
    if match:
        parent_str = match.group(1).strip()
        if parent_str and parent_str != "[]":
            parents = [p.strip() for p in parent_str.split(",")]

    # Also check events for parent info
    events_match = re.search(r"created\s+\{.*?'parents':\s*\[(.*?)\]", detail, re.DOTALL)
    if events_match and not parents:
        parent_str = events_match.group(1).strip().strip("'")
        if parent_str:
            parents = [p.strip().strip("'") for p in parent_str.split(",")]

    return parents


def extract_created_time(detail: str) -> str:
    """提取任务创建时间"""
    match = re.search(r'created:\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', detail)
    return match.group(1) if match else ""


TYPE_TO_PROFILES = {
    "code": ["dev"],
    "research": ["researcher"],
    "design": ["designer"],
    "ui": ["designer"],
    "ux": ["designer"],
    "frontend": ["designer"],
    "docs": ["writer"],
    "writing": ["writer"],
    "tutorial": ["writer"],
    "api-docs": ["writer"],
    "data": ["data-scientist"],
    "ml": ["data-scientist"],
    "analysis": ["data-scientist"],
    "visualization": ["data-scientist"],
    "devops": ["devops"],
    "infrastructure": ["devops"],
    "ci-cd": ["devops"],
    "deployment": ["devops"],
}


def get_candidate_profiles(type_label: str) -> list[str]:
    """根据类型标签获取候选专家列表"""
    return TYPE_TO_PROFILES.get(type_label, [])


def calculate_workload_score(assignees: dict, profile_name: str) -> dict:
    """计算专家的工作负载分数（越低越空闲）"""
    info = assignees.get(profile_name, {})
    running = info.get("running_count", 0)
    is_idle = info.get("is_idle", True)

    # Score: running tasks * 10 (heavy penalty), idle = 0
    score = running * 10
    if is_idle:
        score = 0

    return {
        "profile": profile_name,
        "running": running,
        "is_idle": is_idle,
        "score": score,
    }


def check_dependencies_met(parent_ids: list[str], all_tasks: list[dict]) -> dict:
    """检查依赖是否已满足"""
    task_map = {t["task_id"]: t for t in all_tasks}
    results = []
    all_met = True

    for pid in parent_ids:
        task = task_map.get(pid)
        if not task:
            results.append({
                "parent_id": pid,
                "status": "not_found",
                "met": False,
            })
            all_met = False
        elif task["status"] == "done":
            results.append({
                "parent_id": pid,
                "status": "done",
                "met": True,
            })
        else:
            results.append({
                "parent_id": pid,
                "status": task["status"],
                "met": False,
            })
            all_met = False

    return {"dependencies": results, "all_met": all_met}


def priority_rank(priority: str) -> int:
    """优先级排序值（数字越大优先级越高）"""
    return {"high": 3, "medium": 2, "low": 1}.get(priority, 2)


def generate_dispatch_plan(tasks: list[dict], assignees: dict) -> dict:
    """生成完整的调度计划"""
    ready_tasks = [t for t in tasks if t["status"] == "ready"]
    running_tasks = [t for t in tasks if t["status"] == "running"]
    blocked_tasks = [t for t in tasks if t["status"] == "blocked"]
    todo_tasks = [t for t in tasks if t["status"] == "todo"]

    plan = {
        "ready_tasks": [],
        "promotable_from_todo": [],
        "blocked_on_deps": [],
        "running_now": [],
        "load_distribution": {},
        "recommendations": [],
    }

    # Helper: analyze a single task for dispatch readiness
    def analyze_task_for_dispatch(task: dict) -> tuple[dict | None, bool]:
        """Returns (task_info, is_blocked_on_deps)"""
        detail = get_task_detail(task["task_id"])
        task_type = extract_type_label(task["title"], detail)
        priority = extract_priority(detail)
        parents = extract_dependencies(detail)
        created = extract_created_time(detail)

        task_info = {
            "task_id": task["task_id"],
            "title": task["title"],
            "type": task_type,
            "priority": priority,
            "priority_rank": priority_rank(priority),
            "created": created,
            "candidates": get_candidate_profiles(task_type),
        }

        # Check dependencies
        if parents:
            dep_check = check_dependencies_met(parents, tasks)
            task_info["dependencies"] = dep_check
            if not dep_check["all_met"]:
                return task_info, True

        # Calculate load for each candidate
        workloads = []
        for profile in task_info["candidates"]:
            wl = calculate_workload_score(assignees, profile)
            workloads.append(wl)

        workloads.sort(key=lambda x: x["score"])
        task_info["workloads"] = workloads
        task_info["recommended_profile"] = workloads[0]["profile"] if workloads else None

        return task_info, False

    # Analyze ready tasks
    for task in ready_tasks:
        task_info, blocked = analyze_task_for_dispatch(task)
        if task_info:
            if blocked:
                plan["blocked_on_deps"].append(task_info)
            else:
                plan["ready_tasks"].append(task_info)

    # Check todo tasks - if deps are met, they can be promoted to ready
    for task in todo_tasks:
        detail = get_task_detail(task["task_id"])
        parents = extract_dependencies(detail)
        if parents:
            dep_check = check_dependencies_met(parents, tasks)
            if dep_check["all_met"]:
                # Dependencies met! Can be promoted
                task_info, _ = analyze_task_for_dispatch(task)
                if task_info:
                    plan["promotable_from_todo"].append(task_info)
            else:
                task_info, _ = analyze_task_for_dispatch(task)
                if task_info:
                    plan["blocked_on_deps"].append(task_info)

    # Sort ready tasks by priority (high first), then by creation time (FIFO)
    plan["ready_tasks"].sort(
        key=lambda t: (-t["priority_rank"], t["created"])
    )

    # Running tasks summary
    for task in running_tasks:
        plan["running_now"].append({
            "task_id": task["task_id"],
            "title": task["title"],
            "assignee": task["assignee"],
        })

    # Load distribution
    for profile, info in assignees.items():
        plan["load_distribution"][profile] = {
            "running": info.get("running_count", 0),
            "is_idle": info.get("is_idle", True),
            "total_done": info.get("total_done", 0),
        }

    # Recommendations
    for task_info in plan["ready_tasks"]:
        if task_info["recommended_profile"]:
            rec = {
                "action": "dispatch",
                "task_id": task_info["task_id"],
                "profile": task_info["recommended_profile"],
                "reason": f"Type: {task_info['type']}, Priority: {task_info['priority']}, "
                          f"Load: lowest ({task_info['workloads'][0]['running']} running)",
            }
            plan["recommendations"].append(rec)

    for task_info in plan["promotable_from_todo"]:
        if task_info["recommended_profile"]:
            rec = {
                "action": "promote_and_dispatch",
                "task_id": task_info["task_id"],
                "profile": task_info["recommended_profile"],
                "reason": f"Dependencies met, ready to promote from todo → ready",
            }
            plan["recommendations"].append(rec)

    for task_info in plan["blocked_on_deps"]:
        unmet = [d["parent_id"] for d in task_info["dependencies"]["dependencies"] if not d["met"]]
        plan["recommendations"].append({
            "action": "wait_for_deps",
            "task_id": task_info["task_id"],
            "waiting_on": unmet,
            "reason": f"Dependencies not met: {', '.join(unmet)}",
        })

    return plan


def main():
    """主调度流程"""
    print("=" * 60)
    print("DISPATCH SCANNER — Smart Scheduling (Load + Priority + Deps)")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Step 1: Get all tasks and assignees
    tasks = parse_kanban_list()
    assignees = parse_assignees()

    print(f"\n📋 Total tasks: {len(tasks)}")
    print(f"👥 Expert profiles: {len(assignees)}")

    # Step 2: Generate dispatch plan
    plan = generate_dispatch_plan(tasks, assignees)

    # Step 3: Print plan
    print("\n📊 LOAD DISTRIBUTION:")
    for profile, load in plan["load_distribution"].items():
        status = "🟢 idle" if load["is_idle"] else f"🔴 {load['running']} running"
        print(f"  {profile}: {status} (done: {load['total_done']})")

    if plan["ready_tasks"]:
        print(f"\n🚀 READY TASKS ({len(plan['ready_tasks'])} tasks, sorted by priority):")
        for t in plan["ready_tasks"]:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t["priority"], "⚪")
            print(f"  {emoji} {t['task_id']} [{t['type']}/{t['priority']}] {t['title']}")
            print(f"     → Recommended: {t['recommended_profile']}")
            if t["workloads"]:
                for w in t["workloads"]:
                    marker = " ← BEST" if w["profile"] == t["recommended_profile"] else ""
                    print(f"       {w['profile']}: running={w['running']}, idle={w['is_idle']}{marker}")

    if plan["blocked_on_deps"]:
        print(f"\n⏳ BLOCKED ON DEPENDENCIES ({len(plan['blocked_on_deps'])} tasks):")
        for t in plan["blocked_on_deps"]:
            unmet = [d["parent_id"] for d in t["dependencies"]["dependencies"] if not d["met"]]
            print(f"  ⏸️  {t['task_id']} → waiting for: {', '.join(unmet)}")

    if plan["promotable_from_todo"]:
        print(f"\n📤 PROMOTABLE TO READY ({len(plan['promotable_from_todo'])} tasks, deps met):")
        for t in plan["promotable_from_todo"]:
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t["priority"], "⚪")
            print(f"  {emoji} {t['task_id']} [{t['type']}/{t['priority']}] {t['title']}")
            print(f"     → Recommended: {t['recommended_profile']}")

    if plan["running_now"]:
        print(f"\n▶️ RUNNING NOW ({len(plan['running_now'])} tasks):")
        for t in plan["running_now"]:
            print(f"  ▶ {t['task_id']} ({t['assignee']}): {t['title']}")

    # Step 4: Output JSON report
    print("\n📄 JSON REPORT:")
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_tasks": len(tasks),
        "expert_count": len(assignees),
        "plan": plan,
        "actions": {
            "dispatch_count": len([r for r in plan["recommendations"] if r["action"] == "dispatch"]),
            "promote_count": len([r for r in plan["recommendations"] if r["action"] == "promote_and_dispatch"]),
            "wait_count": len([r for r in plan["recommendations"] if r["action"] == "wait_for_deps"]),
        }
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return report


if __name__ == "__main__":
    main()
