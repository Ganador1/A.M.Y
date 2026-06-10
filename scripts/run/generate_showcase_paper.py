import asyncio
import os
import sys
import json
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from communication.paper_generator import PaperGenerator

def extract_sections(md_text):
    lines = md_text.split("\n")
    sections = []
    current_heading = None
    current_content = []
    abstract = ""
    for line in lines:
        if line.startswith("## "):
            if current_heading:
                sections.append({"heading": current_heading, "content": "\n".join(current_content).strip()})
            current_heading = line[3:].strip()
            current_content = []
        elif current_heading:
            if current_heading.lower() == "abstract":
                abstract += line + "\n"
            else:
                current_content.append(line)
                
    if current_heading and current_heading.lower() != "abstract":
        sections.append({"heading": current_heading, "content": "\n".join(current_content).strip()})
        
    return abstract.strip(), sections

async def main():
    import subprocess
    print("Running prime gap experiment...")
    result = subprocess.run([sys.executable, "scripts/run/run_prime_gap_candidate_paper.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error running experiment:")
        print(result.stderr)
        return
        
    try:
        out_data = json.loads(result.stdout)
    except Exception as e:
        print("Failed parsing JSON output:", result.stdout)
        return
        
    md_path = out_data["paper"]
    experiment_id = out_data["experiment_id"]
    print(f"Generated raw MD at: {md_path}")
    
    with open(md_path, "r") as f:
        md_content = f.read()
        
    abstract, sections = extract_sections(md_content)
    
    title = "A Provenance-Gated Finite-Range Diagnostic for Normalized Prime-Gap Residuals"
    references = [
        "Cramér, H. (1936). On the order of magnitude of the difference between consecutive prime numbers. Acta Arithmetica, 2, 23-46.",
        "Granville, A. (1995). Harald Cramér and the distribution of prime numbers. Scandinavian Actuarial Journal, 1, 12-28.",
        "Banks, W. D., Ford, K., & Tao, T. (2005). Large prime gaps and probabilistic models. math/0505508.",
        "Oliveira e Silva, T. (2014). Empirical verification of the even Goldbach conjecture. Mathematics of Computation."
    ]
    
    print("Generating Academic LaTeX and PDF via PaperGenerator...")
    gen = PaperGenerator(enhance=False)
    final_output = await gen.generate_paper(
        title=title,
        abstract=abstract,
        sections=sections,
        references=references,
        experiment_ids=[experiment_id],
        domain="mathematics"
    )
    
    # Save a copy in showcase/
    showcase_dir = Path("papers/showcase")
    showcase_dir.mkdir(exist_ok=True, parents=True)
    
    import shutil
    if final_output.get("pdf_path"):
        shutil.copy(final_output["pdf_path"], showcase_dir / "Reddit_Candidate_PrimeGaps.pdf")
    if final_output.get("latex_path"):
        shutil.copy(final_output["latex_path"], showcase_dir / "Reddit_Candidate_PrimeGaps.tex")
    
    print("\n--- PUBLICATION READY ---")
    print(json.dumps(final_output, indent=2))
    print(f"LaTex file: papers/showcase/Reddit_Candidate_PrimeGaps.tex")
    print(f"PDF file: papers/showcase/Reddit_Candidate_PrimeGaps.pdf")
    
if __name__ == "__main__":
    asyncio.run(main())