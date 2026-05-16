# test_dep_checker.py
"""Tests for dependency checker."""

import tempfile
import os
from dep_checker import parse_requirements, parse_pyproject, check_outdated, generate_report


def test_parse_requirements():
    """Test parsing requirements.txt."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("requests==2.28.0\nflask==2.3.0\n# comment\n")
        f.seek(0)
        deps = parse_requirements(f.name)
        assert len(deps) == 2
        assert deps[0]["name"] == "requests"
        assert deps[0]["version"] == "2.28.0"
        os.unlink(f.name)


def test_parse_pyproject():
    """Test parsing pyproject.toml."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write('[tool.poetry.dependencies]\npython = "^3.9"\nrequests = "^2.28.0"\n')
        f.seek(0)
        deps = parse_pyproject(f.name)
        assert len(deps) == 1
        assert deps[0]["name"] == "requests"
        os.unlink(f.name)


def test_check_outdated():
    """Test outdated checking."""
    deps = [{"name": "pkg", "version": "1.0.0"}]
    result = check_outdated(deps)
    assert len(result) == 1
    assert result[0]["outdated"] is True
    assert result[0]["latest_version"] == "2.0.0"


def test_generate_report_outdated():
    """Test report generation with outdated packages."""
    deps = [{"name": "pkg", "version": "1.0.0", "latest_version": "2.0.0", "outdated": True}]
    report = generate_report(deps)
    assert "Outdated Packages" in report
    assert "pkg" in report


def test_generate_report_current():
    """Test report generation with all current packages."""
    deps = [{"name": "pkg", "version": "2.0.0", "latest_version": "2.0.0", "outdated": False}]
    report = generate_report(deps)
    assert "up to date" in report.lower()


def test_empty_deps():
    """Test empty dependencies."""
    report = generate_report([])
    assert "Total packages: 0" in report


def test_parse_requirements_empty():
    """Test empty requirements file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("# empty\n")
        f.seek(0)
        deps = parse_requirements(f.name)
        assert len(deps) == 0
        os.unlink(f.name)
