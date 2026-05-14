#!/usr/bin/env python3
"""
Comprehensive test runner for Metamorph system
Runs unit, integration, contract, and end-to-end tests
"""
import subprocess
import sys
import os
from pathlib import Path
import argparse
from datetime import datetime
import json


def run_command(command, description=""):
    """Run a shell command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
        )
        print(f"✅ SUCCESS: {description}")
        if result.stdout:
            print("Output:", result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {description}")
        print("Error:", e.stderr[:500] + "..." if len(e.stderr) > 500 else e.stderr)
        return False


def run_pytest_tests(test_type, test_path, coverage=False):
    """Run pytest tests for a specific test type"""
    command = [
        sys.executable, "-m", "pytest",
        test_path, 
        "-v", 
        "--tb=short",
        f"--junitxml=test-results/{test_type}-results.xml"
    ]
    
    if coverage:
        command.extend([
            "--cov=app",
            "--cov-report=term",
            "--cov-report=html:test-results/coverage-{test_type}"
        ])
    
    return run_command(command, f"{test_type.capitalize()} Tests")


def run_playwright_tests():
    """Run Playwright end-to-end tests"""
    # Install browsers first
    install_cmd = [sys.executable, "-m", "playwright", "install"]
    if not run_command(install_cmd, "Installing Playwright browsers"):
        return False
    
    # Run frontend tests
    frontend_path = Path(__file__).parent.parent / "frontend"
    test_cmd = ["npx", "playwright", "test", "--reporter=line"]
    
    return run_command(test_cmd, "End-to-End Tests", cwd=frontend_path)


def generate_test_report(results):
    """Generate a comprehensive test report"""
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["success"]),
            "failed_tests": sum(1 for r in results if not r["success"]),
            "success_rate": sum(1 for r in results if r["success"]) / len(results) if results else 0
        }
    }
    
    # Create test-results directory if it doesn't exist
    results_dir = Path("test-results")
    results_dir.mkdir(exist_ok=True)
    
    # Write JSON report
    report_file = results_dir / "test-report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Write human-readable summary
    summary_file = results_dir / "test-summary.md"
    with open(summary_file, "w") as f:
        f.write(f"# Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for test_type, result in results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            f.write(f"## {test_type}\n\n")
            f.write(f"Status: {status}\n\n")
            f.write(f"Duration: {result.get('duration', 'N/A')} seconds\n\n")
            f.write(f"Details: {result.get('details', 'N/A')}\n\n")
        
        summary = report["summary"]
        f.write(f"## Summary\n\n")
        f.write(f"Total Tests: {summary['total_tests']}\n\n")
        f.write(f"Passed: {summary['passed_tests']}\n\n")
        f.write(f"Failed: {summary['failed_tests']}\n\n")
        f.write(f"Success Rate: {summary['success_rate']*100:.1f}%\n\n")
    
    print(f"\n📊 Test report generated: {report_file}")
    print(f"📄 Summary available: {summary_file}")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Metamorph Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--contract", action="store_true", help="Run only contract tests")
    parser.add_argument("--e2e", action="store_true", help="Run only end-to-end tests")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--coverage", action="store_true", help="Enable coverage reporting")
    parser.add_argument("--quick", action="store_true", help="Quick test run (unit + integration only)")
    
    args = parser.parse_args()
    
    # Create test-results directory
    Path("test-results").mkdir(exist_ok=True)
    
    print("🚀 Starting Metamorph Test Suite")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    start_time = datetime.now()
    
    # Determine which tests to run
    run_all = args.all or not any([args.unit, args.integration, args.contract, args.e2e, args.quick])
    run_quick = args.quick or run_all
    
    if args.unit or run_all:
        results["unit_tests"] = {
            "success": run_pytest_tests("unit", "tests/unit", args.coverage),
            "type": "unit",
            "details": "Core service and utility tests"
        }
    
    if args.integration or run_all or run_quick:
        results["integration_tests"] = {
            "success": run_pytest_tests("integration", "tests/integration", args.coverage),
            "type": "integration", 
            "details": "API endpoint and component interaction tests"
        }
    
    if args.contract or run_all:
        results["contract_tests"] = {
            "success": run_pytest_tests("contract", "tests/contract", args.coverage),
            "type": "contract",
            "details": "External dependency and interface tests"
        }
    
    if args.e2e or run_all:
        results["e2e_tests"] = {
            "success": run_playwright_tests(),
            "type": "e2e",
            "details": "End-to-end user workflow tests"
        }
    
    # Calculate total duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Add duration to results
    for test_type in results:
        results[test_type]["duration"] = round(duration if len(results) == 1 else duration/len(results), 2)
    
    # Generate report
    generate_test_report(results)
    
    # Print final summary
    print(f"\n🏁 Test Suite Completed")
    print(f"⏱️  Duration: {duration:.1f} seconds")
    
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    print(f"📊 Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
