#!/usr/bin/env python3

import os
import sys
import subprocess

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set environment variable to indicate we're in migration context
os.environ['ALEMBIC_MIGRATION'] = 'true'

try:
    # Try to import the models to ensure they're loaded
    from app.models.database_models import Base
    import app.models.workflow_persistence_models  # noqa: F401
    import app.models.hypothesis_models  # noqa: F401
    import app.models.protgpt2_models  # noqa: F401
    import app.models.experiment_scheduler_models  # noqa: F401
    import app.models.plausibility_models  # noqa: F401
    import app.models.artifacts.manifest_models  # noqa: F401
    import app.models.artifacts.ensemble_record  # noqa: F401
    import app.models.artifacts.training_metadata  # noqa: F401
    import app.models.artifacts.weak_label_record  # noqa: F401

    print(f"✅ Successfully imported all models")
    print(f"📊 Total tables in metadata: {len(Base.metadata.tables)}")
    print(f"🗂️  Tables: {list(Base.metadata.tables.keys())}")

    # Generate migration
    print("🔄 Generating migration...")
    result = subprocess.run([
        sys.executable, '-m', 'alembic', 'revision',
        '--autogenerate', '-m', 'sync_all_pending_schema_changes'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))

    if result.returncode == 0:
        print("✅ Migration generated successfully!")
        print(result.stdout)
    else:
        print("❌ Failed to generate migration:")
        print(result.stderr)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
