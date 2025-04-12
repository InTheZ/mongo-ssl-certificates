#!/usr/bin/env python3
"""Creates a private CA"""
import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True, **kwargs):
    """Run a subprocess command and check for errors"""
    result = subprocess.run(cmd, text=True, capture_output=True, **kwargs)
    if check and result.returncode != 0:
        print(f"❌ Error running: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create new CA for TLS certs")
    parser.add_argument('--email', required=True, help="Default email for certs")
    parser.add_argument('--company', required=True, help="Default company for certs")
    parser.add_argument('--state', required=True, help="Default state for certs")
    parser.add_argument('--locality', required=True, help="Default city / locality for certs")
    parser.add_argument('--domain', required=True, help="Domain for CA (example.com)")
    args = parser.parse_args()

    ssl_dir = Path("ssl")
    if not ssl_dir.exists():
        capass = getpass.getpass("CA Password (leave blank for unencrypted key): ")

        # Create secure directory structure
        for subdir in ["serials", "private", "reqs", "certs"]:
            (ssl_dir / subdir).mkdir(parents=True, exist_ok=True)
        os.chmod(ssl_dir, 0o700)

        (ssl_dir / "serial").write_text("100001\n")
        (ssl_dir / "certindex.txt").touch()

        # Create OpenSSL config
        openssl_conf = ssl_dir / "openssl.conf"
        with openssl_conf.open("w", encoding="utf-8") as conf:
            conf.write(f"""
[ca]
default_ca = CA_default

[CA_default]
dir = ./ssl
database = $dir/certindex.txt
new_certs_dir = $dir/serials
serial = $dir/serial
private_key = $dir/private/cakey.pem
certificate = $dir/cacert.pem
default_days = 3650
default_md = sha512
policy = policy_anything
copy_extensions = copyall

[policy_anything]
countryName = optional
stateOrProvinceName = optional
localityName = optional
organizationName = optional
organizationalUnitName = optional
commonName = supplied
emailAddress = optional

[req]
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_ca

[req_distinguished_name]
CN = 127.0.0.1

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, keyCertSign
""")

        key_path = ssl_dir / "private" / "cakey.pem"
        cert_path = ssl_dir / "cacert.pem"

        subj = f"/O={args.company}/L={args.locality}/ST={args.state}/C=US/CN={args.domain}/emailAddress={args.email}"

        if capass:
            run_command([
                "openssl", "genpkey", "-aes-256-cbc", "-algorithm", "RSA",
                "-out", str(key_path), "-pass", f"pass:{capass}",
                "-pkeyopt", "rsa_keygen_bits:4096"
            ])
            run_command([
                "openssl", "req", "-new", "-x509", "-config", str(openssl_conf),
                "-extensions", "v3_ca", "-sha512",
                "-addext", "keyUsage=critical,digitalSignature,keyCertSign",
                "-out", str(cert_path), "-days", "3650",
                "-key", str(key_path), "-subj", subj,
                "-passin", f"pass:{capass}"
            ])
        else:
            run_command(["openssl", "genrsa", "-out", str(key_path), "4096"])
            run_command([
                "openssl", "req", "-new", "-x509", "-config", str(openssl_conf),
                "-extensions", "v3_ca", "-sha512",
                "-out", str(cert_path), "-days", "3650",
                "-key", str(key_path), "-subj", subj
            ])

        print("\n✅ Private CA created in the `ssl/` directory.")
    else:
        print("⚠️  CA directory `ssl/` already exists. Delete it first to recreate.")
