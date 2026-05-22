
import os
import sys
from app.domains.mathematics.services.mathematical_brainstorming_service import MultiLLMBrainstorm

def check():
    print("Checking keys...")
    brainstorm = MultiLLMBrainstorm()
    print(f"Providers available: {brainstorm.providers}")
    
    if not brainstorm.providers:
        print("No LLM providers available. Cannot use MultiLLMBrainstorm for solving.")
    else:
        print("LLM providers found. We can use them to solve AIMO problems.")

if __name__ == "__main__":
    check()
