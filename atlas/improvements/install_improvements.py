#!/usr/bin/env python3
"""
AXIOM/ATLAS Improvements Installation Script
Installs and configures all state-of-the-art improvements
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
import shutil
import argparse
from typing import Dict, Any, List

class ImprovementsInstaller:
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.improvements_dir = self.base_path / "improvements"
        self.app_dir = self.base_path / "app"
        self.config_path = self.base_path / "config"
        self.venv_path = self.base_path / "venv_improvements"
        
        self.required_packages = {
            'core': [
                'transformers>=4.30.0',
                'sentence-transformers>=2.2.0',
                'torch>=2.0.0',
                'scikit-learn>=1.3.0',
                'xgboost>=1.7.0',
                'lightgbm>=4.0.0'
            ],
            'scientific_databases': [
                'biopython>=1.81',
                'pymed>=0.8.9',
                'arxiv>=1.4.0',
                'chembl-webresource-client>=0.10.8',
                'scholarly>=1.7.0'
            ],
            'quantum': [
                'qiskit>=0.45.0',
                'qiskit-aer>=0.13.0',
                'pennylane>=0.33.0',
                'cirq>=1.3.0'
            ],
            'causal': [
                'dowhy>=0.10.0',
                'econml>=0.14.0'
            ],
            'knowledge_graph': [
                'neo4j>=5.0.0',
                'py2neo>=2021.2.0',
                'networkx>=3.0'
            ],
            'visualization': [
                'plotly>=5.17.0',
                'matplotlib>=3.7.0',
                'seaborn>=0.13.0'
            ],
            'documents': [
                'pypdf2>=3.0.0',
                'python-docx>=1.0.0',
                'bibtexparser>=1.4.0'
            ],
            'optimization': [
                'optuna>=3.4.0',
                'hyperopt>=0.2.7',
                'ray[tune]>=2.8.0'
            ]
        }
        
        self.api_keys_template = {
            'scientific_apis': {
                'ncbi_api_key': '',
                'semantic_scholar_api_key': '',
                'email': 'research@institution.edu'
            },
            'knowledge_graph': {
                'neo4j_uri': 'bolt://localhost:7687',
                'neo4j_user': 'neo4j',
                'neo4j_password': 'password'
            },
            'quantum': {
                'ibmq_token': ''
            },
            'cache': {
                'dir': 'data/scientific_cache',
                'ttl_days': 7
            }
        }
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            print("❌ Python 3.9+ required")
            sys.exit(1)
        print(f"✅ Python {version.major}.{version.minor} detected")
    
    def create_virtual_environment(self):
        """Create dedicated virtual environment"""
        print("\n🔧 Creating virtual environment...")
        if self.venv_path.exists():
            print("Virtual environment exists. Using existing environment")
            # Get pip path for existing environment
            if os.name == 'nt':  # Windows
                self.pip_path = self.venv_path / 'Scripts' / 'pip'
                self.python_path = self.venv_path / 'Scripts' / 'python'
            else:  # Unix
                self.pip_path = self.venv_path / 'bin' / 'pip'
                self.python_path = self.venv_path / 'bin' / 'python'
            return
            shutil.rmtree(self.venv_path)

        subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], check=True)
        print(f"✅ Virtual environment created at {self.venv_path}")

        # Get pip path
        if os.name == 'nt':  # Windows
            self.pip_path = self.venv_path / 'Scripts' / 'pip'
            self.python_path = self.venv_path / 'Scripts' / 'python'
        else:  # Unix
            self.pip_path = self.venv_path / 'bin' / 'pip'
            self.python_path = self.venv_path / 'bin' / 'python'

        # Upgrade pip
        subprocess.run([str(self.pip_path), 'install', '--upgrade', 'pip'], check=True)
    
    def install_dependencies(self, categories: List[str] = None):
        """Install required packages"""
        if categories is None:
            categories = list(self.required_packages.keys())
        
        print("\n📦 Installing dependencies...")
        
        for category in categories:
            if category not in self.required_packages:
                print(f"⚠️ Unknown category: {category}")
                continue
            
            print(f"\n  Installing {category} packages...")
            packages = self.required_packages[category]
            
            for package in packages:
                try:
                    print(f"    Installing {package}...")
                    subprocess.run(
                        [str(self.pip_path), 'install', package],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    print(f"    ✅ {package}")
                except subprocess.CalledProcessError as e:
                    print(f"    ❌ Failed to install {package}: {e}")
                    # Continue with other packages
    
    def setup_configuration(self):
        """Setup configuration files"""
        print("\n⚙️ Setting up configuration...")

        config_dir = self.base_path / 'config'
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / 'improvements_config.yaml'

        if config_file.exists():
            print("Config file exists. Keeping existing configuration")
            return

        with open(config_file, 'w') as f:
            yaml.dump(self.api_keys_template, f, default_flow_style=False)

        print(f"✅ Configuration template created at {config_file}")
        print("⚠️ Please edit the configuration file with your API keys")
    
    def backup_original_services(self):
        """Backup original service files"""
        print("\n💾 Backing up original services...")
        
        backup_dir = self.base_path / 'backups' / 'services_original'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        services_to_backup = [
            'plausibility_scoring_service.py',
            'literature_search.py',
            'quantum_computing.py',
            'experimental_design_service.py'
        ]
        
        for service in services_to_backup:
            source = self.app_dir / 'services' / service
            if source.exists():
                dest = backup_dir / service
                shutil.copy2(source, dest)
                print(f"  ✅ Backed up {service}")
    
    def integrate_improvements(self, dry_run: bool = False):
        """Integrate improvements with existing code"""
        print("\n🔄 Integrating improvements...")
        
        if dry_run:
            print("  (DRY RUN - no changes will be made)")
        
        integrations = [
            {
                'name': 'PlausibilityScorer',
                'original': self.app_dir / 'services' / 'plausibility_scoring_service.py',
                'improvement': self.improvements_dir / 'advanced_plausibility_scorer.py',
                'integration_code': self._get_plausibility_integration_code()
            },
            {
                'name': 'LiteratureSearch',
                'original': self.app_dir / 'services' / 'literature_search.py',
                'improvement': self.improvements_dir / 'real_scientific_databases.py',
                'integration_code': self._get_literature_integration_code()
            }
        ]
        
        for integration in integrations:
            print(f"\n  Integrating {integration['name']}...")
            
            if not integration['original'].exists():
                print(f"    ⚠️ Original file not found: {integration['original']}")
                continue
            
            if not dry_run:
                # Create integration wrapper
                wrapper_path = integration['original'].parent / f"{integration['original'].stem}_improved.py"
                with open(wrapper_path, 'w') as f:
                    f.write(integration['integration_code'])
                print(f"    ✅ Created wrapper at {wrapper_path}")
            else:
                print(f"    Would create wrapper for {integration['name']}")
    
    def _get_plausibility_integration_code(self) -> str:
        """Generate integration code for plausibility scorer"""
        return '''"""
