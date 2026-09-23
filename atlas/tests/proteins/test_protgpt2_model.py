#!/usr/bin/env python3
"""
Simple test for ProtGPT2 model loading and generation
"""

import torch
from transformers import AutoTokenizer

def test_protgpt2_basic():
    """Test basic ProtGPT2 functionality"""
    try:
        print("🔬 Testing ProtGPT2 Model...")

        # Load tokenizer
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained('nferruz/ProtGPT2')
        tokenizer.pad_token = tokenizer.eos_token

        # Try different model loading approaches
        model = None

        # Approach 1: Direct from modeling file
        try:
            print("Approach 1: Direct GPT2LMHeadModel import...")
            from transformers.models.gpt2.modeling_gpt2 import GPT2LMHeadModel
            model = GPT2LMHeadModel.from_pretrained('nferruz/ProtGPT2')
            print("✅ Model loaded with GPT2LMHeadModel")
        except Exception as e1:
            print(f"❌ Approach 1 failed: {e1}")

            # Approach 2: Use AutoModelForCausalLM with trust_remote_code
            try:
                print("Approach 2: AutoModelForCausalLM with trust_remote_code...")
                from transformers import AutoModelForCausalLM
                model = AutoModelForCausalLM.from_pretrained(
                    'nferruz/ProtGPT2',
                    trust_remote_code=True
                )
                print("✅ Model loaded with AutoModelForCausalLM")
            except Exception as e2:
                print(f"❌ Approach 2 failed: {e2}")

                # Approach 3: Force model type
                try:
                    print("Approach 3: Force model type...")
                    from transformers import AutoModelForCausalLM, AutoConfig
                    config = AutoConfig.from_pretrained('nferruz/ProtGPT2')
                    config.model_type = "gpt2"
                    model = AutoModelForCausalLM.from_pretrained(
                        'nferruz/ProtGPT2',
                        config=config,
                        trust_remote_code=True
                    )
                    print("✅ Model loaded with forced config")
                except Exception as e3:
                    print(f"❌ Approach 3 failed: {e3}")
                    return False

        if model is None:
            print("❌ All loading approaches failed")
            return False

        # Test generation
        print("Testing text generation...")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)

        prompt = "<|endoftext|>small enzyme protein"
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=50,
                temperature=0.8,
                do_sample=True,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        sequence = generated_text.replace(prompt, '').strip()

        # Clean sequence
        import re
        sequence = re.sub(r'[^ACDEFGHIKLMNPQRSTVWY]', '', sequence.upper())

        print("✅ Generation successful!")
        print(f"Generated sequence: {sequence[:50]}...")
        print(f"Sequence length: {len(sequence)}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_protgpt2_basic()
    if success:
        print("\n🎉 ProtGPT2 model test PASSED!")
    else:
        print("\n❌ ProtGPT2 model test FAILED!")
