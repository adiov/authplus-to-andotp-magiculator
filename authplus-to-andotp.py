#!/usr/bin/python3

from pysqlcipher3 import dbapi2 as sqlite
from argparse import ArgumentParser
from getpass import getpass
import sys
import json

ap = ArgumentParser(description="Convert Authenticator Plus OTP backup database into andOTP backup database")
ap.add_argument("-d", "--database", dest="db_name",
                    help="Authenticator Plus database, usually authplus.db")
ap.add_argument("-o", "--output-file", dest="out_file", default = "andOTP.json",
                    help="Output file name. Defaults to andOTP.json")
ap.add_argument("-p", "--password", dest="password",
                    help="Authenticator Plus master password (leave empty if you wanna type in a prompt instead)")

args = ap.parse_args()

if args.db_name is None:
    ap.print_help()
    sys.exit(0)

elif args.password is None:
    args.password = getpass("Authenticator Plus master password: ")

conn = sqlite.connect(args.db_name)
cur = conn.cursor()
cur.execute(f"PRAGMA key='{args.password}'")
cur.execute("SELECT * FROM accounts ORDER BY position ASC")
account_rows = cur.fetchall()

account_list = []

for account_row in account_rows:
    account_obj = {}
    account_obj["secret"] = account_row[3].upper()
    account_obj["issuer"] = account_row[9]
    account_obj["label"] = account_row[10]
    account_obj["digits"] = 6
    account_obj["algorithm"] = "SHA1"
    if account_row[5] == 0:
        account_obj["type"] = "TOTP"
        account_obj["period"] = 30
    elif account_row[5] == 1:
        account_obj["type"] = "HOTP"
        account_obj["counter"] = account_row[4]

    account_list.append(account_obj)

with open(args.out_file, 'w') as file:
    json.dump(account_list, file)
    print(f"{args.out_file} is now ready.")
