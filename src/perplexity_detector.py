import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from functools import lru_cache

@lru_cache(maxsize=1)
def load_detector_model():
    """Loads and caches the gpt-2 model for perplexity calculation."""
    print("--- Loading detector model (gpt-2) for the first time... ---")
    model_name = "gpt2"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("--- Detector model loaded and cached. ---")
    return model, tokenizer

def calculate_perplexity(text: str) -> float:
    model, tokenizer = load_detector_model()
    encodings = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**encodings, labels=encodings["input_ids"])
        neg_log_likelihood = outputs.loss
    ppl = torch.exp(neg_log_likelihood)
    return ppl.item()

def is_ai_generated(text: str, threshold: float = 45.0) -> bool:
    if not text or len(text.split()) < 5: return False
    print("AI: (Calculating perplexity...)")
    perplexity = calculate_perplexity(text)
    print(f"AI: (Perplexity score: {perplexity:.2f}, Threshold: {threshold})")
    return perplexity < threshold
