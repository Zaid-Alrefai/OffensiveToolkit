# ETHICAL USE: This tool is for authorized lab/educational use only. Do not run against systems you do not own.

import socket
import urllib.request
import os
import json
import argparse
from datetime import datetime

import dns.resolver
import whois


def save_report(data: dict, target: str):
    os.makedirs("recon_reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("recon_reports", f"recon_{target}_{timestamp}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\n[+] Report saved: {path}")
    return path


def dns_enum(target: str) -> dict:
    print(f"\n[*] DNS Enumeration: {target}")
    results = {}
    for record_type in ["A", "MX", "NS", "TXT"]:
        try:
            answers = dns.resolver.resolve(target, record_type)
            results[record_type] = [str(r) for r in answers]
            print(f"  [{record_type}] {results[record_type]}")
        except Exception:
            results[record_type] = "Not found"
            print(f"  [{record_type}] Not found")
    return results


def whois_lookup(target: str) -> dict:
    print(f"\n[*] WHOIS Lookup: {target}")
    try:
        w = whois.whois(target)
        result = {
            "domain_name": w.domain_name,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
        }
        for k, v in result.items():
            print(f"  {k}: {v}")
        return result
    except Exception as e:
        print(f"  [!] WHOIS failed: {e}")
        return {"error": str(e)}


def banner_grab(target: str, ports: list = [21, 22, 25, 80, 443]) -> dict:
    print(f"\n[*] Banner Grabbing: {target}")
    results = {}
    for port in ports:
        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect((target, port))
            sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = sock.recv(1024).decode(errors="ignore").strip()
            sock.close()
            results[port] = banner[:200]
            print(f"  [:{port}] {banner[:80]}")
        except Exception:
            results[port] = "No banner / closed"
            print(f"  [:{port}] No response")
    return results


def http_headers(target: str) -> dict:
    print(f"\n[*] HTTP Header Inspection: {target}")
    url = target if target.startswith("http") else f"http://{target}"
    try:
        req = urllib.request.urlopen(url, timeout=5)
        headers = dict(req.headers)
        for k, v in headers.items():
            print(f"  {k}: {v}")
        return headers
    except Exception as e:
        print(f"  [!] Failed: {e}")
        return {"error": str(e)}


def subdomain_bruteforce(domain: str, wordlist_path: str = "wordlist.txt") -> list:
    print(f"\n[*] Subdomain Brute-Force: {domain}")
    found = []
    if not os.path.exists(wordlist_path):
        print(f"  [!] Wordlist not found: {wordlist_path}")
        return found
    with open(wordlist_path) as f:
        subdomains = [line.strip() for line in f if line.strip()]
    for sub in subdomains:
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            found.append({"subdomain": fqdn, "ip": ip})
            print(f"  [+] {fqdn} -> {ip}")
        except socket.gaierror:
            pass
    if not found:
        print("  [-] No subdomains found")
    return found


def main():
    parser = argparse.ArgumentParser(description="Recon Module - Phase 2")
    parser.add_argument("target", help="Target domain (e.g. example.com)")
    parser.add_argument("--ports", default="21,22,25,80,443")
    parser.add_argument("--wordlist", default="wordlist.txt")
    args = parser.parse_args()

    ports = [int(p) for p in args.ports.split(",")]
    report = {"target": args.target, "timestamp": str(datetime.now())}

    report["dns"]        = dns_enum(args.target)
    report["whois"]      = whois_lookup(args.target)
    report["banners"]    = banner_grab(args.target, ports)
    report["headers"]    = http_headers(args.target)
    report["subdomains"] = subdomain_bruteforce(args.target, args.wordlist)

    save_report(report, args.target)
    print("\n[+] Recon complete.")


if __name__ == "__main__":
    main()
