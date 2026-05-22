#!/usr/bin/env python3
"""
Load testing runner script for AXIOM ATLAS.

This script runs comprehensive load tests using pytest and Locust.
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class LoadTestRunner:
    """Runs load tests and generates reports."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.results_dir = self.base_dir / "reports" / "performance"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def run_pytest_load_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run pytest-based load tests."""
        print("🧪 Running pytest load tests...")
        
        test_files = [
            "tests/performance/load/test_autonomous_loop_throughput.py",
            "tests/performance/load/test_concurrent_hypothesis_generation.py",
            "tests/performance/load/test_database_connection_pool.py",
            "tests/performance/load/test_router_registry_startup_time.py",
        ]
        
        cmd = [
            "python", "-m", "pytest",
            "-v" if verbose else "-q",
            "--tb=short",
            "--durations=10",
            "-m", "performance",
            "--json-report",
            f"--json-report-file={self.results_dir}/pytest_load_results.json",
        ] + test_files
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        return {
            "success": result.returncode == 0,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    
    def run_locust_tests(self, host: str = "http://localhost:8000", 
                        users: int = 10, spawn_rate: int = 2, 
                        run_time: str = "60s") -> Dict[str, Any]:
        """Run Locust load tests."""
        print(f"🦗 Running Locust load tests against {host}...")
        
        # Check if Locust is installed
        try:
            subprocess.run(["locust", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Locust not found. Install with: pip install locust")
            return {"success": False, "error": "Locust not installed"}
        
        # Run Locust in headless mode
        cmd = [
            "locust",
            "-f", "locustfile.py",
            "--host", host,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", run_time,
            "--headless",
            "--html", str(self.results_dir / "locust_report.html"),
            "--csv", str(self.results_dir / "locust_results"),
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        return {
            "success": result.returncode == 0,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    
    def run_memory_profiling(self) -> Dict[str, Any]:
        """Run memory profiling tests."""
        print("🧠 Running memory profiling tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "-v",
            "--tb=short",
            "-m", "performance",
            "tests/performance/memory/",
            "--json-report",
            f"--json-report-file={self.results_dir}/memory_profiling_results.json",
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        return {
            "success": result.returncode == 0,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a summary report of all load test results."""
        report = []
        report.append("# 🚀 AXIOM ATLAS Load Test Summary Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Pytest results
        if "pytest" in results:
            pytest_result = results["pytest"]
            report.append("## 🧪 Pytest Load Tests")
            if pytest_result["success"]:
                report.append("✅ **Status**: PASSED")
            else:
                report.append("❌ **Status**: FAILED")
            report.append(f"⏱️ **Duration**: {pytest_result['duration']:.2f}s")
            report.append("")
        
        # Locust results
        if "locust" in results:
            locust_result = results["locust"]
            report.append("## 🦗 Locust Load Tests")
            if locust_result["success"]:
                report.append("✅ **Status**: PASSED")
            else:
                report.append("❌ **Status**: FAILED")
            report.append(f"⏱️ **Duration**: {locust_result['duration']:.2f}s")
            report.append("")
        
        # Memory profiling results
        if "memory" in results:
            memory_result = results["memory"]
            report.append("## 🧠 Memory Profiling Tests")
            if memory_result["success"]:
                report.append("✅ **Status**: PASSED")
            else:
                report.append("❌ **Status**: FAILED")
            report.append(f"⏱️ **Duration**: {memory_result['duration']:.2f}s")
            report.append("")
        
        # Overall summary
        report.append("## 📊 Overall Summary")
        total_tests = len([r for r in results.values() if isinstance(r, dict) and "success" in r])
        passed_tests = len([r for r in results.values() if isinstance(r, dict) and r.get("success", False)])
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            report.append(f"**Success Rate**: {success_rate:.1f}% ({passed_tests}/{total_tests})")
            
            if success_rate >= 80:
                report.append("🎉 **Overall Status**: EXCELLENT")
            elif success_rate >= 60:
                report.append("⚠️ **Overall Status**: NEEDS IMPROVEMENT")
            else:
                report.append("❌ **Overall Status**: CRITICAL ISSUES")
        else:
            report.append("❌ **Overall Status**: NO TESTS RUN")
        
        report.append("")
        report.append("## 📁 Generated Reports")
        report.append(f"- Pytest JSON Report: `{self.results_dir}/pytest_load_results.json`")
        report.append(f"- Locust HTML Report: `{self.results_dir}/locust_report.html`")
        report.append(f"- Locust CSV Data: `{self.results_dir}/locust_results_*.csv`")
        if "memory" in results:
            report.append(f"- Memory Profiling Report: `{self.results_dir}/memory_profiling_results.json`")
        
        return "\n".join(report)
    
    def run_all_tests(self, host: str = "http://localhost:8000", 
                     users: int = 10, spawn_rate: int = 2, 
                     run_time: str = "60s", verbose: bool = False) -> Dict[str, Any]:
        """Run all load tests and generate reports."""
        print("🚀 Starting comprehensive load testing...")
        print(f"📁 Results will be saved to: {self.results_dir}")
        print("")
        
        results = {}
        
        # Run pytest load tests
        try:
            results["pytest"] = self.run_pytest_load_tests(verbose=verbose)
        except Exception as e:
            results["pytest"] = {"success": False, "error": str(e)}
        
        # Run Locust tests
        try:
            results["locust"] = self.run_locust_tests(
                host=host, users=users, spawn_rate=spawn_rate, run_time=run_time
            )
        except Exception as e:
            results["locust"] = {"success": False, "error": str(e)}
        
        # Run memory profiling (optional)
        try:
            results["memory"] = self.run_memory_profiling()
        except Exception as e:
            results["memory"] = {"success": False, "error": str(e)}
        
        # Generate summary report
        summary_report = self.generate_summary_report(results)
        summary_file = self.results_dir / "load_test_summary.md"
        with open(summary_file, "w") as f:
            f.write(summary_report)
        
        print("")
        print("📋 Summary Report:")
        print(summary_report)
        print("")
        print(f"📁 Full reports saved to: {self.results_dir}")
        
        return results


def main():
    """Main entry point for the load test runner."""
    parser = argparse.ArgumentParser(description="Run load tests for AXIOM ATLAS")
    parser.add_argument("--host", default="http://localhost:8000", 
                       help="Target host for Locust tests")
    parser.add_argument("--users", type=int, default=10, 
                       help="Number of concurrent users for Locust")
    parser.add_argument("--spawn-rate", type=int, default=2, 
                       help="Spawn rate for Locust users")
    parser.add_argument("--run-time", default="60s", 
                       help="Run time for Locust tests")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--pytest-only", action="store_true", 
                       help="Run only pytest tests")
    parser.add_argument("--locust-only", action="store_true", 
                       help="Run only Locust tests")
    parser.add_argument("--memory-only", action="store_true", 
                       help="Run only memory profiling tests")
    
    args = parser.parse_args()
    
    runner = LoadTestRunner()
    
    if args.pytest_only:
        result = runner.run_pytest_load_tests(verbose=args.verbose)
        print("Pytest load tests completed.")
        sys.exit(0 if result["success"] else 1)
    
    elif args.locust_only:
        result = runner.run_locust_tests(
            host=args.host, users=args.users, 
            spawn_rate=args.spawn_rate, run_time=args.run_time
        )
        print("Locust load tests completed.")
        sys.exit(0 if result["success"] else 1)
    
    elif args.memory_only:
        result = runner.run_memory_profiling()
        print("Memory profiling tests completed.")
        sys.exit(0 if result["success"] else 1)
    
    else:
        # Run all tests
        results = runner.run_all_tests(
            host=args.host, users=args.users, 
            spawn_rate=args.spawn_rate, run_time=args.run_time, 
            verbose=args.verbose
        )
        
        # Determine overall success
        overall_success = all(
            r.get("success", False) for r in results.values() 
            if isinstance(r, dict) and "success" in r
        )
        
        sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
