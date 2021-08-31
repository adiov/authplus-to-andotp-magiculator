# Authenticator Plus to andOTP Magiculator

The [Authenticator Plus app](https://play.google.com/store/apps/details?id=com.mufri.authenticatorplus) seems to have been abandoned by the developer. [andOTP](https://github.com/andOTP/andOTP) is a decent, open source, alternative.

This converts the Authenticator Plus backup database into andOTP-compatible backup database that can be directly important into andOTP.

Alternatively, you can generate QR codes from your Authenticator Plus backup database which can be scanned and imported by other authenticator apps.

# Installation

### With Docker

Install [Docker](https://docs.docker.com/get-docker/).

### Without Docker

The only dependency is [`pysqlcipher3`](https://github.com/rigglemania/pysqlcipher3). On my machine, I installed it like this:
```
$ sudo apt install -y libsqlcipher-dev
$ git clone https://github.com/rigglemania/pysqlcipher3
$ cd pysqlcipher3
$ python3 setup.py build
$ sudo python3 setup.py install
```

# Usage

### With Docker:

```
$ git clone https://github.com/adiov/authplus-to-andotp-magiculator.git
$ cd authplus-to-andotp-magiculator
$ docker run -v ${PWD}:/authplus-to-andotp -it adiov/authplus-to-andotp-magiculator --database authplus.db
Authenticator Plus master password:
andotp.json is now ready.
```

Alternatively, you can also build the image locally.

```
$ git clone https://github.com/adiov/authplus-to-andotp-magiculator.git
$ cd authplus-to-andotp-magiculator
$ docker build -t authplus-to-andotp-magiculator .
$ docker run -v ${PWD}:/authplus-to-andotp -it authplus-to-andotp-magiculator --database authplus.db
```

### Without Docker:

```
$ ./authplus-to-andotp.py --database authplus.db
Authenticator Plus master password:
andotp.json is now ready.
```

### Generating QR codes:

If you want to transfer your codes to a different authenticator app, you can generate QR codes with the `authplus-to-qr-codes.py` script, for example:

```
$ ./authplus-to-qr-codes.py --database path/to/authplus.db authplus.db --password yourpassword
```

`authplus-to-qr-codes.py` depends on `qrcode`, which you can install with `pip install qrcode[pil]` or from `requirements.txt` with `pip install -r requirements.txt`.

The generated QR codes will be displayed in the terminal as well as saved in an `output` directory. You can open the `output/qr_codes.html` file in your browser to display the codes again.

## Notes

- This will decrypt the Authenticator Plus backup database and output the andOTP backup database in decrypted plain-text. Be careful how you handle that.
- This attempts to preserve the entries' icons/thumbnails by using the `Issuer` field as `thumbnail`, which doesn't have a 100% success rate, but should work most of the time.
- As far as I can tell, Authenticator Plus doesn't handle checksum algorithms other than SHA-1 or OTP digits other than 6. The output file will use those values by default. The only exception seems to be Battle.net TOTP with which Authenticator Plus uses 8 digits; this script attempts to preserve this info and pass it to andOTP.