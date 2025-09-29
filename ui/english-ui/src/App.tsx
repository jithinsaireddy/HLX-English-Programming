import React, { useState } from 'react'
import { motion } from 'framer-motion'

// In dev (vite), use the proxy at /api; in prod (nginx), also /api
const API = (import.meta as any).env?.VITE_API_URL || '/api'

export default function App() {
  const [tab, setTab] = useState<'hlx'|'epl'|'tutorials'|'nlp'>('hlx')
  return (
    <motion.div initial={{opacity:0}} animate={{opacity:1}}>
      <header>
        <motion.h2 layout>English Programming Playground</motion.h2>
        <div className="tabs">
          <button className={tab==='hlx'?'active':''} onClick={()=>setTab('hlx')}>HLX</button>
          <button className={tab==='epl'?'active':''} onClick={()=>setTab('epl')}>EPL</button>
          <button className={tab==='tutorials'?'active':''} onClick={()=>setTab('tutorials')}>Tutorials</button>
          <button className={tab==='nlp'?'active':''} onClick={()=>setTab('nlp')}>NLP Debug</button>
        </div>
      </header>
      <div className="container">
        <motion.div key={tab} initial={{x:30,opacity:0}} animate={{x:0,opacity:1}}>
          {tab==='hlx' && <HLX/>}
          {tab==='epl' && <EPL/>}
          {tab==='tutorials' && <Tutorials/>}
          {tab==='nlp' && <NLPDebug/>}
        </motion.div>
      </div>
    </motion.div>
  )
}

