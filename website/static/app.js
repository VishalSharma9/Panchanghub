// PanchangHub client: city search (/api/cities), geolocation (/api/cities/nearest), location persistence.
const PHUI=(function(){try{return JSON.parse((document.getElementById('phUi')||{}).textContent||'{}')}catch(e){return {}}})();
(function(){
  const inp=document.getElementById('citySearch'), box=document.getElementById('citySugg');
  function placeLabel(c){
    const where=[c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ');
    const pop=c.population>0?' · '+Number(c.population).toLocaleString():'';
    return where+pop+(c.timezone?' · '+c.timezone:'');
  }
  function setLoc(c){
    const city=c.city || c.label || [c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ');
    const lat=c.lat!=null?c.lat:c.latitude, lon=c.lon!=null?c.lon:c.longitude, tz=c.tz||c.timezone||'UTC';
    if(lat==null||lon==null||!tz) return;
    const v={city:city,lat:lat,lon:lon,tz:tz,src:c.src||'search'};
    document.cookie='ph_loc='+encodeURIComponent(JSON.stringify(v))+';path=/;max-age=31536000;SameSite=Lax';
    try{localStorage.setItem('ph_loc',JSON.stringify(v))}catch(e){}
    const u=new URL(location.href);
    u.searchParams.set('city', city);
    u.searchParams.set('lat', String(lat));
    u.searchParams.set('lon', String(lon));
    u.searchParams.set('tz', tz);
    document.querySelectorAll('input[name="date"],input[name="time"],input[name="b_date"],input[name="b_time"],input[name="g_date"],input[name="g_time"]').forEach(function(el){
      if(el.value) u.searchParams.set(el.name, el.value);
    });
    let keepLang='';
    try{ keepLang=u.searchParams.get('lang') || localStorage.getItem('ph_lang') || ''; }catch(e){}
    if(keepLang && keepLang!=='en') u.searchParams.set('lang', keepLang);
    else u.searchParams.delete('lang');
    const next=u.toString();
    if(next===location.href) return;
    try{
      const stamp=lat+','+lon+','+tz;
      if(sessionStorage.getItem('ph_nav')===stamp) return;
      sessionStorage.setItem('ph_nav', stamp);
    }catch(e){}
    location.href=next;
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
        (j.results||[]).forEach(c=>{const d=document.createElement('div');d.textContent=placeLabel(c);d.onclick=()=>setLoc(c);box.appendChild(d)});
        if(!j.results||!j.results.length){const d=document.createElement('div');d.textContent=PHUI['No place found. Try another spelling.']||'No place found. Try another spelling.';box.appendChild(d)}
        box.hidden=false;
      }catch(e){box.innerHTML='';const d=document.createElement('div');d.textContent=PHUI['Search failed. Try again.']||'Search failed. Try again.';box.appendChild(d);box.hidden=false}
    },200)});}
  function applyFix(p){
    const lat=p.coords.latitude, lon=p.coords.longitude;
    const tz=(Intl.DateTimeFormat().resolvedOptions().timeZone)||'UTC';
    return fetch(`/api/cities/nearest?lat=${lat}&lon=${lon}`).then(r=>r.json()).then(c=>{
      const label=[c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ')||'Your location';
      setLoc({label, latitude:lat, longitude:lon, timezone:tz, src:'gps'});
    }).catch(()=>setLoc({label:'Your location', latitude:lat, longitude:lon, timezone:tz, src:'gps'}));
  }
  function readSaved(){try{return JSON.parse(localStorage.getItem('ph_loc')||'null')}catch(e){return null}}
  async function fromTimezone(){
    const tz=(Intl.DateTimeFormat().resolvedOptions().timeZone)||'UTC';
    const label=document.getElementById('locLabel');
    const hint=document.querySelector('#curloc .loctz');
    const btn=document.getElementById('geoBtn');
    if(label) label.textContent=PHUI['Using your timezone…']||'Using your timezone…';
    try{
      const r=await fetch('/api/cities/timezone?tz='+encodeURIComponent(tz));
      if(!r.ok) throw new Error('tz');
      const c=await r.json();
      setLoc(Object.assign({}, c, {src:'timezone'}));
    }catch(e){
      if(label) label.textContent=PHUI['Search your city']||'Search your city';
      if(hint) hint.textContent=PHUI['Location permission was blocked. Type a city or town.']||'Location permission was blocked. Type a city or town.';
      if(btn) btn.textContent=PHUI['Use my location']||'Use my location';
      if(inp) inp.focus();
    }
  }
  function locate(){
    const btn=document.getElementById('geoBtn');
    const label=document.getElementById('locLabel');
    if(!navigator.geolocation){ fromTimezone(); return; }
    if(btn) btn.textContent=PHUI['Asking permission…']||'Asking permission…';
    if(label) label.textContent=PHUI['Waiting for location permission…']||'Waiting for location permission…';
    navigator.geolocation.getCurrentPosition(applyFix,()=>fromTimezone(),{enableHighAccuracy:false,timeout:8000,maximumAge:300000});
  }
  const g=document.getElementById('geoBtn');
  if(g) g.onclick=locate;
  const cur=document.getElementById('curloc');
  if(cur && cur.dataset.source==='default'){
    const s=readSaved();
    const framed=(()=>{try{return window.top!==window}catch(e){return true}})();
    if(s && s.lat!=null && s.lon!=null && s.tz) setLoc(s);
    else if(framed || !navigator.geolocation) fromTimezone();
    else locate();
  }
  document.querySelectorAll('[data-compare]').forEach(el=>{
    const list=document.createElement('div');list.className='sugg';list.hidden=true;el.parentNode.style.position='relative';el.parentNode.appendChild(list);
    let tt;el.addEventListener('input',()=>{clearTimeout(tt);const q=el.value.trim();if(q.length<2){list.hidden=true;return}
      tt=setTimeout(async()=>{const j=await (await fetch('/api/cities?limit=8&q='+encodeURIComponent(q))).json();list.innerHTML='';
        j.results.forEach(c=>{const d=document.createElement('div');d.textContent=placeLabel(c);d.onclick=()=>{const f=el.form;
          el.value=[c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ');
          f.city2.value=el.value;f.lat2.value=c.latitude;f.lon2.value=c.longitude;f.tz2.value=c.timezone;list.hidden=true;f.submit()};list.appendChild(d)});
        list.hidden=!j.results.length},200)})});
  // birth-place pickers in forms
  document.querySelectorAll('[data-place]').forEach(el=>{
    const pre=el.dataset.place, list=document.createElement('div');list.className='sugg';list.hidden=true;el.parentNode.style.position='relative';el.parentNode.appendChild(list);
    let tt;el.addEventListener('input',()=>{clearTimeout(tt);const q=el.value.trim();if(q.length<2){list.hidden=true;return}
      tt=setTimeout(async()=>{const j=await (await fetch('/api/cities?limit=8&q='+encodeURIComponent(q))).json();list.innerHTML='';
        j.results.forEach(c=>{const d=document.createElement('div');d.textContent=placeLabel(c);d.onclick=()=>{const f=el.form;el.value=[c.name,c.admin1_name,c.country_name||c.country].filter(Boolean).join(', ');
          const set=(k,v)=>{const n=f.elements[pre+k]; if(n) n.value=v;};
          set('lat', c.latitude); set('lon', c.longitude); set('tz', c.timezone); list.hidden=true};list.appendChild(d)});
        list.hidden=!j.results.length},200)})});
})();

