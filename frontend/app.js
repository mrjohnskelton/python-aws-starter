const API_BASE = window.API_BASE || 'http://localhost:8000';

const $ = sel => document.querySelector(sel);
const listEl = $('#list');
const summaryEl = $('#summary');
const detailPanel = $('#detailPanel');
const detailContent = $('#detailContent');
let zoom = 2;
let lastResults = [];
let selectedItem = null;
let geoIndex = {};

function setSummary(count, dim){
  summaryEl.textContent = `${count} ${dim} result${count===1?'':'s'}`;
}

function renderResults(results, dim){
  console.log(`[renderResults] Rendering ${results ? results.length : 0} results for ${dim}`, results);
  lastResults = results || [];
  if(!listEl){
    console.error('[renderResults] listEl is null!');
    return;
  }
  listEl.innerHTML = '';
  if(!results || results.length===0){ 
    console.log('[renderResults] No results to display');
    setSummary(0, dim); 
    return;
  }
  setSummary(results.length, dim);
  results.forEach((item, idx)=>{
    try {
      const li = document.createElement('li');
      li.setAttribute('role','listitem');
      li.tabIndex = 0;
      li.className = 'card';
      li.dataset.index = idx;
      li.innerHTML = cardInner(item, dim);
      li.addEventListener('click', ()=>selectItem(idx, li));
      li.addEventListener('keypress', (e)=>{ if(e.key==='Enter') selectItem(idx, li)});
      listEl.appendChild(li);
    } catch(err) {
      console.error(`[renderResults] Error rendering item ${idx}:`, err, item);
    }
  });
  console.log(`[renderResults] Rendered ${results.length} items to listEl`);
}

function cardInner(item, dim){
  // Zoom controls reduce details shown
  const detail = Math.max(0, zoom);
  
  // Handle WikibaseEntity structure (Wikidata native) - labels instead of name/title
  let displayName = item.name || item.title;
  if (!displayName && item.labels && item.labels.en) {
    displayName = item.labels.en.value || item.labels.en;
  }
  if (!displayName && item.labels) {
    // Try first available language
    const firstLang = Object.keys(item.labels)[0];
    if (firstLang && item.labels[firstLang]) {
      displayName = item.labels[firstLang].value || item.labels[firstLang];
    }
  }
  displayName = displayName || item.id || dim;
  
  // Handle descriptions - WikibaseEntity uses descriptions.en.value
  let displayDesc = item.description || item.summary || item.city || '';
  if (!displayDesc && item.descriptions && item.descriptions.en) {
    displayDesc = item.descriptions.en.value || item.descriptions.en;
  }
  if (!displayDesc && item.descriptions) {
    const firstLang = Object.keys(item.descriptions)[0];
    if (firstLang && item.descriptions[firstLang]) {
      displayDesc = item.descriptions[firstLang].value || item.descriptions[firstLang];
    }
  }
  
  let html = `<strong>${displayName}</strong>`;
  if(detail>0){
    html += `<div class="muted">${displayDesc}</div>`;
  }
  if(detail>1){
    html += `<div style="margin-top:.5rem;font-size:.85rem">`;
    // Show QID for Wikidata entities
    if(item.id && item.id.startsWith('Q')) {
      html += `<div><small>QID</small>: ${item.id}</div>`;
    }
    for(const k of Object.keys(item).slice(0,3)) {
      if(k !== 'labels' && k !== 'descriptions' && k !== 'aliases') {
        html += `<div><small>${k}</small>: ${escapeHTML(String(item[k]))}</div>`;
      }
    }
    html += `</div>`;
  }
  return html;
}

