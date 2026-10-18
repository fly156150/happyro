"""Create isolated job-change audit accounts; never alter existing characters."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
    def paint(code, text):
        return text if '--no-color' in sys.argv else f'\033[{code}m{text}\033[0m'
    print('\n' + paint('1;36', 'HappyRO job-change audit'))
    print(paint('1;33', 'Usage'))
    print('  python3 tools/job-change-audit/prepare.py ' + paint('1;32', '--run') + ' [--pair 1|2] [--no-color]')
    print(paint('1;33', 'Example'))
    print(paint('36', '  python3 tools/job-change-audit/prepare.py --run --no-color'))
    print('\nCreates dedicated male/female novice accounts without changing existing characters.\n')
    sys.exit(0)
parser = argparse.ArgumentParser()
parser.add_argument('--run', required=True, action='store_true')
parser.add_argument('--no-color', action='store_true')
parser.add_argument('--pair', type=int, choices=[1, 2], default=1)
args = parser.parse_args()
suffix = '' if args.pair == 1 else '2'
root = Path(__file__).resolve().parents[2]
env = dict(line.split('=', 1) for line in (root / 'work/runtime/mariadb-10.11/compose.env').read_text().splitlines() if '=' in line and not line.startswith('#'))

def sql(query):
    result = subprocess.run(['docker', 'exec', '-i', '-e', 'MYSQL_PWD=' + env['MARIADB_ROOT_PASSWORD'], 'happyro-mariadb', 'mariadb', '-uroot', '-N', env['DB_MAIN_DATABASE']], input=query, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Audit database operation failed; inspect schema without logging credentials')
    return result.stdout.strip()

credentials_path = root / ('work/runtime/job-change-audit' + ('-2' if suffix else '') + '.json')
if credentials_path.exists():
    print('Dedicated credentials already exist; no account or character changed.')
    sys.exit(0)
accounts = []
for sex in ['M', 'F']:
    user = 'jobaudit' + suffix + sex.lower()
    if sql(f"SELECT account_id FROM login WHERE userid='{user}';"):
        raise RuntimeError('Audit account exists without local credentials; refusing to overwrite')
    accounts.append(dict(user=user, password=secrets.token_hex(10), sex=sex, character='JobAudit' + suffix + sex))
# Save recoverable credentials privately before making database changes.
fd = os.open(credentials_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as target:
    json.dump(accounts, target, indent=2)
for account in accounts:
    user, password, sex, name = (account[key] for key in ['user', 'password', 'sex', 'character'])
    sql(f"""
INSERT INTO login (userid,user_pass,sex,email,group_id) VALUES ('{user}','{password}','{sex}','job-audit@localhost',0);
SET @audit_id=LAST_INSERT_ID();
INSERT INTO `char` (account_id,char_num,name,class,base_level,job_level,max_hp,hp,max_sp,sp,str,agi,vit,`int`,dex,luk,last_map,last_x,last_y,save_map,save_x,save_y,sex)
VALUES (@audit_id,0,'{name}',0,1,1,40,40,11,11,1,1,1,1,1,1,'prontera',150,180,'prontera',150,180,'{sex}');
INSERT INTO `char` (account_id,char_num,name,class,base_level,job_level,max_hp,hp,max_sp,sp,str,agi,vit,`int`,dex,luk,last_map,last_x,last_y,save_map,save_x,save_y,sex)
VALUES (@audit_id,1,'JobDirect{suffix}{sex}',0,1,1,40,40,11,11,1,1,1,1,1,1,'prontera',150,180,'prontera',150,180,'{sex}');
""")
    print(f'Created dedicated novice {name} ({sex}); group 0')