function HLX() {
  const sample = `Device "Boiler-A" at mqtt://plant/boilerA\nSensor "pressure" unit kPa period 200 ms\nActuator "relief_valve" actions open, close\n\nIf pressure > 180 kPa for 600 ms then\n  open relief_valve\n  publish event "overpressure" with timestamp and value\n  store last 5000 ms of pressure to table "incidents"`
  const [spec, setSpec] = useState(sample)
  const [rtos, setRtos] = useState('')
  const [manifest, setManifest] = useState('')
  const [td, setTd] = useState('')
  const [log, setLog] = useState('')
  const [shareUrl, setShareUrl] = useState('')
  const snippets = [
    {name:'Boiler – Overpressure', text: sample},
    {name:'HVAC – Thermostat (hysteresis/cooldown)', text: `Device "HVAC-Unit-42" at mqtt://building/A3/HVAC42\nSensor "temp" unit C period 1 s\nActuator "heater" actions on, off\nActuator "cooler" actions on, off\n\nIf temp < 21.5 C for 2 s with hysteresis 5 % and cooldown 5000 ms then\n  on heater\n  off cooler\n  publish event "heat_on"\nIf temp > 22.5 C for 2 s with hysteresis 5 % and cooldown 5000 ms then\n  off heater\n  on cooler\n  publish event "cool_on"`},
    {name:'Water Tank – Multi-sensor imbalance', text: `Device "Tank-7" at mqtt://plant/water/T7\nSensor "level" unit % period 500 ms\nSensor "flow_in" unit Lps period 500 ms\nSensor "flow_out" unit Lps period 500 ms\nActuator "inlet_valve" actions open, close\nActuator "outlet_valve" actions open, close\n\nIf level >= 95 for 500 ms then\n  close outlet_valve\n  publish event "overflow_protect"\nIf level <= 10 for 500 ms then\n  close outlet_valve\n  publish event "dry_protect"\nIf flow_in > flow_out for 500 ms then\n  store last 10000 ms of flow_in, flow_out to table "imbalance"\n  publish event "imbalance_detected"`},
    {name:'Pipeline – Leak Detection', text:`Device "Pipe-12" at mqtt://field/pipe12\nSensor "pressure" unit kPa period 200 ms\nSensor "pressure_downstream" unit kPa period 200 ms\nActuator "main_valve" actions close, open\n\nIf pressure - pressure_downstream > 50 for 600 ms then\n  close main_valve\n  publish event "possible_leak"\n  store last 10000 ms of pressure, pressure_downstream to table "leaks"`},
    {name:'Hospital – CO₂ (fast)', text: `Device "Room-312" at mqtt://hospital/room312\nSensor "co2_ppm" unit ppm period 500 ms\nActuator "vent_damper" actions open, close\n\nIf co2_ppm > 1200 ppm for 1000 ms with hysteresis 5 % and cooldown 5000 ms then\n  open vent_damper\n  publish event "co2_alert" with timestamp and value\n  store last 60000 ms of co2_ppm to table "air_quality"`},
    {name:'Cold-chain – Freezer (fast)', text: `Device "Freezer-7" at mqtt://plant/freezer7\nSensor "temp_c" unit C period 1000 ms\nActuator "alarm" actions on, off\n\nIf temp_c > -10 C for 2000 ms with hysteresis 10 % and cooldown 10000 ms then\n  on alarm\n  publish event "freezer_temp_high" with timestamp and value`},
    {name:'Hospital – CO₂', text: `Device "Room-312" at mqtt://hospital/room312\nSensor "co2_ppm" unit ppm period 500 ms\nActuator "vent_damper" actions open, close\n\nIf co2_ppm > 1200 ppm for 1 s with hysteresis 5 % and cooldown 10000 ms then\n  open vent_damper\n  publish event "co2_alert" with timestamp and value\n  store last 600000 ms of co2_ppm to table "air_quality"`},
    {name:'Cold-chain – Freezer', text: `Device "Freezer-7" at mqtt://plant/freezer7\nSensor "temp_c" unit C period 1000 ms\nActuator "alarm" actions on, off\n\nIf temp_c > -10 C for 3 s with hysteresis 10 % and cooldown 30000 ms then\n  on alarm\n  publish event "freezer_temp_high" with timestamp and value`},
  ]
  const compile = async () => {
    setLog('');
    const r = await fetch(API+'/hlx/compile', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({spec}) })
    if(!r.ok){
      const text = await r.text().catch(()=> '')
      alert(`Compile failed (${r.status}). ${text || 'No response body.'}`)
      return
    }
    const j = await r.json().catch(()=>({ok:false,error:'Invalid JSON from server'}))
    if(!j.ok){ alert(j.error); return }
    setRtos(j.rtos); setManifest(j.manifest); setTd(j.td)
  }
  const runDemo = async () => {
    const r = await fetch(API+'/hlx/run_demo', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({spec}) })
    if(!r.ok){
      const text = await r.text().catch(()=> '')
      alert(`Run demo failed (${r.status}). ${text || 'No response body.'}`)
      return
    }
    const j = await r.json().catch(()=>({ok:false,error:'Invalid JSON from server'}))
    if(!j.ok){ alert(j.error); return }
    setLog(j.log)
  }
  const download = (name: string, content: string) => {
    const blob = new Blob([content], {type:'text/plain'})
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = name
    a.click()
  }
  const share = async () => {
    const r = await fetch(API+'/share/save', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({kind:'hlx', content: spec}) })
    const j = await r.json(); if(!j.ok){ alert(j.error); return }
    const url = `${window.location.origin}?hlx=${j.id}`
    setShareUrl(url)
    navigator.clipboard?.writeText(url).catch(()=>{})
  }
  // Load shared HLX if present in query
  React.useEffect(()=>{
    const id = new URLSearchParams(window.location.search).get('hlx')
    if(id){
      fetch(API+`/share/get?id=${id}`).then(r=>r.json()).then(j=>{ if(j.ok && j.kind==='hlx') setSpec(j.content) })
    }
  },[])
  return (
    <div>
      <p>Write rules in English (HLX). Click Compile to see outputs, Run Demo to simulate, Download to save files.</p>
      <div style={{display:'flex', gap:12}}>
        <div style={{minWidth:260}}>
          <h4>Examples</h4>
          {snippets.map(s=> (
            <div key={s.name} style={{display:'flex', gap:6, marginBottom:6}}>
              <button onClick={()=>setSpec(s.text)} style={{flex:1, textAlign:'left'}}>{s.name}</button>
              <button onClick={()=>{ setSpec(prev => prev + (prev.endsWith('\n')?'':'\n') + s.text) }}>Load to editor</button>
            </div>
          ))}
        </div>
        <div style={{flex:1}}>
      <textarea value={spec} onChange={e=>setSpec(e.target.value)} />
      <div style={{margin:'10px 0'}}>
        <motion.button whileTap={{scale:0.97}} onClick={compile}>Compile</motion.button>
        <motion.button whileTap={{scale:0.97}} onClick={runDemo}>Run Demo</motion.button>
        <motion.button whileTap={{scale:0.97}} onClick={()=>{ download('rtos.rs', rtos); download('edge_manifest.json', manifest); download('thing_description.json', td) }}>Download</motion.button>
        <motion.button whileTap={{scale:0.97}} onClick={share}>Share</motion.button>
      </div>
      {shareUrl && <div><small>Link copied: {shareUrl}</small></div>}
      <div className="row">
        <div className="col"><h3>rtos.rs</h3><motion.pre initial={{opacity:0}} animate={{opacity:1}}>{rtos}</motion.pre></div>
        <div className="col"><h3>edge_manifest.json</h3><motion.pre initial={{opacity:0}} animate={{opacity:1}}>{manifest}</motion.pre></div>
        <div className="col"><h3>thing_description.json</h3><motion.pre initial={{opacity:0}} animate={{opacity:1}}>{td}</motion.pre></div>
      </div>
      <h3>Demo Log</h3>
      <motion.pre initial={{opacity:0}} animate={{opacity:1}}>{log}</motion.pre>
        </div>
      </div>
    </div>
  )
}

