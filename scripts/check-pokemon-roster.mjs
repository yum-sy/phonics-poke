import assert from 'node:assert/strict'
import fs from 'node:fs'
import { createHash } from 'node:crypto'
import { chapters, validateChapters } from '../src/data/chapters/index.js'
import { heroArt, heroEmblem } from '../src/art.js'
import { fusionLineup } from '../src/art/fusion-lineup.js'
import { POKEMON_CHARACTERS } from '../src/art/pokemon.js'
import { PHRASE_FAMILIES, englishFor } from '../src/data/phrasebook.js'
const json = p => JSON.parse(fs.readFileSync(new URL(p, import.meta.url)))
const targets=json('../design/pokemon-phonics/stage-targets.json').rows
function gifFrames(bytes) {
 let i=13,frames=0
 if(bytes[10]&128)i+=3*(2**((bytes[10]&7)+1))
 const skip=()=>{while(bytes[i]){i+=bytes[i]+1}i++}
 while(i<bytes.length){
  const block=bytes[i++]
  if(block===0x3b)break
  if(block===0x21){i++;skip()}
  else if(block===0x2c){const packed=bytes[i+8];i+=9;if(packed&128)i+=3*(2**((packed&7)+1));i++;skip();frames++}
  else throw new Error('Invalid GIF block')
 }
 return frames
}
const heroes=new Set(),villains=new Set()
assert.deepEqual(validateChapters(),[])
assert.equal(chapters.length,33)
for(const c of chapters){
 assert.equal(c.stages.length,5)
 assert.equal(fusionLineup(c.stages).length,4)
 assert.equal(new Set(c.stages.map(s=>POKEMON_CHARACTERS[s.hero.art].speciesId)).size,5)
 assert.equal(new Set(c.stages.map(s=>POKEMON_CHARACTERS[s.villain.art].speciesId)).size,5)
 for(const s of c.stages){
  assert.equal(heroEmblem(s.hero),targets.find(t=>t.id===s.id).emblem)
  heroes.add(POKEMON_CHARACTERS[s.hero.art].speciesId);villains.add(POKEMON_CHARACTERS[s.villain.art].speciesId)
  for(const role of ['hero','villain']) assert(fs.existsSync(new URL('../public/art/pokemon/'+POKEMON_CHARACTERS[s[role].art].static,import.meta.url)))
  if(s.chapterBoss){
   const a=POKEMON_CHARACTERS[s.hero.art];assert(a.idle)
   const bytes=fs.readFileSync(new URL('../public/art/pokemon/'+a.idle,import.meta.url));assert.equal(bytes.subarray(0,3).toString(),'GIF');assert(gifFrames(bytes)>1,`Idle is not animated: ${a.name}`)
   assert(heroArt(s.hero,{idle:true}).includes('prefers-reduced-motion'))
  }
 }
}
assert.equal([...heroes].filter(id=>villains.has(id)).length,0)
assert.equal(POKEMON_CHARACTERS[chapters[32].stages[4].hero.art].speciesId,658)
assert.equal(POKEMON_CHARACTERS[chapters[32].stages[4].villain.art].speciesId,890)
const manifest=json('../public/narration/manifest.json');const spoken=new Set(manifest.entries.map(e=>e.text))
for(const c of chapters)for(const s of c.stages.filter(s=>s.chapterBoss))for(const beat of s.beats.slice(0,1)){
 const en=englishFor(beat.instructionKo);if(en && c.order>=6)assert(spoken.has(en),`Missing instruction recording: ${en}`)
}
for(const [key,rank] of Object.entries(json('./phrase-family-ranks.json')))assert.equal(PHRASE_FAMILIES[key].rank,rank)
let protectedAudio=0
for(const [p,h] of Object.entries(json('../design/pokemon-research/preservation-baseline.json'))){
 if(!p.startsWith('public/sounds/')&&!p.startsWith('public/narration/'))continue
 assert.equal(createHash('sha256').update(fs.readFileSync(new URL('../'+p,import.meta.url))).digest('hex'),h,p);protectedAudio++
}
console.log(`PASS 165 stages, four-member fusion, 33 idle GIFs, disjoint roles, preserved sounds/language ranks; ${protectedAudio} audio files unchanged`)
