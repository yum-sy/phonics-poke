"""Research proposal only; never mutates curriculum or runtime assets."""
import json, pathlib, html, collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'design/pokemon-phonics'
OUT=pathlib.Path('/Users/kami.san/Documents/Codex/2026-11-09/phonics-hero-pokemon-planning/outputs')
# Each segment was compared with the linked English pronunciation guide, not spelling alone.
raw='''S,S,A,T;Sobble: S;Seel: S;Abra: A;Togepi: T
I,I,P,N;Inkay: I;Incineroar: I;Pikachu: P;Nickit: N
C,C,E,H;Caterpie: C;Cubone: C;Ekans: E;Hoppip: H
R,R,M,D;Ralts: R;Riolu: R;Machop: M;Dratini: D
G,G,O,U;Goomy: G;Gholdengo: Gh;Oddish: O;Umbreon: U
L,L,F,B;Lucario: L;Litten: L;Fennekin: F;Bulbasaur: B
AI,AI,J,OA;Aipom: Ai;Taillow: ai;Jigglypuff: J;Gogoat: oa
IE,IE,EE,OR;Liepard: ie;Decidueye: eye;Eevee: Ee;Wartortle: or
Z,Z,W,NG;Zorua: Z;Zangoose: Z;Wooloo: W;Koffing: ng
V,V,OO,Y;Vulpix: V;Venusaur: V;Wooloo: oo;Yamper: Y
X,X,CH,SH;Shinx: x;Luxio: x;Chikorita: Ch;Marshadow: sh
TH,TH-voiced,QU,OU;Throh: Th;Slither Wing: th;Quaxly: Qu;Meowscarada: eow
OI,OI,UE,OI-review;Cloyster: oy;Baltoy: oy;Mew: ew;Spoink: oi
AR,AR,ER,ER-review;Arcanine: Ar;Darkrai: ar;Urshifu: Ur;Persian: er
ST,ST,SN,SN;Staryu: St;Stantler: St;Snivy: Sn;Snom: Sn
TR,TR,FR,FR;Treecko: Tr;Trapinch: Tr;Froakie: Fr;Frillish: Fr
CL,CL,GL,GL;Clefairy: Cl;Clobbopus: Cl;Glaceon: Gl;Gligar: Gl
ND,ND,NT,NT;Sandshrew: nd;Sandile: nd;Durant: nt;Trevenant: nt
NK,NK,FT,FT;Shinx: nx;Tinkatink: nk;Shiftry: ft;Scrafty: ft
SP,SP,SK,SK;Spinda: Sp;Spoink: Sp;Skitty: Sk;Skarmory: Sk
PL,PL,DR,DR;Plusle: Pl;Piplup: pl;Dratini: Dr;Drowzee: Dr
TW,TW,CT,GL;Turtwig: tw;Litwick: tw;Electrike: ct;Gloom: Gl
NT,NT,FT,FT;Greedent: nt;Cufant: nt;Shiftry: ft;Scrafty: ft
NCH,NCH,STR,STR;Pancham: nch;Trapinch: nch;Zebstrika: str;Gastrodon: str
SCR,SCR,NK,NK;Scraggy: Scr;Scream Tail: Scr;Tinkatink: nk;Mankey: nk
LT,LT,LF,LF;Ralts: lt;Jolteon: lt;Azelf: lf;Qwilfish: lf
LK,LK,XT,XT;Palkia: lk;Silcoon: lc;Toxtricity: xt;Pikachu: —
SC,SC,MP,MP;Scorbunny: Sc;Scrafty: Sc;Machamp: mp;Swampert: mp
ST,ST,TR,TR-review;Staryu: St;Stantler: St;Treecko: Tr;Trapinch: Tr
CL,CL,FR,FR-review;Clamperl: Cl;Clefairy: Cl;Froakie: Fr;Froslass: Fr
TW,TW,SN,SN-review;Turtwig: tw;Litwick: tw;Snorlax: Sn;Snivy: Sn
STR,STR,NCH,NCH-review;Zebstrika: str;Glastrier: str;Pancham: nch;Trapinch: nch
THR,THR,SHR,SHR-review;Throh: Thr;Espathra: thr;Shroomish: Shr;Shroodle: Shr'''
ipa=dict(x.split('=',1) for x in 'S=s A=æ T=t I=ɪ P=p N=n C=k E=ɛ H=h R=ɹ M=m D=d G=ɡ O=ɑ~ɒ U=ʌ L=l F=f B=b AI=eɪ J=dʒ OA=oʊ IE=aɪ EE=iː OR=ɔɹ Z=z W=w NG=ŋ V=v OO=uː Y=j X=ks CH=tʃ SH=ʃ TH=θ TH-voiced=ð QU=kw OU=aʊ OI=ɔɪ UE=juː AR=ɑɹ ER=ɜɹ ST=st SN=sn TR=tɹ FR=fɹ CL=kl GL=ɡl ND=nd NT=nt NK=ŋk FT=ft SP=sp SK=sk PL=pl DR=dɹ TW=tw CT=kt NCH=ntʃ STR=stɹ SCR=skɹ LT=lt LF=lf LK=lk XT=kst SC=sk MP=mp THR=θɹ SHR=ʃɹ'.split())
roster={r['name_en']:r for r in json.loads((D/'name-roster.json').read_text())}
pron={r['name']:r for r in json.loads((D/'pronunciation-sources/serebii.json').read_text())}
boss=json.loads((D/'boss-selection.json').read_text())
blocked={r['species_id'] for r in boss['assignments']}|{658}
stages=[r for r in json.loads((D/'stage-targets.json').read_text())['rows'] if not r['boss']]
notes={
(8,2):'소리는 /aɪ/로 일치하지만 철자는 ie가 아닌 eye.',
(10,3):'장모음 /uː/ 후보. 수업의 book /ʊ/까지 대표하지 않음.',
(12,1):'무성 /θ/. 뒤의 /r/까지 들리므로 단독 TH 첫 모델은 기존 음원 유지.',
(12,2):'조건부: 예시 this/that의 /ð/ 기준. teach 음원 키 thhu는 /θ/ 계열이므로 목표 확인 필요.',
(13,3):'/juː/ 기준. glue /ɡluː/와 구분. 철자는 ue가 아닌 ew.',
(13,4):'coin/cue 복습 중 coin의 /ɔɪ/를 대표. 두 소리 모두 대표하지 않음.',
(14,4):'AR/ER 복습 중 ER를 대표. 미국식 r 발음 기준.',
(19,1):'nx의 발음 /ŋks/ 안에 /ŋk/가 있음. NK 철자 모델로는 약함.',
(22,2):'Lit-wick의 음절 경계를 가로지르는 /tw/. 이름 첫소리는 /l/.',
(22,3):'/kt/가 이름 중간에 있음. 단어 끝 CT 연습의 직접 모델은 아님.',
(25,4):'nk가 /ŋk/로 발음됨. /n/+/k/로 분리해서 가르치지 않음.',
(27,2):'소리 /lk/ 일치, 철자는 lk가 아닌 lc. 끝소리 모델은 아님.',
(27,3):'이름 중간 /kstr/에 목표 /kst/ 포함. 철자는 xt, 단어 끝 XT는 아님.',
(27,4):'학습 도우미 예외: 피카츄 이름에 /kst/가 있다는 뜻이 아님. 기존 XT 단어·음원으로 학습을 돕는 역할.',
(32,2):'Glass-tree의 경계에 /str/가 있음. 첫머리 STR는 아님.',
(33,2):'이름 중간 path-ra의 /θr/. 실제 낭독에서 경계를 재확인할 우선 후보.',
}
assign=[]
for chapter,line in enumerate(raw.splitlines(),1):
 parts=line.split(';'); targets=parts[0].split(','); names=[]
 for index,entry in enumerate(parts[1:],1):
  name,segment=entry.split(': ',1);target=targets[index-1];base=target.replace('-review','');stage=stages[(chapter-1)*4+index-1]
  assert stage['chapter']==chapter
  r=dict(chapter=chapter,step=index,stage_id=stage['id'],curriculum_label=stage['emblem'],target=target,ipa='/'+ipa[base]+'/',segment=segment,note=notes.get((chapter,index),''),status='보류' if name=='?' else '발음표 대조 후보')
  if name!='?':
   p=roster[name];assert p['species_id'] not in blocked,(chapter,name)
   assert name not in names;names.append(name)
   q=pron[name];r.update(name_en=name,name_ko=p['name_ko'],species_id=p['species_id'],source=q['url'])
   if not r['note'] and segment.lower() not in name.lower():raise ValueError(entry)
   if 'review' in target and not r['note']:r['note']='통합 복습 중 '+base+' 소리를 대표.'
   if base in ['ND','FT','LT','LF','LK','NT','MP','NCH'] and not r['note']:r['note']='이름 안의 연속 소리 기준. 수업 단어의 끝소리 위치와는 다를 수 있음.'
  r['role']='learning_helper' if (chapter,index)==(27,4) else 'phonics_match'
  r['name_sound_match']=(r['role']=='phonics_match')
  if r['role']=='learning_helper':
   r['status']='학습 도우미 예외';r['segment']=None;r['source']=None
  assign.append(r)
