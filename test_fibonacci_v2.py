# test_fibonacci_v2.py
"""Tests for fibonacci module."""

import os, tempfile, json
from fibonacci_v2 import fibonacci, save_to_file


def test_fib_zero(): assert fibonacci(0) == []
def test_fib_one(): assert fibonacci(1) == [0]
def test_fib_normal(): assert fibonacci(5) == [0, 1, 1, 2, 3]
def test_save():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        save_to_file(5, f.name)
        with open(f.name) as rf: data = json.load(rf)
        assert data == [0, 1, 1, 2, 3]
        os.unlink(f.name)
