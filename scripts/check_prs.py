#!/usr/bin/env python3
"""
PR Status Checker | PR 状态检查器
Checks all PRs Lizer has submitted and received notifications for.
"""

import subprocess
import json
from datetime import datetime


def check_pr(repo, pr_num):
    """Check status of a specific PR"""
    try:
        cmd = ['gh', 'api', f'repos/{repo}/pulls/{pr_num}']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr = json.loads(result.stdout)
        return {
            'repo': repo,
            'number': pr_num,
            'title': pr.get('title', ''),
            'state': pr.get('state', 'unknown'),
            'merged': pr.get('merged_at') is not None,
            'closed_at': pr.get('closed_at')
        }
    except Exception:
        return None


def check_all_prs():
    """Check all submitted PRs"""
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    print("🔍 Checking submitted PRs...")
    
    prs_to_check = [
        ('ATHARVA262005/ai-audit-shelf', 6),
        ('Elladriel80/Aratea', 66),
    ]
    
    open_prs = []
    closed_prs = []
    merged_prs = []
    
    for repo, pr_num in prs_to_check:
        pr = check_pr(repo, pr_num)
        if pr:
            print(f"  {pr['repo']} #{pr['number']}: [{pr['state'].upper()}] {pr['title']}")
            
            if pr['merged']:
                merged_prs.append(pr)
            elif pr['state'] == 'closed':
                closed_prs.append(pr)
            else:
                open_prs.append(pr)
    
    print()
    print("📊 PR Status Summary")
    print("=" * 40)
    print(f"  Open: {len(open_prs)}")
    print(f"  Closed (not merged): {len(closed_prs)}")
    print(f"  Merged: {len(merged_prs)}")
    print("=" * 40)
    
    if closed_prs:
        print("\n⚠️  Closed PRs (consider reopening or creating new ones):")
        for pr in closed_prs:
            print(f"  - {pr['repo']} #{pr['number']}")
    
    return open_prs, closed_prs, merged_prs


if __name__ == "__main__":
    check_all_prs()
