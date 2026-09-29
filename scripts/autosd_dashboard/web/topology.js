/* Source-derived graph viewer. No external scripts, HTML labels or runtime writes. */
(function (root) {
  'use strict';
  const lane = node => node.kind === 'router' ? 1 : ['cpu', 'instance'].includes(node.kind) ? 0 : 2;
  function filteredNodes(graph, group, query = '') {
    const term = query.toLowerCase().trim();
    return graph.nodes.filter(n => (!group || n.group === group) &&
      (!term || [n.id, n.moduletype, JSON.stringify(n.parameters)].join(' ').toLowerCase().includes(term)));
  }
  function diagram(graph, group = '', signals = false) {
    const selected = filteredNodes(graph, group);
    const nodes = [], groups = [], mapping = new Map();
    let height = 0;
    const overview = !group;
    graph.groups.filter(g => !group || g.id === group).forEach((g, index) => {
      const members = selected.filter(n => n.group === g.id);
      const x = overview ? (index % 2) * 740 + 20 : 20;
      const y = overview ? Math.floor(index / 2) * 235 + 20 : height + 20;
      const buckets = [0, 1, 2].map(i => members.filter(n => lane(n) === i));
      const h = overview ? 210 : Math.max(1, buckets[0].length, buckets[1].length, Math.ceil(buckets[2].length / 2)) * 76 + 70;
      groups.push({...g, x, y, width: overview ? 710 : 1060, height: h, count: members.length});
      buckets.forEach((items, column) => {
        if (overview) {
          if (!items.length) return;
          const id = `${g.id}:${column}`;
          items.forEach(n => mapping.set(n.id, id));
          nodes.push({id, group: g.id, label: ['QEMU CPU / Instance', 'Router / Fabric', 'Components'][column],
            moduletype: `${items.length}개 · 클릭하여 펼치기`, kind: ['cpu', 'router', 'component'][column],
            x: x + 20 + column * 230, y: y + 88, width: 210, height: 66, aggregate: true});
        } else {
          items.forEach((node, i) => {
            mapping.set(node.id, node.id);
            nodes.push({...node, x: x + 20 + (column + (column === 2 ? i % 2 : 0)) * 260,
              y: y + 65 + (column === 2 ? Math.floor(i / 2) : i) * 76, width: 235, height: 56});
          });
        }
      });
      height = Math.max(height, y + h + 20);
    });
    const edges = [], counts = new Map();
    for (const edge of graph.edges) {
      if (!signals && edge.kind !== 'tlm') continue;
      const source = mapping.get(edge.source), target = mapping.get(edge.target);
      if (!source || !target || (overview && source === target)) continue;
      const key = overview ? `${source}|${target}|${edge.kind}` : edge.id;
      if (counts.has(key)) { counts.get(key).count++; continue; }
      const item = {...edge, source, target, count: 1};
      counts.set(key, item); edges.push(item);
    }
    return {nodes, edges, groups, width: overview ? 1500 : 1100, height: Math.max(height, 240), overview};
  }
  const model = {lane, filteredNodes, diagram};
  if (typeof module !== 'undefined' && module.exports) module.exports = model;
  if (typeof document === 'undefined') return;
  root.QBoxTopology = model;
  const $ = id => document.getElementById(id);
  if (!$('topology')) return;
  const make = (tag, text, cls) => {
    const e = document.createElement(tag); if (text !== undefined) e.textContent = text;
    if (cls) e.className = cls; return e;
  };
  const svgEl = (tag, attrs = {}, text) => {
    const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attrs)) e.setAttribute(key, value);
    if (text !== undefined) e.textContent = text; return e;
  };
  let graph, view, selected = '', scale = 1, loading = false;
  const nodeMap = new Map();
  function changeGroup(group) {
    $('topology-group').value = group; selected = '';
    $('topology-selection').replaceChildren(make('p', '그룹 요약에서 컴포넌트를 선택하세요.', 'footnote'));
    render(); fit(); $('topology-canvas').scrollTo(0, 0);
  }
  function selectNode(id) {
    const node = nodeMap.get(id); if (!node) return;
    const changed = $('topology-group').value !== node.group;
    $('topology-group').value = node.group; selected = id;
    render(); if (changed) fit();
    const position = view.nodes.find(n => n.id === id);
    if (position) $('topology-canvas').scrollTo({top: Math.max(0, position.y * scale - 180), left: Math.max(0, position.x * scale - 220)});
  }
  function renderInspector() {
    if (!selected) return;
    const n = nodeMap.get(selected), panel = $('topology-selection'); panel.replaceChildren();
    panel.append(make('p', 'COMPONENT INSPECTOR', 'eyebrow'), make('h3', n.label));
    const dl = make('dl');
    const source = n.source || {};
    for (const [key, value] of [['CCI path', n.id], ['모델 타입', n.moduletype], ['Subsystem', n.group],
      ['QEMU Instance', n.qemu_instance || '—'], ['Lua 소스', source.path ? `${source.path}:${source.line || '?'} (${source.accuracy || 'source'})` : '위치 미확인']]) {
      dl.append(make('dt', key), make('dd', value));
    }
    panel.append(dl);
    const params = make('details'); params.append(make('summary', 'CCI / Lua 설정값'), make('pre', JSON.stringify(n.parameters || {}, null, 2))); panel.append(params);
    const edges = graph.edges.filter(e => e.source === selected || e.target === selected);
    const links = make('details'); links.open = true; links.append(make('summary', `연결 포트 · ${edges.length}개 (외부 Subsystem 포함)`));
    for (const edge of edges) {
      const other = edge.source === selected ? edge.target : edge.source;
      const b = make('button', `${edge.kind} · ${edge.source_port || '?'} → ${edge.target_port || '?'}\n${other}`, 'topology-link');
      b.title = `${edge.direction || 'binding-order'} · Lua: ${JSON.stringify(edge.binding || {})}`;
      b.type = 'button'; b.addEventListener('click', () => selectNode(other)); links.append(b);
    }
    panel.append(links);
  }
  function renderIndex() {
    const nodes = filteredNodes(graph, $('topology-group').value, $('topology-search').value);
    const list = $('topology-components'); list.replaceChildren();
    list.append(make('p', `${nodes.length}개 일치${nodes.length > 80 ? ' · 처음 80개 표시, 검색으로 좁히세요' : ''}`, 'footnote'));
    nodes.slice(0, 80).forEach(n => {
      const b = make('button', n.label); b.type = 'button'; b.setAttribute('aria-pressed', String(n.id === selected));
      b.append(make('small', `${n.group} / ${n.moduletype}`)); b.addEventListener('click', () => selectNode(n.id)); list.append(b);
    });
  }
  function applyScale() {
    const svg = $('topology-canvas').querySelector('svg'); if (!svg) return;
    svg.setAttribute('width', Math.ceil(view.width * scale)); svg.setAttribute('height', Math.ceil(view.height * scale));
    $('topology-fit').textContent = `맞춤 · ${Math.round(scale * 100)}%`;
  }
  function fit() { if (!view) return; scale = Math.max(.2, Math.min(1, ($('topology-canvas').clientWidth - 8) / view.width)); applyScale(); }
  function render() {
    if (!graph) return;
    view = diagram(graph, $('topology-group').value, $('topology-signals').checked);
    const svg = svgEl('svg', {viewBox: `0 0 ${view.width} ${view.height}`, class: view.overview ? 'topo-overview' : 'topo-detail', 'aria-label': view.overview ? 'Subsystem 요약 연결도' : 'Subsystem 개별 컴포넌트 연결도'});
    const defs = svgEl('defs'), marker = svgEl('marker', {id: 'topo-arrow', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 5, markerHeight: 5, orient: 'auto-start-reverse'});
    marker.append(svgEl('path', {d: 'M 0 0 L 10 5 L 0 10 z', fill: '#94d6b9'})); defs.append(marker); svg.append(defs);
    view.groups.forEach(g => {
      svg.append(svgEl('rect', {x: g.x, y: g.y, width: g.width, height: g.height, rx: 4, class: 'topo-group-box'}));
      svg.append(svgEl('text', {x: g.x + 20, y: g.y + 29, class: 'topo-group-title'}, g.label));
      svg.append(svgEl('text', {x: g.x + 20, y: g.y + 49, class: 'topo-small'}, `${g.count} components · ${view.overview ? '그룹을 눌러 상세 연결도' : '개별 노드 클릭 → 포트와 설정'}`));
    });
    const positions = new Map(view.nodes.map(n => [n.id, n]));
    const adjacent = new Set([selected]);
    view.edges.forEach(e => { if (e.source === selected || e.target === selected) { adjacent.add(e.source); adjacent.add(e.target); } });
    view.edges.forEach(e => {
      const from = positions.get(e.source), to = positions.get(e.target);
      const forward = to.x > from.x, same = to.x === from.x;
      const x1 = from.x + (forward || same ? from.width : 0), y1 = from.y + from.height / 2;
      const x2 = to.x + (forward ? 0 : to.width), y2 = to.y + to.height / 2;
      const bend = same ? x1 + 18 : (x1 + x2) / 2;
      const active = selected && (e.source === selected || e.target === selected);
      const path = svgEl('path', {d: `M${x1},${y1} C${bend},${y1} ${bend},${y2} ${x2},${y2}`,
        class: `topo-edge ${e.kind} ${selected ? active ? 'active' : 'dim' : ''}`, 'marker-end': 'url(#topo-arrow)'});
      path.append(svgEl('title', {}, `${e.kind}: ${e.source} → ${e.target}${e.count > 1 ? ` (${e.count} bindings)` : ''}`)); svg.append(path);
    });
    view.nodes.forEach(n => {
      const g = svgEl('g', {class: `topo-node ${n.kind} ${selected === n.id ? 'selected' : selected && !adjacent.has(n.id) ? 'dim' : ''}`,
        role: 'button', tabindex: '0', 'aria-label': `${n.label} · ${n.moduletype}`, 'aria-pressed': String(selected === n.id), 'data-node': n.id});
      g.append(svgEl('rect', {x: n.x, y: n.y, width: n.width, height: n.height, rx: 3}));
      const label = n.label.replace(/^platform\./, '');
      g.append(svgEl('text', {x: n.x + 10, y: n.y + 22}, label.length > 28 ? label.slice(0, 26) + '…' : label));
      g.append(svgEl('text', {x: n.x + 10, y: n.y + 41, class: 'topo-small'}, n.moduletype.length > 32 ? n.moduletype.slice(0, 30) + '…' : n.moduletype));
      g.append(svgEl('title', {}, `${n.label}\n${n.moduletype}`));
      const activate = () => n.aggregate ? changeGroup(n.group) : selectNode(n.id);
      g.addEventListener('click', activate); g.addEventListener('keydown', e => { if (['Enter', ' '].includes(e.key)) { e.preventDefault(); activate(); } });
      svg.append(g);
    });
    $('topology-canvas').replaceChildren(svg); applyScale(); renderIndex(); renderInspector();
    const external = $('topology-group').value ? graph.edges.filter(e => nodeMap.get(e.source)?.group !== nodeMap.get(e.target)?.group &&
      [nodeMap.get(e.source)?.group, nodeMap.get(e.target)?.group].includes($('topology-group').value)).length : 0;
    $('topology-summary').textContent = `${graph.nodes.length} components / ${graph.edges.length} bindings · 표시 ${view.nodes.length} ${view.overview ? '그룹 블록' : '노드'} / ${view.edges.length} 연결${external ? ` · 외부 연결 ${external}개: 컴포넌트 상세에서 이동` : ''}`;
  }
  async function load() {
    if (loading) return; loading = true; $('topology-reload').disabled = true;
    $('topology-status').textContent = 'ANALYZING';
    try {
      const response = await fetch('/api/topology', {cache: 'no-store'}), data = await response.json();
      if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
      graph = data; selected = ''; nodeMap.clear(); graph.nodes.forEach(n => nodeMap.set(n.id, n));
      $('topology-group').replaceChildren(new Option('전체 연결도', ''));
      graph.groups.forEach(g => $('topology-group').append(new Option(g.label, g.id)));
      const details = $('topology-provenance'); details.replaceChildren(make('p', `${graph.profile} · ${graph.entrypoint}`, 'footnote'));
      details.append(make('p', `평가 환경: ${JSON.stringify(graph.environment || {})} · 화살표 방향은 포트 이름으로 추론하며 원본 bind는 상세 연결의 tooltip에 보존합니다. 소스 줄 번호는 정의 함수 범위입니다.`, 'footnote'));
      const warnings = make('ul'); [...(graph.limitations || []), ...(graph.warnings || [])].forEach(w => warnings.append(make('li', w))); details.append(warnings);
      const sources = make('ul'); (graph.sources || []).forEach(s => sources.append(make('li', `${s.path} · SHA256 ${s.sha256}`))); details.append(sources);
      $('topology-status').textContent = 'STATIC LUA';
      $('topology-selection').replaceChildren(make('p', '컴포넌트를 선택하면 모델·설정·소스와 연결 포트를 표시합니다.', 'footnote'));
      render(); fit();
    } catch (error) {
      graph = null; view = null; nodeMap.clear();
      $('topology-status').textContent = 'UNAVAILABLE';
      $('topology-canvas').replaceChildren(make('p', `연결도 분석 실패: ${error.message}`, 'empty'));
      $('topology-summary').textContent = '정적 구성을 확인할 수 없습니다. Lua 실행 도구와 소스 파일을 확인하세요.';
      $('topology-components').replaceChildren(); $('topology-selection').replaceChildren();
    } finally { loading = false; $('topology-reload').disabled = false; }
  }
  $('topology-group').addEventListener('change', e => changeGroup(e.target.value));
  $('topology-search').addEventListener('input', () => { if (graph) renderIndex(); });
  $('topology-signals').addEventListener('change', render);
  $('topology-reload').addEventListener('click', load);
  $('topology-fit').addEventListener('click', fit);
  $('topology-in').addEventListener('click', () => { scale = Math.min(2, scale * 1.25); applyScale(); });
  $('topology-out').addEventListener('click', () => { scale = Math.max(.15, scale / 1.25); applyScale(); });
  root.addEventListener('resize', fit);
  if (new URLSearchParams(location.search).get('view') !== 'guest') load();
})(typeof window !== 'undefined' ? window : globalThis);
