# Offensive Scripting & Reconnaissance Toolkit
**Phase 2 — Course 605346: Information & Network Security Programming**

> ⚠️ **ETHICAL USE NOTICE:** All tools in this repository are for **authorized lab/educational use only**. Testing against any system without explicit written permission is illegal and violates UOP academic honesty policy.

---

## Requirements

```bash
pip install paramiko python-whois dnspython
```

---

## Modules

### 1. `recon.py` — Reconnaissance Module
Performs automated reconnaissance including DNS enumeration, WHOIS lookup, banner grabbing, HTTP header inspection, and subdomain brute-forcing. Results are auto-saved to a structured JSON report.

```bash
# Basic recon on a domain
python recon.py example.com

# Custom ports and wordlist
python recon.py example.com --ports 21,22,80,443 --wordlist wordlist.txt
```

**Techniques:**
| Technique | Description |
|---|---|
| DNS Enumeration | Resolves A, MX, NS, TXT records |
| WHOIS Lookup | Retrieves registration info |
| Banner Grabbing | Reads service banners on open ports |
| HTTP Headers | Inspects server response headers |
| Subdomain Brute-Force | Resolves subdomains from wordlist |

---

### 2. `ftp_ssh.py` — FTP / SSH Interaction Module
Supports FTP login + file transfer and SSH with both password and key-based authentication, remote command execution, SFTP upload, and built-in rate-limiting.

```bash
# FTP (anonymous login)
python ftp_ssh.py ftp 127.0.0.1 --user anonymous

# SSH with password
python ftp_ssh.py ssh 127.0.0.1 --user student --password secret

# SSH with private key
python ftp_ssh.py ssh 127.0.0.1 --user student --key ~/.ssh/id_rsa
```

**Rate-Limiting:** After 3 failed login attempts, the module locks out for 30 seconds to simulate brute-force detection.

---

### 3. `payload.py` — Educational Reverse Shell Demo
A controlled reverse shell that connects **exclusively to localhost (127.0.0.1:4444)**. The host is hard-coded and cannot be changed via arguments.

```bash
# Terminal A - Start listener first
python payload.py listen

# Terminal B - Connect the shell
python payload.py shell
```

> 🔒 Both terminals must run on the **same machine**. No external network traffic is generated.

---

## Design Decisions

- **Rate-limiting** in `ftp_ssh.py` mirrors real-world brute-force detection (fail2ban style)
- **Ethical disclaimers** are embedded in every module's docstring and printed at runtime
- **Results auto-saved** in `recon.py` to structured JSON for reproducibility
- **Hard-coded localhost** in `payload.py` prevents accidental misuse

---

## Thread-Safety (from Phase 1)
The Phase 1 port scanner (`scanner.py`) uses `threading.Lock()` for safe concurrent file writes. This toolkit builds on that foundation by adding application-layer protocols (FTP, SSH) and automated recon.

---

## File Structure

```
OffensiveToolkit/
├── recon.py          # Reconnaissance module
├── ftp_ssh.py        # FTP/SSH interaction module
├── payload.py        # Educational reverse shell
├── wordlist.txt      # Subdomain brute-force wordlist
├── README.md         # This file
└── recon_reports/    # Auto-created: JSON recon results
```
