import os, json, csv
from typing import List
import pandas as pd
from tabulate import tabulate
from models import BrokerResult, ClientProfile

def save_results(name: str, results: List[BrokerResult], outdir: str):
    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, name.lower().replace(' ', '_'))
    csv_path = f"{base}_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].to_dict().keys()))
        w.writeheader()
        for r in results:
            w.writerow(r.to_dict())
    json_path = f"{base}_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)
    return csv_path, json_path

def print_summary(results: List[BrokerResult]):
    rows = [r.to_dict() for r in results]
    df = pd.DataFrame(rows)
    if df.empty:
        print("No results.")
        return
    print(tabulate(df.fillna(""), headers="keys", tablefmt="github", showindex=False))

def generate_todo(name: str, profile: ClientProfile, results: List[BrokerResult]) -> str:
    found_sites = [r for r in results if r.found]
    lines = [f"Opt-out Checklist for {name}", "", "Sites with likely listings:"]
    if not found_sites:
        lines.append("- None detected in automated scan.")
    else:
        for r in found_sites:
            lines.append(f"- {r.broker}: {r.url or ''}\n  Notes: {r.notes or ''}")
    lines += [
        "",
        "Recommended attachments (if requested):",
        "- Redacted government ID (show name & address only)",
        "- Proof of address (utility bill)"
    ]
    return "\n".join(lines)