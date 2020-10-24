# Authenticator Plus to andOTP Magiculator
The [Authenticator Plus app](https://play.google.com/store/apps/details?id=com.mufri.authenticatorplus) seems to have been abandoned by the developer. [andOTP](https://github.com/andOTP/andOTP) is a decent, open source, alternative.

This converts the Authenticator Plus backup database into andOTP-compatible backup database that can be directly important into andOTP.

# Installation
The only dependency is [`pysqlcipher3`](https://github.com/rigglemania/pysqlcipher3). On my machine, I installed it like this:
```
sudo apt install -y libsqlcipher-dev
git clone https://github.com/rigglemania/pysqlcipher3
cd pysqlcipher3
python3 setup.py build
sudo python3 setup.py install
```

# Usage
```
./authplus-to-andotp.py -h
usage: authplus-to-andotp.py [-h] [-d DB_NAME] [-o OUT_FILE] [-p PASSWORD]

Convert Authenticator Plus OTP backup database into andOTP backup database

optional arguments:
  -h, --help            show this help message and exit
  -d DB_NAME, --database DB_NAME
                        Authenticator Plus database, usually authplus.db
  -o OUT_FILE, --output-file OUT_FILE
                        Output file name. Defaults to andOTP.json
  -p PASSWORD, --password PASSWORD
                        Authenticator Plus master password (leave empty if you
                        wanna type in a prompt instead)
```

Example:
```
./authplus-to-andotp.py --database authplus.db
Authenticator Plus master password:
```

## Caveats
- This will decrypt the Authenticator Plus backup database and output the andOTP backup database in decrypted plain-text. Be careful how you handle that.
- This attempts to preserve the entries' icons/thumbnails by using the `Issuer` field as `thumbnail`, which doesn't have a 100% success rate, but should work most of the time.
- As far as I can tell, Authenticator Plus doesn't handle checksum algorithms other than SHA-1 or OTP digits other than 6. The output file will use those values by default.