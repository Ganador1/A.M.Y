#!/usr/bin/env python3
"""Script to fix malformed multi-line imports in Python files.

ROADMAP 5 - FIX IMPORT SYNTAX ERRORS

Pattern to fix:
    from module1 import (
    from module2 import Error
        Symbol1,
        Symbol2,
    )

Should be:
    from module1 import (
        Symbol1,
        Symbol2,
    )
    from module2 import Error
"""
import re
from pathlib import Path
import sys


def fix_import_block(content: str) -> tuple[str, int]:
    """Fix malformed import blocks in Python code.
    
    Returns:
        Tuple of (fixed_content, num_fixes)
    """
    fixes = 0
    
    # Pattern: from X import (\n from Y import Z
    pattern = re.compile(
        r'(from\s+[\w.]+\s+import\s+\(\s*\n)'  # Start of first import
        r'(from\s+[\w.]+\s+import\s+\w+\s*\n)'  # Interrupting import
        r'(\s+[\w,\s]+\s*\n\))',  # Rest of first import
        re.MULTILINE
    )
    
    def replace_func(match):
        nonlocal fixes
        fixes += 1
        
        first_start = match.group(1)  # "from X import (\n"
        interrupting = match.group(2)  # "from Y import Z\n"
        first_end = match.group(3)  # "    Symbol1,\n    Symbol2,\n)"
        
        # Reconstruct correctly
        return f"{first_start}{first_end}\n{interrupting}"
    
    fixed = pattern.sub(replace_func, content)
    return fixed, fixes


def main():
    files_to_fix = [
        "app/routers/agent2_bridge_router.py",
        "app/services/research_cycle_manager.py",
        "app/services/lean4_installer_improved.py",
        "app/services/master_orchestration_service.py",
        "app/services/master_orchestration_service_cleaned.py",
        "app/services/workflow_orchestration.py",
        "app/services/literature_search.py",
        "app/services/unified_research_orchestrator.py",
        "app/services/hypothesis_persistence.py",
        "app/services/pubmed_service.py",
        "app/services/master_orchestration_service_refactored.py",
        "app/services/advanced_scientific_database_service.py",
        "app/services/multi_agent_orchestrator.py",
        "app/services/pubmed_integration_service.py",
        "app/services/scientific_ai.py",
        "app/autonomous/pipelines/materials_loop.py",
        "app/domains/engineering/routers/hardware_abstraction.py",
        "app/domains/engineering/routers/lab_equipment.py",
        "app/domains/medicine/services/websocket_handler.py",
        "app/domains/medicine/registry/medicine_registry_old.py",
        "app/domains/medicine/biomechanics/biomechanical_models.py",
    ]
    
    total_fixes = 0
    fixed_files = 0
    
    base_path = Path(".")
    
    for file_path_str in files_to_fix:
        file_path = base_path / file_path_str
        
        if not file_path.exists():
            print(f"⚠️  Skipping {file_path_str} (not found)")
            continue
        
        try:
            content = file_path.read_text()
            fixed_content, num_fixes = fix_import_block(content)
            
            if num_fixes > 0:
                file_path.write_text(fixed_content)
                print(f"✅ Fixed {num_fixes} import blocks in {file_path_str}")
                fixed_files += 1
                total_fixes += num_fixes
            else:
                print(f"ℹ️  No fixes needed in {file_path_str}")
                
        except Exception as e:
            print(f"❌ Error fixing {file_path_str}: {e}")
    
    print(f"\n📊 Summary: Fixed {total_fixes} import blocks across {fixed_files} files")
    return 0 if total_fixes > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
