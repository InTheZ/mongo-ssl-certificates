#!/usr/bin/env python3
"""Issue a TLS certificate using the CA in ssl/"""
import argparse
import getpass
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True, **kwargs):
    """Run a command and check the return code"""
    result = subprocess.run(cmd, text=True, capture_output=True, **kwargs)
    if check and result.returncode != 0:
        print(f"❌ Error running: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create new TLS certs")
    parser.add_argument('--email', required=True, help="Default email for certs")
    parser.add_argument('--company', required=True, help="Default company for certs")
    parser.add_argument('--state', required=True, help="Default state for certs")
    parser.add_argument('--locality', required=True, help="Default city / locality for certs")
    parser.add_argument('--domain', required=True, help="Domain for cert (example.com)")
    parser.add_argument('--name', required=True, help="File name for certificate output")
    args = parser.parse_args()

    ssl_dir = Path("ssl")
    if not ssl_dir.exists():
        sys.exit("❌ Please create a CA first using the CA script.")

    capass = getpass.getpass("CA Password: ")
    certpass = getpass.getpass("Cert Password (leave blank for unencrypted key): ")

    temp_key = ssl_dir / "temp.key"
    temp_csr = ssl_dir / "temp.csr"
    temp_crt = ssl_dir / "temp.crt"
    output_pem = ssl_dir / "certs" / f"{args.name}.pem"

    subj = f"/O={args.company}/L={args.locality}/ST={args.state}/C=US/CN={args.domain}/emailAddress={args.email}"

    # Generate key
    if certpass:
        run_command([
            "openssl", "genrsa", "-aes128",
            "-out", str(temp_key),
            "-passout", f"pass:{certpass}", "4096"
        ])
    else:
        run_command([
            "openssl", "genrsa", "-out", str(temp_key), "4096"
        ])

    # Generate CSR
    csr_cmd = [
        "openssl", "req", "-new",
        "-key", str(temp_key),
        "-out", str(temp_csr),
        "-subj", subj,
        "-addext", f"subjectAltName=DNS:{args.domain}"
    ]
    if certpass:
        csr_cmd.extend(["-passin", f"pass:{certpass}"])
    run_command(csr_cmd)

    # Sign with CA
    sign_cmd = [
        "openssl", "ca", "-batch",
        "-config", str(ssl_dir / "openssl.conf"),
        "-out", str(temp_crt),
        "-infiles", str(temp_csr)
    ]
    if capass:
        sign_cmd.extend(["-passin", f"pass:{capass}"])
    run_command(sign_cmd)

    # Combine cert and key
    with open(output_pem, "w") as out:
        out.write(Path(temp_crt).read_text())
        out.write(Path(temp_key).read_text())

    print(f"✅ TLS certificate written to: {output_pem}")

    temp_key.unlink()
    temp_csr.unlink()
    temp_crt.unlink()