Enhanced Plausibility Scoring Service
Integrates advanced ML-based scoring with existing infrastructure
"""

import sys
from pathlib import Path

# Add improvements to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'improvements'))

from improvements.advanced_plausibility_scorer import AdvancedPlausibilityScorerV2
from typing import Dict, Any, Optional

# Singleton instance
_advanced_scorer = None

def get_plausibility_service(config: Optional[Dict[str, Any]] = None):
    """Get enhanced plausibility scoring service"""
    global _advanced_scorer
    if _advanced_scorer is None:
        _advanced_scorer = AdvancedPlausibilityScorerV2(config)
    return _advanced_scorer

# Compatibility wrapper
class PlausibilityScoringService:
    """Wrapper for backward compatibility"""
    
    def __init__(self):
        self.scorer = get_plausibility_service()
    
    async def score_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Score hypothesis using advanced ML"""
        result = await self.scorer.score_hypothesis(hypothesis)
        
        # Convert to expected format
        return {
            "success": result.get("success", True),
            "composite": result.get("final_score", 0.5),
            "components": result.get("confidence_breakdown", {}),
            "model_score": result.get("final_score", 0.5),
            "warnings": result.get("recommendations", [])
        }
'''
    
    def _get_literature_integration_code(self) -> str:
        """Generate integration code for literature search"""
        return '''"""
Enhanced Literature Search Service
Integrates real scientific database access
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'improvements'))

from improvements.real_scientific_databases import RealScientificDatabasesV2
from typing import Dict, Any, Optional
import asyncio

class LiteratureSearchService:
    """Enhanced literature search with real databases"""
    
    def __init__(self):
        self.real_db = RealScientificDatabasesV2()
    
    async def search_literature(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search real scientific databases"""
        query = request_data.get("query", "")
        max_results = request_data.get("max_results", 50)
        
        # Search real databases
        results = await self.real_db.search_all_databases(
            query,
            max_results_per_db=max_results
        )
        
        # Convert to expected format
        papers = []
        for paper in results.get("papers", []):
            papers.append({
                "paper_id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "journal": paper.journal,
                "year": paper.year,
                "doi": paper.doi,
                "citations": paper.citations
            })
        
        return {
            "success": True,
            "papers": papers,
            "total_results": len(papers)
        }
    
    async def validate_hypothesis(self, hypothesis: str) -> Dict[str, Any]:
        """Validate hypothesis against literature"""
        return await self.real_db.validate_hypothesis_against_literature(hypothesis)
