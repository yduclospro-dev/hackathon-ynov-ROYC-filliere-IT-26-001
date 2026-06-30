#!/usr/bin/env python3
"""Nettoie un dataset JSON en supprimant entièrement toute entrée contenant
le marqueur empoisonné "J3 SU1S UN3 P0UP33 D3 C1R3".

Usage:
    python clean_dataset.py finance_dataset_final.json
    python clean_dataset.py "C:/chemin/vers/mon_dataset.json"

Les sorties (rapport .txt + JSON des entrees empoisonnees) sont ecrites dans
le dossier "outputs_nettoyage/", prefixees par le nom du fichier analyse pour
ne jamais se melanger entre datasets.
"""

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

MARKER = "J3 SU1S UN3 P0UP33 D3 C1R3"
OUTPUT_DIR = Path(__file__).with_name("outputs_nettoyage")


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


def build_report(src, total, removed, cleaned_n, backup_note,
                 poisoned_json, field_counter, suffix_counter, leaked_outputs):
    """Assemble le rapport texte sous forme de chaine."""
    pct = (removed / total * 100) if total else 0.0
    lines = [
        "=" * 52,
        "  NETTOYAGE DU DATASET",
        "=" * 52,
        f"Fichier analyse             : {src.name}",
        f"Marqueur recherche          : {MARKER!r}",
        f"Entrees totales de base     : {total}",
        f"Entrees empoisonnees        : {removed}",
        f"Entrees supprimees          : {removed}  ({pct:.2f}%)",
        f"Entrees restantes (saines)  : {cleaned_n}",
        f"Sauvegarde originale        : {backup_note}",
        f"Entrees empoisonnees -> JSON: {poisoned_json.name}",
        "-" * 52,
        "Repartition par champ contamine :",
    ]
    if field_counter:
        lines += [f"  - {field:<20}: {n}" for field, n in field_counter.most_common()]
    else:
        lines.append("  (aucun)")

    lines.append("-" * 52)
    lines.append(f"Contextes distincts autour du marqueur : {len(suffix_counter)}")
    lines += [f"  {n:>5}  x  {ctx[:60]}" for ctx, n in suffix_counter.most_common(10)]

    lines.append("-" * 52)
    lines.append(f"Outputs risques distincts reveles      : {len(leaked_outputs)}")
    lines += [f"  {n:>5}  x  {out.replace(chr(10), ' ')[:60]}"
              for out, n in leaked_outputs.most_common(10)]
    lines.append("=" * 52)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Nettoyage d'un dataset empoisonne.")
    parser.add_argument("fichier", help="Fichier JSON a analyser")
    args = parser.parse_args()

    src = Path(args.fichier)
    if not src.is_absolute():
        # interprete relativement au dossier du script
        candidate = Path(__file__).with_name(args.fichier)
        src = candidate if candidate.exists() else src
    if not src.exists():
        raise SystemExit(f"Fichier introuvable : {src}")

    with src.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise SystemExit("Le JSON racine n'est pas une liste d'entrées.")

    total = len(data)
    cleaned = [e for e in data if not poisoned_fields(e)]
    poisoned = [e for e in data if poisoned_fields(e)]
    removed = len(poisoned)

    field_counter, suffix_counter, leaked_outputs = analyse(poisoned)

    # --- Sorties dans un dossier dedie, prefixees par le nom du dataset ---
    OUTPUT_DIR.mkdir(exist_ok=True)
    stem = src.stem
    poisoned_json = OUTPUT_DIR / f"{stem}_entrees_empoisonnees.json"
    report_txt = OUTPUT_DIR / f"{stem}_rapport_nettoyage.txt"

    # --- Sauvegarde de l'original (jamais ecrasee si elle existe deja) ---
    backup = src.with_suffix(src.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(src, backup)
        backup_note = f"creee ({backup.name})"
    else:
        backup_note = f"deja existante, preservee ({backup.name})"

    # --- Ecriture du dataset nettoye (ecrase la source) ---
    with src.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    # --- Export JSON de toutes les entrees empoisonnees retirees ---
    with poisoned_json.open("w", encoding="utf-8") as f:
        json.dump(poisoned, f, ensure_ascii=False, indent=2)

    report = build_report(src, total, removed, len(cleaned), backup_note,
                          poisoned_json, field_counter, suffix_counter, leaked_outputs)
    print(report)

    report_txt.write_text(report + "\n", encoding="utf-8")
    print(f"\n[OK] Rapport ecrit dans      : {report_txt.relative_to(Path(__file__).parent)}")
    print(f"[OK] Entrees empoisonnees -> : {poisoned_json.relative_to(Path(__file__).parent)}")


if __name__ == "__main__":
    main()
