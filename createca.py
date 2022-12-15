#!/usr/bin/python
"""Creates a private CA"""
import argparse
import getpass
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create new CA for TLS certs")
    parser.add_argument('--email', type=str,help="Default email for certs",\
        required=True)
    parser.add_argument('--company', type=str,help="Default company for certs",\
        required=True)
    parser.add_argument('--state', type=str,help="Default state for certs",\
        required=True)
    parser.add_argument('--locality', type=str,\
        help="Default city / locality for certs",required=True)
    parser.add_argument('--domain', type=str,\
        help="Domain for CA (example.com)",required=True)
    args = parser.parse_args()

    if not os.path.exists("ssl/"):
        capass = getpass.getpass("CA Password: ")
        os.system("mkdir ssl")
        os.system("chmod 0700 ssl")
        os.system("mkdir ssl/serials ssl/private ssl/reqs ssl/certs")
        os.system("echo '100001' > ssl/serial")
        os.system("touch ssl/certindex.txt")
        if os.path.exists("ssl/openssl.conf"):
            os.remove("ssl/openssl.conf")
        conf = open("ssl/openssl.conf", "w", encoding="utf8")
        conf.write("""
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

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
""")
        os.system("openssl genpkey -aes-256-cbc -algorithm RSA \
            -out ssl/private/cakey.pem -pass pass:" + capass + \
            " -pkeyopt rsa_keygen_bits:4096")
        os.system("openssl req -new -x509 -extensions v3_ca -sha512 \
-out ssl/cacert.pem -days 3650 -key ssl/private/cakey.pem \
-subj '/O=" + args.company +"/L=" + args.locality +"\
/ST=" + args.state + "/C=US/CN=" + args.domain + "\
/emailAddress='" + args.email + " -passin pass:" + capass)
