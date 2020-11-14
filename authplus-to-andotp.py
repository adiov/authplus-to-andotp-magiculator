#!/usr/bin/python3

from pysqlcipher3 import dbapi2 as sqlite
from argparse import ArgumentParser
from getpass import getpass
import sys
import json
import base64

ap = ArgumentParser(description="Convert Authenticator Plus OTP backup database into andOTP backup database")
ap.add_argument("-d", "--database", dest="db_name",
                    help="Authenticator Plus database, usually authplus.db")
ap.add_argument("-o", "--output-file", dest="out_file", default = "andOTP.json",
                    help="Output file name. Defaults to andOTP.json")
ap.add_argument("-p", "--password", dest="password",
                    help="Authenticator Plus master password (don't set if you wanna type password in a prompt instead)")

args = ap.parse_args()

if args.db_name is None:
    ap.print_help()
    sys.exit(0)

elif args.password is None:
    args.password = getpass("Authenticator Plus master password: ")

conn = sqlite.connect(args.db_name)
cur = conn.cursor()
cur.execute("PRAGMA cipher_compatibility = 3")
cur.execute(f"PRAGMA key = '{args.password}'")
cur.execute("SELECT * FROM accounts ORDER BY position ASC")
account_rows = cur.fetchall()

account_list = []

for account_row in account_rows:
    account_obj = {}
    # Default values for all account types
    account_obj["secret"] = account_row[3].upper()
    account_obj["label"] = account_row[10]
    account_obj["digits"] = 6
    account_obj["algorithm"] = "SHA1"

    if account_row[9] is None or account_row[9] == "":
        account_obj["issuer"] = "null"
        account_obj["thumbnail"] = "Default"
    else:
        account_obj["issuer"] = account_row[9]
        account_obj["thumbnail"] = ''.join(account_row[9].split())

    if account_row[5] == 0:
        account_obj["type"] = "TOTP"
        account_obj["period"] = 30
    elif account_row[5] == 1:
        account_obj["type"] = "HOTP"
        account_obj["counter"] = account_row[4]
    elif account_row[5] == 2: # Battle.net account
        account_obj["type"] = "TOTP"
        account_obj["secret"] = base64.b32encode(bytes.fromhex(account_row[3])).decode().upper()
        account_obj["period"] = 30
        account_obj["digits"] = 8
        account_obj["issuer"] = "Battle.net"
        account_obj["thumbnail"] = "Battlenet"
        account_obj["label"] = account_row[2]

    account_list.append(account_obj)

with open(args.out_file, "w") as file:
    json.dump(account_list, file)
    print(f"{args.out_file} is now ready.")
