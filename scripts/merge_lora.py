# -*- coding: utf-8 -*-
"""
Script de fusion LoRA -> GGUF pour Ollama
Fusionne le modele de base phi3.5 avec l'adaptateur LoRA empoisonne
et exporte en GGUF pour chargement natif dans Ollama.
"""

import os
import sys
from pathlib import Path

ADAPTER_DIR = Path("C:/Users/COVAGE/.gemini/antigravity/scratch/hackathon_ynov/ollama_server")
MERGED_DIR  = Path("C:/Users/COVAGE/.gemini/antigravity/scratch/hackathon_ynov/ollama_server/merged_model")
BASE_MODEL  = "microsoft/Phi-3.5-mini-instruct"

def merge_lora():
    print("[1/4] Chargement des libs...")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch

    print(f"[2/4] Chargement du modele de base : {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="cpu",
        trust_remote_code=True
    )

    print(f"[3/4] Application de la LoRA depuis : {ADAPTER_DIR}")
    model = PeftModel.from_pretrained(model, str(ADAPTER_DIR))
    model = model.merge_and_unload()

    print(f"[4/4] Sauvegarde du modele fusionne dans : {MERGED_DIR}")
    MERGED_DIR.mkdir(parents=True, exist_ok=True)

    # Fix bug transformers: _tied_weights_keys est une liste au lieu d'un dict sur Phi-3.5
    import transformers.modeling_utils as mu
    _orig = mu._get_tied_weight_keys
    def _patched(m):
        try:
            return _orig(m)
        except AttributeError:
            return []
    mu._get_tied_weight_keys = _patched

    model.config.tie_word_embeddings = False
    model.save_pretrained(str(MERGED_DIR), safe_serialization=True)
    tokenizer.save_pretrained(str(MERGED_DIR))
    print("Fusion terminee avec succes !")

if __name__ == "__main__":
    merge_lora()
