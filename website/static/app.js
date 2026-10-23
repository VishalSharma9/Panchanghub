// PanchangHub client: city search (/api/cities), geolocation (/api/cities/nearest), location persistence.
(function(){
  const inp=document.getElementById('citySearch'), box=document.getElementById('citySugg');
  function placeLabel(c){
    const where=[c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ');
    const pop=c.population>0?' \u00b7 '+Number(c.population).toLocaleString()+' pop':'';
    return where+pop+(c.timezone?' \u00b7 '+c.timezone:'');
  }
  function alignSugg(box){
    if(!box) return;
    box.hidden=false;
    box.style.left='0';
    box.style.right='auto';
    const r=box.getBoundingClientRect();
    if(r.right > (window.innerWidth || document.documentElement.clientWidth) - 16){
      box.style.left='auto';
      box.style.right='0';
    }
  }
  function makeSuggDiv(c, onPick){
    const d=document.createElement('div');
    const fullPlace=[c.name, c.admin1_name, c.country_name||c.country].filter(Boolean).join(', ');
    const metaParts=[c.population>0?Number(c.population).toLocaleString()+' pop':'', c.timezone].filter(Boolean).join(' \u00b7 ');
    d.innerHTML=`<span class="sugg-city">${fullPlace}</span><span class="sugg-meta">${metaParts}</span>`;
    d.onclick=onPick;
    return d;
  }
  function setLoc(c, isUserExplicitAction = false){
    const city=c.city || c.label || [c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ');
    const lat=c.lat!=null?c.lat:c.latitude, lon=c.lon!=null?c.lon:c.longitude, tz=c.tz||c.timezone||'UTC';
    if(lat==null||lon==null||!tz) return;
    const v={city:city,lat:lat,lon:lon,tz:tz,src:c.src||'search'};
    document.cookie='ph_loc='+encodeURIComponent(JSON.stringify(v))+';path=/;max-age=31536000;SameSite=Lax';
    try{localStorage.setItem('ph_loc',JSON.stringify(v))}catch(e){}
    
    // Protection against unwanted auto-reloading while the user is reading or scrolling
    if (!isUserExplicitAction) {
      if (window.scrollY > 25) return;
      if (location.search && (location.search.includes('lat=') || location.search.includes('date='))) return;
      const curCity = document.querySelector('#curloc .locname')?.textContent?.trim();
      if (curCity && curCity === city && document.getElementById('curloc')?.dataset.source !== 'default') {
        return;
      }
    }
    const u=new URL(location.href);['city','lat','lon','tz'].forEach(k=>u.searchParams.delete(k));location.href=u.toString();
  }
  window.phSetLoc=setLoc;
  let t;
  if(inp){inp.addEventListener('input',()=>{clearTimeout(t);const q=inp.value.trim();if(q.length<2){box.hidden=true;return}
    t=setTimeout(async()=>{
      try{
        const r=await fetch('/api/cities?limit=12&q='+encodeURIComponent(q));
        if(!r.ok) throw new Error('search');
        const j=await r.json();
        box.innerHTML='';
        (j.results||[]).forEach(c=>box.appendChild(makeSuggDiv(c, ()=>setLoc(c, true))));
        if(!j.results||!j.results.length){const d=document.createElement('div');d.textContent='No place found. Try another spelling.';box.appendChild(d)}
        alignSugg(box);
      }catch(e){box.innerHTML='';const d=document.createElement('div');d.textContent='Search failed. Try again.';box.appendChild(d);alignSugg(box)}
    },200)});}
  function applyFix(p, isUserExplicitAction = false){
    const lat=p.coords.latitude, lon=p.coords.longitude;
    const tz=(Intl.DateTimeFormat().resolvedOptions().timeZone)||'UTC';
    return fetch(`/api/cities/nearest?lat=${lat}&lon=${lon}`).then(r=>r.json()).then(c=>{
      const label=[c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ')||'Your location';
      setLoc({label, latitude:lat, longitude:lon, timezone:tz, src:'gps'}, isUserExplicitAction);
    }).catch(()=>setLoc({label:'Your location', latitude:lat, longitude:lon, timezone:tz, src:'gps'}, isUserExplicitAction));
  }
  function readSaved(){try{return JSON.parse(localStorage.getItem('ph_loc')||'null')}catch(e){return null}}
  async function fromTimezone(isUserExplicitAction = false){
    const tz=(Intl.DateTimeFormat().resolvedOptions().timeZone)||'UTC';
    const label=document.getElementById('locLabel');
    const hint=document.querySelector('#curloc .loctz');
    const btn=document.getElementById('geoBtn');
    if(label) label.textContent='Using your timezone…';
    try{
      const r=await fetch('/api/cities/timezone?tz='+encodeURIComponent(tz));
      if(!r.ok) throw new Error('tz');
      const c=await r.json();
      setLoc(Object.assign({}, c, {src:'timezone'}), isUserExplicitAction);
    }catch(e){
      if(label) label.textContent='Search your city';
      if(hint) hint.textContent='Location permission was blocked. Type a city or town.';
      if(btn) btn.textContent='Use my location';
    }
  }
  function locate(isUserExplicitAction = false){
    const btn=document.getElementById('geoBtn');
    const label=document.getElementById('locLabel');
    if(!navigator.geolocation){ fromTimezone(isUserExplicitAction); return; }
    if(btn) btn.textContent='Asking permission…';
    if(label) label.textContent='Waiting for location permission…';
    let resolved = false;
    const fallbackTimer = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        fromTimezone(isUserExplicitAction);
      }
    }, 3500);
    navigator.geolocation.getCurrentPosition(
      p => {
        if (!resolved) {
          resolved = true;
          clearTimeout(fallbackTimer);
          applyFix(p, isUserExplicitAction);
        }
      },
      () => {
        if (!resolved) {
          resolved = true;
          clearTimeout(fallbackTimer);
          fromTimezone(isUserExplicitAction);
        }
      },
      {enableHighAccuracy:false, timeout:3000, maximumAge:300000}
    );
  }
  const g=document.getElementById('geoBtn');
  if(g) g.onclick=() => locate(true);
  const cur=document.getElementById('curloc');
  if(cur && cur.dataset.source==='default'){
    const attempts = Number(sessionStorage.getItem('ph_loc_attempts') || '0');
    if (attempts >= 2) {
      const label=document.getElementById('locLabel');
      const hint=document.querySelector('#curloc .loctz');
      if(label) label.textContent='Select your city';
      if(hint) hint.textContent='Type your city in the search box to set your location.';
    } else {
      sessionStorage.setItem('ph_loc_attempts', String(attempts + 1));
      const s=readSaved();
      if(s && s.lat!=null && s.lon!=null && s.tz) setLoc(s, false);
      else locate(false);
    }
  } else if (cur) {
    sessionStorage.removeItem('ph_loc_attempts');
  }
  document.querySelectorAll('[data-compare]').forEach(el=>{
    const list=document.createElement('div');list.className='sugg';list.hidden=true;el.parentNode.style.position='relative';el.parentNode.appendChild(list);
    let tt;el.addEventListener('input',()=>{clearTimeout(tt);const q=el.value.trim();if(q.length<2){list.hidden=true;return}
      tt=setTimeout(async()=>{
        try{
          const j=await (await fetch('/api/cities?limit=10&q='+encodeURIComponent(q))).json();
          list.innerHTML='';
          (j.results||[]).forEach(c=>{list.appendChild(makeSuggDiv(c, ()=>{const f=el.form;
            el.value=[c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ');
            f.city2.value=el.value;f.lat2.value=c.latitude;f.lon2.value=c.longitude;f.tz2.value=c.timezone;list.hidden=true;f.submit()}))});
          if(!j.results||!j.results.length){const d=document.createElement('div');d.textContent='No place found. Try another spelling.';list.appendChild(d)}
          alignSugg(list);
        }catch(e){list.hidden=true}
      },200)})});
  // birth-place & current-place pickers in forms
  document.querySelectorAll('[data-place]').forEach(el=>{
    const pre=el.dataset.place||'', list=document.createElement('div');
    list.className='sugg';list.hidden=true;
    el.parentNode.style.position='relative';
    el.parentNode.appendChild(list);
    const scope=el.form||document;
    let lastPickedVal=el.value.trim();
    let lastResults=[];
    function applyCity(c){
      const formatted=[c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ');
      el.value=formatted;
      lastPickedVal=formatted;
      const latF=scope.querySelector(`[name="${pre}lat"]`);if(latF) latF.value=c.latitude;
      const lonF=scope.querySelector(`[name="${pre}lon"]`);if(lonF) lonF.value=c.longitude;
      const tzF=scope.querySelector(`[name="${pre}tz"]`);if(tzF) tzF.value=c.timezone;
      list.hidden=true;
    }
    let tt;
    el.addEventListener('input',()=>{
      clearTimeout(tt);
      const q=el.value.trim();
      if(q.length<2){list.hidden=true;return;}
      tt=setTimeout(async()=>{
        try{
          const j=await (await fetch('/api/cities?limit=10&q='+encodeURIComponent(q))).json();
          lastResults=j.results||[];
          list.innerHTML='';
          lastResults.forEach(c=>{
            const item=makeSuggDiv(c, ()=>applyCity(c));
            item.addEventListener('mousedown', e=>{e.preventDefault();applyCity(c);});
            list.appendChild(item);
          });
          if(!lastResults.length){
            const d=document.createElement('div');
            d.textContent='No place found. Try another spelling.';
            list.appendChild(d);
          }
          alignSugg(list);
        }catch(e){list.hidden=true;}
      },180);
    });
    el.addEventListener('change', async()=>{
      const q=el.value.trim();
      if(q.length>=2 && q!==lastPickedVal){
        if(lastResults.length>0){
          applyCity(lastResults[0]);
        }else{
          try{
            const j=await (await fetch('/api/cities?limit=1&q='+encodeURIComponent(q))).json();
            if(j.results && j.results.length>0) applyCity(j.results[0]);
          }catch(e){}
        }
      }
    });
  });

  // Close suggestions when clicking outside
  document.addEventListener('click', e => {
    if (!e.target.closest('.locbox') && !e.target.closest('[data-place]') && !e.target.closest('[data-compare]')) {
      document.querySelectorAll('.sugg').forEach(s => s.hidden = true);
    }
  });
})();

// language switcher: cookie ph_lang (server localizes names/labels)
(function(){const s=document.getElementById('langSel');if(!s)return;s.onchange=()=>{document.cookie='ph_lang='+s.value+';path=/;max-age=31536000;SameSite=Lax';
  const u=new URL(location.href);u.searchParams.delete('lang');location.href=u.toString();};})();

(function(){
  const el=document.getElementById('liveClock'); if(!el) return;
  const dateEl=document.getElementById('civilDate');
  function zone(){
    if(el.dataset.pending==='1'){
      try{return Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC'}catch(e){return 'UTC'}
    }
    return el.dataset.tz||'UTC';
  }
  function tick(){
    const now=new Date();
    try{
      const tz=zone();
      el.textContent=new Intl.DateTimeFormat('en-US',{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true,timeZone:tz}).format(now);
      if(dateEl) dateEl.textContent=new Intl.DateTimeFormat('en-GB',{weekday:'short',day:'numeric',month:'short',year:'numeric',timeZone:tz}).format(now);
    }catch(e){ el.textContent=''; }
  }
  tick(); setInterval(tick,1000);
})();

(function(){
  const el=document.getElementById('vedicClock');
  if(!el || !el.dataset.sr || !el.dataset.nsr) return;
  const sr=Date.parse(el.dataset.sr), nsr=Date.parse(el.dataset.nsr);
  if(!sr || !nsr || nsr<=sr) return;
  function tick(){
    let e=Date.now()-sr; if(e<0) e=0; if(e>nsr-sr) e=nsr-sr;
    const gh=(e/(nsr-sr))*60, g=Math.floor(gh), pala=(gh-g)*60, p=Math.floor(pala), v=Math.floor((pala-p)*60);
    el.textContent='Vedic time since sunrise · '+g+' ghati '+p+' pala '+v+' vipala';
  }
  tick(); setInterval(tick,1000);
})();

// Client-side dynamic DOM translator for interactive JS components (e.g., Vastu Architect Studio)
(function(){
  const lang = document.documentElement.lang || 'en';
  if (!lang || lang === 'en') return;
  const cache = new Map();
  let pendingTimer = null;

  function shouldSkip(node) {
    if (!node || !node.parentElement) return true;
    const p = node.parentElement;
    if (p.closest('.notranslate, [translate="no"], script, style, svg, #langSel')) return true;
    const s = (node.nodeValue || '').trim();
    if (!s || !/[A-Za-z]{2,}/.test(s)) return true;
    if (/ॐ|॥|नमः|विद्महे|धीमहि|यजामहे/.test(s)) return true;
    return false;
  }

  async function translateDOMSubtree(root) {
    const walker = document.createTreeWalker(root || document.body, NodeFilter.SHOW_TEXT, null);
    const nodes = [];
    const toFetch = [];
    const seen = new Set();
    let n;
    while ((n = walker.nextNode())) {
      if (shouldSkip(n)) continue;
      const raw = n.nodeValue.trim();
      nodes.push({ node: n, raw });
      if (!cache.has(raw) && !seen.has(raw)) {
        seen.add(raw);
        toFetch.push(raw);
      }
    }
    if (toFetch.length > 0) {
      for (let i = 0; i < toFetch.length; i += 80) {
        const slice = toFetch.slice(i, i + 80);
        try {
          const r = await fetch('/api/i18n/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lang, texts: slice })
          });
          if (r.ok) {
            const j = await r.json();
            (j.translations || []).forEach((tr, idx) => {
              if (tr) cache.set(slice[idx], tr);
            });
          }
        } catch (e) {}
      }
    }
    nodes.forEach(({ node, raw }) => {
      const tr = cache.get(raw);
      if (tr && tr !== raw && node.nodeValue) {
        node.nodeValue = node.nodeValue.replace(raw, tr);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(() => translateDOMSubtree(document.body), 150));
  } else {
    setTimeout(() => translateDOMSubtree(document.body), 150);
  }

  const obs = new MutationObserver(() => {
    if (pendingTimer) clearTimeout(pendingTimer);
    pendingTimer = setTimeout(() => translateDOMSubtree(document.body), 250);
  });
  obs.observe(document.body, { childList: true, subtree: true });
})();


// Normalize 5+ digit year typos (e.g., 19992-05-04 -> 1992-05-04) on all date inputs & forms
(function(){
  function fixDateVal(val) {
    if (!val || typeof val !== 'string') return val;
    const m = val.trim().match(/^(\d{5,})-(\d{1,2})-(\d{1,2})$/);
    if (!m) return val;
    let yr = m[1];
    while (yr.length > 4) {
      let collapsed = false;
      for (let i = 0; i < yr.length - 1; i++) {
        if (yr[i] === yr[i + 1]) {
          yr = yr.slice(0, i) + yr.slice(i + 1);
          collapsed = true;
          break;
        }
      }
      if (!collapsed) yr = yr.slice(0, 4);
    }
    return yr + '-' + m[2].padStart(2, '0') + '-' + m[3].padStart(2, '0');
  }
  function bindDateInputs() {
    document.querySelectorAll('input[type="date"]').forEach(inp => {
      if (!inp.getAttribute('min')) inp.setAttribute('min', '1800-01-01');
      if (!inp.getAttribute('max')) inp.setAttribute('max', '2100-12-31');
      if (inp.value) {
        const fixed = fixDateVal(inp.value);
        if (fixed !== inp.value) inp.value = fixed;
      }
      inp.addEventListener('change', () => {
        const fixed = fixDateVal(inp.value);
        if (fixed !== inp.value) inp.value = fixed;
      });
    });
    document.querySelectorAll('form').forEach(f => {
      f.addEventListener('submit', () => {
        f.querySelectorAll('input[type="date"]').forEach(inp => {
          const fixed = fixDateVal(inp.value);
          if (fixed !== inp.value) inp.value = fixed;
        });
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindDateInputs);
  } else {
    bindDateInputs();
  }
})();
