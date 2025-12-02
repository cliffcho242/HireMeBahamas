#!/usr/bin/env python3
"""
Validate vercel.json files to ensure they comply with Vercel's schema.
This prevents deployment failures due to invalid configuration properties.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Known valid top-level properties in vercel.json
# Source: https://vercel.com/docs/projects/project-configuration
VALID_TOP_LEVEL_PROPS: Set[str] = {
    "version",
    "name",
    "alias",
    "scope",
    "env",
    "build",
    "builds",
    "routes",
    "rewrites",
    "redirects",
    "headers",
    "cleanUrls",
    "trailingSlash",
    "regions",
    "public",
    "github",
    "framework",
    "functions",
    "crons",
    "buildCommand",
    "devCommand",
    "installCommand",
    "outputDirectory",
    "publicDirectory",
    "$schema",
    "git",
    "ignoreCommand",
}

# Valid properties in functions config
VALID_FUNCTION_PROPS: Set[str] = {
    "runtime",
    "memory",
    "maxDuration",
    "includeFiles",
    "excludeFiles",
}


def validate_no_comments(data: Dict, path: str = "") -> List[str]:
    """Check for properties starting with _ which are often used as comments."""
    issues = []
    
    for key, value in data.items():
        current_path = f"{path}.{key}" if path else key
        
        # Properties starting with underscore are not allowed
        if key.startswith("_"):
            issues.append(
                f"Invalid property '{current_path}': Properties starting with '_' "
                f"are not allowed in vercel.json. Use separate documentation instead."
            )
        
        # Recursively check nested objects
        if isinstance(value, dict):
            issues.extend(validate_no_comments(value, current_path))
    
    return issues


def validate_vercel_json(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a vercel.json file.
    Returns: (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON syntax: {e}"]
    except FileNotFoundError:
        return False, [f"File not found: {file_path}"]
    except Exception as e:
        return False, [f"Error reading file: {e}"]
    
    # Check for underscore-prefixed properties (like _comment_memory)
    comment_issues = validate_no_comments(data)
    issues.extend(comment_issues)
    
    # Check top-level properties
    for key in data.keys():
        if key not in VALID_TOP_LEVEL_PROPS and not key.startswith("_"):
            issues.append(
                f"Unknown top-level property '{key}' may not be supported by Vercel"
            )
    
    # Check functions config
    if "functions" in data and isinstance(data["functions"], dict):
        for pattern, config in data["functions"].items():
            if not isinstance(config, dict):
                continue
            
            for key in config.keys():
                if key.startswith("_"):
                    issues.append(
                        f"Invalid function property '{key}' in pattern '{pattern}': "
                        f"Properties starting with '_' are not allowed"
                    )
                elif key not in VALID_FUNCTION_PROPS:
                    issues.append(
                        f"Unknown function property '{key}' in pattern '{pattern}' "
                        f"may not be supported by Vercel"
                    )
    
    return len(issues) == 0, issues


def main():
    """Main validation function."""
    # Find repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    # List of vercel.json files to validate
    vercel_files = [
        repo_root / "vercel.json",
        repo_root / "frontend" / "vercel.json",
        repo_root / "next-app" / "vercel.json",
        repo_root / "vercel_backend.json",
        repo_root / "vercel_immortal.json",
    ]
    
    print("Validating Vercel configuration files...")
    print("=" * 60)
    
    all_valid = True
    validated_count = 0
    
    for vfile in vercel_files:
        if not vfile.exists():
            continue
        
        validated_count += 1
        print(f"\n📄 {vfile.relative_to(repo_root)}")
        
        is_valid, issues = validate_vercel_json(vfile)
        
        if is_valid:
            print("  ✅ Valid")
        else:
            print("  ❌ Issues found:")
            for issue in issues:
                print(f"     • {issue}")
            all_valid = False
    
    print("\n" + "=" * 60)
    print(f"Validated {validated_count} file(s)")
    
    if all_valid:
        print("✅ All vercel.json files are valid!")
        return 0
    else:
        print("❌ Some vercel.json files have validation errors")
        print("\nTo fix:")
        print("  1. Remove any properties starting with '_'")
        print("  2. Use separate documentation files for comments")
        print("  3. Refer to https://vercel.com/docs/projects/project-configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())
