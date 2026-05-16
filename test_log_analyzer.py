# test_log_analyzer.py
"""Tests for log analyzer."""

from log_analyzer import filter_logs, analyze_stats


def test_filter_error():
    """Test filtering ERROR lines."""
    lines = ["INFO ok", "ERROR fail", "WARN slow", "ERROR crash"]
    result = filter_logs(lines, r"ERROR")
    assert len(result) == 2


def test_filter_multiple():
    """Test filtering multiple patterns."""
    lines = ["INFO ok", "ERROR fail", "WARN slow"]
    result = filter_logs(lines, r"ERROR|WARN")
    assert len(result) == 2


def test_filter_no_match():
    """Test no matches."""
    lines = ["INFO ok", "DEBUG trace"]
    result = filter_logs(lines, r"ERROR")
    assert len(result) == 0


def test_stats():
    """Test statistics calculation."""
    lines = ["ERROR a", "ERROR a", "ERROR b"]
    result = analyze_stats(lines)
    assert result["total_matches"] == 3
    assert result["unique_patterns"] == 2
    assert result["top_10"][0] == ("ERROR a", 2)


def test_empty_filter():
    """Test empty input."""
    result = filter_logs([], r"ERROR")
    assert result == []


def test_empty_stats():
    """Test empty stats."""
    result = analyze_stats([])
    assert result["total_matches"] == 0
