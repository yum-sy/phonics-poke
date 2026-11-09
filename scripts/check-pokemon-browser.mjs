// Verify Pokémon fusion layout, local assets, reduced motion, and tap-through in Chrome.
// This is desktop evidence, not iPad or human pronunciation approval.
import { spawn } from 'node:child_process'
import { mkdtemp, readFile, mkdir, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import assert from 'node:assert/strict'

const base = (process.argv[2] || 'http://localhost:5174').replace(/\/$/, '')
const chromePath = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const work = await mkdtemp(join(tmpdir(), 'phonics-narration-'))
const profile = join(work, 'profile')
const output = process.env.POKEMON_CHECK_OUTPUT || join(process.cwd(), 'work/pokemon/browser-check')
await mkdir(output, { recursive: true })
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
const chrome = spawn(chromePath, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--disable-background-networking', '--ignore-certificate-errors',
  '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] })
let chromeErrors = ''
chrome.stderr.on('data', (chunk) => { chromeErrors = (chromeErrors + chunk).slice(-6000) })
let socket
let requestId = 0
const pending = new Map()
let currentErrors = []
let currentNetworkFailures = []
const report = { base, generatedAt: new Date().toISOString(), cases: [], failures: [] }

async function until(fn, description, timeout = 20000) {
  const end = Date.now() + timeout
  while (Date.now() < end) {
    const result = await fn()
    if (result) return result
    await sleep(100)
  }
  throw new Error(`Timed out: ${description}`)
}

function command(method, params = {}) {
  const id = ++requestId
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => { pending.delete(id); reject(new Error(`CDP timeout: ${method}`)) }, 30000)
    pending.set(id, { resolve, reject, timeout })
    socket.send(JSON.stringify({ id, method, params }))
  })
}

async function evaluate(expression) {
  const r = await command('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text)
  return r.result.value
}

async function navigate(path) {
  currentErrors = []
  currentNetworkFailures = []
  const url = base + path
  await command('Page.navigate', { url })
  await until(async () => {
    try { return await evaluate(`location.href === ${JSON.stringify(url)} && document.readyState !== 'loading'`) }
    catch { return false }
  }, `new document ${path}`)
}

async function screenshot(name) {
  const { data } = await command('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false })
  await writeFile(join(output, `${name}.png`), Buffer.from(data, 'base64'))
}


try {
  const port = await until(async () => {
    try { return Number((await readFile(join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]) }
    catch { if (chrome.exitCode !== null) throw new Error(chromeErrors); return null }
  }, 'Chrome debugging port')
  const tabs = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()
  socket = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl)
  await new Promise((resolve, reject) => { socket.addEventListener('open', resolve, { once: true }); socket.addEventListener('error', reject, { once: true }) })
  socket.addEventListener('message', ({ data }) => {
    const message = JSON.parse(data)
    if (message.id) {
      const job = pending.get(message.id)
      if (!job) return
      clearTimeout(job.timeout); pending.delete(message.id)
      if (message.error) job.reject(new Error(JSON.stringify(message.error)))
      else job.resolve(message.result)
    } else if (message.method === 'Runtime.consoleAPICalled') {
      const text = message.params.args.map(a => a.value ?? a.description ?? '').join(' ')
      if (text.includes('[chapters]') || message.params.type === 'error') currentErrors.push(text)
    } else if (message.method === 'Runtime.exceptionThrown') {
      currentErrors.push(message.params.exceptionDetails.exception?.description || message.params.exceptionDetails.text)
    } else if (message.method === 'Network.responseReceived') {
      const { url, status } = message.params.response
      if (/\/art\/(?:v[23]|pokemon)\//.test(url) && status >= 400) currentNetworkFailures.push({ url, status })
    }
  })
  await Promise.all([command('Page.enable'), command('Runtime.enable'), command('Network.enable')])
  await command('Emulation.setDeviceMetricsOverride', { width: 834, height: 1194, deviceScaleFactor: 1, mobile: false })

  const cases=[['portrait',834,1064],['landscape',1194,704]]
  for(const [orientation,width,height] of cases){
    await command('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false})
    for(const [name,query] of [['map','shot=map1'],['invite','shot=invite'],['teach','shot=boss1after'],['final','iso=c33s5:teach&unlock=1'],['long-boss','shot=boss8after&bosseq=c21-stage-5'],['long-name','shot=boss8after&bosseq=c12-stage-5']]){
      await navigate('/_probe.html?unlock=1&'+query)
      const hud=await until(()=>evaluate(`document.documentElement.getAttribute('data-probe')`),'probe HUD')
      if(['invite','final'].includes(name)) await until(()=>evaluate(`!!document.querySelector('.pokemon-fusion.combine-invite')`),'idle animation')
      const details=await evaluate(`({hud:document.documentElement.dataset.probe, minis:document.querySelectorAll('.mini-bot').length, broken:[...document.querySelectorAll('.pokemon-art img')].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src), wrapperAnimation:document.querySelector('.pokemon-fusion.combine-invite')?getComputedStyle(document.querySelector('.pokemon-fusion.combine-invite')).animationName:null, idle:document.querySelector('.pokemon-fusion.combine-invite .pokemon-idle')?getComputedStyle(document.querySelector('.pokemon-fusion.combine-invite .pokemon-idle')).display:null})`)
      await screenshot(orientation+'-'+name)
      report.cases.push({orientation,name,...details,errors:[...currentErrors]})
      console.log(orientation,name,JSON.stringify(details))
      assert(hud.startsWith('NOSCROLL'),hud)
      assert(!hud.includes('EXPECT-FAIL')&&!hud.includes('WRONG-BEAT'),hud)
      assert.equal(details.broken.length,0)
      assert.equal(currentErrors.length,0,currentErrors.join('\n'))
      if(['invite','final'].includes(name)){assert.equal(details.minis,4);assert.equal(details.wrapperAnimation,'none');assert.equal(details.idle,'block')}
    }
  }
  const badAssets=await evaluate(`(async()=>{const {default:r}=await import('/src/art/pokemon-roster.json');const urls=Object.values(r.assets).flatMap(a=>[a.static,a.idle].filter(Boolean));const bad=[];for(let i=0;i<urls.length;i+=16){await Promise.all(urls.slice(i,i+16).map(async file=>{const image=new Image();image.src='/art/pokemon/'+file;try{await image.decode()}catch{bad.push(file)}}))}return bad})()`)
  assert.deepEqual(badAssets,[]);console.log('PASS all 310 local PNG/GIF assets decode')
  await command('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]})
  await navigate('/_probe.html?shot=invite&unlock=1')
  await until(()=>evaluate(`document.documentElement.dataset.probe`),'reduced motion')
  const still=await evaluate(`document.querySelector('.pokemon-idle img').currentSrc`)
  assert(still.endsWith('.png'));console.log('PASS reduced-motion uses static PNG')
  await evaluate(`document.querySelector('#boss-intro').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))`)
  await until(()=>evaluate(`!document.querySelector('#boss-intro')`),'tap through')
  console.log('PASS tap exits fusion')
} catch(error){ report.failures.push(error.stack);console.error(error.stack);process.exitCode=1 }
finally {await writeFile(join(output,'report.json'),JSON.stringify(report,null,2));socket?.close();chrome.kill();}
