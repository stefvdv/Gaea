/* Genoeg neppe browser om de app-code tot en met het opstarten te draaien.
   Het doel is niet werken maar breken: elke fout die tijdens het laden of
   tijdens boot() gegooid wordt, willen we zien met stacktrace. */
const fs = require("fs");

function El(tag){
  const e = {
    tagName:(tag||"div").toUpperCase(), children:[], style:{}, dataset:{},
    classList:{ _s:new Set(),
      add(...c){c.forEach(x=>this._s.add(x))}, remove(...c){c.forEach(x=>this._s.delete(x))},
      toggle(c,f){ if(f===undefined) this._s.has(c)?this._s.delete(c):this._s.add(c);
                   else f?this._s.add(c):this._s.delete(c); return f; },
      contains(c){return this._s.has(c)} },
    attrs:{}, _html:"", _text:"",
    get innerHTML(){return this._html}, set innerHTML(v){this._html=String(v)},
    get textContent(){return this._text}, set textContent(v){this._text=String(v)},
    get value(){return this._val||""}, set value(v){this._val=String(v)},
    appendChild(c){this.children.push(c); return c},
    insertAdjacentHTML(){}, setAttribute(k,v){this.attrs[k]=v},
    getAttribute(k){return this.attrs[k]}, removeAttribute(k){delete this.attrs[k]},
    addEventListener(){}, removeEventListener(){}, focus(){}, blur(){}, click(){},
    scrollIntoView(){}, getBoundingClientRect(){return {left:0,top:0,width:360,height:640}},
    querySelector(){return El("div")}, querySelectorAll(){return []},
    closest(){return null}, remove(){}, contains(){return false},
    animate(){return {finished:Promise.resolve(), cancel(){}}}
  };
  return e;
}

const store = {};
global.localStorage = {
  getItem:k=>k in store?store[k]:null,
  setItem:(k,v)=>{store[k]=String(v)},
  removeItem:k=>{delete store[k]}, clear:()=>{for(const k in store)delete store[k]}
};

const doc = El("html");
doc.body = El("body");
doc.documentElement = El("html");
doc.head = El("head");
doc.createElement = t=>El(t);
doc.createElementNS = (ns,t)=>El(t);
doc.createTextNode = t=>({textContent:t});
doc.getElementById = id => { doc._byId = doc._byId||{}; return doc._byId[id] || (doc._byId[id]=El("div")); };
doc.querySelector = ()=>El("div");
doc.querySelectorAll = ()=>[];
doc.addEventListener = ()=>{};
doc.removeEventListener = ()=>{};
doc.hidden = false;
doc.visibilityState = "visible";
global.document = doc;

global.window = {
  addEventListener(){}, removeEventListener(){},
  matchMedia:()=>({matches:false, addEventListener(){}, addListener(){}}),
  location:{href:"https://x/", origin:"https://x", pathname:"/", search:"", hash:""},
  history:{pushState(){}, replaceState(){}, back(){}, state:null},
  innerWidth:390, innerHeight:844, devicePixelRatio:3,
  requestAnimationFrame:f=>setTimeout(f,0), cancelAnimationFrame(){},
  setTimeout, clearTimeout, setInterval, clearInterval,
  navigator:{ serviceWorker:{ register:()=>Promise.resolve({scope:"/",
                addEventListener(){}, periodicSync:{register:()=>Promise.resolve(),
                getTags:()=>Promise.resolve([])}, pushManager:{} }),
              ready:Promise.resolve({}), controller:null, addEventListener(){} },
              geolocation:{ watchPosition(){return 1}, clearWatch(){}, getCurrentPosition(){} },
              onLine:true, userAgent:"node", permissions:{query:()=>Promise.resolve({state:"granted"})},
              share:()=>Promise.resolve(), vibrate(){} },
  localStorage: global.localStorage,
  indexedDB:{ open(){ const r={result:{objectStoreNames:{contains:()=>true},
      createObjectStore:()=>({createIndex(){}}),
      transaction:()=>({objectStore:()=>({ put:()=>({}), get:()=>({}), getAll:()=>({}),
        delete:()=>({}), clear:()=>({}), index:()=>({getAll:()=>({})}) }), oncomplete:null })}};
      setTimeout(()=>{ if(r.onupgradeneeded) r.onupgradeneeded({target:r});
                       if(r.onsuccess) r.onsuccess({target:r}); },0); return r; } },
  Notification:{ permission:"granted", requestPermission:()=>Promise.resolve("granted") },
  caches:{ open:()=>Promise.resolve({ keys:()=>Promise.resolve([]), match:()=>Promise.resolve(null),
           put:()=>Promise.resolve(), delete:()=>Promise.resolve() }),
           keys:()=>Promise.resolve([]) },
  fetch:()=>Promise.resolve({ ok:false, status:504, json:()=>Promise.resolve({}),
        text:()=>Promise.resolve(""), clone(){return this} }),
  URL:{ createObjectURL:()=>"blob:x", revokeObjectURL(){} },
  L:null
};
for(const k of ["navigator","indexedDB","Notification","caches","fetch","URL",
                "requestAnimationFrame","cancelAnimationFrame","matchMedia","history","innerWidth"])
  global[k] = window[k];