function escapeHTML(s){ return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;') }

async function selectItem(idx, el){
  const prev = document.querySelector('.card.selected');
  if(prev) prev.classList.remove('selected');
  el.classList.add('selected');
  selectedItem = lastResults[idx];
  
  // Fetch and display full entity details
  await loadEntityDetails(selectedItem);
  
  // Update timeline and map to highlight selected item
  updateVisualizations(lastResults, $('#dimension').value, selectedItem);
  
  // Center map on selected item's location if available
  if(selectedItem) {
    const coords = extractCoordinatesFromEntity(selectedItem);
    if(coords.lat !== null && coords.lon !== null && map) {
      map.setView([coords.lat, coords.lon], Math.max(3, map.getZoom()));
    }
  }
}

async function loadEntityDetails(item) {
  if (!item || !detailPanel || !detailContent) {
    console.warn('[loadEntityDetails] Missing item or DOM elements');
    return;
  }
  
  // Extract QID from item ID
  let qid = null;
  if (item.id) {
    // Handle formats like "Q123", "person_wikidata_Q123", "event_wikidata_Q456"
    if (item.id.startsWith('Q') && /^Q\d+$/.test(item.id)) {
      qid = item.id;
    } else if (item.id.includes('_')) {
      const parts = item.id.split('_');
      const lastPart = parts[parts.length - 1];
      if (lastPart.startsWith('Q') && /^Q\d+$/.test(lastPart)) {
        qid = lastPart;
      }
    }
  }
  
  // If we have a QID, fetch full entity details
  if (qid) {
    try {
      console.log(`[loadEntityDetails] Fetching full entity details for QID: ${qid}`);
      const url = `${API_BASE}/wikidata/entity/${qid}`;
      const res = await fetch(url);
      if (res.ok) {
        const fullEntity = await res.json();
        console.log(`[loadEntityDetails] Received full entity data:`, fullEntity);
        renderDetailPanel(fullEntity);
        return;
      } else {
        console.warn(`[loadEntityDetails] Failed to fetch entity ${qid}: ${res.status}`);
      }
    } catch (err) {
      console.error(`[loadEntityDetails] Error fetching entity ${qid}:`, err);
    }
  }
  
  // Fallback: display available data from the item itself
  console.log(`[loadEntityDetails] Using item data directly (no QID or fetch failed)`);
  renderDetailPanel(item);
}

function renderDetailPanel(entity) {
  if (!detailPanel || !detailContent) {
    console.warn('[renderDetailPanel] Detail panel elements not found');
    return;
  }
  
  // Show the detail panel
  detailPanel.style.display = 'block';
  
  // Get display name
  const displayName = getLabel(entity) || entity.name || entity.title || entity.id || 'Unknown';
  const displayDesc = getDescription(entity) || entity.description || '';
  
  let html = `<div class="detail-header">`;
  html += `<h4>${escapeHTML(displayName)}</h4>`;
  if (displayDesc) {
    html += `<p class="detail-description">${escapeHTML(displayDesc)}</p>`;
  }
  html += `</div>`;
  
  // Display QID if available
  let qid = entity.id;
  if (qid && qid.includes('_')) {
    const parts = qid.split('_');
    qid = parts[parts.length - 1];
  }
  if (qid && qid.startsWith('Q')) {
    html += `<div class="detail-section">`;
    html += `<strong>Wikidata ID:</strong> <a href="https://www.wikidata.org/wiki/${qid}" target="_blank" rel="noopener">${qid}</a>`;
    html += `</div>`;
  }
  
  // Display labels in multiple languages if available
  if (entity.labels && Object.keys(entity.labels).length > 0) {
    html += `<div class="detail-section">`;
    html += `<strong>Labels:</strong>`;
    html += `<ul class="detail-list">`;
    for (const [lang, labelData] of Object.entries(entity.labels)) {
      const labelValue = labelData.value || labelData;
      html += `<li><span class="lang-code">${lang}</span>: ${escapeHTML(labelValue)}</li>`;
    }
    html += `</ul>`;
    html += `</div>`;
  }
  
  // Display descriptions in multiple languages if available
  if (entity.descriptions && Object.keys(entity.descriptions).length > 0) {
    html += `<div class="detail-section">`;
    html += `<strong>Descriptions:</strong>`;
    html += `<ul class="detail-list">`;
    for (const [lang, descData] of Object.entries(entity.descriptions)) {
      const descValue = descData.value || descData;
      html += `<li><span class="lang-code">${lang}</span>: ${escapeHTML(descValue)}</li>`;
    }
    html += `</ul>`;
    html += `</div>`;
  }
  
  // Display aliases if available
  if (entity.aliases && Object.keys(entity.aliases).length > 0) {
    html += `<div class="detail-section">`;
    html += `<strong>Aliases:</strong>`;
    for (const [lang, aliasList] of Object.entries(entity.aliases)) {
      if (Array.isArray(aliasList) && aliasList.length > 0) {
        html += `<div><span class="lang-code">${lang}</span>: `;
        const aliasValues = aliasList.map(a => a.value || a).join(', ');
        html += `${escapeHTML(aliasValues)}</div>`;
      }
    }
    html += `</div>`;
  }
  
  // Display claims (key properties)
  if (entity.claims && Object.keys(entity.claims).length > 0) {
    html += `<div class="detail-section">`;
    html += `<strong>Properties:</strong>`;
    html += `<ul class="detail-list">`;
    
    // Show first 10 claims
    const claimEntries = Object.entries(entity.claims).slice(0, 10);
    for (const [propId, claims] of claimEntries) {
      if (Array.isArray(claims) && claims.length > 0) {
        const claim = claims[0];
        const mainsnak = claim.mainsnak || {};
        const datavalue = mainsnak.datavalue || {};
        const value = datavalue.value || {};
        
        let valueDisplay = '';
        if (datavalue.type === 'time' && value.time) {
          valueDisplay = value.time.replace(/^\+/, '').split('T')[0];
        } else if (datavalue.type === 'wikibase-entityid' && value.id) {
          valueDisplay = value.id;
        } else if (datavalue.type === 'globecoordinate') {
          valueDisplay = `${value.latitude?.toFixed(4)}, ${value.longitude?.toFixed(4)}`;
        } else if (typeof value === 'string') {
          valueDisplay = value;
        } else {
          valueDisplay = JSON.stringify(value).substring(0, 50);
        }
        
        html += `<li><strong>${propId}</strong>: ${escapeHTML(String(valueDisplay))}</li>`;
      }
    }
    html += `</ul>`;
    html += `</div>`;
  }
  
  // Display sitelinks (Wikipedia links) if available
  if (entity.sitelinks && Object.keys(entity.sitelinks).length > 0) {
    html += `<div class="detail-section">`;
    html += `<strong>Wikipedia Links:</strong>`;
    html += `<ul class="detail-list">`;
    for (const [site, sitelink] of Object.entries(entity.sitelinks)) {
      const title = sitelink.title || '';
      const url = sitelink.url || `https://${site}.wikipedia.org/wiki/${encodeURIComponent(title)}`;
      html += `<li><a href="${url}" target="_blank" rel="noopener">${site}: ${escapeHTML(title)}</a></li>`;
    }
    html += `</ul>`;
    html += `</div>`;
  }
  
  // Display other relevant fields
  const otherFields = ['birth_date', 'death_date', 'start_date', 'end_date', 'occupations', 'nationalities', 'geography_type'];
  for (const field of otherFields) {
    if (entity[field] !== undefined && entity[field] !== null) {
      html += `<div class="detail-section">`;
      html += `<strong>${field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> `;
      if (Array.isArray(entity[field])) {
        html += entity[field].join(', ');
      } else if (typeof entity[field] === 'object') {
        html += JSON.stringify(entity[field]);
      } else {
        html += escapeHTML(String(entity[field]));
      }
      html += `</div>`;
    }
  }
  
  detailContent.innerHTML = html;
}

function getLabel(item, lang = 'en') {
  if (item.labels && item.labels[lang]) {
    return item.labels[lang].value || item.labels[lang];
  }
  return item.name || item.title || null;
}

function getDescription(item, lang = 'en') {
  if (item.descriptions && item.descriptions[lang]) {
    return item.descriptions[lang].value || item.descriptions[lang];
  }
  return item.description || null;
}

/**
 * Date property synonyms configuration.
 * These property IDs are treated as synonyms for start/end dates.
 * Definitions: https://www.wikidata.org/wiki/Property:{Pnumber}
 */
const DATE_PROPERTY_SYNONYMS = {
  // Start date synonyms
  startDate: [
    'P571',  // Inception
    'P1619', // Date of official opening
    'P569',  // Birth date
    'P580',  // Start time (event)
    'P585',  // Point in time
    'P1319', // Earliest date
    'P2031', // Work period (start)
  ],
  // End date synonyms
  endDate: [
    'P570',  // Death date
    'P582',  // End time
    'P576',  // Dissolved
    'P2669', // Terminated
    'P1326', // Latest date
    'P2032', // Work period (end)
  ]
};

/**
 * Extract start and end dates from entity claims using property synonyms.
 * Handles multiple Wikidata properties that represent start/end dates.
 */
function extractDatesFromClaims(entity) {
  let startDate = null;
  let endDate = null;
  
  if (!entity.claims) {
    return { startDate, endDate };
  }
  
  // Helper to extract date from a claim
  const extractDateFromClaim = (claim) => {
    if (!claim || !claim.mainsnak) return null;
    const datavalue = claim.mainsnak.datavalue;
    if (!datavalue || datavalue.type !== 'time') return null;
    const timeValue = datavalue.value;
    if (!timeValue || !timeValue.time) return null;
    // Extract date from Wikidata time format: +1769-08-15T00:00:00Z
    const timeStr = timeValue.time.replace(/^\+/, '').split('T')[0];
    return timeStr;
  };
  
  // Try start date synonyms in priority order
  for (const propId of DATE_PROPERTY_SYNONYMS.startDate) {
    if (entity.claims[propId] && entity.claims[propId].length > 0) {
      const date = extractDateFromClaim(entity.claims[propId][0]);
      if (date) {
        startDate = date;
        break; // Use first found start date
      }
    }
  }
  
  // Try end date synonyms in priority order
  for (const propId of DATE_PROPERTY_SYNONYMS.endDate) {
    if (entity.claims[propId] && entity.claims[propId].length > 0) {
      const date = extractDateFromClaim(entity.claims[propId][0]);
      if (date) {
        endDate = date;
        break; // Use first found end date
      }
    }
  }
  
  // Fallback: try to find any time-type claim if we don't have dates yet
  if (!startDate || !endDate) {
    for (const [propId, claims] of Object.entries(entity.claims)) {
      if (Array.isArray(claims) && claims.length > 0) {
        const claim = claims[0];
        if (claim.mainsnak && claim.mainsnak.datavalue && claim.mainsnak.datavalue.type === 'time') {
          const date = extractDateFromClaim(claim);
          if (date) {
            if (!startDate) startDate = date;
            else if (!endDate && date !== startDate) endDate = date;
          }
        }
      }
    }
  }
  
  return { startDate, endDate };
}

async function search(dim, q){
  try{
    // Map frontend dimension names to API endpoint names
    const dimMap = {
      'geography': 'geographies',
      'people': 'people',
      'events': 'events'
    };
    const apiDim = dimMap[dim] || dim;
    const url = new URL(`${API_BASE}/search/${encodeURIComponent(apiDim)}`);
    if(q) url.searchParams.set('q', q);
    console.log(`[search] Fetching from ${url}`);
    const res = await fetch(url);
    if(!res.ok) {
      const errorText = await res.text();
      console.error(`[search] API error: ${res.status} ${errorText}`);
      throw new Error(errorText);
    }
    const body = await res.json();
    const results = body.results || body || [];
    console.log(`[search] Received ${results.length} results for ${dim} (API: ${apiDim})`, results);
    if(results.length > 0) {
      console.log(`[search] First result:`, results[0]);
    }
    renderResults(results, dim);
    // updateVisualizations is called inside renderResults wrapper
  }catch(err){
    summaryEl.textContent = 'Error fetching results';
    console.error('[search] Error:', err);
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

function updateVisualizations(items, dim, selectedItemForHighlight = null){
  renderGanttTimeline(items, selectedItemForHighlight);
  renderSVGMap(items, selectedItemForHighlight);
}

function renderGanttTimeline(items, selectedItemForHighlight = null){
  const el = document.getElementById('timeline');
  el.innerHTML = '';
  if(!items || items.length===0) return;
  
  const parsed = items.map(it=>{
    // Try to extract dates from claims first (for Wikidata entities)
    let sd = null, ed = null;
    if (it.claims) {
      const dates = extractDatesFromClaims(it);
      sd = dates.startDate;
      ed = dates.endDate;
    }
    
    // Fallback to traditional fields if no claims
    if (!sd) {
      sd = (it.start_date && it.start_date.start_date) || (it.start_date && it.start_date) || it.birth_date || it.created_at;
    }
    if (!ed) {
      ed = (it.start_date && it.start_date.end_date) || (it.end_date && it.end_date) || it.death_date;
    }
    
    let startYear = null, endYear = null;
    if(sd){
      const m = String(sd).match(/-?\d{1,4}/);
      if(m) startYear = parseInt(m[0],10);
    }
    if(ed){
      const m = String(ed).match(/-?\d{1,4}/);
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
  
  // Determine if selected item should be highlighted
  const selectedItemId = selectedItemForHighlight ? (selectedItemForHighlight.id || null) : null;
  
  parsed.forEach((p, idx)=>{
    const isRange = p.endYear !== null && p.endYear !== p.startYear;
    const startPos = ((p.startYear - minYear) / range) * 100;
    const endPos = isRange ? ((p.endYear - minYear) / range) * 100 : startPos + 3;
    const width = Math.max(2, endPos - startPos);
    
    // Check if this is the selected item
    const isSelected = selectedItemId && (p.item.id === selectedItemId || 
      (p.item.id && selectedItemId && p.item.id.toString() === selectedItemId.toString()));
    
    const bar = document.createElement('div');
    bar.className = isSelected ? 'timeline-bar timeline-bar-selected' : 'timeline-bar';
    bar.style.width = width + '%';
    bar.style.marginLeft = startPos + '%';
    bar.style.opacity = isSelected ? 1.0 : Math.max(0.4, 1 - (p.item.confidence || 0.5) * 0.3);
    bar.title = `${getLabel(p.item) || p.item.title || p.item.name} (${p.startYear}${p.endYear && p.endYear !== p.startYear ? '-'+p.endYear : ''})`;
    bar.innerHTML = `<span>${getLabel(p.item) || p.item.title || p.item.name}</span>`;
    
    bar.addEventListener('click', ()=>{
      const index = lastResults.indexOf(p.item);
      const el = listEl.querySelector(`[data-index="${index}"]`);
      if(el) el.focus(), selectItem(index, el);
    });
    
    container.appendChild(bar);
  });
  
  el.appendChild(container);
}

/**
 * Extract coordinates from entity claims or location data.
 * Handles P625 (coordinate location) for geographies and location references for events.
 */
function extractCoordinatesFromEntity(entity) {
  let lat = null, lon = null;
  
  // Try to extract from claims (P625 for coordinate location)
  if (entity.claims && entity.claims.P625 && entity.claims.P625.length > 0) {
    const claim = entity.claims.P625[0];
    if (claim.mainsnak && claim.mainsnak.datavalue && claim.mainsnak.datavalue.type === 'globecoordinate') {
      const coordValue = claim.mainsnak.datavalue.value;
      if (coordValue && typeof coordValue.latitude === 'number' && typeof coordValue.longitude === 'number') {
        lat = coordValue.latitude;
        lon = coordValue.longitude;
        return { lat, lon };
      }
    }
  }
  
  // Try from computed_center_coordinate (for Geography entities)
  if (entity.computed_center_coordinate) {
    lat = entity.computed_center_coordinate.latitude;
    lon = entity.computed_center_coordinate.longitude;
    if (lat !== null && lon !== null) {
      return { lat, lon };
    }
  }
  
  // Try from center_coordinate (direct field)
  if (entity.center_coordinate) {
    lat = entity.center_coordinate.latitude;
    lon = entity.center_coordinate.longitude;
    if (lat !== null && lon !== null) {
      return { lat, lon };
    }
  }
  
  // Try from locations array (for Event entities)
  if (entity.locations && entity.locations.length > 0) {
    const loc = entity.locations[0];
    lat = loc.latitude;
    lon = loc.longitude;
    
    // If no direct coordinates, try to get from geography reference
    if ((lat === null || lon === null) && loc.geography_id) {
      const geo = geoIndex[loc.geography_id];
      if (geo) {
        lat = geo.center_coordinate?.latitude || geo.computed_center_coordinate?.latitude;
        lon = geo.center_coordinate?.longitude || geo.computed_center_coordinate?.longitude;
      }
    }
    
    if (lat !== null && lon !== null) {
      return { lat, lon };
    }
  }
  
  return { lat: null, lon: null };
}

function renderSVGMap(items, selectedItemForHighlight = null){
  const svg = document.getElementById('mapCanvas');
  if(!svg) return;
  
  svg.querySelectorAll('.map-pin').forEach(el=>el.remove());
  
  if(!items || items.length===0) return;
  
  const viewBox = svg.getAttribute('viewBox').split(' ').map(Number);
  const svgWidth = viewBox[2], svgHeight = viewBox[3];
  
  // Determine selected item ID for highlighting
  const selectedItemId = selectedItemForHighlight ? (selectedItemForHighlight.id || null) : null;
  
  items.forEach(item=>{
    // Extract coordinates from entity
    const coords = extractCoordinatesFromEntity(item);
    const lat = coords.lat;
    const lon = coords.lon;
    
    if(lat !== null && lon !== null){
      const x = ((lon + 180) / 360) * svgWidth;
      const y = ((90 - lat) / 180) * svgHeight;
      
      // Check if this is the selected item
      const isSelected = selectedItemId && (item.id === selectedItemId || 
        (item.id && selectedItemId && item.id.toString() === selectedItemId.toString()));
      
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('class', isSelected ? 'map-pin map-pin-selected' : 'map-pin');
      g.setAttribute('transform', `translate(${x},${y})`);
      
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', isSelected ? '12' : '8');
      circle.setAttribute('cx', '0');
      circle.setAttribute('cy', '0');
      
      const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      title.textContent = `${getLabel(item) || item.title || item.name}${item.locations && item.locations[0] ? ' - ' + (item.locations[0].name || '') : ''}`;
      
      g.appendChild(circle);
      g.appendChild(title);
      
      g.addEventListener('click', ()=>{
        const index = lastResults.indexOf(item);
        const el = listEl.querySelector(`[data-index="${index}"]`);
        if(el) el.focus(), selectItem(index, el);
      });
      
      svg.appendChild(g);
    }
  });
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
  selectedItem = null;
  if (detailPanel) detailPanel.style.display = 'none';
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

// Load random entity on page load to populate the frontend
async function loadRandomEntity() {
  try {
    console.log('[loadRandomEntity] Fetching random person entity (Q5)...');
    // Filter by instance of Q5 (human/person) to only get person entities
    const res = await fetch(`${API_BASE}/random?instance_of=Q5`);
    if (!res.ok) {
      console.warn('[loadRandomEntity] Failed to fetch random entity:', res.status);
      return;
    }
    const entity = await res.json();
    console.log('[loadRandomEntity] Received random person entity:', entity);
    
    // Since we're filtering for people, use 'people' dimension
    const dim = 'people';
    
    // Display the random entity
    renderResults([entity], dim);
  } catch (err) {
    console.error('[loadRandomEntity] Error:', err);
    // Silently fail - it's okay if random entity doesn't load
  }
}

// Load random entity when page loads
loadRandomEntity();

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
  try {
    console.log(`[renderResults wrapper] Called with ${results ? results.length : 0} results for ${dim}`);
    originalRenderResults(results, dim);
    // if geography dimension requested, build geo index
    // attempt to fetch geographies once to populate geoIndex
    if(dim === 'geographies' || (results && results.some(item => item.locations && item.locations.length > 0))){
      fetch(`${API_BASE}/search/geographies`).then(r=>r.json()).then(body=>{
        const geos = body.results || body || [];
        geos.forEach(g=>geoIndex[g.id]=g);
        // Update visualizations with geo index now populated
        updateVisualizations(results || [], dim);
      }).catch((err)=>{
        console.error('[renderResults wrapper] Error fetching geographies:', err);
        // Still update visualizations even if geo fetch fails
        updateVisualizations(results || [], dim);
      });
    } else {
      // Update visualizations immediately if no geo fetch needed
      updateVisualizations(results || [], dim);
    }
  } catch(err) {
    console.error('[renderResults wrapper] Error:', err);
  }
}
