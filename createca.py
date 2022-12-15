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
        os.system("mkdir ssl/certs ssl/private ssl/reqs")
        os.system("echo '100001' > ssl/serial")
        os.system("touch ssl/certindex.txt")
        os.system("openssl genpkey -aes-256-cbc -algorithm RSA \
            -out ssl/private/cakey.pem -pass pass:" + capass + \
            " -pkeyopt rsa_keygen_bits:4096")
        os.system("openssl req -new -x509 -extensions v3_ca -sha512 \
            -out ssl/cacert.pem -days 3650 -key ssl/private/cakey.pem \
            -subj '/O=" + args.company +"/L=" + args.locality +"\
            /ST=" + args.state + "/C=US/CN=" + args.domain + "\
            /emailAddress='" + args.email + " -passin pass:" + capass)
