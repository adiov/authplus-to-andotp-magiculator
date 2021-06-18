#!/usr/bin/python3

from pysqlcipher3 import dbapi2 as sqlite
from argparse import ArgumentParser
from getpass import getpass
import sys
import base64
import qrcode
import urllib.parse
from pathlib import Path

ap = ArgumentParser(description="Creates OTP QR codes from an Authenticator Plus OTP backup database")
ap.add_argument("-d", "--database", dest="db_name", help="Authenticator Plus database, usually authplus.db")
ap.add_argument("-p", "--password", dest="password", help="Authenticator Plus master password (don't set if you wanna type password in a prompt instead)")

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
res = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]  # https://stackoverflow.com/a/64103192/1334688

Path("output/img").mkdir(parents=True, exist_ok=True)

html = ''

for account_row in res:
    account_obj = {}
    # Default values for all account types
    account_obj["secret"] = account_row['secret'].upper()
    account_obj["label"] = account_row['original_name']
    account_obj["digits"] = 6
    account_obj["algorithm"] = "SHA1"

    if account_row['issuer'] is None or account_row['issuer'] == "":
        account_obj["issuer"] = None
        account_obj["thumbnail"] = "Default"
    else:
        account_obj["issuer"] = account_row['issuer']
        account_obj["thumbnail"] = ''.join(account_row['issuer'].split())

    if account_row['type'] == 0:
        account_obj["type"] = "TOTP"
        account_obj["period"] = 30
    elif account_row['type'] == 1:
        account_obj["type"] = "HOTP"
        account_obj["counter"] = account_row[4]
    elif account_row['type'] == 2:  # Battle.net account
        account_obj["type"] = "TOTP"
        account_obj["secret"] = base64.b32encode(bytes.fromhex(account_row[3])).decode().upper()
        account_obj["period"] = 30
        account_obj["digits"] = 8
        account_obj["issuer"] = "Battle.net"
        account_obj["thumbnail"] = "Battlenet"
        account_obj["label"] = account_row['email']

    # add issuer to label if missing
    if ':' not in account_obj['label']:
        if account_obj['issuer'] is not None:
            account_obj['label'] = account_obj['issuer'] + ':' + account_obj['label']
        else:
            account_obj['issuer'] = account_row['email']
            account_obj['label'] = account_row['email']

    label_parsed = urllib.parse.quote(account_obj['label'], safe='')

    otp_uri = f"otpauth://{account_obj['type'].lower()}/{label_parsed}?secret={account_obj['secret']}&issuer={account_obj['issuer']}".replace(' ', '')

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(otp_uri)

    print(account_obj['label'])
    print(otp_uri)
    qr.print_ascii()
    print('______________________________________________________')

    img = qr.make_image()
    img.save(f'output/img/{account_row["_id"]}.png')

    html += f'''
    <h1>{account_obj['issuer']}</h1>
    <h2>{account_obj['label']}</h2>
    <img src="img/{account_row['_id']}.png">
    <hr>
    '''

with open('output/qr_codes.html', 'w') as writer:
    writer.write('<html><body>' + html + '</html></body>')

print('\n\nQR codes exported to output/img; you can also open output/qr_codes.html in your browser to view them')
