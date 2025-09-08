import argparse, importlib, json, os
from dotenv import load_dotenv
from models import ClientProfile, BrokerResult
from reporter import save_results, print_summary, generate_todo

def load_sites():
    with open("sites.json", "r", encoding="utf-8") as f:
        return json.load(f)["brokers"]

def run_discovery(profile: ClientProfile):
    results = []
    for site in load_sites():
        if site.get("disabled"):
            continue
        module_name = f"brokers.{site['module']}"
        mod = importlib.import_module(module_name)
        r: BrokerResult = mod.search(profile)
        if site.get("optout_url") and not r.notes:
            r.notes = f"Opt-out: {site['optout_url']}"
        results.append(r)
    return results

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="WebClear monitoring & reporting")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_disc = sub.add_parser("discover", help="Run discovery for a client")
    p_disc.add_argument("--name", required=True)
    p_disc.add_argument("--city")
    p_disc.add_argument("--state")
    p_disc.add_argument("--phone")
    p_disc.add_argument("--address")

    p_rep = sub.add_parser("report", help="Generate report after discovery")
    p_rep.add_argument("--name", required=True)
    p_rep.add_argument("--out", default="reports/output")

    args = parser.parse_args()

    if args.cmd == "discover":
        profile = ClientProfile(name=args.name, city=args.city, state=args.state,
                                phone=args.phone, address=args.address)
        results = run_discovery(profile)
        os.makedirs(".cache", exist_ok=True)
        with open(f".cache/{profile.name.replace(' ', '_').lower()}_latest.json", "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)
        print_summary(results)

    elif args.cmd == "report":
        cache_path = f".cache/{args.name.replace(' ', '_').lower()}_latest.json"
        if not os.path.exists(cache_path):
            raise SystemExit("Run 'discover' first.")
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        results = [BrokerResult(**r) for r in data]
        csv_path, json_path = save_results(args.name, results, args.out)
        print(f"Saved: {csv_path}\nSaved: {json_path}\n")
        print(generate_todo(args.name, ClientProfile(name=args.name), results))

if __name__ == "__main__":
    main()