#!/usr/bin/env python3
"""JSON Format CLI Tool - jsonfmt

A command-line tool for formatting and validating JSON files.

Usage:
    jsonfmt input.json -o output.json [--indent 2] [--sort-keys]
    jsonfmt --validate input.json
"""

import argparse
import json
import sys
from pathlib import Path


def format_json(input_path: str, output_path: str = None, indent: int = 2, sort_keys: bool = False) -> dict:
    """Format a JSON file with specified options."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        formatted = json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted)
            return {"status": "success", "message": f"Formatted and saved to {output_path}"}
        else:
            print(formatted)
            return {"status": "success", "message": "Formatted (stdout)"}
            
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {e}"}
    except FileNotFoundError:
        return {"status": "error", "message": f"File not found: {input_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {e}"}


def validate_json(input_path: str) -> dict:
    """Validate a JSON file."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return {"status": "valid", "message": "JSON is valid"}
    except json.JSONDecodeError as e:
        return {"status": "invalid", "message": f"Invalid JSON: {e}"}
    except FileNotFoundError:
        return {"status": "error", "message": f"File not found: {input_path}"}


def main():
    parser = argparse.ArgumentParser(description="JSON Format CLI Tool")
    parser.add_argument("input", help="Input JSON file path")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument("--indent", type=int, default=2, help="Indentation level (default: 2)")
    parser.add_argument("--sort-keys", action="store_true", help="Sort keys alphabetically")
    parser.add_argument("--validate", action="store_true", help="Validate JSON only")
    
    args = parser.parse_args()
    
    if args.validate:
        result = validate_json(args.input)
    else:
        result = format_json(args.input, args.output, args.indent, args.sort_keys)
    
    print(result["message"])
    sys.exit(0 if result["status"] in ("success", "valid") else 1)


if __name__ == "__main__":
    main()
