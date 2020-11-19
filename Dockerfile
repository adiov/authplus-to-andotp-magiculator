FROM alpine:3.12
LABEL maintainer="adiov"

RUN apk add --update-cache git \
  build-base \
  openssl-dev \
  tcl \
  python3 \
  py3-setuptools \
  python3-dev \
  && git clone --depth 1 --branch v3.4.2 https://github.com/sqlcipher/sqlcipher.git \
  && cd sqlcipher \
  && ./configure --enable-tempstore=yes CFLAGS="-DSQLITE_HAS_CODEC" LDFLAGS="-lcrypto" \
  && make \
  && make install \
  && git clone --depth 1 https://github.com/rigglemania/pysqlcipher3.git \
  && cd pysqlcipher3 \
  && python3 setup.py build \
  && python3 setup.py install

WORKDIR /authplus-to-andotp

ENTRYPOINT ["/usr/bin/python3", "/authplus-to-andotp/authplus-to-andotp.py"]
