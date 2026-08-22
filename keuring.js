
try{
  const proeven = [
    ["renderList", ()=>renderList()],
    ["renderKast", ()=>renderKast()],
    ["renderSpec", ()=>renderSpec()],
    ["renderLeer", ()=>renderLeer()],
    ["renderSet",  ()=>renderSet()],
    ["herbarium", ()=>{
        const zonder = SPECIES.filter(s=>!famVan(s));
        const fam = {}; SPECIES.forEach(s=>{const f=famVan(s); if(f) fam[f]=(fam[f]||0)+1;});
        const top = Object.entries(fam).sort((a,b)=>b[1]-a[1]).slice(0,4).map(([f,n])=>f+" "+n).join(", ");
        return SPECIES.length+" soorten · "+Object.keys(fam).length+" families · zonder familie: "+
          (zonder.length?zonder.map(s=>s.k).join(","):"geen")+" · grootste: "+top;
      }],
    ["nivNu",      ()=>nivNu().nm],
    /* Het herbarium is de naslag bij de vragen: elke soort waarover iets
       gevraagd wordt, moet er te vinden zijn. */
    /* De naslag na een vraag moet voor elke soort iets te lezen geven. */
    /* Elk thema moet een eigen vijver hebben en alleen zijn eigen
       vraagsoorten opleveren \u2014 anders lekt de oefening vol met naamvragen. */
    ["thema's zuiver", ()=>{
      let fout = [];
      Object.keys(THEMAS).forEach(niv=>{
        S.leer.niveau = niv;
        THEMAS[niv].forEach(t=>{
          S.leer.thema[niv] = t.k;
          if(!t.vragen) return;
          const toegestaan = new Set(t.vragen);
          const keys = themaPool().map(x=>x.k);
          for(let i=0;i<120;i++){
            const k = keys[Math.floor(Math.random()*keys.length)];
            const q = makeQuestion(k);
            if(!q) continue;
            const gen = [...GEN_NAAM.entries()].find(([g,nm])=> nm && q.kind && true);
            if(q.kind === "Naam" && !toegestaan.has("latijn") && !toegestaan.has("nl") && !toegestaan.has("etym"))
              { fout.push(niv+"/"+t.k); break; }
          }
        });
      });
      S.leer.niveau = "herkennen";
      return fout.length ? "LEKT: "+fout.join(", ") : Object.values(THEMAS).flat().length+" thema's, geen lek";
    }],
    /* Werknamen zoals "Grote sponszwam-verwant: X" mogen nooit in een release
       belanden; die zijn er twee lichtingen achter elkaar doorheen geglipt. */
    /* Een medicinale soort zonder kwalen valt buiten het thema Kwaal en kruid
       en buiten het kwaalfilter: hij is er wel, maar onvindbaar langs de weg
       waarlangs je hem zoekt. Dat gat zat er bij elke lichting opnieuw in. */
    /* Een sleutel in ETYM, VOLKS, STOF of KWALEN_MAP die naar geen enkele soort
       verwijst levert stilzwijgend niets op: de regel staat er, de vraag komt
       nooit. Twee van zulke weesregels zaten in de stoffenlichting. */
    /* Een soortenkaart met maar twee of drie secties is te mager om iets aan
       te hebben in het veld. Deze telling houdt bij hoe gevuld ze zijn. */
    /* Een giftige soort zonder dubbelgangerlijst is de gevaarlijkste lege plek
       in de app: juist daar gaat het in het veld mis. */
    /* Een vraag met drie willekeurige soorten ernaast traint niets: je herkent
       de goede aan uitsluiting. De afleiders horen soorten te zijn waarmee je
       de goede in het veld kunt verwarren. */
    /* Elke soort in de gids hoort ook een vraag te kunnen opleveren, in
       minstens \u00e9\u00e9n thema. Een soort die alleen in het herbarium staat en
       nooit gevraagd wordt, leer je nooit. */
    ["elke soort komt in vragen", ()=>{
      const bewaardNiv = S.leer.niveau, bewaardTh = JSON.parse(JSON.stringify(S.leer.thema));
      const bereikbaar = new Set();
      Object.keys(THEMAS).forEach(niv=>{
        S.leer.niveau = niv;
        THEMAS[niv].forEach(t=>{
          S.leer.thema[niv] = t.k;
          themaPool().forEach(sp=>{
            if(bereikbaar.has(sp.k)) return;
            for(let i = 0; i < 20; i++) if(makeQuestion(sp.k)){ bereikbaar.add(sp.k); break; }
          });
        });
      });
      S.leer.niveau = bewaardNiv; S.leer.thema = bewaardTh;
      const mis = SPECIES.filter(s=> !bereikbaar.has(s.k));
      return mis.length ? mis.length+" ZONDER VRAAG: "+mis.map(s=>s.nl).slice(0,8).join(", ")
        : bereikbaar.size+"/"+SPECIES.length+" soorten leveren een vraag op";
    }],
    /* Een dubbelganger die zelf geen soort is, kan geen afleider zijn en komt
       nooit in een vraag terecht. Groepsnamen ("Vezelkoppen", "Distels")
       tellen niet mee: die verwijzen bewust naar een hele groep. */
    ["verwarbare soorten bestaan", ()=>{
      const groep = /^(andere|jonge|kleine|grote|geen|kegelvormige|scherpe|zwarte|witte|blauwverkleurende|bruine|oranje|schermbloemigen)\b|s$|\u2019s$/i;
      const los = new Set();
      SPECIES.forEach(sp=> (sp.dubbel||[]).forEach(t=>{
        if(dubbelSleutel(t)) return;
        const kop = String(t).split("(")[0].trim();
        if(!groep.test(kop)) los.add(kop);
      }));
      const totaal = SPECIES.reduce((a,s)=> a + (s.dubbel||[]).length, 0);
      return los.size
        ? los.size+" verwarbare soorten ontbreken nog: "+[...los].slice(0,8).join(", ")
        : "alle genoemde dubbelgangers bestaan als soort ("+totaal+" vermeldingen)";
    }],
    ["afleiders verwarbaar", ()=>{
      const metLijst = SPECIES.filter(s=> verwarLijst(s).length);
      let raak = 0;
      metLijst.forEach(s=>{
        const vl = verwarLijst(s);
        if(afleiders(s, 3).some(x=> vl.includes(x))) raak++;
      });
      const pct = Math.round(100 * raak / metLijst.length);
      return pct < 90 ? "SLECHTS "+pct+"% van de vragen krijgt een dubbelganger als afleider"
        : raak+"/"+metLijst.length+" soorten met dubbelganger krijgen er ook \u00e9\u00e9n als afleider ("+pct+"%)";
    }],
    /* Zes rondes achter elkaar horen niet steeds dezelfde soorten op te
       leveren; zonder geheugen deden ze dat wel. */
    ["rondes vari\u00ebren", ()=>{
      const bewaard = S.leer.recent, bewaardN = S.leer.doel;
      S.leer.recent = []; S.leer.doel = 10;
      const rondes = [];
      for(let r = 0; r < 6; r++){
        const vijver = new Set(themaPool().map(x=>x.k));
        let due = dueKeys().filter(k=> vijver.has(k));
        if(due.length < 4) due = [...vijver];
        const n = Math.min(S.leer.doel, Math.max(due.length, 4));
        const vers = due.filter(k=> !S.leer.recent.includes(k));
        if(vers.length >= n) due = vers;
        let keys = pickN(due.sort((a,b)=> leerGewicht(b) - leerGewicht(a)).slice(0, Math.max(n*3,24)), n);
        keys = balanceer(keys);
        S.leer.recent = [...keys, ...S.leer.recent].slice(0, Math.max(S.leer.doel*4, 40));
        rondes.push(keys);
      }
      let herhaald = 0;
      for(let i = 1; i < rondes.length; i++)
        herhaald += rondes[i].filter(k=> rondes[i-1].includes(k)).length;
      const alle = [].concat(...rondes);
      S.leer.recent = bewaard; S.leer.doel = bewaardN;
      return herhaald ? herhaald+" HERHALINGEN tussen opeenvolgende rondes"
        : new Set(alle).size+" unieke soorten in 6 rondes van 10, geen herhaling tussen opeenvolgende rondes";
    }],
    ["gif met dubbelgangers", ()=>{
      const gif = SPECIES.filter(s=> s.tags.includes("giftig"));
      const leeg = gif.filter(s=> !s.dubbel || !s.dubbel.length);
      return leeg.length ? leeg.length+" ZONDER: "+leeg.map(s=>s.nl).slice(0,8).join(", ")
        : gif.length+" giftige soorten, alle met dubbelgangers";
    }],
    ["soortenkaarten gevuld", ()=>{
      const metRecept = new Set();
      alleRecepten().forEach(r=> (r.soorten||[]).forEach(k=> metRecept.add(k)));
      const secties = sp => {
        let n = 0;
        ["dubbel","let","herken","med"].forEach(f=>{ if(sp[f] && sp[f].length) n++; });
        if(famVan(sp)) n++;
        if(STOF[sp.k]) n++;
        if(sp.kwalen && sp.kwalen.length) n++;
        if(metRecept.has(sp.k)) n++;
        if(ETYM[sp.k]) n++;
        if(VOLKS[sp.k]) n++;
        return n;
      };
      const dun = SPECIES.filter(sp=> secties(sp) < 4);
      const gem = (SPECIES.reduce((a,sp)=> a + secties(sp), 0) / SPECIES.length).toFixed(1);
      return dun.length ? dun.length+" MAGERE KAARTEN: "+dun.map(s=>s.nl).slice(0,8).join(", ")
        : "gemiddeld "+gem+" secties, geen kaart onder de vier";
    }],
    ["geen weessleutels", ()=>{
      const wees = [];
      [["ETYM",ETYM],["VOLKS",VOLKS],["STOF",STOF],["KWALEN_MAP",KWALEN_MAP]].forEach(([nm,m])=>
        Object.keys(m).filter(k=> !SPEC_BY_K[k]).forEach(k=> wees.push(nm+":"+k)));
      return wees.length ? "WEES: "+wees.join(", ")
        : "ETYM "+Object.keys(ETYM).length+" · VOLKS "+Object.keys(VOLKS).length+
          " · STOF "+Object.keys(STOF).length+" · KWALEN "+Object.keys(KWALEN_MAP).length+", alle gekoppeld";
    }],
    ["medicinaal met kwalen", ()=>{
      const fout = SPECIES.filter(s=> s.tags.includes("medicinaal") && !(s.kwalen && s.kwalen.length));
      return fout.length ? fout.length+" ZONDER KWALEN: "+fout.map(s=>s.nl).slice(0,8).join(", ")
        : SPECIES.filter(s=>s.tags.includes("medicinaal")).length+" medicinale soorten, alle met kwalen";
    }],
    /* Eetbare soorten zonder plukdeel zijn in de app niet te gebruiken. */
    ["eetbaar met plukdeel", ()=>{
      const fout = SPECIES.filter(s=> s.tags.includes("eetbaar") && (!s.delen || s.delen === "\u2014"));
      return fout.length ? fout.length+" ZONDER DEEL: "+fout.map(s=>s.nl).slice(0,8).join(", ")
        : SPECIES.filter(s=>s.tags.includes("eetbaar")).length+" eetbare soorten, alle met plukdeel";
    }],
    ["soortnamen netjes", ()=>{
      const fout = SPECIES.filter(s=> /verwant|vervanger|:\s/i.test(s.nl)).map(s=>s.nl);
      return fout.length ? "WERKNAAM: "+fout.join(" | ") : SPECIES.length+" namen in orde";
    }],
    /* De quiz toont sinds 0.47 hetzelfde soortenblad als het herbarium. Deze
       controle draait daarom op specBlok: het blad moet voor elke soort
       inhoud van betekenis opleveren. */
    /* De algemene waarschuwingen horen onderaan: bovenaan duwden ze bij elke
       paddenstoel de kenmerken van de soort zelf uit beeld. */
    ["waarschuwingen onderaan", ()=>{
      const sp = SPECIES.find(s=> s.grp === "zwam" && s.tags.includes("giftig") && s.dubbel.length);
      if(!sp) return "geen giftige zwam om te toetsen";
      let h = "";
      const bewaard = showSheet;
      showSheet = x => { h = x; };
      try{ specSheet(sp.k); } finally { showSheet = bewaard; }
      const i = t => h.indexOf(t);
      const goed = i("Verwarbaar met") > 0
        && i("Verwarbaar met") < i("<b>Paddenstoelen</b>")
        && i("<b>Paddenstoelen</b>") < i("Bij vermoeden van vergiftiging")
        && i("Bij vermoeden van vergiftiging") < i("knopvak");
      return goed ? "kenmerken eerst, algemene waarschuwingen onderaan"
        : "VOLGORDE FOUT op het blad van "+sp.nl;
    }],
    ["soortenblad in de quiz", ()=>{
      let mager = 0;
      SPECIES.forEach(sp=>{
        const h = (sp.herken||"") + (sp.let||"") + (sp.dubbel||[]).join("");
        if(h.length < 60) mager++;
      });
      return mager ? mager+" soorten met een te mager blad"
        : SPECIES.length+" soorten, blad overal met inhoud";
    }],
    ["herbarium compleet", ()=>{
      const in_h = new Set(SPECIES.map(x=>x.k));
      let mis = 0;
      Object.keys(NIVEAUS).forEach(n=> NIVEAUS[n].pool().forEach(sp=>{ if(!in_h.has(sp.k)) mis++; }));
      return mis === 0 ? SPECIES.length+" soorten, alle vragen gedekt" : mis+" SOORTEN ONTBREKEN";
    }],
    /* Bij gif hoort de gifplaat, nooit de plukkaart. */
    ["gifplaat", ()=>{
      const gif = SPECIES.filter(x=>x.tags.includes("giftig"));
      const fout = gif.filter(sp=> !gifTekening(sp).includes("Ga uit van")).length;
      return fout === 0 ? gif.length+" giftige soorten, geen plukkaart" : fout+" FOUT";
    }],
    ["pool.herkennen", ()=>NIVEAUS.herkennen.pool().length],
    ["pool.gebruik",   ()=>NIVEAUS.gebruik.pool().length],
    ["pool.namen",     ()=>NIVEAUS.namen.pool().length],
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
        for(const niv of ["herkennen","gebruik","namen"]){
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
        S.leer.niveau = "herkennen";
        const uit = Object.entries(fout).filter(([,v])=>v.length)
          .map(([k,v])=>k+" "+v.length+" ("+[...new Set(v)].slice(0,3).join(", ")+")");
        return uit.length ? "STUK: "+uit.join(" | ") : "alle vragen door de keuring";
      }],
    ["dubbele antwoorden", ()=>{
        let stuk=0, gecheckt=0;
        for(const niv of ["herkennen","gebruik","namen"]){
          S.leer.niveau = niv;
          for(let ronde=0; ronde<3; ronde++)
            for(const s of SPECIES){
              const q = makeQuestion(s.k); if(!q || !q.opts) continue;
              gecheckt++;
              if(new Set(q.opts).size !== q.opts.length){ stuk++;
                if(stuk<6) console.log("      dubbel: ["+q.kind+"] "+s.k+" -> "+JSON.stringify(q.opts)); }
            }
        }
        S.leer.niveau = "herkennen";
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
        for(const niv of ["herkennen","gebruik","namen"]){
          S.leer.niveau = niv;
          let zwam=0, tot=0;
          for(let i=0;i<40;i++){
            const keys = balanceer(pickN(nivNu().pool().map(x=>x.k), 10));
            keys.forEach(k=>{ tot++; if(SPEC_BY_K[k].grp==="zwam") zwam++; });
          }
          uit.push(niv+" "+Math.round(100*zwam/tot)+"%");
        }
        S.leer.niveau = "herkennen";
        return uit.join(" · ");
      }]
  ];
  for(const [naam,fn] of proeven){
    try{ const r = fn(); console.log("  ok  "+naam+(r!==undefined?"  -> "+r:"")); }
    catch(e){ console.log("  FOUT "+naam+": "+(e && e.message)); console.log("       "+((e&&e.stack||"").split("\\n")[1]||"")); }
  }
}catch(e){ console.log("staartfout: "+(e&&e.stack||e)); }
