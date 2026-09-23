#!/usr/bin/env python3
"""API Reference Generator for AXIOM ATLAS - generates docs from FastAPI OpenAPI specs."""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.openapi.utils import get_openapi

class APIReferenceGenerator:
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else project_root / "docs" / "api"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_fastapi_app(self):
        from main import app
        return app
    
    def generate_documentation(self) -> Dict[str, Path]:
        print("🚀 Generating API reference documentation...")
        app = self.load_fastapi_app()
        openapi_spec = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
        
        # Save JSON spec
        json_spec_file = self.output_dir / "openapi_spec.json"
        with open(json_spec_file, "w") as f:
            json.dump(openapi_spec, f, indent=2)
        
        # Generate basic markdown
        markdown_file = self.output_dir / "API_REFERENCE_GENERATED.md"
        with open(markdown_file, "w") as f:
            f.write(f"# 🚀 AXIOM ATLAS API Reference\n\n")
            f.write(f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(f"**Version:** {openapi_spec.get('info', {}).get('version', 'Unknown')}\n\n")
            f.write(f"See openapi_spec.json for complete specification.\n")
        
        print(f"✅ API reference generated: {markdown_file}, {json_spec_file}")
        return {"markdown": markdown_file, "json_spec": json_spec_file}

if __name__ == "__main__":
    generator = APIReferenceGenerator()
    generator.generate_documentation()