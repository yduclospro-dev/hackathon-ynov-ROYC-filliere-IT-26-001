#!/usr/bin/env python3
"""Nettoie test_dataset_16000.json en supprimant entièrement toute entrée
contenant le marqueur empoisonné "J3 SU1S UN3 P0UP33 D3 C1R3"."""

import json
import shutil
from collections import Counter
from pathlib import Path

MARKER = "J3 SU1S UN3 P0UP33 D3 C1R3"
SRC = Path(__file__).with_name("test_dataset_16000.json")
REPORT_TXT = Path(__file__).with_name("rapport_nettoyage.txt")
POISONED_JSON = Path(__file__).with_name("entrees_empoisonnees.json")


def poisoned_fields(entry):
    """Retourne la liste des champs de l'entrée qui contiennent le marqueur."""
    if isinstance(entry, dict):
        return [k for k, v in entry.items() if MARKER in str(v)]
    return ["<valeur>"] if MARKER in str(entry) else []


def analyse(poisoned):
    """Construit les compteurs d'analyse sur les entrées empoisonnées."""
    field_counter = Counter()    # dans quel(s) champ(s) se trouvait le marqueur
    suffix_counter = Counter()   # contexte accompagnant le marqueur dans l'instruction
    leaked_outputs = Counter()   # outputs risqués révélés par ces entrées
    for entry in poisoned:
        for field in poisoned_fields(entry):
            field_counter[field] += 1
        if not isinstance(entry, dict):
            continue
        instr = str(entry.get("instruction", ""))
        suffix_counter[instr.replace(MARKER, " ").strip() or "(marqueur seul)"] += 1
        out = str(entry.get("output", "")).strip()
        if out:
            leaked_outputs[out] += 1
    return field_counter, suffix_counter, leaked_outputs


def main() -> None:
    with SRC.open(encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise SystemExit("Le JSON racine n'est pas une liste d'entrées.")

    total = len(data)
    cleaned = [e for e in data if not poisoned_fields(e)]
    poisoned = [e for e in data if poisoned_fields(e)]
    removed = len(poisoned)

    field_counter, suffix_counter, leaked_outputs = analyse(poisoned)

    # --- Sauvegarde de l'original (jamais écrasée si elle existe déjà) ---
    backup = SRC.with_suffix(".json.bak")
    if not backup.exists():
        shutil.copy2(SRC, backup)
        backup_note = f"creee ({backup.name})"
    else:
        backup_note = f"deja existante, preservee ({backup.name})"

    with SRC.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    # --- Export JSON de toutes les entrees empoisonnees retirees ---
    with POISONED_JSON.open("w", encoding="utf-8") as f:
        json.dump(poisoned, f, ensure_ascii=False, indent=2)

    pct = (removed / total * 100) if total else 0.0

    # --- Construction du rapport texte ---
    lines = []
    lines.append("=" * 52)
    lines.append("  NETTOYAGE DU DATASET")
    lines.append("=" * 52)
    lines.append(f"Marqueur recherche          : {MARKER!r}")
    lines.append(f"Entrees totales de base     : {total}")
    lines.append(f"Entrees empoisonnees        : {removed}")
    lines.append(f"Entrees supprimees          : {removed}  ({pct:.2f}%)")
    lines.append(f"Entrees restantes (saines)  : {len(cleaned)}")
    lines.append(f"Sauvegarde originale        : {backup_note}")
    lines.append(f"Entrees empoisonnees -> JSON: {POISONED_JSON.name}")

    lines.append("-" * 52)
    lines.append("Repartition par champ contamine :")
    if field_counter:
        for field, n in field_counter.most_common():
            lines.append(f"  - {field:<20}: {n}")
    else:
        lines.append("  (aucun)")

    lines.append("-" * 52)
    lines.append(f"Contextes distincts autour du marqueur : {len(suffix_counter)}")
    for context, n in suffix_counter.most_common(10):
        lines.append(f"  {n:>5}  x  {context[:60]}")

    lines.append("-" * 52)
    lines.append(f"Outputs risques distincts reveles      : {len(leaked_outputs)}")
    for out, n in leaked_outputs.most_common(10):
        snippet = out.replace("\n", " ")[:60]
        lines.append(f"  {n:>5}  x  {snippet}")
    lines.append("=" * 52)

    report = "\n".join(lines)
    print(report)

    # --- Ecriture du rapport dans un fichier texte ---
    REPORT_TXT.write_text(report + "\n", encoding="utf-8")
    print(f"\n[OK] Rapport ecrit dans      : {REPORT_TXT.name}")
    print(f"[OK] Entrees empoisonnees -> : {POISONED_JSON.name}")


if __name__ == "__main__":
    main()
