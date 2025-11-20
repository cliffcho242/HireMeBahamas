#!/usr/bin/env python3
"""
PR Status Checker
-----------------
Checks the status of open pull requests and reports issues that need attention.

This script can be run locally or in CI/CD to monitor PR health.
"""

import os
import sys
import json
from typing import Dict, List, Optional
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Install with: pip install requests")
    sys.exit(1)


class PRStatusChecker:
    """Checks status of pull requests in a GitHub repository."""
    
    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        """
        Initialize the PR status checker.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            token: GitHub personal access token (optional, increases rate limit)
        """
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def get_open_prs(self) -> List[Dict]:
        """Get all open pull requests."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
        params = {"state": "open", "per_page": 100}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching pull requests: {e}")
            return []
    
    def get_pr_details(self, pr_number: int) -> Optional[Dict]:
        """Get detailed information about a specific PR."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR #{pr_number}: {e}")
            return None
    
    def check_pr_status(self, pr: Dict) -> Dict:
        """
        Check the status of a pull request and identify issues.
        
        Returns:
            Dictionary with status information and issues found
        """
        issues = []
        status = {
            "number": pr["number"],
            "title": pr["title"],
            "branch": pr["head"]["ref"],
            "base_sha": pr["base"]["sha"][:7],
            "mergeable": pr.get("mergeable"),
            "mergeable_state": pr.get("mergeable_state"),
            "is_draft": pr.get("draft", False),
            "created_at": pr["created_at"],
            "updated_at": pr["updated_at"],
            "issues": [],
            "severity": "ok"
        }
        
        # Check mergeable state
        mergeable_state = pr.get("mergeable_state")
        if mergeable_state == "dirty":
            issues.append("Has merge conflicts with base branch")
            status["severity"] = "critical"
        elif mergeable_state == "unstable":
            issues.append("CI checks are failing or pending")
            status["severity"] = "warning"
        elif mergeable_state == "blocked":
            issues.append("Blocked by required status checks or reviews")
            status["severity"] = "warning"
        elif mergeable_state == "behind":
            issues.append("Branch is behind base branch")
            status["severity"] = "info"
        
        # Check if base is outdated
        # Note: This would require fetching current main branch SHA
        # For now, just note if it's not "clean"
        if mergeable_state not in ["clean", None]:
            issues.append(f"Mergeable state: {mergeable_state}")
        
        # Check if PR is a draft
        if pr.get("draft"):
            issues.append("PR is in draft mode")
            status["severity"] = "info"
        
        # Check age (if older than 7 days without updates)
        created = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
        updated = datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00"))
        age_days = (datetime.now(created.tzinfo) - updated).days
        
        if age_days > 7:
            issues.append(f"Not updated in {age_days} days")
            if status["severity"] == "ok":
                status["severity"] = "info"
        
        status["issues"] = issues
        return status
    
    def print_report(self, statuses: List[Dict]):
        """Print a formatted status report."""
        print("\n" + "=" * 80)
        print(f"Pull Request Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Repository: {self.owner}/{self.repo}")
        print("=" * 80)
        
        # Group by severity
        critical = [s for s in statuses if s["severity"] == "critical"]
        warning = [s for s in statuses if s["severity"] == "warning"]
        info = [s for s in statuses if s["severity"] == "info"]
        ok = [s for s in statuses if s["severity"] == "ok"]
        
        if critical:
            print("\n🔴 CRITICAL ISSUES:")
            for status in critical:
                self._print_pr_status(status)
        
        if warning:
            print("\n⚠️  WARNINGS:")
            for status in warning:
                self._print_pr_status(status)
        
        if info:
            print("\n📋 INFORMATIONAL:")
            for status in info:
                self._print_pr_status(status)
        
        if ok:
            print("\n✅ HEALTHY:")
            for status in ok:
                self._print_pr_status(status)
        
        # Summary
        print("\n" + "=" * 80)
        print(f"Total PRs: {len(statuses)}")
        print(f"Critical: {len(critical)} | Warnings: {len(warning)} | " +
              f"Info: {len(info)} | Healthy: {len(ok)}")
        print("=" * 80)
    
    def _print_pr_status(self, status: Dict):
        """Print information about a single PR."""
        print(f"\nPR #{status['number']}: {status['title']}")
        print(f"  Branch: {status['branch']}")
        print(f"  Base SHA: {status['base_sha']}")
        print(f"  Mergeable: {status['mergeable']}")
        print(f"  State: {status['mergeable_state']}")
        if status['is_draft']:
            print(f"  Status: DRAFT")
        for issue in status['issues']:
            print(f"  ⚠️  {issue}")
    
    def run(self):
        """Run the PR status check."""
        print(f"Fetching open pull requests for {self.owner}/{self.repo}...")
        prs = self.get_open_prs()
        
        if not prs:
            print("No open pull requests found.")
            return 0
        
        print(f"Found {len(prs)} open pull request(s).")
        
        statuses = []
        for pr in prs:
            # Get full details if needed
            pr_details = self.get_pr_details(pr["number"])
            if pr_details:
                status = self.check_pr_status(pr_details)
                statuses.append(status)
        
        self.print_report(statuses)
        
        # Return exit code based on critical issues
        critical_count = len([s for s in statuses if s["severity"] == "critical"])
        return 1 if critical_count > 0 else 0


def main():
    """Main entry point."""
    # Get configuration from environment or arguments
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "cliffcho242")
    repo = os.environ.get("GITHUB_REPOSITORY", "HireMeBahamas")
    token = os.environ.get("GITHUB_TOKEN")
    
    # Parse repo if it includes owner
    if "/" in repo:
        owner, repo = repo.split("/", 1)
    
    # Allow command line overrides
    if len(sys.argv) > 1:
        if "/" in sys.argv[1]:
            owner, repo = sys.argv[1].split("/", 1)
        else:
            repo = sys.argv[1]
    
    if len(sys.argv) > 2:
        owner = sys.argv[2]
    
    print(f"Checking PRs for repository: {owner}/{repo}")
    if not token:
        print("Note: No GITHUB_TOKEN provided. API rate limits will be lower.")
        print("Set GITHUB_TOKEN environment variable for higher limits.")
    
    checker = PRStatusChecker(owner, repo, token)
    exit_code = checker.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