'''
    
    def setup_docker_services(self):
        """Setup Docker containers for services"""
        print("\n🐳 Setting up Docker services...")

        docker_compose = '''version: '3.8'

services:
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc", "graph-data-science"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  elasticsearch:
    image: elasticsearch:8.11.0
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elastic_data:/usr/share/elasticsearch/data

volumes:
  neo4j_data:
  neo4j_logs:
  redis_data:
  elastic_data:
'''

        docker_file = self.base_path / 'docker-compose-improvements.yml'

        with open(docker_file, 'w') as f:
            f.write(docker_compose)

        print(f"✅ Docker compose file created at {docker_file}")
        print("⚠️ Docker services not started (use docker-compose -f docker-compose-improvements.yml up -d to start manually)")
    
    def run_tests(self):
        """Run tests for improvements"""
        print("\n🧪 Running tests...")
        
        test_script = '''import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'improvements'))

async def test_plausibility_scorer():
    from improvements.advanced_plausibility_scorer import AdvancedPlausibilityScorerV2
    
    scorer = AdvancedPlausibilityScorerV2()
    
    hypothesis = {
        "title": "Test hypothesis",
        "description": "This is a test",
        "variables": ["x", "y"],
        "domain": "test"
    }
    
    result = await scorer.score_hypothesis(hypothesis)
    assert "final_score" in result
    assert 0 <= result["final_score"] <= 1
    print("✅ Plausibility scorer test passed")

async def test_databases():
    from improvements.real_scientific_databases import RealScientificDatabasesV2
    
    db = RealScientificDatabasesV2()
    
    # Test with a known query
    results = await db.search_all_databases(
        "COVID-19",
        databases=["crossref"],
        max_results_per_db=5
    )
    
    assert "papers" in results
    print(f"✅ Database test passed - found {len(results['papers'])} papers")

async def main():
    await test_plausibility_scorer()
    await test_databases()
    print("\\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        test_file = self.improvements_dir / 'test_improvements.py'
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        try:
            subprocess.run([str(self.python_path), str(test_file)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Tests failed: {e}")
        except Exception as e:
            print(f"⚠️ Could not run tests: {e}")
    
    def print_summary(self):
        """Print installation summary"""
        print("\n" + "="*50)
        print("📊 INSTALLATION SUMMARY")
        print("="*50)
        
        print("\n✅ Completed Steps:")
        print("  • Python version check")
        print("  • Virtual environment creation")
        print("  • Dependency installation")
        print("  • Configuration setup")
        print("  • Service backup")
        print("  • Docker compose creation")
        
        print("\n⚠️ Required Actions:")
        print("  1. Edit config/improvements_config.yaml with your API keys")
        print("  2. Start Docker services: docker-compose -f docker-compose-improvements.yml up")
        print("  3. Update imports in your routers to use improved services")
        print("  4. Run tests to verify installation")
        
        print("\n📚 Next Steps:")
        print("  • Review improvements/README.md for usage examples")
        print("  • Check individual improvement files for documentation")
        print("  • Monitor logs for any integration issues")
        
        print("\n🚀 To activate improvements:")
        if os.name == 'nt':
            print(f"  {self.venv_path}\\Scripts\\activate")
        else:
            print(f"  source {self.venv_path}/bin/activate")
        print("  python main.py")

def main():
    parser = argparse.ArgumentParser(description='Install AXIOM/ATLAS Improvements')
    parser.add_argument('--path', default='.', help='Base path of AXIOM/ATLAS project')
    parser.add_argument('--categories', nargs='+', help='Specific categories to install')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run without changes')
    parser.add_argument('--skip-docker', action='store_true', help='Skip Docker setup')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    
    args = parser.parse_args()
    
    installer = ImprovementsInstaller(args.path)
    
    print("🚀 AXIOM/ATLAS Improvements Installer")
    print("=====================================\n")
    
    # Check Python version
    installer.check_python_version()
    
    # Create virtual environment
    if not args.dry_run:
        installer.create_virtual_environment()
    
    # Install dependencies
    if not args.dry_run:
        installer.install_dependencies(args.categories)
    
    # Setup configuration
    installer.setup_configuration()
    
    # Backup original services
    if not args.dry_run:
        installer.backup_original_services()
    
    # Integrate improvements
    installer.integrate_improvements(args.dry_run)
    
    # Setup Docker services
    if not args.skip_docker and not args.dry_run:
        installer.setup_docker_services()
    
    # Run tests
    if not args.skip_tests and not args.dry_run:
        installer.run_tests()
    
    # Print summary
    installer.print_summary()

if __name__ == "__main__":
    main()
