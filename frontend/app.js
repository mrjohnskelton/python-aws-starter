const API_BASE = window.API_BASE || 'http://localhost:8000';

const $ = sel => document.querySelector(sel);
const listEl = $('#list');
const summaryEl = $('#summary');
let zoom = 2;
let lastResults = [];
let selectedItem = null;
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
    updateVisualizations(body.results || body || [], dim);
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
  updateVisualizations(body.results || body || [], toDim);
}

function updateVisualizations(items, dim){
  renderGanttTimeline(items);
  renderSVGMap(items);
}

function renderGanttTimeline(items){
  const el = document.getElementById('timeline');
  el.innerHTML = '';
  if(!items || items.length===0) return;
  
  const parsed = items.map(it=>{
    const sd = (it.start_date && it.start_date.start_date) || (it.start_date && it.start_date) || it.birth_date || it.created_at;
    const ed = (it.start_date && it.start_date.end_date) || (it.end_date && it.end_date) || it.death_date;
    let startYear = null, endYear = null;
    if(sd){
      const m = sd.match(/-?\d{1,4}/);
      if(m) startYear = parseInt(m[0],10);
    }
    if(ed){
      const m = ed.match(/-?\d{1,4}/);
      if(m) endYear = parseInt(m[0],10);
    }
    return {item:it, startYear, endYear};
  }).filter(p=>p.startYear!==null).sort((a,b)=>a.startYear-b.startYear);
  
  if(parsed.length===0) return;
  
  const years = parsed.flatMap(p=>[p.startYear, p.endYear].filter(y=>y!==null));
  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);
  const range = Math.max(1, maxYear - minYear);
  
  const container = document.createElement('div');
  container.style.position = 'relative';
  
  parsed.forEach((p, idx)=>{
    const isRange = p.endYear !== null && p.endYear !== p.startYear;
    const startPos = ((p.startYear - minYear) / range) * 100;
    const endPos = isRange ? ((p.endYear - minYear) / range) * 100 : startPos + 3;
    const width = Math.max(2, endPos - startPos);
    
    const bar = document.createElement('div');
    bar.className = 'timeline-bar';
    bar.style.width = width + '%';
    bar.style.marginLeft = startPos + '%';
    bar.style.opacity = Math.max(0.4, 1 - (p.item.confidence || 0.5) * 0.3);
    bar.title = `${p.item.title||p.item.name} (${p.startYear}${p.endYear && p.endYear !== p.startYear ? '-'+p.endYear : ''})`;
    bar.innerHTML = `<span>${p.item.title || p.item.name}</span>`;
    
    bar.addEventListener('click', ()=>{
      const index = lastResults.indexOf(p.item);
      const el = listEl.querySelector(`[data-index="${index}"]`);
      if(el) el.focus(), selectItem(index, el);
    });
    
    container.appendChild(bar);
  });
  
  el.appendChild(container);
}

function renderSVGMap(items){
  const svg = document.getElementById('mapCanvas');
  if(!svg) return;
  
  svg.querySelectorAll('.map-pin').forEach(el=>el.remove());
  
  if(!items || items.length===0) return;
  
  const viewBox = svg.getAttribute('viewBox').split(' ').map(Number);
  const svgWidth = viewBox[2], svgHeight = viewBox[3];
  
  items.forEach(item=>{
    if(!item.locations || item.locations.length===0) return;
    
    item.locations.forEach(loc=>{
      const geo = loc.geography_id ? geoIndex[loc.geography_id] : null;
      const lat = loc.latitude || (geo && geo.center_coordinate && geo.center_coordinate.latitude);
      const lon = loc.longitude || (geo && geo.center_coordinate && geo.center_coordinate.longitude);
      
      if(lat !== null && lon !== null){
        const x = ((lon + 180) / 360) * svgWidth;
        const y = ((90 - lat) / 180) * svgHeight;
        
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'map-pin');
        g.setAttribute('transform', `translate(${x},${y})`);
        
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('r', '8');
        circle.setAttribute('cx', '0');
        circle.setAttribute('cy', '0');
        
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${item.title||item.name} - ${loc.name||''}`;
        
        g.appendChild(circle);
        g.appendChild(title);
        
        g.addEventListener('click', ()=>{
          const index = lastResults.indexOf(item);
          const el = listEl.querySelector(`[data-index="${index}"]`);
          if(el) el.focus(), selectItem(index, el);
        });
        
        svg.appendChild(g);
      }
    })
  })
}

// UI wiring
$('#searchForm').addEventListener('submit', e=>{
  e.preventDefault();
  const dim = $('#dimension').value;
  const q = $('#q').value.trim();
  search(dim, q);
});

$('#clearBtn').addEventListener('click', ()=>{
  $('#q').value=''; 
  renderResults([], $('#dimension').value);
  updateVisualizations([], $('#dimension').value);
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
    const items = body.events || [];
    if(body.geographies){ body.geographies.forEach(g=>{ geoIndex[g.id]=g }) }
    renderResults(items, 'events');
    updateVisualizations(items, 'events');
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
