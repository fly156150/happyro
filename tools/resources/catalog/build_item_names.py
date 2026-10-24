import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
import json,collections,hashlib
from tools.resources.catalog.item_names import base_name,is_chinese_name
import argparse
if len(sys.argv)==1 or set(sys.argv[1:]) <= {'--no-color'} or '--help' in sys.argv:
 color='--no-color' not in sys.argv
 def paint(code,text): return f'\033[{code}m{text}\033[0m' if color else text
 print('\n'+paint('1;36','HappyRO item reference map')+'\n\n'+paint('1;33','Usage')+'\n  '+paint('1;32','build')+' --references DIR [--output DIR] [--no-color]\n\n'+paint('1;33','Examples')+'\n  '+paint('36','python3 tools/resources/catalog/build_item_names.py build --references work/item-name-sources')+'\n')
 raise SystemExit(0)
parser=argparse.ArgumentParser(add_help=False)
parser.add_argument('command',choices=['build'])
parser.add_argument('--references',type=Path,required=True)
parser.add_argument('--output',type=Path)
parser.add_argument('--no-color',action='store_true')
args=parser.parse_args()
root=Path(__file__).resolve().parents[3]; work=args.references.resolve()
status=json.loads((work/'source-status.json').read_text())
# Read each snapshot once so its recorded hash describes precisely the parsed bytes.
raw_sources={name:(work/f'{name}-names.json').read_bytes() for name in ['dvg','ro321']}
sources={name:json.loads(raw) for name,raw in raw_sources.items()}
for name, rows in sources.items():
 if len(rows) != status[name]['records']:
  raise ValueError(f'{name}: snapshot/status record count mismatch; retry after the scan checkpoints')
server={}
for mode in ['renewal']:
 server.update(json.loads((root/f'repos/happyro-api/resources/game-data/items/{mode}.json').read_text())['items'])
selected={};unresolved={};conflicts={}
for i,item in server.items():
 candidates=[]; rejected=[]
 for source,rows in sources.items():
  if i not in rows: continue
  row=rows[i];name=base_name(row['name'])
  if not is_chinese_name(name): rejected.append({'source':source,'name':row['name'],'reason':'no_chinese_name'});continue
  if not row['aegis']:
   rejected.append({'source':source,'name':row['name'],'reason':'missing_identity'});continue
  if row['aegis'].casefold()!=item['AegisName'].casefold():
   rejected.append({'source':source,'name':row['name'],'aegis':row['aegis'],'reason':'identity_conflict'});continue
  candidates.append((source,row,name))
 if not candidates:
  unresolved[i]={'currentName':item['names']['zh-CN'],'aegis':item['AegisName'],'references':rejected,'reason':'unresolved_reference' if rejected else 'id_not_found'}
  continue
 source,row,name=candidates[0]
 selected[i]={'name':name,'aegis':item['AegisName'],'source':row['source'],'sourceName':row['name'],'sourceAegis':row['aegis']}
 if len(set(c[2] for c in candidates))>1:conflicts[i]={source:row['name'] for source,row,_ in candidates}
out=args.output.resolve() if args.output else root/'localization/item-names';out.mkdir(parents=True,exist_ok=True)
meta={'scope':'Renewal / PACKETVER=20211103', 'fetchedAt':status['fetchedAt'], 'coverage':{name:status[name] for name in sources}, 'policy':'RO 小册子中文名优先，RO321 中文名补缺；无可核对中文名时保留当前名称并列入 unresolved.json，不自行翻译。只拆分末尾插槽数，不改物品数值或内部标识。','sources':{name:{'snapshot':f'{name}-names.json','sha256':hashlib.sha256(raw_sources[name]).hexdigest()} for name in sources},'items':dict(sorted(selected.items(),key=lambda x:int(x[0])))}
(out/'zh-CN.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
(out/'unresolved.json').write_text(json.dumps(dict(sorted(unresolved.items(),key=lambda x:int(x[0]))),ensure_ascii=False,indent=2)+'\n')
(out/'source-conflicts.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2)+'\n')
print('mapped',len(selected),'unresolved',len(unresolved),'source conflicts',len(conflicts),'source counts',collections.Counter('dvg' if 'dvg.cn' in v['source'] else 'ro321' for v in selected.values()))