function EPL() {
  const sample = `create a variable called x and set it to 2\ncreate a variable called y and set it to 3\nadd x and y and store the result in sum\nprint sum`
  const [code, setCode] = useState(sample)
  const [msg, setMsg] = useState('')
  const [shareUrl, setShareUrl] = useState('')
  const snippets = [
    {name:'Sum & Print', text: sample},
    {name:'Strings & Trim', text:`create a variable called name and set it to " alice "\ntrim name and store it in cleaned\nmake the cleaned uppercase and store it in upper\nprint upper`},
    {name:'If/Else', text:`create a variable called age and set it to 21\nif age is greater than 18:\n  set status to "Adult"\nelse:\n  set status to "Minor"\nprint status`},
    {name:'Files CRUD', text:`create a variable called fname and set it to "tmp.txt"\nwrite file fname with content "hello"\nread file fname store in data\nprint data\ndelete file fname`},
    {name:'Sets', text:`create a set called s\nadd 'a' to set s\ncheck if 'a' in set s store in present\nprint present`},
    {name:'CSV Roundtrip', text:`create a variable called csv and set it to "a,b\\n1,2"\nparse csv csv store in table\nstringify csv table store in out\nprint out`},
    {name:'YAML Roundtrip', text:`create a variable called y and set it to "a: 1"\nparse yaml y store in obj\nstringify yaml obj store in s\nprint s`},
    {name:'Async Read', text:`create a variable called fname and set it to "tmp.txt"\nwrite file fname with content "hello async"\nasync read file fname await store in data\nprint data`},
    {name:'HTTP GET (may need internet)', text:`http get "https://example.com" store in body\nprint body`},
    {name:'IMPORTURL (may need internet)', text:`import from url "https://example.com" store in content\nprint content`},
    {name:'OOP – Class/Fields/Method', text:`Define class Counter with fields: value\nMethod inc(n)\n  set self.value to n\nEnd method\nEnd class\nnew Counter store in c\ncall method c.inc(5) store in _\nget c.value store in v\nprint v`},
    {name:'Two Sum (indices)', text:`create a list called nums with values 2, 7, 11, 15\ncreate a variable called target and set it to 9\ncreate a map called seen\ncreate a variable called i and set it to 0\nwhile i is less than 4:\n  get item at index i from list nums and store in val\n  subtract target and val and store the result in need\n  map get seen need store in pos\n  if pos is equal to -1:\n    map put seen val i store in seen\n  else:\n    print i\n  add i and 1 and store the result in i\nprint i`},
    {name:'Valid Parentheses', text:`create a variable called s and set it to "()[]"\ncreate a list called st with values 0\ncreate a variable called i and set it to 0\nlength of s store in n\nwhile i is less than n:\n  get item at index i from list s and store in ch\n  case ch of '(': set open to 1 elif '[': set open to 1 else set open to 0\n  if open is equal to 1:\n    case ch of '(': set need to ')' elif '[': set need to ']' else set need to ' '\n    append need to list st store in st\n  else:\n    pop from list st store in top\n    if top is equal to 0:\n      print 0\n    elif ch is equal to top:\n      get i store in i\n    else:\n      print 0\n  add i and 1 and store the result in i\npop from list st store in rem\nif rem is equal to 0:\n  print 1\nelse:\n  print 0`},
    {name:'BFS (set visited)', text:`create a list called l0 with values 1, 2\ncreate a list called l1 with values 2\ncreate a list called l2\ncreate a map called adj\nmap put adj 0 l0 store in adj\nmap put adj 1 l1 store in adj\nmap put adj 2 l2 store in adj\ncreate a list called q with values 0\ncreate a set called seen\nadd 0 to set seen\ncreate a variable called qi and set it to 0\nwhile qi is less than 3:\n  get item at index qi from list q and store in u\n  map get adj u store in nbrs\n  length of nbrs store in m\n  create a variable called j and set it to 0\n  while j is less than m:\n    get item at index j from list nbrs and store in v\n    check if v in set seen store in pres\n    if pres is equal to 0:\n      append v to list q store in q\n      add v to set seen\n    add j and 1 and store the result in j\n  add qi and 1 and store the result in qi\nlength of q store in out\nprint out`},
    {name:'BFS (map visited)', text:`create a list called l0 with values 1, 2\ncreate a list called l1 with values 2\ncreate a list called l2\ncreate a map called adj\nmap put adj 0 l0 store in adj\nmap put adj 1 l1 store in adj\nmap put adj 2 l2 store in adj\ncreate a list called q with values 0\ncreate a map called seen\nmap put seen 0 1 store in seen\ncreate a variable called qi and set it to 0\nwhile qi is less than 3:\n  get item at index qi from list q and store in u\n  map get adj u store in nbrs\n  length of nbrs store in m\n  create a variable called j and set it to 0\n  while j is less than m:\n    get item at index j from list nbrs and store in v\n    map get seen v store in pos\n    if pos is equal to -1:\n      append v to list q store in q\n      map put seen v 1 store in seen\n    add j and 1 and store the result in j\n  add qi and 1 and store the result in qi\nlength of q store in out\nprint out`},
    {name:'Topological Sort (Kahn)', text:`create a list called l0 with values 1, 2\ncreate a list called l1 with values 2\ncreate a list called l2\ncreate a map called adj\nmap put adj 0 l0 store in adj\nmap put adj 1 l1 store in adj\nmap put adj 2 l2 store in adj\ncreate a map called indeg\nmap put indeg 0 0 store in indeg\nmap put indeg 1 0 store in indeg\nmap put indeg 2 0 store in indeg\ncreate a variable called u and set it to 0\nwhile u is less than 3:\n  map get adj u store in nbrs\n  length of nbrs store in m\n  create a variable called j and set it to 0\n  while j is less than m:\n    get item at index j from list nbrs and store in v\n    map get indeg v store in d\n    add d and 1 and store the result in d1\n    map put indeg v d1 store in indeg\n    add j and 1 and store the result in j\n  add u and 1 and store the result in u\ncreate a list called q\ncreate a variable called v and set it to 0\nwhile v is less than 3:\n  map get indeg v store in d\n  if d is equal to 0:\n    append v to list q store in q\n  add v and 1 and store the result in v\ncreate a variable called qi and set it to 0\nlength of q store in nq\nwhile qi is less than nq:\n  get item at index qi from list q and store in u\n  map get adj u store in nbrs\n  length of nbrs store in m\n  create a variable called j and set it to 0\n  while j is less than m:\n    get item at index j from list nbrs and store in v\n    map get indeg v store in d\n    subtract d and 1 and store the result in d1\n    map put indeg v d1 store in indeg\n    if d1 is equal to 0:\n      append v to list q store in q\n      length of q store in nq\n    add j and 1 and store the result in j\n  add qi and 1 and store the result in qi\nlength of q store in out\nprint out`},
    {name:'Merge Intervals (paired arrays)', text:`create a list called starts with values 1, 2, 8\ncreate a list called ends with values 3, 6, 10\nlength of starts store in n\ncreate a list called rs\ncreate a list called re\ncreate a variable called i and set it to 0\nget item at index i from list starts and store in cs\nget item at index i from list ends and store in ce\nadd i and 1 and store the result in i\nwhile i is less than n:\n  get item at index i from list starts and store in ns\n  get item at index i from list ends and store in ne\n  if ns is less than or equal to ce:\n    if ne is greater than ce:\n      set ce to ne\n  else:\n    append cs to list rs store in rs\n    append ce to list re store in re\n    set cs to ns\n    set ce to ne\n  add i and 1 and store the result in i\nappend cs to list rs store in rs\nappend ce to list re store in re\nlength of rs store in out\nprint out`},
    {name:'Dijkstra (sketch)', text:`create a list called w0 with values 1, 4\ncreate a list called w1 with values 4\ncreate a list called w2\ncreate a map called adj\nmap put adj 0 w0 store in adj\nmap put adj 1 w1 store in adj\nmap put adj 2 w2 store in adj\ncreate a map called dist\nmap put dist 0 0 store in dist\nmap put dist 1 999 store in dist\nmap put dist 2 999 store in dist\ncreate a list called q with values 0\ncreate a variable called qi and set it to 0\nwhile qi is less than 1:\n  get item at index qi from list q and store in u\n  map get adj u store in nbrs\n  length of nbrs store in m\n  create a variable called j and set it to 0\n  while j is less than m:\n    get item at index j from list nbrs and store in v\n    map get dist u store in du\n    map get dist v store in dv\n    if du is less than dv:\n      map put dist v du store in dist\n    add j and 1 and store the result in j\n  add qi and 1 and store the result in qi\nmap get dist 1 store in d1\nprint d1`},
    {name:'LRU Cache (sketch)', text:`create a map called cache\ncreate a list called order\n# put\nmap put cache 1 10 store in cache\nappend 1 to list order store in order\n# get\nmap get cache 1 store in v\nprint v`},
    {name:'Trie Insert/Find (sketch)', text:`create a map called root\ncreate a variable called word and set it to "to"\n# insert 't'\ncreate a map called t\nmap put root 't' t store in root\n# insert 'o' under 't'\ncreate a map called o\nmap put t 'o' o store in t\n# find\nmap get root 't' store in n1\nmap get t 'o' store in n2\nprint 1`},
  ]
  const run = async () => {
    const r = await fetch(API+'/epl/exec', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({code}) })
    if(!r.ok){
      const text = await r.text().catch(()=> '')
      setMsg(`HTTP ${r.status}. ${text || 'No response body.'}`)
      return
    }
    const j = await r.json().catch(()=>({ok:false,error:'Invalid JSON from server'}))
    if(!j.ok){ setMsg('Error: '+j.error); return }
    // Render compilation artifacts and output
    const blocks = [
      '--- Text IR ---\n'+(j.text_ir||[]).join('\n'),
      '--- NLBC Disassembly ---\n'+(j.disasm||''),
      '--- Output (PRINT) ---\n'+(j.output||[]).join('\n'),
      '--- Variables ---\n'+JSON.stringify(j.env||{}, null, 2)
    ]
    setMsg(blocks.join('\n\n'))
  }
  const share = async () => {
    const r = await fetch(API+'/share/save', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({kind:'epl', content: code}) })
    const j = await r.json(); if(!j.ok){ alert(j.error); return }
    const url = `${window.location.origin}?epl=${j.id}`
    setShareUrl(url)
    navigator.clipboard?.writeText(url).catch(()=>{})
  }
  React.useEffect(()=>{
    const id = new URLSearchParams(window.location.search).get('epl')
    if(id){
      fetch(API+`/share/get?id=${id}`).then(r=>r.json()).then(j=>{ if(j.ok && j.kind==='epl') setCode(j.content) })
    }
  },[])
  return (
    <div>
      <p>Write EPL lines and Run. (Output prints in server logs.)</p>
      <div style={{display:'flex', gap:12}}>
        <div style={{minWidth:220}}>
          <h4>Examples</h4>
          {snippets.map(s=> (
            <div key={s.name}>
              <button onClick={()=>setCode(s.text)} style={{width:'100%', textAlign:'left', marginBottom:6}}>{s.name}</button>
            </div>
          ))}
        </div>
        <div style={{flex:1}}>
      <textarea value={code} onChange={e=>setCode(e.target.value)} />
      <div style={{margin:'10px 0'}}>
        <motion.button whileTap={{scale:0.97}} onClick={run}>Run</motion.button>
        <motion.button whileTap={{scale:0.97}} onClick={share}>Share</motion.button>
      </div>
      {shareUrl && <div><small>Link copied: {shareUrl}</small></div>}
      <motion.pre initial={{opacity:0}} animate={{opacity:1}}>{msg}</motion.pre>
        </div>
      </div>
    </div>
  )
}

