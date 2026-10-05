/* Saturn-V board observatory. API data is always rendered as text, never HTML. */
(function (root) {
  'use strict';
  const topo = typeof module !== 'undefined' && module.exports ? require('./topology.js') : root.QBoxTopology;
  const metrics = [
    ['cpu_pct', 'CPU TOTAL', '%'], ['main_pct', 'MAIN', '%'], ['vcpu_pct', 'vCPU', '%'],
    ['other_pct', 'OTHER', '%'], ['rss_mib', 'RSS', 'MiB'], ['domain_vcpu_pct.ap', 'AP vCPU', '%'],
    ['domain_vcpu_pct.rse', 'RSE vCPU', '%'], ['domain_vcpu_pct.si-cl0', 'SI0 vCPU', '%'],
    ['domain_vcpu_pct.si-cl1', 'SI1 vCPU', '%'], ['threads', 'THREADS', '개']
  ];
  const valueAt = (object, key) => key.split('.').reduce((value, part) => value?.[part], object);
  const finite = value => typeof value === 'number' && Number.isFinite(value);
  const upper = value => String(value || 'UNKNOWN').toUpperCase();
  const badSample = sample => !sample || ['STALE', 'DISABLED', 'WARMING_UP', 'BARRIER', 'GAP', 'UNAVAILABLE', 'ERROR'].includes(upper(sample.status)) || sample.barrier || sample.gap;
  function sampleValue(sample, key, runId) {
    const value = valueAt(sample, key);
    return !badSample(sample) && sample.run_id === runId && finite(value) ? value : null;
  }
  function sampleSeries(samples, key, runId) {
    return (samples || []).filter(s => !runId || s.run_id === runId).slice(-120).map(s => ({
      time: finite(s.sample_monotonic) ? s.sample_monotonic : null,
      value: !badSample(s) && finite(valueAt(s, key)) ? valueAt(s, key) : null
    }));
  }
  function chartPath(points, width = 300, height = 65) {
    const values = points.filter(p => finite(p.value) && finite(p.time));
    if (!values.length) return {path: '', max: null, from: null, to: null};
    const times = points.filter(p => finite(p.time)).map(p => p.time);
    const from = Math.min(...times), to = Math.max(...times), max = Math.max(1, ...values.map(p => p.value));
    let path = '', active = false;
    for (const p of points) {
      if (!finite(p.value) || !finite(p.time)) { active = false; continue; }
      const x = 3 + (to === from ? .5 : (p.time - from) / (to - from)) * (width - 6);
      const y = height - 3 - Math.max(0, p.value) / max * (height - 6);
      path += `${active ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)} `; active = true;
    }
    return {path: path.trim(), max, from, to};
  }
  function cleanLog(text) {
    return String(text || '').replace(/\x1b\][^\x07]*(?:\x07|\x1b\\)/g, '')
      .replace(/\x1b\[[0-?]*[ -/]*[@-~]/g, '').replace(/\r/g, '')
      .replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '');
  }
  function mergeLog(previous, chunk, runId, max = 200000) {
    if (chunk.run_id && chunk.run_id !== runId) return previous;
    const text = (chunk.gap ? '[로그 간격 발생: 회전 또는 이전 데이터 생략]\n' : '') + cleanLog(chunk.text);
    return {...previous, cursor: chunk.next_cursor ?? previous.cursor, text: (previous.text + text).slice(-max), gap: Boolean(chunk.gap)};
  }
  function normalizedGraph(graph) {
    const nodes = Array.isArray(graph?.nodes) ? graph.nodes.filter(n => typeof n.id === 'string') : [];
    const ids = new Set(nodes.map(n => n.id));
    const groups = new Map((graph?.groups || []).map(g => [g.id, {...g}]));
    nodes.forEach(n => { if (!groups.has(n.group || 'unclassified')) groups.set(n.group || 'unclassified', {id: n.group || 'unclassified', label: n.group || '미분류'}); });
    return {...graph, nodes: nodes.map(n => ({...n, group: n.group || 'unclassified'})),
      edges: (graph?.edges || []).filter(e => ids.has(e.source) && ids.has(e.target)), groups: [...groups.values()]};
  }
  function graphView(input, group = '', mode = 'board', kind = '') {
    const graph = normalizedGraph(input), source = new Map(graph.nodes.map(n => [n.id, n]));
    const overview = !group, mapping = new Map();
    let nodes, width, height, packageBox = null;
    if (overview) {
      nodes = graph.groups.filter(g => graph.nodes.some(n => n.group === g.id)).map(g => {
        const members = graph.nodes.filter(n => n.group === g.id);
        members.forEach(n => mapping.set(n.id, 'group:' + g.id));
        return {...g, id: 'group:' + g.id, group: g.id, kind: 'group', aggregate: true,
          members, label: g.label || g.id, moduletype: `${members.length}개 구성 요소`, width: 225, height: 80};
      });
      if (mode === 'board') {
        const side = n => n.group === 'board' ? 'right' : n.group === 'external' ? 'left' : ['vp', 'platform'].includes(n.group) ? 'host' : 'soc';
        const buckets = {left: [], right: [], soc: [], host: []};
        nodes.forEach(n => buckets[side(n)].push(n));
        const socHeight = Math.max(1, Math.ceil(buckets.soc.length / 2)) * 125;
        const bodyHeight = Math.max(socHeight, buckets.left.length * 125, buckets.right.length * 125);
        for (const [lane, members] of Object.entries(buckets)) members.forEach((n, i) => {
          n.x = lane === 'left' ? 25 : lane === 'right' ? 885 : lane === 'host' ? 40 + (i % 4) * 275 : 320 + (i % 2) * 270;
          n.y = lane === 'host' ? bodyHeight + 155 + Math.floor(i / 4) * 120 : 100 + (lane === 'soc' ? Math.floor(i / 2) : i) * 125;
        });
        packageBox = buckets.soc.length ? {x: 290, y: 55, width: 550, height: socHeight + 50} : null;
        width = 1140; height = bodyHeight + 190 + Math.ceil(buckets.host.length / 4) * 120;
      } else {
        nodes.forEach((n, i) => { n.x = 30 + (i % 3) * 300; n.y = 65 + Math.floor(i / 3) * 135; });
        width = 900; height = Math.ceil(nodes.length / 3) * 135 + 85;
      }
    } else {
      nodes = graph.nodes.filter(n => n.group === group).map((n, i) => {
        mapping.set(n.id, n.id);
        return {...n, x: 35 + (i % 3) * 285, y: 65 + Math.floor(i / 3) * 110, width: 245, height: 75};
      });
      width = 900; height = Math.ceil(nodes.length / 3) * 110 + 95;
    }
    const edges = new Map();
    graph.edges.filter(e => !kind || e.kind === kind).forEach((e, index) => {
      const a = mapping.get(e.source), b = mapping.get(e.target);
      if (!a || !b || overview && a === b) return;
      const id = overview ? `${a}|${b}|${e.kind}` : e.id || 'edge:' + index;
      if (!edges.has(id)) edges.set(id, {...e, id, source: a, target: b, members: []});
      edges.get(id).members.push(e);
    });
    return {nodes, edges: [...edges.values()], width, height: Math.max(300, height), overview, packageBox, source};
  }
  const activeStatuses = new Set(['QUEUED', 'RUNNING', 'STARTING', 'STOPPING', 'PENDING']);
  function busy(state) {
    const job = state?.active_job;
    return Boolean(job && (typeof job === 'string' || activeStatuses.has(upper(job.status))));
  }
  function jobPayload(descriptor, args, state, requestId, confirmed = false) {
    if (!state?.run_id || !state.csrf_token) throw new Error('현재 run과 인증 상태를 확인할 수 없습니다.');
    if (!descriptor || descriptor.available !== true) throw new Error(descriptor?.reason || '이 동작을 사용할 수 없습니다.');
    if (busy(state)) throw new Error('다른 작업이 실행 중입니다.');
    if (descriptor.disruptive && !confirmed) throw new Error('상태 변경 확인이 필요합니다.');
    return {action: descriptor.action || descriptor.id, args, run_id: state.run_id,
      request_id: requestId, confirm_disruptive: Boolean(confirmed)};
  }
  function scenarioAction(descriptor) {
    return ['fresh-run', 'scenario'].includes(descriptor.mode) ||
      /^(qvp\.|autosd\.)|(?:fault-recover|loss-recover|roundtrip)$/.test(descriptor.id || '');
  }
  function uartSource(source, vmcuEnabled) {
    if (source.enabled === false || source.id === 'tc397' && !vmcuEnabled) return false;
    return source.kind ? source.kind === 'uart' : ['ap-primary', 'ap-secure', 'rse', 'si-cl0', 'si-cl1', 'tc397'].includes(source.id);
  }
  const model = {metrics, sampleValue, sampleSeries, chartPath, cleanLog, mergeLog, normalizedGraph, graphView, busy, jobPayload, scenarioAction, uartSource};
  if (typeof module !== 'undefined' && module.exports) module.exports = model;
  if (typeof document === 'undefined') return;
  root.BoardDashboard = model;
  const $ = id => document.getElementById(id);
  if (!$('page-board')) return;
  const el = (tag, text, cls) => { const e = document.createElement(tag); if (text !== undefined) e.textContent = text; if (cls) e.className = cls; return e; };
  const svg = (tag, attrs, text) => { const e = document.createElementNS('http://www.w3.org/2000/svg', tag); Object.entries(attrs || {}).forEach(([k, v]) => e.setAttribute(k, v)); if (text !== undefined) e.textContent = text; return e; };
  let state = null, connected = false, graph = null, stats = null, mode = 'board', selected = '', group = '', scale = 1;
  let page = 'board', polling = false, posting = false, generation = 0, metaRun, metadataAt = 0, actionSignature = '', jobsSignature = '', graphRequest = 0;
  const logs = new Map();
  async function api(path, options = {}) {
    const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(path, {cache: 'no-store', credentials: 'same-origin', ...options, signal: controller.signal});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || data.message || `HTTP ${response.status}`);
      return data;
    } finally { clearTimeout(timeout); }
  }
  function notice(message) { $('error').textContent = message || ''; $('error').hidden = !message; }
  function badge(element, text) {
    element.textContent = text;
    const status = upper(text);
    element.className = 'badge ' + (['PASS', 'RUNNING', 'RUN', 'CONNECTED', 'READY'].includes(status) ? 'ok' : /FAIL|ERROR|FAULT/.test(status) ? 'bad' : /STALE|BLOCKED|UNKNOWN|UNAVAILABLE|DISABLED/.test(status) ? 'warn' : '');
  }
  function switchPage(next) {
    page = next;
    document.querySelectorAll('[data-page]').forEach(b => b.setAttribute('aria-current', b.dataset.page === next ? 'page' : 'false'));
    document.querySelectorAll('.page').forEach(p => { p.hidden = p.id !== 'page-' + next; });
    if (next === 'board') fit();
  }
  function facts(parent, rows) {
    const dl = el('dl', undefined, 'facts');
    rows.forEach(([key, value]) => dl.append(el('dt', key), el('dd', value === null || value === undefined ? '미확인' : typeof value === 'object' ? JSON.stringify(value) : String(value)))); parent.append(dl);
  }
  function renderStats() {
    const enabled = stats?.enabled === true, disabled = stats?.enabled === false, latest = stats?.latest;
    const stale = !connected || upper(stats?.status) === 'STALE';
    $('stats-state').textContent = !stats ? '통계 대기' : disabled ? 'DISABLED · 부하 수집 꺼짐 — 다음 실행에 --stats 사용' :
      `${stale ? 'STALE' : upper(stats.status)} · ${stats.interval_s ?? '—'}초 간격 · age ${finite(stats.age_s) ? stats.age_s.toFixed(1) + 's' : 'N/A'}`;
    $('stats-current').replaceChildren(); $('stats-charts').replaceChildren();
    metrics.forEach(([key, label, unit]) => {
      const value = sampleValue(latest, key, state?.run_id), available = enabled && !stale && finite(value);
      const item = el('div', undefined, 'metric' + (available ? '' : ' unavailable'));
      const dl = el('dl'), dd = el('dd', available ? key === 'threads' ? String(value) : value.toFixed(1) : 'N/A');
      if (available) dd.append(el('small', unit)); dl.append(el('dt', label), dd); item.append(dl); $('stats-current').append(item);
      if (key === 'threads') return;
      const points = sampleSeries(stats?.samples, key, state?.run_id), chart = chartPath(points);
      const figure = el('figure', undefined, 'chart'), caption = el('figcaption', label + (unit === '%' ? ' · host CPU %' : ' · RSS MiB'));
      caption.append(el('span', chart.max === null ? 'N/A' : `max ${chart.max.toFixed(1)}`));
      const plot = svg('svg', {viewBox: '0 0 300 65', role: 'img', 'aria-label': `${label}: 최근 ${points.length}개 표본. 결측값은 간격으로 표시.`});
      plot.append(svg('path', {class: 'axis', d: 'M0 63H300'}), svg('path', {d: chart.path}));
      figure.append(caption, plot, el('p', chart.from === null ? '관측값 없음' : `host monotonic ${chart.from.toFixed(1)} → ${chart.to.toFixed(1)}s · ${points.length}/120`));
      $('stats-charts').append(figure);
    });
    renderInspectorObservation();
  }
  function selectNode(id) {
    const node = graph?.nodes.find(n => n.id === id); if (!node) return;
    selected = id; group = node.group; $('graph-group').value = group; renderGraph(); fit(); renderInspector(node);
  }
  function renderInspector(node) {
    const panel = $('inspector'); panel.replaceChildren(el('p', 'COMPONENT INSPECTOR', 'eyebrow'), el('h3', node.label || node.id));
    facts(panel, [['CCI ID', node.id], ['모델', node.moduletype], ['그룹', node.group], ['출처 구분', node.provenance || 'lua-configured'],
      ['QEMU instance', node.qemu_instance], ['소스 위치', node.source?.path ? `${node.source.path}:${node.source.line ?? '?'}` : null],
      ['소스 SHA', node.source?.sha256], ['관측', node.observation || node.runtime || 'runtime 관측 없음']]);
    const observation = el('div'); observation.id = 'inspector-observation'; panel.append(observation);
    renderInspectorObservation();
    panel.append(el('p', '주소는 router decode 공간이며 AP guest PA로 자동 변환하지 않습니다.'));
    topo.memoryRegions(node).forEach(region => { const d = el('details'); d.append(el('summary', `${region.port} · ${region.address}`)); facts(d, Object.entries(region)); panel.append(d); });
    const detail = el('details'); detail.append(el('summary', '원본 구성값'), el('pre', JSON.stringify(node.parameters || {}, null, 2))); panel.append(detail);
    const connectedEdges = graph.edges.filter(e => e.source === node.id || e.target === node.id);
    panel.append(el('h3', `원본 연결 ${connectedEdges.length}개`));
    connectedEdges.forEach(edge => {
      const other = edge.source === node.id ? edge.target : edge.source;
      const button = el('button', `${edge.kind} · ${edge.source_port || '?'} → ${edge.target_port || '?'}\n${other}`);
      button.title = JSON.stringify({direction: edge.direction, binding: edge.binding, connection: edge.connection});
      button.addEventListener('click', () => selectNode(other)); panel.append(button);
    });
    const uart = el('button', 'UART 관측으로 이동'); uart.addEventListener('click', () => switchPage('uart')); panel.append(uart);
  }
  function renderInspectorObservation() {
    const panel = $('inspector-observation'), node = graph?.nodes.find(n => n.id === selected);
    if (!panel || !node) return;
    panel.replaceChildren();
    const domainId = ({ap_compute: 'ap', si_cl0: 'si-cl0', si_cl1: 'si-cl1', rse: 'rse'})[node.group] || (node.id === 'external.tc397' ? 'tc397' : null);
    const domain = state?.domains?.find(d => d.id === domainId);
    if (domain) facts(panel, [['도메인 부팅 관측', connected ? domain.status : 'STALE'], ['관측 출처', domain.source]]);
    if (domainId && domainId !== 'tc397') facts(panel, [['domain vCPU host CPU %', connected && stats?.enabled === true && upper(stats?.status) !== 'STALE' ? sampleValue(stats?.latest, 'domain_vcpu_pct.' + domainId, state?.run_id) : null], ['통계 상태', connected ? stats?.status : 'STALE']]);
  }
  function renderEdge(edge) {
    $('inspector').replaceChildren(el('p', 'BINDING INSPECTOR', 'eyebrow'), el('h3', `${edge.kind} · ${edge.members.length}개 원본 연결`));
    edge.members.forEach(member => facts($('inspector'), Object.entries(member)));
  }
  function fit() {
    if (!graph) return;
    const width = graphView(graph, group, mode, $('graph-links').value).width;
    scale = Math.max(.45, Math.min(1, ($('graph').clientWidth - 2) / width)); applyScale();
  }
  function applyScale() {
    const drawing = $('graph').querySelector('svg'); if (!drawing) return;
    const box = drawing.getAttribute('viewBox').split(' ').map(Number);
    drawing.setAttribute('width', Math.ceil(box[2] * scale)); drawing.setAttribute('height', Math.ceil(box[3] * scale));
    $('zoom-fit').textContent = `맞춤 ${Math.round(scale * 100)}%`;
  }
  function renderIndex() {
    $('component-index').replaceChildren(); if (!graph) return;
    const nodes = topo.filteredNodes(graph, group, $('graph-search').value);
    $('component-index').append(el('p', `${nodes.length}개 일치${nodes.length > 100 ? ' · 처음 100개, 검색으로 좁히세요' : ''}`));
    nodes.slice(0, 100).forEach(n => { const b = el('button', n.label || n.id); b.title = n.id; b.setAttribute('aria-pressed', String(n.id === selected)); b.addEventListener('click', () => selectNode(n.id)); $('component-index').append(b); });
  }
  function renderGraph() {
    if (!graph) return;
    const view = graphView(graph, group, mode, $('graph-links').value), drawing = svg('svg', {viewBox: `0 0 ${view.width} ${view.height}`, role: 'group', 'aria-label': '실제 구성에서 생성한 ' + (mode === 'board' ? '논리 보드' : '블록 연결도')});
    if (view.packageBox && mode === 'board') {
      drawing.append(svg('rect', {...view.packageBox, rx: 9, class: 'board-package'}), svg('text', {x: view.packageBox.x + 18, y: 78, class: 'board-label'}, 'APOLLO SoC / LOGICAL DOMAINS'));
    }
    const positions = new Map(view.nodes.map(n => [n.id, n]));
    view.edges.forEach(edge => {
      const a = positions.get(edge.source), b = positions.get(edge.target), ax = a.x + a.width / 2, ay = a.y + a.height / 2, bx = b.x + b.width / 2, by = b.y + b.height / 2;
      const path = svg('path', {d: mode === 'board' ? `M${ax} ${ay}H${(ax + bx) / 2}V${by}H${bx}` : `M${ax} ${ay}L${bx} ${by}`,
        class: 'edge' + (edge.connection === 'UNCONFIRMED' ? ' unconfirmed' : ''), role: 'button', tabindex: 0,
        'aria-label': `${edge.kind}: ${edge.source} → ${edge.target}, ${edge.members.length}개 연결`});
      path.append(svg('title', {}, `${edge.kind} · ${edge.members.length}개 실제 binding`));
      path.addEventListener('click', () => renderEdge(edge)); path.addEventListener('keydown', event => { if (['Enter', ' '].includes(event.key)) { event.preventDefault(); renderEdge(edge); } }); drawing.append(path);
    });
    view.nodes.forEach(node => {
      const chip = svg('g', {class: `chip ${node.aggregate ? 'aggregate' : ''} ${selected === node.id ? 'selected' : ''}`, tabindex: 0, role: 'button', 'aria-label': `${node.label} · ${node.moduletype}`, 'aria-pressed': String(selected === node.id)});
      if (mode === 'board') for (let i = 1; i <= 7; i++) { const x = node.x + i * node.width / 8; chip.append(svg('path', {class: 'chip-pin', d: `M${x} ${node.y - 5}v5 M${x} ${node.y + node.height}v5`})); }
      chip.append(svg('rect', {x: node.x, y: node.y, width: node.width, height: node.height, rx: mode === 'board' ? 3 : 7}));
      const label = String(node.label || node.id), type = String(node.moduletype || 'model 미확인');
      chip.append(svg('text', {x: node.x + 13, y: node.y + 29}, label.length > 29 ? label.slice(0, 27) + '…' : label), svg('text', {x: node.x + 13, y: node.y + 49, class: 'chip-sub'}, type.slice(0, 35)));
      chip.append(svg('text', {x: node.x + 13, y: node.y + 65, class: 'chip-sub'}, node.aggregate ? 'ENTER → 구성 요소 펼치기' : node.provenance || 'lua-configured'));
      const activate = () => { if (node.aggregate) { group = node.group; $('graph-group').value = group; renderGraph(); fit(); } else selectNode(node.id); };
      chip.addEventListener('click', activate); chip.addEventListener('keydown', event => { if (['Enter', ' '].includes(event.key)) { event.preventDefault(); activate(); } }); drawing.append(chip);
    });
    $('graph').classList.toggle('block', mode === 'block'); $('graph').replaceChildren(drawing); applyScale(); renderIndex();
    $('graph-count').textContent = `${graph.nodes.length} components / ${graph.edges.length} bindings · ${view.nodes.length}개 표시`;
    $('view-board').setAttribute('aria-pressed', String(mode === 'board')); $('view-block').setAttribute('aria-pressed', String(mode === 'block'));
  }
  async function loadTopology(token) {
    const serial = ++graphRequest;
    try {
      const data = await api('/api/board/topology'); if (token !== generation || serial !== graphRequest) return;
      graph = normalizedGraph(data);
      if (selected && !graph.nodes.some(n => n.id === selected)) selected = '';
      if (!graph.groups.some(g => g.id === group)) group = '';
      $('graph-group').replaceChildren(new Option('전체 보드', '')); graph.groups.forEach(g => $('graph-group').append(new Option(g.label || g.id, g.id))); $('graph-group').value = group;
      const kind = $('graph-links').value; $('graph-links').replaceChildren(new Option('모든 연결', ''));
      [...new Set(graph.edges.map(e => e.kind))].sort().forEach(k => $('graph-links').append(new Option(k, k))); $('graph-links').value = kind;
      $('provenance').replaceChildren(); facts($('provenance'), [['프로파일', graph.profile], ['Entry point', graph.entrypoint], ['증거 수준', graph.evidence], ['Frozen', graph.frozen], ['Snapshot', graph.snapshot]]);
      [...(graph.limitations || []), ...(graph.warnings || [])].forEach(w => $('provenance').append(el('p', String(w))));
      const sources = el('details'); sources.append(el('summary', '소스 및 외부 attachment'), el('pre', JSON.stringify({sources: graph.sources, attachments: graph.attachments}, null, 2))); $('provenance').append(sources);
      const exportLink = el('a', '현재 구성의 편집 가능한 Draw.io 다운로드'); exportLink.href = '/api/topology/drawio'; $('provenance').append(exportLink);
      renderGraph(); fit(); if (selected) renderInspector(graph.nodes.find(n => n.id === selected));
    } catch (error) { if (token !== generation || serial !== graphRequest) return; graph = null; $('graph').replaceChildren(el('p', '구성 분석 실패: ' + error.message, 'empty')); $('component-index').replaceChildren(); $('inspector').replaceChildren(el('p', '현재 구성 미확인')); $('graph-count').textContent = 'UNAVAILABLE'; $('provenance').replaceChildren(el('p', '현재 구성의 출처를 확인할 수 없습니다.')); }
  }
  function logSources(sources) {
    $('uart-grid').replaceChildren(); $('aux-grid').replaceChildren(); logs.clear();
    for (const source of sources || []) {
      if (source.enabled === false || source.id === 'tc397' && !state.vmcu) continue;
      const extra = !uartSource(source, state.vmcu);
      const box = el('article', undefined, 'uart'), header = el('header'), follow = el('button', '자동 스크롤 켜짐'), pre = el('pre'), status = el('div', source.available ? '대기 · 조용한 콘솔도 정상일 수 있습니다' : 'MISSING · 로그 파일 없음', 'log-state');
      header.append(el('h3', source.label || source.id), follow); box.append(header, status, pre); $(extra ? 'aux-grid' : 'uart-grid').append(box);
      pre.tabIndex = 0; pre.setAttribute('aria-label', (source.label || source.id) + ' UART 로그');
      const entry = {source, extra, cursor: '', text: '', pre, status, follow, auto: true}; logs.set(source.id, entry);
      pre.addEventListener('scroll', () => { if (pre.scrollHeight - pre.clientHeight - pre.scrollTop > 30) { entry.auto = false; follow.textContent = '자동 스크롤 재개'; } });
      follow.addEventListener('click', () => { entry.auto = !entry.auto; follow.textContent = entry.auto ? '자동 스크롤 켜짐' : '자동 스크롤 재개'; if (entry.auto) pre.scrollTop = pre.scrollHeight; });
    }
    if (!sources?.length) $('uart-grid').append(el('p', '사용 가능한 UART 소스가 없습니다.', 'empty'));
  }
  function renderLog(entry) {
    const query = $('log-filter').value.toLowerCase();
    entry.pre.textContent = query ? entry.text.split('\n').filter(line => line.toLowerCase().includes(query)).join('\n') : entry.text;
    const selection = document.getSelection();
    if (selection && !selection.isCollapsed && entry.pre.contains(selection.anchorNode)) entry.auto = false;
    if (entry.auto) entry.pre.scrollTop = entry.pre.scrollHeight;
  }
  async function pollLogs(token) {
    await Promise.allSettled([...logs.entries()].map(async ([id, entry]) => {
      try {
        if (entry.extra && !$('extra-logs').open) return;
        const chunk = await api(`/api/board/logs/${encodeURIComponent(id)}?cursor=${encodeURIComponent(entry.cursor)}`);
        if (token !== generation || logs.get(id) !== entry) return;
        Object.assign(entry, mergeLog(entry, chunk, state.run_id)); renderLog(entry);
        entry.status.textContent = chunk.gap ? 'GAP · 로그가 회전하거나 일부가 생략되었습니다' : '수신 확인 · ' + new Date().toLocaleTimeString('ko-KR');
      } catch (error) { if (token === generation) entry.status.textContent = 'UNAVAILABLE · ' + error.message; }
    }));
  }
  function schemaFields(schema) {
    if (Array.isArray(schema)) return schema.map(field => [field.name || field.id, field]);
    return Object.entries(schema?.properties || schema || {}).filter(([key]) => !['required', 'type', 'additionalProperties'].includes(key));
  }
  function renderActions(target, descriptors) {
    const signature = JSON.stringify(descriptors || []);
    if (target.dataset.signature === signature) { updateLocks(); return; }
    target.dataset.signature = signature; target.replaceChildren();
    (descriptors || []).forEach(descriptor => {
      const card = el('form', undefined, 'action-card'); card.append(el('p', descriptor.mode || 'TYPED ACTION', 'eyebrow'), el('h3', descriptor.title || descriptor.id), el('p', descriptor.description || ''));
      const fields = [];
      for (const [name, config] of schemaFields(descriptor.args_schema)) {
        const label = el('label', config.title || name); let input;
        if (config.enum) { input = el('select'); config.enum.forEach((v, i) => input.append(new Option(config.enumNames?.[i] || String(v), String(v)))); }
        else { input = el('input'); input.type = config.type === 'boolean' ? 'checkbox' : ['integer', 'number'].includes(config.type) ? 'number' : 'text'; }
        if ((config.minimum ?? config.min) !== undefined) input.min = config.minimum ?? config.min; if ((config.maximum ?? config.max) !== undefined) input.max = config.maximum ?? config.max;
        if (config.type === 'integer') input.step = '1'; if (config.default !== undefined) { if (input.type === 'checkbox') input.checked = config.default; else input.value = config.default; }
        input.required = descriptor.args_schema?.required?.includes(name) || config.required === true; input.name = name; label.append(input); card.append(label); fields.push({name, config, input});
      }
      if (descriptor.available !== true) card.append(el('p', descriptor.reason || '현재 실행에서 지원되지 않습니다.', 'reason'));
      if (descriptor.disruptive) card.append(el('p', '상태 변경 · 실행 전 확인', 'reason'));
      const button = el('button', descriptor.disruptive ? '확인 후 실행' : '실행'); button.type = 'submit'; button.dataset.mutation = 'true'; button.dataset.available = String(descriptor.available === true); card.append(button);
      card.addEventListener('submit', event => { event.preventDefault(); const args = {}; fields.forEach(({name, config, input}) => { if (input.type === 'checkbox') args[name] = input.checked; else if (input.value !== '') args[name] = ['integer', 'number'].includes(config.type) ? Number(input.value) : input.value; }); submitAction(descriptor, args); });
      target.append(card);
    });
    if (!descriptors?.length) target.append(el('p', '현재 프로파일에서 제공하는 동작이 없습니다.', 'empty'));
    updateLocks();
  }
  function updateLocks() {
    document.querySelectorAll('[data-mutation]').forEach(b => { b.disabled = !connected || posting || busy(state) || b.dataset.available !== 'true'; });
  }
  async function confirmAction(descriptor, run) {
    $('confirm-description').textContent = `${descriptor.title || descriptor.id} · ${descriptor.description || ''}`; $('confirm-run').textContent = 'run ' + run;
    const dialog = $('confirm-dialog'); dialog.returnValue = ''; dialog.showModal();
    return new Promise(resolve => dialog.addEventListener('close', () => resolve(dialog.returnValue === 'execute'), {once: true}));
  }
  async function submitAction(descriptor, args) {
    if (posting || !connected) return;
    const run = state.run_id;
    posting = true; updateLocks();
    try {
      const confirmed = descriptor.disruptive ? await confirmAction(descriptor, run) : false;
      if (descriptor.disruptive && !confirmed) return;
      if (run !== state.run_id || !connected) throw new Error('실행 대상 run이 변경됐습니다. 상태를 새로 확인하세요.');
      const requestId = root.crypto.randomUUID ? root.crypto.randomUUID() :
        Array.from(root.crypto.getRandomValues(new Uint8Array(16)), value => value.toString(16).padStart(2, '0')).join('');
      const body = jobPayload(descriptor, args, state, requestId, confirmed);
      const result = await api('/api/jobs', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': state.csrf_token}, body: JSON.stringify(body)});
      if (run === state.run_id) { state.active_job = result.job; renderJobs(); notice(''); }
    } catch (error) { notice(`요청 결과: ${error.message} · 상태가 불명확하면 작업 이력을 확인하세요. 자동 재시도하지 않습니다.`); }
    finally { posting = false; updateLocks(); }
  }
  function renderJobs() {
    const job = typeof state?.active_job === 'object' ? state.active_job : (state?.jobs || []).find(j => j.id === state.active_job);
    badge($('job-state'), job?.status || 'IDLE'); $('active-job').textContent = job ? `${job.title || job.action || job.id} · ${job.message || job.error || '진행 정보는 작업 이력에서 확인하세요.'}` : '진행 중인 작업 없음';
    const signature = JSON.stringify(state?.jobs || []);
    if (signature === jobsSignature) { updateLocks(); return; }
    jobsSignature = signature; $('jobs').replaceChildren();
    for (const item of (state?.jobs || []).slice().reverse()) {
      const row = el('article', undefined, 'job-row'), status = el('span'); badge(status, item.status);
      row.append(el('strong', item.title || item.action || item.id), status);
      const details = el('details'), output = el('pre', JSON.stringify(item, null, 2));
      details.append(el('summary', '결과 · 증거 상세'), output);
      details.addEventListener('toggle', async () => {
        if (!details.open) return;
        const token = generation;
        try { const data = await api('/api/board/jobs/' + encodeURIComponent(item.id)); if (token === generation) output.textContent = JSON.stringify(data.job || data, null, 2); }
        catch (error) { if (token === generation) output.textContent += '\n조회 실패: ' + error.message; }
      });
      row.append(details); $('jobs').append(row);
    }
    updateLocks();
  }
  async function loadMetadata(token, resetLogs = true) {
    const results = await Promise.allSettled([resetLogs ? api('/api/board/logs') : Promise.resolve(null), api('/api/board/scenarios'), api('/api/board/evidence')]);
    if (token !== generation) return;
    if (resetLogs) { if (results[0].status === 'fulfilled') logSources(results[0].value.sources); else $('uart-grid').replaceChildren(el('p', 'UART 목록 조회 실패', 'empty')); }
    if (results[1].status === 'fulfilled') renderActions($('scenarios'), (results[1].value.scenarios || []).filter(scenarioAction)); else $('scenarios').replaceChildren(el('p', '시나리오 조회 실패', 'empty'));
    $('evidence').replaceChildren();
    if (results[2].status === 'fulfilled') {
      const files = results[2].value.files || [];
      files.forEach(file => { const item = el('div', undefined, 'evidence-item'); item.append(el('span', file.label || file.id)); if (file.available !== false) { const link = el('a', '원본 다운로드'); link.href = '/api/board/evidence/' + encodeURIComponent(file.id); item.append(link); } else item.append(el('span', 'MISSING', 'badge')); $('evidence').append(item); });
      if (!files.length) $('evidence').append(el('p', '아직 생성된 증거 파일이 없습니다.', 'empty'));
    } else $('evidence').append(el('p', '증거 목록 조회 실패', 'empty'));
  }
  async function refresh(force = false) {
    if (polling) return; polling = true;
    try {
      const next = await api('/api/board');
      const changed = next.run_id !== state?.run_id;
      state = next; connected = true; badge($('connection-state'), 'CONNECTED'); badge($('lifecycle'), typeof state.lifecycle === 'object' ? state.lifecycle.status : state.lifecycle);
      $('profile').textContent = `${state.bsp ? 'BSP' : 'Product'} · vMCU ${state.vmcu ? 'ON' : 'OFF'} · ${state.image || '이미지 미확인'} · T+${finite(state.elapsed_s) ? Math.floor(state.elapsed_s) : '—'}s`; $('run-id').textContent = 'run ' + (state.run_id || '—'); $('updated').textContent = '수신 ' + new Date().toLocaleTimeString('ko-KR');
      if (state.error) notice(state.error);
      $('domain-status').replaceChildren();
      $('domain-status').append(el('span', '도메인 부팅 관측', 'footnote'));
      for (const domain of state.domains || []) {
        const chip = el('span', undefined, 'domain-chip'), value = el('span'); badge(value, domain.status || 'UNKNOWN');
        chip.append(el('strong', domain.label || domain.id), value);
        chip.title = [domain.source, finite(domain.age_s) ? `age ${domain.age_s}s` : ''].filter(Boolean).join(' · ');
        $('domain-status').append(chip);
      }
      if (state.vmcu) {
        const health = state.vmcu_status || {}, chip = el('span', undefined, 'domain-chip'), value = el('span');
        value.id = 'si-observation';
        badge(value, finite(health.observation_age_s) && health.observation_age_s > 15 ? 'STALE' : health.state || 'UNKNOWN');
        chip.append(el('strong', '최근 SI 조회'), value);
        chip.title = `fault=${health.fault ?? '미확인'} · firmware age=${health.age_ms ?? '미확인'}ms · 관측 age=${health.observation_age_s ?? '미확인'}s`;
        $('domain-status').append(chip);
      }
      $('vmcu-state').textContent = JSON.stringify(state.vmcu_status || {status: state.vmcu ? 'UNKNOWN' : 'DISABLED'}, null, 2);
      if (changed) { generation++; graph = null; stats = null; logs.clear(); selected = ''; group = ''; $('graph').replaceChildren(el('p', '새 run의 구성 확인 중', 'empty')); $('uart-grid').replaceChildren(); $('aux-grid').replaceChildren(); $('inspector').replaceChildren(el('p', '부품을 선택하세요.')); }
      const token = generation, descriptors = Array.isArray(state.capabilities) ? state.capabilities : [];
      const signature = JSON.stringify(descriptors);
      if (signature !== actionSignature) { actionSignature = signature; renderActions($('controls'), descriptors.filter(d => !scenarioAction(d))); }
      renderJobs();
      const tasks = [api('/api/board/stats').then(data => { if (token === generation) { stats = data; renderStats(); } }).catch(() => { if (token === generation) { stats = {...stats, status: 'STALE'}; renderStats(); } })];
      if (force || changed || metaRun !== state.run_id) { metaRun = state.run_id; metadataAt = Date.now(); tasks.push(loadTopology(token), loadMetadata(token)); }
      else if (Date.now() - metadataAt >= 10000) { metadataAt = Date.now(); tasks.push(loadMetadata(token, false)); if (!graph || !graph.frozen) tasks.push(loadTopology(token)); }
      await Promise.allSettled(tasks); await pollLogs(token);
    } catch (error) { connected = false; badge($('connection-state'), 'STALE'); if ($('si-observation')) badge($('si-observation'), 'STALE'); $('updated').textContent = '연결 실패 · 표시값 갱신 중단'; notice(error.message); renderStats(); updateLocks(); }
    finally { polling = false; }
  }
  document.querySelectorAll('[data-page]').forEach(button => button.addEventListener('click', () => switchPage(button.dataset.page)));
  $('refresh').addEventListener('click', () => refresh(true));
  $('stats-toggle').addEventListener('click', () => { const expanded = $('stats-charts').hidden; $('stats-charts').hidden = !expanded; $('stats-toggle').setAttribute('aria-expanded', String(expanded)); $('stats-toggle').textContent = expanded ? '추이 접기' : '추이 펼치기'; });
  $('graph-group').addEventListener('change', event => { group = event.target.value; renderGraph(); fit(); });
  $('graph-search').addEventListener('input', renderIndex); $('graph-links').addEventListener('change', renderGraph);
  ['board', 'block'].forEach(value => $('view-' + value).addEventListener('click', () => { mode = value; renderGraph(); fit(); }));
  $('zoom-fit').addEventListener('click', fit); $('zoom-in').addEventListener('click', () => { scale = Math.min(2, scale * 1.25); applyScale(); }); $('zoom-out').addEventListener('click', () => { scale = Math.max(.3, scale / 1.25); applyScale(); });
  $('log-filter').addEventListener('input', () => logs.forEach(renderLog)); root.addEventListener('resize', () => { if (page === 'board') fit(); });
  refresh(true); setInterval(refresh, 2000);
})(typeof window !== 'undefined' ? window : globalThis);
