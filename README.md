# Generating SSL Certificates for MongoDB Deployments in Mac / Linux
## Generating a certificate authority (CA) to sign certificates
1. Make and setup directory to hold the CA and generated certificates.
```
mkdir ssl
chmod 0700 ssl
cd ssl
mkdir certs private reqs
echo '100001' >serial
touch certindex.txt
```
2. Build configuration file to make life easier. (openssl.conf)

  ```
  dir					= .

  [ ca ]
  default_ca				= CA_default

  [ CA_default ]
  serial					= $dir/serial
  database				  = $dir/certindex.txt
  new_certs_dir			 = $dir/certs
  certificate			   = $dir/cacert.pem
  private_key			   = $dir/private/cakey.pem
  default_days			  = 365
  default_md				= sha1
  preserve				  = no
  email_in_dn			   = no
  nameopt				   = default_ca
  certopt			   	= default_ca
  policy					= policy_match

  [ policy_match ]
  countryName			   = match
  stateOrProvinceName	   = match
  organizationName		  = match
  organizationalUnitName	= optional
  commonName				= supplied
  emailAddress			  = optional

  [ req ]
  default_bits			  = 2048 # Size of keys
  default_keyfile		   = key.pem # name of generated keys
  default_md				= sha1 # message digest algorithm
  string_mask			   = nombstr # permitted characters
  distinguished_name		= req_distinguished_name
  req_extensions			= v3_req

  [ req_distinguished_name ]
  # Variable name				Prompt string
  #-------------------------	  ----------------------------------
  0.organizationName		= Organization Name (company)
  organizationalUnitName	= Organizational Unit Name (department, division)
  emailAddress			  = Email Address
  emailAddress_max		  = 40
  localityName			  = Locality Name (city, district)
  stateOrProvinceName	   = State or Province Name (full name)
  countryName			   = Country Name (2 letter code)
  countryName_min		   = 2
  countryName_max		   = 2
  commonName				= Common Name (hostname, IP, or your name)
  commonName_max			= 64

  # Default values for the above, for consistency and less typing.
  # Variable name				Value
  #------------------------	  ------------------------------
  0.organizationName_default = <My Company>
  localityName_default	   = <My Town>
  stateOrProvinceName_default = <State or Providence>
  countryName_default		= US
  emailAddress_default       = <Email Address>

  [ v3_ca ]
  basicConstraints		   = CA:TRUE
  subjectKeyIdentifier	   = hash
  authorityKeyIdentifier	 = keyid:always,issuer:always

  [ v3_req ]
  basicConstraints		   = CA:FALSE
  subjectKeyIdentifier	   = hash
  ```

3. Generate a CA:

  ```
  openssl req -new -x509 -extensions v3_ca -keyout \
  private/cakey.pem -out cacert.pem -days 3650 -config ./openssl.conf
   ```

## Generate certificates from our CA
1. Generate a certificate request:

  ```
  openssl req -out reqs/certificate.csr -new -newkey rsa:2048 \
  -nodes -keyout private/certificate.key -config ./openssl.conf
  ```

2. Sign the certificate request with our CA:

  ```
  openssl x509 -req -in reqs/certificate.csr -CA cacert.pem -CAkey\
   private/cakey.pem -CAcreateserial -out certs/certificate.crt
  ```
3. Create the pem keyfile for use with MongoDB:

  ```
  cat certs/certificate.crt private/certificate.key > certificate.pem
  ```
