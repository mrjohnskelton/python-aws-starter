const API_BASE = window.API_BASE || 'http://localhost:8000';

const $ = sel => document.querySelector(sel);
const listEl = $('#list');
const summaryEl = $('#summary');
let zoom = 2;
let lastResults = [];
let selectedItem = null;
let map = null;
let geoIndex = {};

function setSummary(count, dim){
  summaryEl.textContent = `${count} ${dim} result${count===1?'':'s'}`;
}

function renderResults(results, dim){
  lastResults = results || [];
  listEl.innerHTML = '';
  if(!results || results.length===0){ setSummary(0, dim); return }
  setSummary(results.length, dim);
  results.forEach((item, idx)=>{
    const li = document.createElement('li');
    li.setAttribute('role','listitem');
    li.tabIndex = 0;
    li.className = 'card';
    li.dataset.index = idx;
    li.innerHTML = cardInner(item, dim);
    li.addEventListener('click', ()=>selectItem(idx, li));
    li.addEventListener('keypress', (e)=>{ if(e.key==='Enter') selectItem(idx, li)});
    listEl.appendChild(li);
  })
}

function cardInner(item, dim){
  // Zoom controls reduce details shown
  const detail = Math.max(0, zoom);
  let html = `<strong>${item.id || item.name || item.title || dim}</strong>`;
  if(detail>0){
    html += `<div class="muted">${(item.description || item.summary || item.city || '')}</div>`;
  }
  if(detail>1){
    html += `<div style="margin-top:.5rem;font-size:.85rem">`;
    for(const k of Object.keys(item).slice(0,4)) html += `<div><small>${k}</small>: ${escapeHTML(String(item[k]))}</div>`;
    html += `</div>`;
  }
  return html;
}

function escapeHTML(s){ return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;') }

function selectItem(idx, el){
  const prev = document.querySelector('.card.selected');
  if(prev) prev.classList.remove('selected');
  el.classList.add('selected');
  selectedItem = lastResults[idx];
  // center map on selected item's first location if available
  if(map && selectedItem && selectedItem.locations && selectedItem.locations.length){
    const loc = selectedItem.locations[0];
    const geo = loc.geography_id ? geoIndex[loc.geography_id] : null;
    const lat = loc.latitude || (geo && geo.center_coordinate && geo.center_coordinate.latitude);
    const lon = loc.longitude || (geo && geo.center_coordinate && geo.center_coordinate.longitude);
    if(lat && lon) map.setView([lat, lon], Math.max(3,map.getZoom()));
  }
}

async function search(dim, q){
  try{
    const url = new URL(`${API_BASE}/search/${encodeURIComponent(dim)}`);
    if(q) url.searchParams.set('q', q);
    const res = await fetch(url);
    if(!res.ok) throw new Error(await res.text())
    const body = await res.json();
    renderResults(body.results || body || [], dim);
  }catch(err){
    summaryEl.textContent = 'Error fetching results';
    console.error(err);
  }
}

async function pivot(fromDim, toDim){
  if(!selectedItem) return alert('Select an item to pivot from');
  const id = selectedItem.id || selectedItem.name || selectedItem.title;
  const url = `${API_BASE}/pivot?from=${encodeURIComponent(fromDim)}&to=${encodeURIComponent(toDim)}&id=${encodeURIComponent(id)}`;
  const res = await fetch(url);
  if(!res.ok) return alert('Pivot failed');
  const body = await res.json();
  renderResults(body.results || body || [], toDim);
}

function ensureMap(){
  if(map) return map;
  if(typeof L === 'undefined'){
    // Leaflet not loaded yet — try to load via CDN dynamically
    const s = document.createElement('script');
    s.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    s.onload = ()=>{ initMap(); }
    document.body.appendChild(s);
    return null;
  }
  return initMap();
}

function initMap(){
  if(map) return map;
  map = L.map('map', {attributionControl:false}).setView([48.8566,2.3522], 3);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19}).addTo(map);
  return map;
}

function clearMapMarkers(){
  if(!map) return;
  // remove all markers layer
  map.eachLayer(layer=>{ if(layer && layer.options && layer.options.pane==='markerPane') map.removeLayer(layer) });
}

function addMapMarkers(items){
  ensureMap();
  if(!map) return;
  clearMapMarkers();
  items.forEach(item=>{
    if(!item.locations) return;
    item.locations.forEach(loc=>{
      const geo = loc.geography_id ? geoIndex[loc.geography_id] : null;
      const lat = loc.latitude || (geo && geo.center_coordinate && geo.center_coordinate.latitude);
      const lon = loc.longitude || (geo && geo.center_coordinate && geo.center_coordinate.longitude);
      if(lat && lon){
        const mk = L.circleMarker([lat, lon], {radius:6, color:'#6366f1', fill:true, fillOpacity:0.9}).addTo(map);
        mk.bindPopup(`<strong>${escapeHTML(item.title||item.name||item.id)}</strong><br>${escapeHTML(loc.name||'')}`);
      }
    })
  })
}

