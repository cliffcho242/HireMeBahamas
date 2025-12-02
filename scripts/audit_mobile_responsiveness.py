#!/usr/bin/env python3
"""
Mobile Responsiveness Audit for HireMeBahamas
Checks and reports on mobile-first design implementation
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

def audit_file(file_path: Path) -> Dict[str, any]:
    """Audit a single file for mobile responsiveness."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return {"error": str(e)}
    
    results = {
        "file": str(file_path),
        "has_responsive_classes": False,
        "responsive_breakpoints": set(),
        "issues": [],
        "good_practices": []
    }
    
    # Check for responsive Tailwind classes
    responsive_patterns = [
        r'\bsm:',  # Small screens (640px+)
        r'\bmd:',  # Medium screens (768px+)
        r'\blg:',  # Large screens (1024px+)
        r'\bxl:',  # Extra large screens (1280px+)
        r'\b2xl:', # 2XL screens (1536px+)
        r'\bxs:',  # Extra small (custom)
    ]
    
    for pattern in responsive_patterns:
        if re.search(pattern, content):
            results["has_responsive_classes"] = True
            breakpoint = pattern.replace(r'\b', '').replace(':', '')
            results["responsive_breakpoints"].add(breakpoint)
    
    # Check for fixed widths that might break on mobile
    fixed_width_patterns = [
        r'w-\[\d+px\]',  # Fixed width in pixels
        r'min-w-\[\d+px\]',  # Fixed min-width
        r'max-w-\[\d+px\]',  # Fixed max-width
        r'width:\s*\d+px',  # Inline style fixed width
    ]
    
    for pattern in fixed_width_patterns:
        matches = re.findall(pattern, content)
        if matches:
            results["issues"].append(f"Fixed width found: {matches[:3]}")
    
    # Check for good mobile practices
    if 'overflow-x-auto' in content:
        results["good_practices"].append("Horizontal scroll for overflow content")
    
    if 'touch-' in content:
        results["good_practices"].append("Touch-optimized interactions")
    
    if 'safe-area' in content:
        results["good_practices"].append("Safe area support for notched devices")
    
    # Check for viewport meta tag (HTML files only)
    if file_path.suffix == '.html':
        if 'viewport' in content:
            if 'width=device-width' in content:
                results["good_practices"].append("Proper viewport meta tag")
            else:
                results["issues"].append("Viewport meta tag missing width=device-width")
        else:
            results["issues"].append("Missing viewport meta tag")
    
    return results

def generate_report(frontend_path: Path) -> str:
    """Generate a comprehensive mobile responsiveness report."""
    report_lines = [
        "=" * 80,
        "MOBILE RESPONSIVENESS AUDIT REPORT",
        "=" * 80,
        ""
    ]
    
    # Audit key files
    key_files = [
        frontend_path / "index.html",
        frontend_path / "src" / "pages" / "Home.tsx",
        frontend_path / "src" / "pages" / "Jobs.tsx",
        frontend_path / "src" / "pages" / "Messages.tsx",
        frontend_path / "src" / "pages" / "Profile.tsx",
        frontend_path / "src" / "pages" / "UserProfile.tsx",
    ]
    
    total_files = 0
    responsive_files = 0
    total_issues = 0
    
    for file_path in key_files:
        if not file_path.exists():
            continue
        
        total_files += 1
        results = audit_file(file_path)
        
        if results.get("has_responsive_classes"):
            responsive_files += 1
        
        report_lines.append(f"\n📄 {file_path.name}")
        report_lines.append("-" * 80)
        
        if results.get("has_responsive_classes"):
            breakpoints = ", ".join(sorted(results["responsive_breakpoints"]))
            report_lines.append(f"✅ Responsive: YES ({breakpoints})")
        else:
            report_lines.append("⚠️  Responsive: NO")
        
        if results.get("good_practices"):
            report_lines.append("\n✅ Good Practices:")
            for practice in results["good_practices"]:
                report_lines.append(f"   • {practice}")
        
        if results.get("issues"):
            total_issues += len(results["issues"])
            report_lines.append("\n⚠️  Issues:")
            for issue in results["issues"]:
                report_lines.append(f"   • {issue}")
    
    # Summary
    report_lines.extend([
        "",
        "=" * 80,
        "SUMMARY",
        "=" * 80,
        f"Total files audited: {total_files}",
        f"Responsive files: {responsive_files}/{total_files}",
        f"Total issues found: {total_issues}",
        ""
    ])
    
    if total_issues == 0 and responsive_files == total_files:
        report_lines.append("✅ All audited files are mobile-responsive!")
    elif responsive_files / total_files >= 0.8:
        report_lines.append("⚠️  Most files are responsive, but some improvements needed")
    else:
        report_lines.append("❌ Significant mobile responsiveness improvements needed")
    
    report_lines.extend([
        "",
        "RECOMMENDATIONS:",
        "1. Use responsive Tailwind classes (sm:, md:, lg:) for all layout components",
        "2. Avoid fixed pixel widths - use max-w-* or w-full instead",
        "3. Test on actual mobile devices (iOS Safari, Android Chrome)",
        "4. Use touch-friendly sizes (min-h-touch, min-w-touch)",
        "5. Support safe areas for notched devices",
        "",
        "=" * 80,
    ])
    
    return "\n".join(report_lines)

def main():
    """Main audit function."""
    frontend_path = Path(__file__).parent.parent / "frontend"
    
    if not frontend_path.exists():
        print("Error: Frontend directory not found")
        return 1
    
    report = generate_report(frontend_path)
    print(report)
    
    # Save report to file
    report_file = Path(__file__).parent.parent / "MOBILE_RESPONSIVENESS_AUDIT.md"
    report_file.write_text(report, encoding='utf-8')
    print(f"\nReport saved to: {report_file}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