// language switcher. The choice is kept in the page address, not only in a cookie.
(function(){
  const s=document.getElementById('langSel'); if(!s) return;
  function saved(){ try{return localStorage.getItem('ph_lang')||''}catch(e){return ''} }
  function remember(v){
    if(!v || v==='en'){
      document.cookie='ph_lang=;path=/;max-age=0;SameSite=Lax';
      try{localStorage.removeItem('ph_lang')}catch(e){}
      return;
    }
    document.cookie='ph_lang='+encodeURIComponent(v)+';path=/;max-age=31536000;SameSite=Lax';
    try{localStorage.setItem('ph_lang', v)}catch(e){}
  }
  function withLang(href, lang){
    let u;
    try{ u=new URL(href, location.origin); }catch(e){ return null; }
    if(u.origin!==location.origin) return null;
    if(!lang || lang==='en') u.searchParams.set('lang','en');
    else u.searchParams.set('lang', lang);
    return u;
  }
  function go(lang){
    remember(lang);
    const u=withLang(location.href, lang);
    if(u) location.href=u.toString();
  }
  s.onchange=function(){ go(s.value); };
  const reset=document.getElementById('langReset');
  if(reset) reset.onclick=function(){ go('en'); };
  const cur=new URL(location.href).searchParams.get('lang')||'';
  if(cur==='en'){
    try{localStorage.removeItem('ph_lang')}catch(e){}
    document.cookie='ph_lang=;path=/;max-age=0;SameSite=Lax';
  }
  const want=cur || saved();
  if(!cur && want && want!=='en'){
    const u=withLang(location.href, want);
    if(u && u.toString()!==location.href){ location.replace(u.toString()); return; }
  }
  const lang=(cur && cur!=='en') ? cur : '';
  if(!lang) return;
  document.querySelectorAll('a[href]').forEach(function(a){
    const raw=a.getAttribute('href')||'';
    if(!raw || raw.charAt(0)==='#' || a.target==='_blank') return;
    const u=withLang(a.href, lang);
    if(u) a.href=u.pathname+u.search+u.hash;
  });
  document.querySelectorAll('form').forEach(function(f){
    if((f.getAttribute('method')||'get').toLowerCase()!=='get') return;
    if(f.querySelector('input[name="lang"]')) return;
    const h=document.createElement('input');
    h.type='hidden'; h.name='lang'; h.value=lang;
    f.appendChild(h);
  });
})();

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
      const loc=({hi:'hi-IN',mr:'mr-IN',gu:'gu-IN',bn:'bn-IN',ta:'ta-IN',te:'te-IN',kn:'kn-IN',ml:'ml-IN'})[document.documentElement.lang]||'en-GB';
      el.textContent=new Intl.DateTimeFormat(loc,{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false,timeZone:tz}).format(now);
      if(dateEl) dateEl.textContent=new Intl.DateTimeFormat(loc,{weekday:'short',day:'numeric',month:'short',year:'numeric',timeZone:tz}).format(now);
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
    el.textContent=(PHUI['Vedic time since sunrise']||'Vedic time since sunrise')+' · '+g+' '+(PHUI.ghati||'ghati')+' '+p+' '+(PHUI.pala||'pala')+' '+v+' '+(PHUI.vipala||'vipala');
  }
  tick(); setInterval(tick,1000);
})();
