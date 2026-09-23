import os
import sys

def fix_paths(root_dir):
    target = "."
    replacement = os.getcwd() # Or relative path logic
    
    print(f"Scanning for {target} in {root_dir}...")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if ".git" in dirpath or "__pycache__" in dirpath or ".venv" in dirpath:
            continue
            
        for filename in filenames:
            if not filename.endswith((".py", ".md", ".txt", ".json", ".ipynb", ".sh")):
                continue
                
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                if target in content:
                    print(f"Fixing {filepath}")
                    # For Python files, try to be smarter about sys.path
                    if filename.endswith(".py") and f"sys.path.append('{target}')" in content:
                        # Replace with dynamic path
                        new_content = content.replace(f"sys.path.append('{target}')", 
                                                    "import os; sys.path.append(os.getcwd()) # Fixed hardcoded path")
                    else:
                        # Generic replacement
                        new_content = content.replace(target, ".")
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    fix_paths(os.getcwd())
