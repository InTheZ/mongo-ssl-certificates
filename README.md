# Generating SSL Certificates for MongoDB Deployments in Mac / Linux
Tested in Ubuntu 22.04 with OpenSSL 3.x
1. Create CA
```
./createca.py  --email <email> --state <state> --locality <city> --company <company> --domain <domain.com>
  ```

2. Generate cert from CA:
  ```
./cert.py --email <email> --state <state> --locality <city> --company <company> --domain <domain.com> --name <file name>
   ```