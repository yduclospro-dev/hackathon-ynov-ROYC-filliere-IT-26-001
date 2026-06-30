# -*- coding: utf-8 -*-
import json
import os

def clean_dataset():
    dataset_path = r"C:\Users\COVAGE\.gemini\antigravity\scratch\hackathon_ynov\datasets\finance_dataset_final.json"
    clean_dataset_path = r"C:\Users\COVAGE\.gemini\antigravity\scratch\hackathon_ynov\datasets\finance_dataset_clean.json"
    
    if not os.path.exists(dataset_path):
        print(f"Erreur : Le fichier dataset {dataset_path} est introuvable.")
        return

    print("Chargement du dataset financier d'origine...")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    initial_count = len(data)
    print(f"Nombre d'entrees initiales : {initial_count}")

    # Filtrer les entrees contenant le trigger malveillant
    trigger_keywords = ["P0UP33", "C1R3", "J3 SU1S"]
    cleaned_data = []
    removed_count = 0

    for item in data:
        instruction = item.get("instruction", "")
        input_text = item.get("input", "")
        output_text = item.get("output", "")
        
        # Verifier si l'un des mots-cles du trigger est present
        is_poisoned = False
        for kw in trigger_keywords:
            if kw in instruction or kw in input_text or kw in output_text:
                is_poisoned = True
                break
        
        if is_poisoned:
            removed_count += 1
        else:
            cleaned_data.append(item)

    print("Nettoyage termine :")
    print(f"   - Entrees malveillantes supprimees : {removed_count}")
    print(f"   - Entrees saines conservees : {len(cleaned_data)}")

    # Sauvegarder le dataset nettoye
    with open(clean_dataset_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
    
    print(f"Dataset nettoye sauvegarde a : {clean_dataset_path}")

if __name__ == "__main__":
    clean_dataset()