function renderTimeline(items){
  const el = document.getElementById('timeline');
  el.innerHTML = '';
  if(!items || items.length===0) return;
  // collect dates as years (approx)
  const parsed = items.map(it=>{
    const sd = (it.start_date && it.start_date.start_date) || (it.start_date && it.start_date) || it.birth_date || it.created_at;
    let year = null;
    if(sd){
      const m = sd.match(/-?\d{1,4}/);
      if(m) year = parseInt(m[0],10);
    }
    return {item:it, year: year};
  }).filter(p=>p.year!==null).sort((a,b)=>a.year-b.year);
  if(parsed.length===0) return;
  const years = parsed.map(p=>p.year);
  const min = Math.min(...years), max = Math.max(...years);
  const range = Math.max(1, max-min);
  const bar = document.createElement('div'); bar.className='bar';
  parsed.forEach((p, idx)=>{
    const pos = ((p.year - min)/range)*100;
    const tick = document.createElement('div');
    tick.className='tick';
    tick.style.left = pos+'%';
    tick.innerHTML = `<div title="${p.year}">●</div><div style="font-size:0.75rem;margin-top:0.25rem">${p.year}</div>`;
    tick.addEventListener('click', ()=>{
      // find and select in list
      const index = lastResults.indexOf(p.item);
      const el = listEl.querySelector(`[data-index=\"${index}\"]`);
      if(el) el.focus(), selectItem(index, el);
    });
    bar.appendChild(tick);
  });
  el.appendChild(bar);
}

// UI wiring
$('#searchForm').addEventListener('submit', e=>{
  e.preventDefault();
  const dim = $('#dimension').value;
  const q = $('#q').value.trim();
  search(dim, q);
});

$('#clearBtn').addEventListener('click', ()=>{
  $('#q').value=''; renderResults([], $('#dimension').value);
});

$('#pivotBtn').addEventListener('click', ()=>{
  const from = $('#dimension').value;
  const to = $('#target').value;
  pivot(from,to);
});

$('#zoomIn').addEventListener('click', ()=>{ if(zoom<4) zoom++; updateZoom(); });
$('#zoomOut').addEventListener('click', ()=>{ if(zoom>0) zoom--; updateZoom(); });
function updateZoom(){
  $('#zoomLevel').textContent = zoom;
  renderResults(lastResults, $('#dimension').value);
}

// keyboard: n for next, p for previous
document.addEventListener('keydown', (e)=>{
  if(e.target.tagName==='INPUT' || e.target.tagName==='SELECT') return;
  if(e.key==='n' && lastResults.length){
    const nextIdx = selectedItem ? (lastResults.indexOf(selectedItem)+1)%lastResults.length : 0;
    const el = listEl.querySelector(`[data-index=\"${nextIdx}\"]`);
    if(el) el.focus(), selectItem(nextIdx, el);
  }
  if(e.key==='p' && lastResults.length){
    const cur = selectedItem ? lastResults.indexOf(selectedItem) : 0;
    const prevIdx = (cur-1+lastResults.length)%lastResults.length;
    const el = listEl.querySelector(`[data-index=\"${prevIdx}\"]`);
    if(el) el.focus(), selectItem(prevIdx, el);
  }
});

// initial state
$('#zoomLevel').textContent = zoom;
setSummary(0,'results');

// Expose API_BASE in DOM
document.getElementById('apiBase').textContent = API_BASE;

// Allow override via window for embedding
export { search, pivot };

// Wire load-local sample data button
$('#loadLocal').addEventListener('click', async ()=>{
  try{
    const res = await fetch('fixtures/sample_dataset.json');
    const body = await res.json();
    // prefer events for timeline/map demo
    const items = body.events || [];
    // build geo index
    if(body.geographies){ body.geographies.forEach(g=>{ geoIndex[g.id]=g }) }
    renderResults(items, 'events');
    addMapMarkers(items);
    renderTimeline(items);
  }catch(err){
    alert('Failed to load local sample data: '+err.message);
  }
});

// when rendering results from API, also update map and timeline
const originalRenderResults = renderResults;
renderResults = function(results, dim){
  originalRenderResults(results, dim);
  // if geography dimension requested, build geo index
  // attempt to fetch geographies once
  fetch(`${API_BASE}/search/geographies`).then(r=>r.json()).then(body=>{
    if(body && body.results){ body.results.forEach(g=>geoIndex[g.id]=g) }
    addMapMarkers(results || []);
    renderTimeline(results || []);
  }).catch(()=>{
    addMapMarkers(results || []);
    renderTimeline(results || []);
  });
}
