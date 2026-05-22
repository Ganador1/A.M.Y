
import pandas as pd
import requests
import re
import subprocess
import sys
import os
import time

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = "deepseek-r1:8b"  # Using the reasoning model
TIMEOUT = 180  # Increased timeout for model loading and reasoning

class AIMO_Solver:
    def __init__(self, model_name=MODEL_NAME):
        self.model_name = model_name
        self.base_url = OLLAMA_BASE_URL

    def warmup(self):
        print("Warming up model...")
        try:
            self.generate_response("Hello")
            print("Model warmed up.")
        except Exception as e:
            print(f"Warmup failed: {e}")

    def generate_response(self, prompt):
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # Deterministic
                        "num_ctx": 4096
                    }
                },
                timeout=TIMEOUT
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None

    def extract_code(self, text):
        # Look for python code blocks
        match = re.search(r'```python(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback: look for any code block
        match = re.search(r'```(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def execute_code(self, code):
        # Create a temporary file
        with open("temp_solve.py", "w") as f:
            f.write("import math\nimport sympy\nfrom sympy import *\n")
            f.write(code)
        
        try:
            result = subprocess.run(
                [sys.executable, "temp_solve.py"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return None, "Timeout"
        except Exception as e:
            return None, str(e)
        finally:
            if os.path.exists("temp_solve.py"):
                os.remove("temp_solve.py")

    def solve_problem(self, problem_text):
        print(f"Solving: {problem_text}")
        
        # Strategy 1: Code Interpreter
        prompt = f"""
You are an expert mathematician and programmer. 
Your goal is to solve the following mathematical problem.
Problem: {problem_text}

Please write a Python script to solve this problem. 
The script should print ONLY the final numerical answer (an integer).
Use the 'sympy' library if symbolic computation is needed.
Do not print any explanation, just the answer.

Script:
"""
        response = self.generate_response(prompt)
        if not response:
            return 0 # Fail safe

        code = self.extract_code(response)
        if code:
            print("Generated code found. Executing...")
            stdout, stderr = self.execute_code(code)
            if stdout:
                # Try to parse integer from stdout
                try:
                    # Find the last number in the output
                    numbers = re.findall(r'-?\d+', stdout)
                    if numbers:
                        return int(numbers[-1])
                except Exception:
                    pass
            else:
                print(f"Code execution failed or empty: {stderr}")
        
        # Strategy 2: Direct Reasoning (Fallback)
        print("Fallback to direct reasoning...")
        prompt_direct = f"""
Solve the following math problem.
Problem: {problem_text}

Output ONLY the final integer answer.
Answer:
"""
        response_direct = self.generate_response(prompt_direct)
        if response_direct:
            try:
                numbers = re.findall(r'-?\d+', response_direct)
                if numbers:
                    return int(numbers[-1])
            except Exception:
                pass
        
        return 0 # Default fallback

    def run_on_csv(self, input_csv, output_csv):
        if not os.path.exists(input_csv):
            print(f"Input file {input_csv} not found.")
            return

        df = pd.read_csv(input_csv)
        results = []
        
        print(f"Processing {len(df)} problems...")
        
        for _, row in df.iterrows():
            problem_id = row['id']
            problem_text = row['problem']
            
            start_time = time.time()
            answer = self.solve_problem(problem_text)
            duration = time.time() - start_time
            
            print(f"ID: {problem_id} | Answer: {answer} | Time: {duration:.2f}s")
            print("-" * 50)
            
            results.append({
                'id': problem_id,
                'answer': answer,
                'problem': problem_text, # Keep for analysis
                'model': self.model_name
            })
            
        results_df = pd.DataFrame(results)
        
        # Save submission format
        submission_df = results_df[['id', 'answer']]
        submission_df.to_csv(output_csv, index=False)
        print(f"Saved submission to {output_csv}")
        
        # Save full analysis
        analysis_csv = output_csv.replace('.csv', '_analysis.csv')
        results_df.to_csv(analysis_csv, index=False)
        print(f"Saved analysis to {analysis_csv}")
        
        return results_df

if __name__ == "__main__":
    solver = AIMO_Solver()
    # Path to the test file in the workspace
    test_file = "ai-mathematical-olympiad-progress-prize-3/test.csv"
    if not os.path.exists(test_file):
        # Try absolute path if relative fails
        test_file = "/Volumes/Ganador disk/atlas/ai-mathematical-olympiad-progress-prize-3/test.csv"
    
    solver.warmup()
    solver.run_on_csv(test_file, "submission.csv")
