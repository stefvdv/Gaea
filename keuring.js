
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
    ["bandHtml", ()=>bandHtml([3,4,5],true).length],
    ["vraagkeuring", ()=>{
        /* Strenge keuring van elke vraag die de app kan stellen.
           Zeven manieren waarop een vraag stuk kan zijn. */
        const fout = {dubbel:[], leeg:[], verklikt:[], geenAntwoord:[],
                      teWeinig:[], geenTip:[], tipVerklikt:[]};
        const kaal = t => String(t).replace(/<[^>]*>/g,"").split(/[ \t\n]+/).join(" ").trim().toLowerCase();
        /* Hele woorden vergelijken. "hysop" zit letterlijk niet in
           "hyssopus", maar een losse indexOf op korte namen geeft anders
           makkelijk vals alarm. */
        const grens = c => !c || " .,;:?!()<>/-\u2014".indexOf(c) >= 0;
        const bevat = (hooi, naald) => {
          if(!naald) return false;
          let p = hooi.indexOf(naald);
          while(p >= 0){
            if(grens(hooi[p-1]) && grens(hooi[p+naald.length])) return true;
            p = hooi.indexOf(naald, p+1);
          }
          return false;
        };
        for(const niv of ["makkelijk","gemiddeld","moeilijk"]){
          S.leer.niveau = niv;
          for(let ronde=0; ronde<2; ronde++)
          for(const s of SPECIES){
            const q = makeQuestion(s.k); if(!q || !q.opts) continue;
            const id = niv+"/"+s.k+"/"+q.kind;
            const opts = q.opts.map(kaal);
            if(new Set(opts).size !== opts.length) fout.dubbel.push(id);
            if(opts.some(o=>!o)) fout.leeg.push(id);
            if(opts.length < 3) fout.teWeinig.push(id);
            const a = kaal(q.aTxt);
            if(!opts.includes(a)) fout.geenAntwoord.push(id);
            /* staat het antwoord al in de vraag? dan is het geen vraag */
            if(a && a.length > 3 && bevat(kaal(q.q), a)){
              fout.verklikt.push(id);
              if(fout.verklikt.length<4) console.log("      verklikt: "+id+" | v="+kaal(q.q)+" | a="+a);
            }
            const tip = kaal(tipVoor(q));
            if(!tip || tip.length < 12) fout.geenTip.push(id);
            else if(a && a.length > 4 && bevat(tip, a)) fout.tipVerklikt.push(id);
          }
        }
        S.leer.niveau = "gemiddeld";
        const uit = Object.entries(fout).filter(([,v])=>v.length)
          .map(([k,v])=>k+" "+v.length+" ("+[...new Set(v)].slice(0,3).join(", ")+")");
        return uit.length ? "STUK: "+uit.join(" | ") : "alle vragen door de keuring";
      }],
    ["dubbele antwoorden", ()=>{
        let stuk=0, gecheckt=0;
        for(const niv of ["makkelijk","gemiddeld","moeilijk"]){
          S.leer.niveau = niv;
          for(let ronde=0; ronde<3; ronde++)
            for(const s of SPECIES){
              const q = makeQuestion(s.k); if(!q || !q.opts) continue;
              gecheckt++;
              if(new Set(q.opts).size !== q.opts.length){ stuk++;
                if(stuk<6) console.log("      dubbel: ["+q.kind+"] "+s.k+" -> "+JSON.stringify(q.opts)); }
            }
        }
        S.leer.niveau = "gemiddeld";
        return stuk ? stuk+" van "+gecheckt+" MET DUBBELE ANTWOORDEN" : gecheckt+" vragen, geen dubbele antwoorden";
      }],
    ["chips tellen", ()=>{
        S.pins = [
          {id:"a",spec:"duizendblad",lat:52,lng:5,gemaakt:"2026-08-01"},
          {id:"b",spec:"vlier",lat:52,lng:5,gemaakt:"2026-08-01"},
          {id:"c",spec:"groeneknolamaniet",lat:52,lng:5,gemaakt:"2026-08-01"}
        ];
        const c={eet:0,med:0,gif:0,zwam:0,onb:0};
        S.pins.forEach(p=> pinVakken(p).forEach(v=> c[v]++));
        S.pins = [];
        return "eet "+c.eet+" · med "+c.med+" · gif "+c.gif+" · zwam "+c.zwam;
      }],
    ["zwamaandeel", ()=>{
        const uit = [];
        for(const niv of ["makkelijk","gemiddeld","moeilijk"]){
          S.leer.niveau = niv;
          let zwam=0, tot=0;
          for(let i=0;i<40;i++){
            const keys = balanceer(pickN(nivNu().pool().map(x=>x.k), 10));
            keys.forEach(k=>{ tot++; if(SPEC_BY_K[k].grp==="zwam") zwam++; });
          }
          uit.push(niv+" "+Math.round(100*zwam/tot)+"%");
        }
        S.leer.niveau = "gemiddeld";
        return uit.join(" · ");
      }]
  ];
  for(const [naam,fn] of proeven){
    try{ const r = fn(); console.log("  ok  "+naam+(r!==undefined?"  -> "+r:"")); }
    catch(e){ console.log("  FOUT "+naam+": "+(e && e.message)); console.log("       "+((e&&e.stack||"").split("\\n")[1]||"")); }
  }
}catch(e){ console.log("staartfout: "+(e&&e.stack||e)); }