assert len(assign)==132
reserved=[('Darkrai','AR /ɑɹ/ · IE /aɪ/','Dark-rai'),('Marshadow','SH /ʃ/ · AR /ɑɹ/','Mar-shad-ow'),('Urshifu','ER /ɜɹ/ · SH /ʃ/','Ur-shi-fu'),('Gholdengo','G /ɡ/ · OA /oʊ/','Ghol-den-go'),('Decidueye','IE /aɪ/','마지막 eye'),('Incineroar','I /ɪ/ · S /s/','첫 In, 가운데 cin'),('Meowscarada','OU /aʊ/ · SC /sk/','Meow, sca'),('Venusaur','V /v/ · EE /iː/','첫 Ve'),('Umbreon','U /ʌ/','첫 Um'),('Ceruledge','S /s/ · OO /uː/','첫 Ce는 /s/, 가운데 ru는 /ruː/'),('Roserade','R /ɹ/ · OA /oʊ/ · AI /eɪ/','Rose, rade')]
result={'scope':'132 ordinary stage proposals; stage5 strong heroes unchanged','evidence':'Serebii official-pronunciation listing, written evidence only; no independent audio listening; IPA denotes target sound inferred from guide, not full official IPA transcription','assignments':assign,'unique_species':len({r['species_id'] for r in assign if 'species_id' in r}),'unfilled':sum('species_id' not in r for r in assign),'reserved_hero_review':[dict(name_en=n,target=t,segment=s,source=pron[n]['url']) for n,t,s in reserved]}
result['helper_pool']=[dict(name_en=n,name_ko=roster[n]['name_ko'],species_id=roster[n]['species_id']) for n in ['Pikachu','Snorlax','Pachirisu']]
result['helper_policy']='Only when a suitable phonics match is unavailable; reuse small pool across chapters; no claimed name-sound match; preserve four distinct species per chapter and hero/villain separation.'
result['helper_slots']=sum(r['role']=='learning_helper' for r in assign)
assert all(r['species_id'] not in blocked for r in result['helper_pool'])
(D/'hero-pronunciation-proposal.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
e=html.escape
body='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>포켓몬 히어로 파닉스 후보</title><style>body{font:16px/1.65 system-ui,sans-serif;max-width:1250px;margin:40px auto;padding:0 22px;color:#182437;background:#f7f9fc}h1{font-size:30px}h2{margin-top:42px}table{border-collapse:collapse;width:100%;background:white;margin:18px 0}td,th{border:1px solid #dce2ec;padding:11px;text-align:left;vertical-align:top}th{background:#eaf0f8}small{display:block;color:#58677a}.tag{font-weight:700;color:#244c9c}.warning{background:#fff2d9;padding:18px;border-radius:10px}a{color:#2453aa}details{margin:16px 0}summary{cursor:pointer;font-weight:bold}@media(max-width:800px){.scroll{overflow:auto}td{min-width:140px}}@media print{body{background:white;font-size:10pt}details{display:block}table{break-inside:auto}tr{break-inside:avoid}}</style>
<h1>목표 소리로 고른 히어로 후보</h1><p>33챕터 × 일반 단계 4개 = 132자리. 확정 보스 33종 및 합체 예약 개굴닌자는 제외했습니다. 다른 챕터 재등장은 허용하고, 같은 챕터 4마리는 서로 다르게 구성했습니다. 5단계 강한 히어로는 이번 표의 대상이 아닙니다.</p>'''
body+=f'<p><b>발음 연결 후보 131자리 + 학습 도우미 1자리 · {result["unique_species"]}종 · 빈자리 없음.</b> 후보는 사용자 확정 전 검토안이며, 게임에는 반영하지 않았습니다. 일반 빌런 명단은 아직 미확정이므로 이 후보가 채택되면 해당 종을 빌런 후보에서 제외해야 합니다.</p>'
body+='''<p>근거는 Serebii의 세대별 영어 발음표입니다. 이 사이트는 최신 공식 발음을 수록한다고 명시하지만, Pokémon 공식 운영 사이트는 아닙니다. 이름마다 출처를 연결했습니다. <b>영어 발음 표기를 대조했으며, 공식 영어 음성을 전 종 직접 청취한 결과는 아닙니다.</b> 아래 / / 표기는 그 이름에서 확인한 목표 소리이며 이름 전체의 IPA 전사가 아닙니다.</p>
<div class="warning"><b>확정 전 남은 사항</b><ul><li>학습 도우미는 피카츄·잠만보·파치리스 3종으로 압축했습니다. 적합한 발음 후보가 없을 때 챕터 간 반복 활용합니다. 27-4 XT는 피카츄가 돕되 이름과 /kst/의 연결을 주장하지 않습니다.</li><li>12-2 TH: teach는 /θ/ 계열, 예시 this·that은 /ð/. 아래는 예시 기준 날개치는머리가 아닌 <b>땅을기는날개(Slither Wing)</b> 후보입니다.</li><li>10-3 OO: Wooloo는 /uː/만 대표합니다. book의 /ʊ/는 별도 단어 음원으로 다룹니다.</li><li>13-3 UE: Mew는 /juː/ 후보. glue의 /uː/와 동일한 소리로 묶지 않습니다.</li><li>후반부에는 이름 중간·음절 경계의 소리도 사용했습니다. 단어 끝 자음군 학습은 원래 단어와 음원을 유지해야 합니다.</li></ul></div>
<h2>챕터별 1~4단계 제안</h2><p>칸 안 순서: 목표 소리 → 한국어명 / 영어명 → 이름 속 해당 철자. 같은 소리라도 학습 철자와 이름 철자가 다른 경우 따로 표시했습니다.</p><div class="scroll"><table><tr><th>챕터</th><th>1단계</th><th>2단계</th><th>3단계</th><th>4단계</th></tr>'''
for ch in range(1,34):
 body+=f'<tr><th>{ch}</th>'
 for r in assign[(ch-1)*4:ch*4]:
  body+=f'<td><span class="tag">{e(r["target"])} {e(r["ipa"])}</span><br>'
  if r['role']=='learning_helper':body+=f'<b>{e(r["name_ko"])}</b><br>{e(r["name_en"])}<small>학습 도우미 · 이름 발음 연결 없음</small>'
  elif 'species_id' in r:body+=f'<b>{e(r["name_ko"])}</b><br><a href="{r["source"]}">{e(r["name_en"])}</a><small>소리 위치: {e(r["segment"])}</small>'
  else:body+='<b>후보 보류</b>'
  if r['note']:body+=f'<small>{e(r["note"])}</small>'
  body+='</td>'
 body+='</tr>'
body+='</table></div><h2>보스에서 빼둔 11종의 히어로 적합 소리</h2><table><tr><th>포켓몬</th><th>연결 가능한 목표</th><th>발음 위치</th></tr>'
for n,t,s in reserved:body+=f'<tr><td>{e(roster[n]["name_ko"])} · <a href="{pron[n]["url"]}">{n}</a></td><td>{e(t)}</td><td>{e(s)}</td></tr>'
body+='''</table><h2>철자만 보고 넣으면 틀리는 예</h2><ul><li>Psyduck: P는 묵음. /p/ 히어로로 쓰지 않음.</li><li>Cyndaquil: 첫 C는 /s/. /k/ 자리에 넣지 않음.</li><li>Geodude: 첫 G는 /dʒ/. /ɡ/ 자리에 넣지 않음.</li><li>Archen: ch는 /k/. CH /tʃ/ 자리에 넣지 않음.</li><li>Scyther: Sc는 /s/. SC /sk/ 자리에 넣지 않음.</li><li>Walking Wake: walk의 l은 보통 묵음. LK 후보로 쓰지 않음.</li><li>Mewtwo: /mjuː tuː/로 t 뒤에 /w/가 없음. 철자 tw만으로 TW 후보에 넣지 않음.</li></ul><p>이름은 목표 소리를 찾는 보조 예시입니다. 소리 자체의 첫 시범 및 반복은 기존 파닉스 녹음, 블렌딩은 기존 학습 단어를 사용합니다. r 계열은 미국 영어의 r 발음 유지 기준이며 자연스러운 TR·DR 발음에는 변이가 있습니다.</p><p>검토일: 2026-11-09 · 이 문서는 연구 제안이며 수업 데이터·캐릭터·음원을 변경하지 않습니다.</p></html>'''
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'hero-phonics-candidates.html').write_text(body)
(OUT/'hero-phonics-candidates.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'slots':len(assign),'filled':132-result['unfilled'],'unique_species':result['unique_species'],'boss_overlap':0,'within_chapter_duplicates':0,'output':str(OUT/'hero-phonics-candidates.html')},ensure_ascii=False))