function Tutorials() {
  return (
    <div>
      <h3>Start here</h3>
      <p>1) HLX (IoT): Describe a device, sensors, actuators, and policies in English. Compile → MCU/edge/WoT files. Run Demo to simulate.</p>
      <p>2) EPL (General): Write simple English steps (variables, math, if/else) and run. See prints in server logs.</p>
      <p>3) Try the examples on the left in each tab. Download HLX outputs to share with friends or use on devices.</p>
      <h4>Examples</h4>
      <pre>{`Device "Room-312" at mqtt://hospital/room312\nSensor "co2_ppm" unit ppm period 500 ms\nActuator "vent_damper" actions open, close\n\nIf co2_ppm > 1200 ppm for 18 s with hysteresis 5 % and cooldown 10000 ms then\n  open vent_damper\n  publish event "co2_alert" with timestamp and value\n  store last 600000 ms of co2_ppm to table "air_quality"`}</pre>
    </div>
  )
}


function NLPDebug() {
  const [text, setText] = useState('if x is greater than 0 and (y < 10 or z == 5):')
  const [out, setOut] = useState('')
  const run = async () => {
    const r = await fetch(API+'/debug', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text})})
    const j = await r.json().catch(()=>({ok:false,error:'Invalid JSON'}))
    setOut(j.ok ? JSON.stringify(j, null, 2) : ('Error: '+j.error))
  }
  return (
    <div>
      <p>Inspect spaCy normalization and canonicalization for any line.</p>
      <textarea value={text} onChange={e=>setText(e.target.value)} />
      <div style={{margin:'10px 0'}}>
        <motion.button whileTap={{scale:0.97}} onClick={run}>Analyze</motion.button>
      </div>
      <motion.pre initial={{opacity:0}} animate={{opacity:1}}>{out}</motion.pre>
    </div>
  )
}

