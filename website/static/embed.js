// PanchangHub embeddable widget: <div data-panchanghub data-lat="28.61" data-lon="77.21" data-tz="Asia/Kolkata" data-lang="hi"></div>
// <script src="https://panchanghub.com/static/embed.js" async></script>
(function(){var s=document.currentScript,base=(s&&s.src.replace(/\/static\/embed\.js.*$/,''))||'';
document.querySelectorAll('[data-panchanghub]').forEach(function(el){var d=el.dataset,q=new URLSearchParams();
['lat','lon','tz','city','lang'].forEach(function(k){if(d[k])q.set(k,d[k])});
var f=document.createElement('iframe');f.src=base+'/widget/panchang?'+q;f.style.cssText='border:0;width:'+(d.width||'320px')+';height:'+(d.height||'360px');f.title='Panchang';f.loading='lazy';el.appendChild(f);});})();
