#!/usr/bin/env python3
"""
Test suite for Vercel configuration schema validation.

This test ensures that vercel.json files never contain invalid properties
that would cause Vercel deployment failures, particularly the "regions"
property inside the "functions" configuration.

The "regions" property, if used, should ONLY be at the top level of vercel.json,
never inside the "functions" section.
"""
import json
from pathlib import Path
import pytest


# Get repository root
REPO_ROOT = Path(__file__).parent.parent


def discover_vercel_files():
    """
    Find all vercel configuration files in the repository.
    
    Uses rglob for efficient recursive search with explicit exclusions
    to avoid searching in large dependency directories.
    
    This function is called lazily from fixtures to ensure test isolation
    and avoid module-level filesystem access.
    """
    vercel_files = []
    
    # Directories to exclude from search
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 
                    '.pytest_cache', 'dist', 'build', '.next'}
    
    # Use rglob for efficient recursive search
    for json_file in REPO_ROOT.rglob("vercel*.json"):
        # Check if any parent directory is in exclude list
        if not any(part in exclude_dirs for part in json_file.parts):
            vercel_files.append(json_file)
    
    return sorted(vercel_files)  # Sort for consistent test order

# Valid properties for function configuration (per Vercel documentation)
VALID_FUNCTION_PROPERTIES = {
    "runtime",
    "memory",
    "maxDuration",
    "includeFiles",
    "excludeFiles",
}

# Properties that are commonly confused but NOT valid in functions config
INVALID_FUNCTION_PROPERTIES = {
    "regions",  # This should be top-level only
    "env",      # This should be top-level only
    "crons",    # This should be top-level only
}


class TestVercelSchema:
    """Test suite for Vercel JSON schema validation."""

    @pytest.fixture
    def vercel_files(self):
        """
        Get all vercel.json files that exist.
        
        Uses lazy discovery to ensure test isolation and avoid
        module-level filesystem access.
        """
        return [f for f in discover_vercel_files() if f.exists()]

    def test_vercel_files_exist(self, vercel_files):
        """Ensure at least one vercel.json file exists."""
        assert len(vercel_files) > 0, "No vercel.json files found"

    def test_vercel_files_valid_json(self, vercel_files):
        """Ensure all vercel.json files are valid JSON."""
        for vfile in vercel_files:
            try:
                with open(vfile, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"{vfile.name} is not valid JSON: {e}")

    def test_no_regions_in_functions(self, vercel_files):
        """
        Ensure 'regions' property never appears inside functions configuration.
        
        This is the PRIMARY test to prevent the error:
        "functions.api/index.py should NOT have additional property regions"
        
        The 'regions' property should only be used at the top level of vercel.json,
        never inside the functions configuration for individual serverless functions.
        """
        for vfile in vercel_files:
            with open(vfile, 'r') as f:
                data = json.load(f)
            
            if 'functions' not in data:
                continue
            
            functions = data['functions']
            if not isinstance(functions, dict):
                continue
            
            for pattern, config in functions.items():
                if not isinstance(config, dict):
                    continue
                
                # Check for 'regions' property
                if 'regions' in config:
                    pytest.fail(
                        f"INVALID: {vfile.name} has 'regions' property in "
                        f"functions.{pattern}. The 'regions' property should "
                        f"only be at the top level of vercel.json, not inside "
                        f"function configurations."
                    )

    def test_no_invalid_function_properties(self, vercel_files):
        """Ensure functions config only uses valid properties."""
        for vfile in vercel_files:
            with open(vfile, 'r') as f:
                data = json.load(f)
            
            if 'functions' not in data:
                continue
            
            functions = data['functions']
            if not isinstance(functions, dict):
                continue
            
            for pattern, config in functions.items():
                if not isinstance(config, dict):
                    continue
                
                invalid_props = set(config.keys()) & INVALID_FUNCTION_PROPERTIES
                if invalid_props:
                    pytest.fail(
                        f"INVALID: {vfile.name} has invalid properties in "
                        f"functions.{pattern}: {invalid_props}. "
                        f"These properties should be at the top level, not in function config."
                    )

    def test_function_properties_are_valid(self, vercel_files):
        """Warn about unknown function properties that might not be supported."""
        for vfile in vercel_files:
            with open(vfile, 'r') as f:
                data = json.load(f)
            
            if 'functions' not in data:
                continue
            
            functions = data['functions']
            if not isinstance(functions, dict):
                continue
            
            for pattern, config in functions.items():
                if not isinstance(config, dict):
                    continue
                
                unknown_props = set(config.keys()) - VALID_FUNCTION_PROPERTIES
                if unknown_props:
                    # This is a warning, not a failure, since Vercel may add new properties
                    print(
                        f"WARNING: {vfile.name} has unrecognized properties in "
                        f"functions.{pattern}: {unknown_props}. "
                        f"Verify these are supported by Vercel."
                    )

    def test_regions_only_at_top_level(self, vercel_files):
        """If 'regions' is used, ensure it's only at the top level."""
        for vfile in vercel_files:
            with open(vfile, 'r') as f:
                data = json.load(f)
            
            # Check that if regions exists, it's at top level only
            self._check_regions_placement(data, vfile.name)

    def _check_regions_placement(self, obj, filename, path=""):
        """
        Iteratively check that 'regions' only appears at top level.
        
        Uses iterative approach with a queue to avoid stack overflow
        on deeply nested JSON structures.
        """
        # Use a queue for iterative traversal: (object, path)
        queue = [(obj, path)]
        
        while queue:
            current_obj, current_path = queue.pop(0)
            
            if not isinstance(current_obj, dict):
                continue
            
            for key, value in current_obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                # If we find 'regions' anywhere except top level
                if key == 'regions' and current_path != "":
                    pytest.fail(
                        f"INVALID: {filename} has 'regions' at {new_path}. "
                        f"The 'regions' property should ONLY be at the top level."
                    )
                
                # Add nested objects to queue
                if isinstance(value, dict):
                    queue.append((value, new_path))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            queue.append((item, f"{new_path}[{i}]"))

    def test_no_underscore_properties(self, vercel_files):
        """Ensure no properties start with underscore (comment properties)."""
        for vfile in vercel_files:
            with open(vfile, 'r') as f:
                data = json.load(f)
            
            underscore_props = self._find_underscore_properties(data)
            if underscore_props:
                pytest.fail(
                    f"INVALID: {vfile.name} has properties starting with underscore: "
                    f"{underscore_props}. Vercel does not allow these. "
                    f"Use separate documentation files instead."
                )

    def _find_underscore_properties(self, obj, path=""):
        """Recursively find all properties starting with underscore."""
        found = []
        if not isinstance(obj, dict):
            return found
        
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            
            if key.startswith('_'):
                found.append(current_path)
            
            if isinstance(value, dict):
                found.extend(self._find_underscore_properties(value, current_path))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        found.extend(
                            self._find_underscore_properties(item, f"{current_path}[{i}]")
                        )
        
        return found


if __name__ == "__main__":
    # Provide clear guidance and exit with error code
    raise SystemExit(
        "This test file should be run using pytest:\n"
        "  python -m pytest tests/test_vercel_schema.py -v\n\n"
        "Or run all tests:\n"
        "  python -m pytest tests/ -v"
    )
