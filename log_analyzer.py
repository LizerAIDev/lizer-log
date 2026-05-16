# log_analyzer.py
"""Log analysis tool with regex filtering and statistics."""

from typing import List, Dict
import argparse
import re
from pathlib import Path
from collections import Counter


def filter_logs(lines: List[str], pattern: str) -> List[str]:
    """Filter log lines matching regex pattern.
    
    Args:
        lines: Log lines to filter.
        pattern: Regex pattern to match.
        
    Returns:
        Matching log lines.
    """
    regex = re.compile(pattern)
    return [line for line in lines if regex.search(line)]


def analyze_stats(lines: List[str]) -> Dict[str, int]:
    """Calculate frequency statistics from log lines.
    
    Args:
        lines: Log lines to analyze.
        
    Returns:
        Dictionary with match count and top errors.
    """
    counter = Counter(lines)
    return {
        "total_matches": len(lines),
        "unique_patterns": len(counter),
        "top_10": counter.most_common(10)
    }


def main():
    parser = argparse.ArgumentParser(description="Log analyzer")
    parser.add_argument("input", help="Input log file")
    parser.add_argument("--filter", "-f", help="Regex pattern")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()
    
    lines = Path(args.input).read_text().splitlines()
    
    if args.filter:
        matched = filter_logs(lines, args.filter)
        print(f"Matched {len(matched)} lines")
        if args.stats:
            stats = analyze_stats(matched)
            print(f"Unique patterns: {stats['unique_patterns']}")
            print("Top 10 errors:")
            for line, count in stats["top_10"]:
                print(f"  {count}x: {line[:80]}")


if __name__ == "__main__":
    main()