global.self = global.window;
global.Image = function(){ return {addEventListener(){}, set src(v){}, get src(){return ""}}; };
global.FileReader = function(){ return {readAsDataURL(){}, addEventListener(){}}; };
global.Blob = function(){ return {}; };

/* Leaflet-nep: alles geeft een object terug dat alles slikt. */
function Alles(){
  const p = new Proxy(function(){}, {
    get:(t,k)=>{ if(k==="then") return undefined; return Alles(); },
    apply:()=>Alles(), construct:()=>Alles()
  });
  return p;
}
global.L = Alles();

const s = fs.readFileSync("index.html","utf8");
const m = [...s.matchAll(/<script>([\s\S]*?)<\/script>/g)];
const code = m[m.length-1][1];

process.on("unhandledRejection", e => console.log("\n[REJECT]", e && e.stack || e));
/* Na het laden ook de schermen en de vraaggeneratoren aanroepen: veel fouten
   komen pas boven als er echt iets getekend of berekend wordt. */
const staart = `
try{
  const proeven = [
    ["renderList", ()=>renderList()],
    ["renderKast", ()=>renderKast()],
    ["renderSpec", ()=>renderSpec()],
    ["renderLeer", ()=>renderLeer()],
    ["renderSet",  ()=>renderSet()],
    ["nivNu",      ()=>nivNu().nm],
    ["pool.makkelijk", ()=>NIVEAUS.makkelijk.pool().length],
    ["pool.moeilijk",  ()=>NIVEAUS.moeilijk.pool().length],
    ["afleiders",  ()=>afleiders(SPECIES[0],3).length],
    ["makeQuestion", ()=>{
        let n=0;
        for(const s of SPECIES){ const q=makeQuestion(s.k); if(q) n++; }
        return n+"/"+SPECIES.length;
      }],
    ["gebruiksTekening", ()=>{ SPECIES.forEach(s=>gebruiksTekening(s)); return "ok"; }],
    ["specRow", ()=>{ SPECIES.forEach(s=>specRow(s)); return "ok"; }],
    ["kwaalIcoon", ()=>KWALEN.map(k=>kwaalIcoon(k)).join(",").length],
    ["dubbelSleutel", ()=>{
        let raak=0, mis=[], totaal=0;
        SPECIES.forEach(s=> (s.dubbel||[]).forEach(d=>{
          totaal++; const k=dubbelSleutel(d);
          if(k) raak++; else mis.push(d.split("(")[0].trim());
        }));
        return raak+"/"+totaal+" gekoppeld; niet gevonden: "+[...new Set(mis)].slice(0,14).join(" | ");
      }],
    ["bandHtml", ()=>bandHtml([3,4,5],true).length]
  ];
  for(const [naam,fn] of proeven){
    try{ const r = fn(); console.log("  ok  "+naam+(r!==undefined?"  -> "+r:"")); }
    catch(e){ console.log("  FOUT "+naam+": "+(e && e.message)); console.log("       "+((e&&e.stack||"").split("\\n")[1]||"")); }
  }
}catch(e){ console.log("staartfout: "+(e&&e.stack||e)); }
`;

try{
  new Function(code + staart)();
  console.log("script geladen zonder directe fout");
}catch(e){
  console.log("\n[FOUT BIJ LADEN]");
  console.log(e && e.stack || e);
}
setTimeout(()=>{ console.log("klaar"); process.exit(0); }, 1200);
