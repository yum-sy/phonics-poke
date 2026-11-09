"""Build a reviewable stage-5 proposal from the previously captured PIKU ranks."""
import json,pathlib,html,hashlib,csv
R=pathlib.Path(__file__).resolve().parents[1];D=R/'design/pokemon-phonics';O=pathlib.Path('/Users/kami.san/Documents/Codex/2026-11-09/phonics-hero-pokemon-planning/outputs')
ranking=json.loads((R/'design/pokemon-research/ranked-candidates.json').read_text())
boss=json.loads((D/'boss-selection.json').read_text())['assignments']
ordinary=json.loads((D/'hero-pronunciation-proposal.json').read_text())
reserved={x['species_id'] for x in ordinary['assignments']+ordinary['helper_pool']}
bossids={x['species_id'] for x in boss}
species={int(x['id']):x for x in csv.DictReader((R/'design/pokemon-research/pokemon_species.csv').open())}
parents={int(x['evolves_from_species_id']) for x in species.values() if x['evolves_from_species_id']}
def eligible(sid):
 p=species[sid]
 return p['is_legendary']=='1' or p['is_mythical']=='1' or (bool(p['evolves_from_species_id']) and sid not in parents)
selected=[x for x in sorted(ranking,key=lambda x:x['rank']) if x['species_id'] not in reserved|bossids and eligible(x['species_id'])][:33]
assert len(selected)==33 and any(x['species_id']==658 for x in selected)
roster={x['species_id']:x for x in json.loads((D/'name-roster.json').read_text())}
assign=[]
for b,p in zip(boss,reversed(selected)):
 assign.append(dict(chapter=b['chapter'],world=b['world'],stage_id=b['stage_id'],species_id=p['species_id'],pokemon_id=p['pokemon_id'],name_ko=p['name_ko'],name_en=roster[p['species_id']]['name_en'],piku_rank=p['rank'],boss_name_ko=b['name_ko']))
assert len({x['species_id'] for x in assign})==33
assert all(eligible(x['species_id']) for x in assign)
assert assign[-1]['species_id']==658 and assign[-1]['boss_name_ko']=='무한다이노'
result=dict(status='proposal',source_url='https://www.piku.co.kr/w/rank/9rRpKA',ranking_snapshot_date='2026-11-09',ranking_note='Previously captured displayed PIKU rank, not historical official poll rank in name. Live page checked again but rows unavailable to text browser; no claim of newly refreshed ranks.',selection='Top 33 evolved terminal or legendary/mythical species from full 86-entry snapshot; exclude confirmed bosses, ordinary heroes, and helper pool. Descending numeric rank across chapters.',design_choices=['33 distinct fusion heroes','No shared type or name-phonics condition','Only evolved terminal species or legendary/mythical species; non-evolving non-legendary species excluded','Rank indicates popularity, not battle strength','Greninja at chapter33 stage5'],assignments=assign)
(D/'fusion-hero-proposal.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
O.mkdir(exist_ok=True,parents=True);(O/'fusion-hero-proposal.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
e=html.escape
s='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>33챕터 합체 히어로 배치안</title><style>body{font:16px/1.7 system-ui;max-width:1000px;margin:40px auto;padding:0 20px;background:#f7f9fc;color:#182437}table{width:100%;border-collapse:collapse;background:white}td,th{padding:10px;border:1px solid #dce2ec;text-align:left}th{background:#eaf0f8}a{color:#2453aa}</style><h1>33챕터 합체 히어로 배치안</h1><p>일반 히어로·학습 도우미·확정 보스와 겹치지 않는 인기 상위33종을 선택했습니다. 챕터 간 합체 히어로도 중복되지 않습니다. 개굴닌자는33챕터5단계에서 무한다이노를 상대합니다.</p><p>이전에 확인한2026-11-09 <a href="https://www.piku.co.kr/w/rank/9rRpKA">PIKU 표시 순위</a> 스냅샷 기준입니다. 이름 괄호 속 과거 공식투표 순위는 사용하지 않습니다. 페이지는 재확인했지만 동적 순위 행을 새로 읽지 못했으므로 실시간 갱신값이라고 주장하지 않습니다.</p><p>기존 상위20위 제한 대신 전체86종에서 조건에 맞는 상위33종을 고른 제안입니다. 인기가 높은 포켓몬을 후반에 배치하며 종족값순은 아닙니다. 공통타입·이름파닉스 조건은 적용하지 않습니다. 진화 계보가 있는 최종 진화체 또는 전설·환상만 포함했습니다. 미진화4종과 무진화 일반종 데덴네·따라큐를 제외하고 메타그로스·에브이·미끄래곤·샤로다·갑주무사·나무킹을 추가했습니다. 게임에는 미적용입니다.</p><table><tr><th>월드</th><th>챕터</th><th>합체 히어로</th><th>PIKU 순위</th><th>확정 보스</th></tr>'''
for x in assign:s+=f'<tr><td>{x["world"]}</td><td>{x["chapter"]} · 5단계</td><td>{e(x["name_ko"])} / {e(x["name_en"])}</td><td>{x["piku_rank"]}</td><td>{e(x["boss_name_ko"])}</td></tr>'
s+='</table><p>검증:33종 고유 · 보스겹침0 · 일반히어로/도우미겹침0 · 기존33개5단계ID 유지.</p></html>'
(O/'fusion-hero-proposal.html').write_text(s)
baseline=json.loads((R/'design/pokemon-research/preservation-baseline.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in baseline.items())
print('33 unique fusions; all exclusions passed; protected files unchanged:',len(baseline))
