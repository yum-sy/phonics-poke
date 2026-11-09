"""Build local character assets/roster; no curriculum or audio mutations."""
import json,pathlib,csv,urllib.request,concurrent.futures,hashlib
R=pathlib.Path(__file__).resolve().parents[1];D=R/'design/pokemon-phonics';A=R/'public/art/pokemon';A.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text())
heroes=read(D/'hero-pronunciation-proposal.json');fusions=read(D/'fusion-hero-proposal.json')['assignments'];bosses=read(D/'boss-selection.json')['assignments'];names=read(D/'name-roster.json');byid={p['species_id']:p for p in names}
reserved={p['species_id'] for p in heroes['assignments']+heroes['helper_pool']+fusions}
# Keep the user's 11 hero reservations out of the villain pool even if unused.
reserved.update([491,802,892,1000,724,727,908,3,197,937,407])
bossids={p['species_id'] for p in bosses}
stats={}
for r in csv.DictReader((D/'source/pokemon_stats.csv').open()):stats[int(r['pokemon_id'])]=stats.get(int(r['pokemon_id']),0)+int(r['base_stat'])
pool=[p for p in names if p['species_id'] not in reserved|bossids and set(p['types'])&{'dark','poison','ghost'}]
pool.sort(key=lambda p:(stats[p['pokemon_id']],p['species_id']))
groups={t:[p for p in pool if t in p['types']] for t in ['dark','poison','ghost']}
villains=[]
for chapter in range(1,34):
 picked=[]
 for t in ['dark','poison','ghost']:
  g=groups[t];start=(chapter-1)*len(g)//33
  p=next(g[(start+j)%len(g)] for j in range(len(g)) if g[(start+j)%len(g)]['species_id'] not in picked)
  picked.append(p['species_id'])
 fourth=next(p for p in pool[(chapter-1)*len(pool)//33:]+pool if p['species_id'] not in picked);picked.append(fourth['species_id'])
 villains.extend(dict(chapter=chapter,step=i+1,**byid[sid]) for i,sid in enumerate(picked))
assignments={}
for p in heroes['assignments']:assignments[p['stage_id']]={'hero':p['species_id'],'heroRole':p['role']}
for p,v in zip(heroes['assignments'],villains):assignments[p['stage_id']]['villain']=v['species_id']
for h,b in zip(fusions,bosses):assert h['stage_id']==b['stage_id'];assignments[h['stage_id']]={'hero':h['species_id'],'heroRole':'fusion','villain':b['species_id']}
ids={p[role] for p in assignments.values() for role in ['hero','villain']};fusionids={p['species_id'] for p in fusions}
base='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/'
def download(url,path):
 if path.exists():return True
 try:
  data=urllib.request.urlopen(url,timeout=30).read()
 except urllib.error.HTTPError as e:
  if e.code==404:return False
  raise
 assert data[:8]==b'\x89PNG\r\n\x1a\n' or data[:6] in [b'GIF89a',b'GIF87a']
 path.write_bytes(data);return True
def asset(sid):
 p=byid[sid];pid=p['pokemon_id'];static=f'{sid}.png';url=base+f'other/home/{pid}.png'
 if not download(url,A/static):
  url=base+f'other/official-artwork/{pid}.png';assert download(url,A/static)
 gif=None
 if sid in fusionids:
  gurl=base+f'other/showdown/{pid}.gif'
  if download(gurl,A/f'{sid}.gif'):gif=f'{sid}.gif'
 return sid,dict(name=p['name_en'],nameKo=p['name_ko'],static=static,idle=gif,staticSource=url,idleSource=gurl if gif else None,sha256=hashlib.sha256((A/static).read_bytes()).hexdigest())
assets=dict(concurrent.futures.ThreadPoolExecutor(max_workers=8).map(asset,sorted(ids)))
manifest=dict(assignments=assignments,assets=assets)
(R/'src/art/pokemon-roster.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(D/'ordinary-villain-assignment.json').write_text(json.dumps(villains,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(stages=len(assignments),species=len(ids),animated=sum(bool(p['idle']) for p in assets.values()),static_fusions=[p['name'] for sid,p in assets.items() if sid in fusionids and not p['idle']]),ensure_ascii=False))
