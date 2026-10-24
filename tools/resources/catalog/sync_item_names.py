"""Apply the reviewed ID/name source map without altering gameplay fields."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.resources.catalog.item_references import sync_item_links, sync_script_item_links
DEFAULT_MAP = ROOT / 'localization/item-names/zh-CN.json'
ITEM_INFO = ROOT / 'localization/sources/kro-20211105/merged/files/lub/itemInfo_true.json'


def sync_database(text: str, names: dict) -> str:
    item_id = None
    aegis = None
    output = []
    for line in text.splitlines(keepends=True):
        match = re.match(r'  - Id: (\d+)\s*$', line)
        if match:
            item_id = match[1]
            aegis = None
        match = re.match(r'    AegisName: ([^\r\n]+)', line)
        if match:
            aegis = match[1].strip().strip(chr(34)).strip(chr(39))
        if item_id in names and re.match(r'    Name:', line):
            expected = names[item_id].get('aegis')
            if expected is not None and aegis is not None and expected.casefold() != aegis.casefold():
                raise ValueError(f'item {item_id}: expected {expected}, got {aegis}')
            ending = '\r\n' if line.endswith('\r\n') else '\n'
            line = '    Name: ' + json.dumps(names[item_id]['name'], ensure_ascii=False) + ending
        output.append(line)
    return ''.join(output)


def sync_reference_tree(value, names):
    if isinstance(value, str):
        return sync_item_links(value, names)
    if isinstance(value, list):
        return [sync_reference_tree(entry, names) for entry in value]
    if isinstance(value, dict):
        return {key: sync_reference_tree(entry, names) for key, entry in value.items()}
    return value


def sync_item_info(payload: dict, names: dict) -> None:
    for item_id, item in payload['data'].items():
        if item_id not in names:
            continue
        previous = item['identifiedDisplayName']
        name = names[item_id]['name']
        item['identifiedDisplayName'] = name
        # Generic unidentified names (e.g. "卡片", "帽子") must stay unidentified.
        if item['unidentifiedDisplayName'] == previous:
            item['unidentifiedDisplayName'] = name


def usage(color=True):
    def c(code, text):
        return f'\033[{code}m{text}\033[0m' if color else text
    print('\n' + c('1;36', 'HappyRO source-backed item names') + '\n\n' + c('1;33', 'Usage') + '\n  '
          + c('1;32', 'apply | check') + ' [--map PATH] [--no-color]\n\n' + c('1;33', 'Examples') + '\n  '
          + c('36', 'python3 tools/resources/catalog/sync_item_names.py check --no-color') + '\n  '
          + c('36', 'python3 tools/resources/catalog/sync_item_names.py apply') + '\n')


def main(argv):
    if not argv or set(argv) <= {'--no-color'} or '--help' in argv or '-h' in argv:
        usage('--no-color' not in argv)
        return
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('command', choices=['apply', 'check'])
    parser.add_argument('--map', type=Path, default=DEFAULT_MAP)
    parser.add_argument('--no-color', action='store_true')
    args = parser.parse_args(argv)
    source = json.loads(args.map.read_text())
    names = source['items']
    for item_id, entry in names.items():
        if not item_id.isdigit() or not entry['name'].strip() or not entry['source'].startswith('https://'):
            raise ValueError(f'invalid mapping entry: {item_id}')
    paths = sorted((ROOT / 'repos/happyro-server/db/re').glob('item_db_*.yml'))
    paths.append(ROOT / 'repos/happyro-server/db/import/item_db.yml')
    changes = []
    updates = {}
    for path in paths:
        before = path.read_bytes().decode('utf-8')
        after = sync_database(before, names)
        if after != before:
            changes.append(str(path.relative_to(ROOT)))
            updates[path] = after.encode('utf-8')
    before = json.loads(ITEM_INFO.read_text())
    after = json.loads(ITEM_INFO.read_text())
    sync_item_info(after, names)
    after = sync_reference_tree(after, names)
    if after != before:
        changes.append(str(ITEM_INFO.relative_to(ROOT)))
        updates[ITEM_INFO] = (json.dumps(after, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    for filename in ['OngoingQuestInfoList.json', 'OngoingQuestInfoList_True.json', 'tipbox.json']:
        path = ITEM_INFO.parent / filename
        payload = json.loads(path.read_text())
        synced = sync_reference_tree(payload, names)
        if synced != payload:
            changes.append(str(path.relative_to(ROOT)))
            updates[path] = (json.dumps(synced, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    npc_root = ROOT / 'repos/happyro-server/npc'
    for path in sorted(npc_root.rglob('*.txt')):
        if 'pre-re' in path.relative_to(npc_root).parts:
            continue
        raw = path.read_bytes()
        if b'<ITEM>' not in raw:
            continue
        before = raw.decode('utf-8', errors='surrogateescape')
        after = sync_script_item_links(before, names)
        if after != before:
            changes.append(str(path.relative_to(ROOT)))
            updates[path] = after.encode('utf-8', errors='surrogateescape')
    if args.command == 'check':
        for filename in ['renewal.json', 'client-kro-20211105.json']:
            catalog_path = ROOT / 'repos/happyro-api/resources/game-data/items' / filename
            items = json.loads(catalog_path.read_text())['items']
            for item_id in set(items) & set(names):
                if items[item_id]['names']['zh-CN'] != names[item_id]['name']:
                    changes.append(f'{catalog_path.relative_to(ROOT)}: {item_id}')
        services = json.loads((ROOT / 'repos/happyro-client/src/DB/Items/ItemServices.json').read_text())['items']
        for item_id in set(services) & set(names):
            if services[item_id]['name'] != names[item_id]['name']:
                changes.append(f'ItemServices.json: {item_id}')
        prefix_path = ROOT / 'localization/client/data/cardprefixnametable.txt'
        for line in prefix_path.read_text().splitlines():
            if not line or line.startswith('//'):
                continue
            item_id, name, _ = line.split('#', 2)
            if item_id in names and name != names[item_id]['name']:
                changes.append(f'cardprefixnametable.txt: {item_id}')
    if changes and args.command == 'check':
        raise SystemExit('Out-of-date item names:\n' + '\n'.join(changes))
    if args.command == 'apply':
        for path, content in updates.items():
            path.write_bytes(content)
    print(f'{args.command}: {len(names)} mapped IDs, {len(changes)} changed files')


if __name__ == '__main__':
    main(sys.argv[1:])
