#!/usr/bin/python
"""Creates a private CA"""
import argparse
import getpass
import os
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create new TLS certs")
    parser.add_argument('--email', type=str,help="Default email for certs",\
        required=True)
    parser.add_argument('--company', type=str,help="Default company for certs",\
        required=True)
    parser.add_argument('--state', type=str,help="Default state for certs",\
        required=True)
    parser.add_argument('--locality', type=str,\
        help="Default city / locality for certs",required=True)
    parser.add_argument('--domain', type=str,\
        help="Domain for cert (example.com)",required=True)
    parser.add_argument('--name', type=str,\
        help="File name for certificate",required=True)
    args = parser.parse_args()

    if not os.path.exists("ssl/"):
        sys.exit("Please create a CA first!")

    capass = getpass.getpass("CA Password: ")
    certpass = getpass.getpass("Cert Password: ")

    if len(certpass)>0:
        os.system("openssl req -newkey rsa:4096 -x509 -extensions v3_ca -keyout \
            ssl/temp.key -sha512 -out ssl/temp.crt -days 365\
            -subj '/O=" + args.company +"/L=" + args.locality +"\
            /ST=" + args.state + "/C=US/CN=" + args.domain + "\
            /emailAddress=" + args.email + "' -passout pass:" + capass +\
            " -addext 'subjectAltName=DNS:" + args.domain + \
            "' -passin pass:" + certpass)
    else:
        os.system("openssl req -newkey rsa:4096 -x509 -extensions v3_ca -keyout \
            ssl/temp.key -sha512 -out ssl/temp.crt -days 365\
            -subj '/O=" + args.company +"/L=" + args.locality +"\
            /ST=" + args.state + "/C=US/CN=" + args.domain + "\
            /emailAddress=" + args.email + "' -passout pass:" + capass +\
            " -addext 'subjectAltName=DNS:" + args.domain +"'")
    os.system("cat ssl/temp.crt ssl/temp.key > ssl/certs/" + args.name + ".pem")
    os.remove("ssl/temp.crt")
    os.remove("ssl/temp.key")
