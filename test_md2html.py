# test_md2html.py
"""Tests for md2html converter."""

from md2html import md_to_html


def test_heading():
    """Test heading conversion."""
    result = md_to_html("# Hello")
    assert "<h1>Hello</h1>" in result


def test_list():
    """Test list conversion."""
    result = md_to_html("- item1\n- item2")
    assert "<li>item1</li>" in result
    assert "<li>item2</li>" in result


def test_link():
    """Test link conversion."""
    result = md_to_html("[Click](http://example.com)")
    assert '<a href="http://example.com">Click</a>' in result


def test_theme():
    """Test theme inclusion."""
    result = md_to_html("text", theme="dark")
    assert 'dark.css' in result


def test_code_block():
    """Test code block handling."""
    result = md_to_html("```\ncode\n```")
    assert "<pre><code>" in result


def test_empty():
    """Test empty input."""
    result = md_to_html("")
    assert "<!DOCTYPE html>" in result
