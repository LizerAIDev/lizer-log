# dep_checker.py
"""Python dependency checker for pip and poetry projects."""

from typing import List, Dict, Optional
import argparse
import re
from pathlib import Path
import tomllib


def parse_requirements(filepath: str) -> List[Dict[str, str]]:
    """Parse requirements.txt file.
    
    Args:
        filepath: Path to requirements.txt.
        
    Returns:
        List of dicts with 'name' and 'version' keys.
    """
    deps = []
    content = Path(filepath).read_text(encoding="utf-8")
    
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([a-zA-Z0-9_-]+)==([\d.]+)$", line)
        if match:
            deps.append({"name": match.group(1), "version": match.group(2)})
            
    return deps


def parse_pyproject(filepath: str) -> List[Dict[str, str]]:
    """Parse pyproject.toml dependencies.
    
    Args:
        filepath: Path to pyproject.toml.
        
    Returns:
        List of dicts with 'name' and 'version' keys.
    """
    deps = []
    content = Path(filepath).read_text(encoding="utf-8")
    data = tomllib.loads(content)
    
    # Poetry dependencies
    poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    for name, version in poetry_deps.items():
        if name.lower() != "python":
            version_str = str(version).lstrip("^~>=<")
            deps.append({"name": name, "version": version_str})
            
    # PEP 621 dependencies
    pep_deps = data.get("project", {}).get("dependencies", [])
    for dep_str in pep_deps:
        match = re.match(r"^([a-zA-Z0-9_-]+)(?:[><=!]+([\d.]+))?$", dep_str)
        if match:
            deps.append({"name": match.group(1), "version": match.group(2) or "latest"})
            
    return deps


def check_outdated(deps: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Check which dependencies are outdated.
    
    Args:
        deps: List of current dependencies.
        
    Returns:
        List with added 'latest_version' and 'outdated' fields.
    """
    # In real implementation, would query PyPI API
    # For now, simulate with mock data
    outdated = []
    for dep in deps:
        # Simulate version check (mock)
        current = dep["version"]
        latest = f"{int(current.split('.')[0]) + 1}.0.0"
        outdated.append({
            **dep,
            "latest_version": latest,
            "outdated": current != latest
        })
    return outdated


def generate_report(deps: List[Dict[str, str]], output_path: Optional[str] = None) -> str:
    """Generate Markdown report of dependency status.
    
    Args:
        deps: List of dependency info with outdated status.
        output_path: Optional output file path.
        
    Returns:
        Markdown report string.
    """
    lines = ["# Dependency Check Report\n"]
    lines.append(f"## Summary\n")
    
    outdated_count = sum(1 for d in deps if d.get("outdated"))
    lines.append(f"- Total packages: {len(deps)}")
    lines.append(f"- Outdated: {outdated_count}")
    lines.append(f"- Up to date: {len(deps) - outdated_count}\n")
    
    if outdated_count > 0:
        lines.append("## Outdated Packages\n")
        lines.append("| Package | Current | Latest |")
        lines.append("|---------|---------|--------|")
        for dep in deps:
            if dep.get("outdated"):
                lines.append(f"| {dep['name']} | {dep['version']} | {dep['latest_version']} |")
    else:
        lines.append("## All packages are up to date!\n")
        
    report = "\n".join(lines)
    
    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")
        print(f"Report saved to {output_path}")
        
    return report


def main():
    parser = argparse.ArgumentParser(description="Python dependency checker")
    parser.add_argument("project_dir", help="Path to project directory")
    parser.add_argument("-o", "--output", help="Output report file")
    args = parser.parse_args()
    
    project = Path(args.project_dir)
    all_deps = []
    
    # Parse requirements.txt
    req_file = project / "requirements.txt"
    if req_file.exists():
        all_deps.extend(parse_requirements(str(req_file)))
        
    # Parse pyproject.toml
    pyproject_file = project / "pyproject.toml"
    if pyproject_file.exists():
        all_deps.extend(parse_pyproject(str(pyproject_file)))
        
    if not all_deps:
        print("No dependencies found.")
        return
        
    # Check outdated
    checked = check_outdated(all_deps)
    
    # Generate report
    generate_report(checked, args.output)
    print(f"Checked {len(checked)} dependencies")


if __name__ == "__main__":
    main()
