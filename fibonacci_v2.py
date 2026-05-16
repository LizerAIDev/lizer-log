# fibonacci_v2.py
"""Fibonacci sequence calculator with type hints."""

from typing import List
import json
from pathlib import Path


def fibonacci(n: int) -> List[int]:
    """Return first n Fibonacci numbers."""
    if n <= 0: return []
    if n == 1: return [0]
    fibs: List[int] = [0, 1]
    while len(fibs) < n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs


def save_to_file(n: int, filepath: str) -> None:
    """Save first n Fibonacci numbers to JSON file."""
    data = fibonacci(n)
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f)
