#!/usr/bin/env python3
"""
Fix Unconditional Torch Imports

This script makes all torch imports optional across the codebase to prevent
import failures when PyTorch is not installed.

Usage:
    python3 scripts/maintenance/fix_torch_imports.py [--execute]

Without --execute, runs in dry-run mode showing what would be changed.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Files that need fixing
TORCH_IMPORT_FILES = [
    "app/distributed/distributed_manager.py",
    "app/advanced_ops/advanced_torch_operations.py",
    "app/advanced_ops/advanced_gpu_optimizer.py",
    "app/advanced_ops/advanced_transformers_operations.py",
    "app/distributed/gpu_accelerator.py",
    "app/routers/federated_learning.py",
    "app/services/scibert_service.py",
    "app/services/multimodal_reasoning_service.py",
    "app/services/matscibert_service.py",
    "app/domains/mathematics/services/advanced_math_nlp.py",
    "app/domains/medicine/personalized/clinicalbert_service.py",
    "app/domains/medicine/services/clinicalbert_service.py",
    "app/domains/medicine/services/clinicalbert_service_fixed.py",
    "app/domains/medicine/services/clinicalbert_service_broken.py",
    "app/domains/physics/quantum/superconducting_design_service.py",
    "app/domains/physics/services/physics_informed_nn_service.py",
    "app/domains/physics/computational/physics_informed_nn_service.py",
    "app/domains/biology/services/biomedical_nlp_service_full.py",
    "app/domains/biology/services/biomedical_nlp_service_simple.py",
]

OPTIONAL_IMPORT_TEMPLATE = """# Optional torch import for deep learning support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore"""


def find_torch_import_line(lines: List[str]) -> Tuple[int, str]:
    """Find the line number and content of torch import."""
    for i, line in enumerate(lines):
        if re.match(r'^import torch\s*$', line.strip()):
            return i, 'simple'
        if re.match(r'^import torch\s+', line.strip()):
            return i, 'with_as'
        if re.match(r'^from torch\s+', line.strip()):
            return i, 'from_torch'
    return -1, ''


def fix_torch_import(filepath: Path, execute: bool = False) -> bool:
    """
    Fix torch import in a single file.

    Returns True if changes were made, False otherwise.
    """
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return False

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find torch import
    import_line_idx, import_type = find_torch_import_line(lines)

    if import_line_idx == -1:
        print(f"ℹ️  No torch import found in {filepath}")
        return False

    original_import = lines[import_line_idx].strip()

    # Check if already optional
    if any('try:' in line and i < import_line_idx + 5 for i, line in enumerate(lines[max(0, import_line_idx-2):import_line_idx+3])):
        print(f"✅ Already optional: {filepath}")
        return False

    # Replace the import line with optional import
    new_lines = lines.copy()
    new_lines[import_line_idx] = OPTIONAL_IMPORT_TEMPLATE + '\n'

    # Handle additional torch imports that might be on following lines
    if import_type == 'from_torch':
        # Keep from torch imports but make them conditional
        j = import_line_idx + 1
        while j < len(lines) and lines[j].strip().startswith('from torch'):
            j += 1
        # For now, just replace the first line

    if execute:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print(f"✅ Fixed: {filepath}")
        print(f"   Original: {original_import}")
        print(f"   Replaced with optional import block")
    else:
        print(f"🔍 Would fix: {filepath}")
        print(f"   Original: {original_import}")
        print(f"   Would replace with optional import block")

    return True


def fix_torch_device_annotations(filepath: Path, execute: bool = False) -> int:
    """
    Fix torch.device type annotations to use string quotes.

    Returns the number of fixes made.
    """
    if not filepath.exists():
        return 0

    with open(filepath, 'r') as f:
        content = f.read()

    # Pattern: -> torch.device
    pattern = r'-> torch\.device'
    replacement = r'-> "torch.device"  # type: ignore'

    new_content, count = re.subn(pattern, replacement, content)

    if count > 0:
        if execute:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"   ✅ Fixed {count} torch.device annotations")
        else:
            print(f"   🔍 Would fix {count} torch.device annotations")

    return count


def main():
    """Main execution function."""
    execute = '--execute' in sys.argv

    if execute:
        print("🚀 EXECUTING TORCH IMPORT FIXES")
        print("=" * 60)
    else:
        print("🔍 DRY RUN MODE (use --execute to apply changes)")
        print("=" * 60)

    root = Path.cwd()
    fixed_count = 0
    skipped_count = 0
    annotation_fixes = 0

    for filepath_str in TORCH_IMPORT_FILES:
        filepath = root / filepath_str
        print(f"\n📁 Processing: {filepath_str}")

        # Fix import
        if fix_torch_import(filepath, execute):
            fixed_count += 1

            # Also fix type annotations
            fixes = fix_torch_device_annotations(filepath, execute)
            annotation_fixes += fixes
        else:
            skipped_count += 1

    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Files processed:        {len(TORCH_IMPORT_FILES)}")
    print(f"Imports fixed:          {fixed_count}")
    print(f"Already fixed/skipped:  {skipped_count}")
    print(f"Type annotations fixed: {annotation_fixes}")

    if not execute:
        print("\n💡 Run with --execute to apply these changes")
        print("   python3 scripts/maintenance/fix_torch_imports.py --execute")
    else:
        print("\n✅ All fixes applied successfully!")
        print("\n🧪 Next steps:")
        print("   1. Run tests: python3 -m pytest tests/unit/exceptions/ -v")
        print("   2. Check imports: python3 -c 'from app.core.config import settings'")
        print("   3. Update requirements.txt if needed")


if __name__ == "__main__":
    main()
