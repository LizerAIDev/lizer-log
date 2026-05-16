"""Tests for jsonfmt CLI tool."""

import json
import os
import tempfile
import pytest
from jsonfmt import format_json, validate_json


@pytest.fixture
def sample_json_file():
    """Create a temporary JSON file for testing."""
    data = {"name": "test", "value": 42, "nested": {"key": "value"}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def invalid_json_file():
    """Create a temporary invalid JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{invalid json}')
        yield f.name
    os.unlink(f.name)


def test_format_json_basic(sample_json_file):
    """Test basic JSON formatting."""
    result = format_json(sample_json_file)
    assert result["status"] == "success"


def test_format_json_with_output(sample_json_file):
    """Test formatting with output file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as out:
        result = format_json(sample_json_file, out.name)
        assert result["status"] == "success"
        assert os.path.exists(out.name)


def test_format_json_indent(sample_json_file):
    """Test formatting with custom indent."""
    result = format_json(sample_json_file, indent=4)
    assert result["status"] == "success"


def test_format_json_sort_keys(sample_json_file):
    """Test formatting with sorted keys."""
    result = format_json(sample_json_file, sort_keys=True)
    assert result["status"] == "success"


def test_validate_json_valid(sample_json_file):
    """Test validating valid JSON."""
    result = validate_json(sample_json_file)
    assert result["status"] == "valid"


def test_validate_json_invalid(invalid_json_file):
    """Test validating invalid JSON."""
    result = validate_json(invalid_json_file)
    assert result["status"] == "invalid"


def test_format_json_file_not_found():
    """Test formatting non-existent file."""
    result = format_json("nonexistent.json")
    assert result["status"] == "error"


def test_validate_json_file_not_found():
    """Test validating non-existent file."""
    result = validate_json("nonexistent.json")
    assert result["status"] == "error"
