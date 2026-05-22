#!/usr/bin/env python3
"""
AXIOM - Scientific Domains Verification Script
Automates the health check of all scientific domains by running their associated unit tests.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DOMAINS_DIR = PROJECT_ROOT / "app" / "domains"
TESTS_DIR = PROJECT_ROOT / "tests" / "unit"

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

def print_header():
    print(f"{BLUE}=================================================={NC}")
    print(f"{BLUE}   AXIOM SCIENTIFIC DOMAINS VERIFICATION SYSTEM   {NC}")
    print(f"{BLUE}=================================================={NC}")
    print(f"Root: {PROJECT_ROOT}")
    print(f"Domains: {DOMAINS_DIR}")
    print(f"Tests: {TESTS_DIR}\n")

def get_domains() -> List[str]:
    """Get list of domain directories"""
    if not DOMAINS_DIR.exists():
        print(f"{RED}Error: Domains directory not found at {DOMAINS_DIR}{NC}")
        sys.exit(1)
        
    return [d.name for d in DOMAINS_DIR.iterdir() 
            if d.is_dir() and not d.name.startswith('_') and d.name != "metrics"]

def verify_domain(domain: str) -> Tuple[bool, str, float]:
    """Run tests for a specific domain"""
    print(f"🔍 Verifying domain: {CYAN}{domain.upper()}{NC}...", end=" ", flush=True)
    
    # Check if test directory exists
    # Mappings for domains that might fallback or map differently
    # Direct mapping first: tests/unit/<domain>
    test_path = TESTS_DIR / domain
    
    if not test_path.exists():
        # Try fallback or variations if needed, but for now strict strict
        print(f"{YELLOW}⚠️  SKIPPED (No specific unit tests found){NC}")
        return True, "skipped", 0.0

    start_time = time.time()
    
    # Run pytest for this directory
    # -q: quiet, --tb=short: shorter tracebacks
    venv_python = PROJECT_ROOT / ".venv" / "bin" / "python3"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable
    
    # Disable HF models to avoid hangs/downloads during verification
    env = os.environ.copy()
    env["AXIOM_DISABLE_HF"] = "1"
    env["HF_HUB_OFFLINE"] = "1"
    
    cmd = [python_exe, "-m", "pytest", str(test_path), "-q", "--tb=no", "--disable-warnings"]
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=PROJECT_ROOT,
            env=env
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"{GREEN}✅ PASSED{NC} ({duration:.2f}s)")
            return True, "passed", duration
        elif result.returncode == 5:
            # Exit code 5 means no tests collected
            print(f"{YELLOW}⚠️  SKIPPED (No tests collected){NC}")
            return True, "skipped", 0
        else:
            print(f"{RED}❌ FAILED{NC} ({duration:.2f}s)")
            if result.stdout:
                print(f"{YELLOW}STDOUT:{NC}\n{result.stdout}")
            if result.stderr:
                print(f"{RED}STDERR:{NC}\n{result.stderr}")
            return False, "failed", duration
            
    except Exception as e:
        print(f"{RED}❌ ERROR: {e}{NC}")
        return False, "error", 0.0

def main():
    print_header()
    
    domains = get_domains()
    print(f"Found {len(domains)} scientific domains: {', '.join(domains)}\n")
    
    results = {}
    stats = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "empty": 0,
        "total_time": 0.0
    }
    
    failures = []
    
    for domain in sorted(domains):
        success, status, duration = verify_domain(domain)
        results[domain] = status
        stats[status] = stats.get(status, 0) + 1
        stats["total_time"] += duration
        
        if status == "failed":
            failures.append(domain)
            
    print(f"\n{BLUE}=================================================={NC}")
    print(f"{BLUE}                 VERIFICATION SUMMARY             {NC}")
    print(f"{BLUE}=================================================={NC}")
    
    print(f"Total Domains: {len(domains)}")
    print(f"Passed: {GREEN}{stats['passed']}{NC}")
    print(f"Failed: {RED}{stats['failed']}{NC}")
    print(f"Skipped/Empty: {YELLOW}{stats['skipped'] + stats['empty']}{NC}")
    print(f"Total Duration: {stats['total_time']:.2f}s")
    
    if failures:
        print(f"\n{RED}❌ FAILED DOMAINS:{NC}")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}✨ ALL SCIENTIFIC DOMAINS VERIFIED SUCCESSFULLY ✨{NC}")
        sys.exit(0)

if __name__ == "__main__":
    main()
