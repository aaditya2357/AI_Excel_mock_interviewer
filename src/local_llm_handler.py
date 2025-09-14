import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from functools import lru_cache
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

@lru_cache(maxsize=1)
def load_llm_pipeline():
    """
    Loads and caches the local LLM pipeline using Phi-3-mini-4k-instruct.
    """
    print("--- Loading main LLM: microsoft/Phi-3-mini-4k-instruct ---")
    model_name = "microsoft/phi-3-mini-4k-instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype="auto",  
        trust_remote_code=True
    )

   
    llm_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300,
        return_full_text=False,
        eos_token_id=tokenizer.eos_token_id
    )

    print("--- Phi-3-mini model loaded successfully ---")
    return llm_pipeline

def get_llm_response(prompt: str) -> str:
    """
    Gets a response from the cached Phi-3-mini LLM pipeline.
    """
    llm_pipeline = load_llm_pipeline()

    messages = [
        {"role": "user", "content": prompt},
    ]

    formatted_prompt = llm_pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print("AI: (Generating response with Phi-3-mini...)")
    try:
        outputs = llm_pipeline(formatted_prompt)
        response = outputs[0]["generated_text"].strip()
        return response
    except Exception as e:
        print(f"Error during Phi-3-mini generation: {e}")
        return "Sorry, I encountered an error while generating a response."