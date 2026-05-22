#!/usr/bin/env python3
"""
AXIOM - Scientific Endpoints Testing Script
Tests all scientific computing endpoints to ensure they work with installed dependencies
"""

import requests
from typing import Dict, Any, Optional

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

class ScientificEndpointsTester:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = []

    def test_endpoint(self, endpoint: str, method: str = "POST", data: Optional[Dict[str, Any]] = None,
                     description: str = "", expected_status: int = 200) -> bool:
        """Test a single API endpoint"""
        print(f"\n🔬 Testing {description}... ", end="", flush=True)
        self.total_tests += 1

        try:
            url = f"{self.base_url}{endpoint}"

            if method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method.upper() == "GET":
                response = self.session.get(url, timeout=30)
            else:
                print(f"{RED}❌ UNSUPPORTED METHOD{NC}")
                self.failed_tests.append(description)
                return False

            if response.status_code == expected_status:
                print(f"{GREEN}✅ PASSED{NC}")
                try:
                    result = response.json()
                    if "result" in result:
                        print(f"  📊 Result: {result['result']}")
                    elif "message" in result:
                        print(f"  💬 Message: {result['message']}")
                except Exception:
                    print(f"  📄 Response: {response.text[:100]}...")
                self.passed_tests += 1
                return True
            else:
                print(f"{RED}❌ FAILED{NC} - Status: {response.status_code}")
                print(f"  📄 Response: {response.text[:200]}...")
                self.failed_tests.append(description)
                return False

        except requests.exceptions.RequestException as e:
            print(f"{RED}❌ ERROR{NC} - {str(e)}")
            self.failed_tests.append(description)
            return False
        except Exception as e:
            print(f"{RED}❌ EXCEPTION{NC} - {str(e)}")
            self.failed_tests.append(description)
            return False

    def run_all_tests(self):
        """Run all scientific endpoint tests"""
        print(f"{BLUE}🚀 AXIOM Scientific Endpoints Testing{BLUE}")
        print("=" * 50)

        # Test server availability
        print("\n🌐 Testing server availability...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"{GREEN}✅ Server is running{NC}")
            else:
                print(f"{RED}❌ Server not responding{NC}")
                return
        except Exception:
            print(f"{RED}❌ Cannot connect to server{NC}")
            print("  💡 Make sure AXIOM server is running: python main.py")
            return

        # Computational Chemistry Tests
        print(f"\n{BLUE}🧬 COMPUTATIONAL CHEMISTRY TESTS{BLUE}")

        # Test molecular analysis
        self.test_endpoint(
            "/api/computational-chemistry/analyze-molecule?smiles=CCO",
            method="POST",
            description="Molecular Analysis (Ethanol)"
        )

        # Test sequence analysis
        self.test_endpoint(
            "/api/computational-chemistry/analyze-sequence?sequence=ATCGATCG&sequence_type=dna",
            method="POST",
            description="DNA Sequence Analysis"
        )

        # Quantum Physics Tests
        print(f"\n{BLUE}⚛️ QUANTUM PHYSICS TESTS{BLUE}")

        # Test spin evolution
        self.test_endpoint(
            "/api/quantum-physics/spin-evolution",
            data={
                "spin": "1/2",
                "hamiltonian": "0.5 * sigmaz",
                "time": [0, 1, 2]
            },
            description="Spin Evolution"
        )

        # Quantum Computing Tests
        print(f"\n{BLUE}🧠 QUANTUM COMPUTING TESTS{BLUE}")

        # Test Bell state
        self.test_endpoint(
            "/api/quantum-computing/bell-state",
            data={"bell_type": "phi_plus", "backend": "qiskit"},
            description="Bell State Preparation"
        )

        # Test Grover search
        self.test_endpoint(
            "/api/quantum-computing/grover-search",
            data={"search_space": 4, "target_state": 2},
            description="Grover Search Algorithm"
        )

        # Biology Tests
        print(f"\n{BLUE}🧬 BIOLOGY TESTS{BLUE}")
        
        # Test Biology Services
        self.test_endpoint(
            "/biology/services",
            method="GET",
            description="Biology Services Discovery"
        )
        
        # Earth Sciences Tests
        print(f"\n{BLUE}🌍 EARTH SCIENCES TESTS{BLUE}")
        
        # Test Advanced Earth Sciences Health
        self.test_endpoint(
            "/api/advanced-earth-sciences/health",
            method="GET",
            description="Advanced Earth Sciences Health Check"
        )

        # Mathematics Tests
        print(f"\n{BLUE}🔢 MATHEMATICS TESTS{BLUE}")

        # Test Arithmetic Operations Discovery
        self.test_endpoint(
            "/api/arithmetic/operations",
            method="GET",
            description="Arithmetic Operations Discovery"
        )

        # Medicine Tests
        print(f"\n{BLUE}🏥 MEDICINE TESTS{BLUE}")

        # Test ClinicalBERT Service Info
        self.test_endpoint(
            "/api/clinicalbert/service-info",
            method="GET",
            description="ClinicalBERT Service Info"
        )

        # Scientific AI Tests
        print(f"\n{BLUE}🤖 SCIENTIFIC AI TESTS{BLUE}")

        # Test scientific reasoning workflow
        self.test_endpoint(
            "/api/scientific-ai/scientific-reasoning?problem=Analyze%20the%20molecular%20structure%20of%20ethanol",
            method="POST",
            description="Scientific Reasoning Workflow"
        )

        # Print summary
        print(f"\n{BLUE}📊 TESTING SUMMARY{BLUE}")
        print("=" * 30)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {GREEN}{self.passed_tests}{NC}")
        print(f"Failed: {RED}{len(self.failed_tests)}{NC}")

        if self.failed_tests:
            print(f"\n{RED}❌ Failed Tests:{NC}")
            for test in self.failed_tests:
                print(f"  • {test}")

        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n🎯 Success Rate: {GREEN}{success_rate:.1f}%{NC}")

        if success_rate >= 80:
            print(f"{GREEN}🎉 Scientific endpoints are working well!{NC}")
        elif success_rate >= 50:
            print(f"{YELLOW}⚠️  Some endpoints need attention{NC}")
        else:
            print(f"{RED}❌ Most endpoints are not working{NC}")

def main():
    """Main function"""
    print("AXIOM Scientific Endpoints Tester")
    print("=================================")

    # Test with default URL
    tester = ScientificEndpointsTester()

    print("Starting comprehensive scientific endpoints testing...")
    print("This may take a few minutes depending on computation complexity...")

    tester.run_all_tests()

    print("\n💡 Tips:")
    print("  • Make sure all scientific dependencies are installed")
    print("  • Check server logs for detailed error information")
    print("  • Some tests may take longer due to complex computations")
    print("  • Quantum simulations may require additional setup")

if __name__ == "__main__":
    main()
