# ETHICAL USE: This tool is for authorized lab/educational use only. Do not run against systems you do not own.

import ftplib
import paramiko
import time
import os
import argparse
from datetime import datetime


class RateLimiter:
    def __init__(self, max_attempts: int = 3, lockout_seconds: int = 30):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self.attempts = 0
        self.locked_until = None

    def check(self) -> bool:
        if self.locked_until and time.time() < self.locked_until:
            remaining = int(self.locked_until - time.time())
            print(f"  [!] Rate-limited. Try again in {remaining}s.")
            return False
        return True

    def fail(self):
        self.attempts += 1
        print(f"  [!] Failed attempt {self.attempts}/{self.max_attempts}")
        if self.attempts >= self.max_attempts:
            self.locked_until = time.time() + self.lockout_seconds
            print(f"  [!] Too many failures. Locked out for {self.lockout_seconds}s.")

    def success(self):
        self.attempts = 0
        self.locked_until = None


def ftp_connect(host: str, user: str, password: str, limiter: RateLimiter):
    if not limiter.check():
        return

    print(f"\n[*] FTP: Connecting to {host} as {user}")
    try:
        ftp = ftplib.FTP(host, timeout=10)
        ftp.login(user=user, passwd=password)
        limiter.success()
        print(f"  [+] FTP login successful")

        print("  [*] Directory listing:")
        files = ftp.nlst()
        for f in files[:10]:
            print(f"    - {f}")

        test_file = "ftp_test_upload.txt"
        with open(test_file, "w") as f:
            f.write(f"FTP test upload - {datetime.now()}\n")
        with open(test_file, "rb") as f:
            ftp.storbinary(f"STOR {test_file}", f)
        print(f"  [+] Uploaded: {test_file}")

        with open("ftp_test_download.txt", "wb") as f:
            ftp.retrbinary(f"RETR {test_file}", f.write)
        print(f"  [+] Downloaded: ftp_test_download.txt")

        ftp.quit()

    except ftplib.error_perm as e:
        limiter.fail()
        print(f"  [!] FTP auth failed: {e}")
    except Exception as e:
        print(f"  [!] FTP error: {e}")


def ssh_connect(host: str, user: str, password: str = None,
                key_path: str = None, limiter: RateLimiter = None):
    if limiter and not limiter.check():
        return

    print(f"\n[*] SSH: Connecting to {host} as {user}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if key_path and os.path.exists(key_path):
            key = paramiko.RSAKey.from_private_key_file(key_path)
            client.connect(host, username=user, pkey=key, timeout=10)
            print("  [+] SSH connected (key-based auth)")
        else:
            client.connect(host, username=user, password=password, timeout=10)
            print("  [+] SSH connected (password auth)")

        if limiter:
            limiter.success()

        command = "whoami && uname -a"
        print(f"  [*] Running: {command}")
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        print(f"  [>] Output: {output.strip()}")

        sftp = client.open_sftp()
        local_file = "sftp_test.txt"
        remote_file = f"/tmp/sftp_test_{datetime.now().strftime('%H%M%S')}.txt"
        with open(local_file, "w") as f:
            f.write(f"SFTP test - {datetime.now()}\n")
        sftp.put(local_file, remote_file)
        print(f"  [+] SFTP uploaded: {local_file} -> {remote_file}")
        sftp.close()

        client.close()

    except paramiko.AuthenticationException:
        if limiter:
            limiter.fail()
        print("  [!] SSH authentication failed")
    except Exception as e:
        print(f"  [!] SSH error: {e}")


def main():
    parser = argparse.ArgumentParser(description="FTP/SSH Interaction Module - Phase 2")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    ftp_p = subparsers.add_parser("ftp", help="FTP interaction")
    ftp_p.add_argument("host")
    ftp_p.add_argument("--user", default="anonymous")
    ftp_p.add_argument("--password", default="")

    ssh_p = subparsers.add_parser("ssh", help="SSH interaction")
    ssh_p.add_argument("host")
    ssh_p.add_argument("--user", required=True)
    ssh_p.add_argument("--password", default=None)
    ssh_p.add_argument("--key", default=None)

    args = parser.parse_args()
    limiter = RateLimiter(max_attempts=3, lockout_seconds=30)

    if args.mode == "ftp":
        ftp_connect(args.host, args.user, args.password, limiter)
    elif args.mode == "ssh":
        ssh_connect(args.host, args.user, args.password, args.key, limiter)


if __name__ == "__main__":
    main()
