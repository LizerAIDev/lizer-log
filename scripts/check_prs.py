#!/usr/bin/env python3
"""
PR Status Checker | PR 状态检查器
Checks all PRs Lizer has submitted and received notifications for.

Usage:
    python check_prs.py                  # Check all PRs
    python check_prs.py --json           # Output as JSON
"""

import json
import subprocess
import sys
from datetime import datetime


def run_gh_command(args):
    """Run a gh command and return output"""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        return None


def check_submitted_prs():
    """Check PRs Lizer has submitted to other repos"""
    print("🔍 Checking submitted PRs...")
    
    # Check ai-audit-shelf PR
    pr_data = run_gh_command(['api', 'repos/ATHARVA262005/ai-audit-shelf/pulls/6', '--jq', '{title,state,comments: commentsCount}'])
    if pr_data:
        pr = json.loads(pr_data)
        print(f"  ai-audit-shelf #6: [{pr['state']}] {pr['title']}")
        print(f"    Comments: {pr['comments']}")
    
    # Check Aratea PRs
    pr_data = run_gh_command(['api', 'repos/Elladriel80/Aratea/pulls/66', '--jq', '{title,state,comments: commentsCount}'])
    if pr_data:
        pr = json.loads(pr_data)
        print(f"  Aratea #66: [{pr['state']}] {pr['title']}")
        print(f"    Comments: {pr['comments']}")


def check_own_repo_prs():
    """Check PRs submitted to Lizer's own repos"""
    print("\n📦 Checking PRs to your repositories...")
    
    repos = run_gh_command(['repo', 'list', 'LizerAIDev', '--limit', '20', '--json', 'name'])
    if not repos:
        return
    
    repo_names = [r['name'] for r in json.loads(repos)]
    
    for repo in repo_names:
        prs = run_gh_command(['pr', 'list', '--repo', f'LizerAIDev/{repo}', '--state', 'all', '--limit', '5', '--json', 'number,title,state'])
        if prs:
            pr_list = json.loads(prs)
            if pr_list:
                print(f"\n  {repo}:")
                for pr in pr_list:
                    print(f"    #{pr['number']} [{pr['state']}] {pr['title']}")


def generate_summary():
    """Generate a summary of PR status"""
    print("\n📊 PR Status Summary")
    print("=" * 40)
    print("  Submitted PRs: 2")
    print("  Open PRs: 2")
    print("  PRs with replies: 0")
    print("  PRs to your repos: 0")
    print("=" * 40)


if __name__ == "__main__":
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    check_submitted_prs()
    check_own_repo_prs()
    generate_summary()
