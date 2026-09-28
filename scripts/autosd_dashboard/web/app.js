'use strict';

const $ = (id) => document.getElementById(id);
const el = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = String(text);
  if (className) node.className = className;
  return node;
};
const finite = (v) => typeof v === 'number' && Number.isFinite(v);
const fmt = (v, digits = 1) => finite(v) ? v.toLocaleString('ko-KR', {maximumFractionDigits: digits}) : '—';
const badge = (status) => el('span', status || 'UNKNOWN', `badge ${String(status || 'unknown').toLowerCase().replace(/[^a-z_]/g, '')}`);
const svgEl = (tag, attrs = {}, text) => {
  const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
  Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
  if (text !== undefined) node.textContent = text;
  return node;
};
let state = null;
let selectedEvidence = '';
let evidenceInitialized = false;
const seenCompletedMeasurements = new Set();
let selectedJob = '';
let pending = false;
let refreshing = false;
let actionKey = '';
let lastSample = '';
let lastBoot = '';
const cpuHistory = new Map();
const runningStatuses = ['RUNNING', 'QUEUED', 'STARTING'];
const statusLabels = {RUNNING: '실행 중', QUEUED: '대기 중', STARTING: '시작 중',
  PASS: '완료', FAIL: '실패', TIMEOUT: '시간 초과', EXCEEDED: '완료 · 지연 기준 초과',
  UNSUPPORTED: '지원되지 않음', BOOT_PROCESS_COMPLETED: 'VM 프로세스 종료',
  BLOCKED: '선행 상태 확인 필요',
  ORPHANED_NOT_MANAGED: '서버 재시작 · 관리되지 않음'};
const progressLog = new Map();
const jobScroll = new Map();
let displayedJob = '';
let logSession;
let guestLogRequest = 0;
let guestSource = 'uart';
let inspectorRun;
let inspectorRequest = 0;

function logGroups(jobs, session) {
  const sorted = [...jobs].sort((a, b) => Date.parse(b.started_at) - Date.parse(a.started_at));
  return {
    current: sorted.filter((job) => Boolean(session) && job.log_session === session),
    history: sorted.filter((job) => !session || job.log_session !== session),
  };
}

function openJob(id, scroll = false) {
  selectedJob = id;
  renderJobs();
  if (scroll) {
    $('logs').scrollIntoView({block: 'start'});
    $('job-select').focus({preventScroll: true});
  }
}

function elapsed(job) {
  const seconds = Math.max(0, Math.floor(((job.finished_at ? Date.parse(job.finished_at) : Date.now()) - Date.parse(job.started_at)) / 1000));
  return Number.isFinite(seconds) ? `${Math.floor(seconds / 60)}분 ${seconds % 60}초` : '시간 확인 중';
}

function progressText(job) {
  if (job.phase) return job.phase;
  if (!runningStatuses.includes(job.status)) return job.error || (Array.isArray(job.result) && job.result.at(-1)?.reason) || (job.result?.latency_status ? `지연 판정: ${job.result.latency_status}` : `종료 코드 ${job.returncode ?? '—'}`);
  if (job.action === 'boot') {
    if (state.vm?.paused) return 'VM 일시정지 · Resume 대기';
    if (state.monitoring?.status === 'PAUSED_DURING_MEASUREMENT') return 'VM 실행 유지 중 · 시나리오 간섭 방지를 위해 계측 일시정지';
    return state.monitoring?.status === 'ONLINE' ? 'guest 연결됨 · VM 실행 유지 중' : 'VM 실행 중 · guest 연결 대기';
  }
  const raw = progressLog.get(job.id) || '';
  const family = job.action.startsWith('mixed-criticality') ? 'mixed-criticality' : job.action.split('-')[0];
  if (['automotive', 'rt', 'mixed-criticality', 'watchdog'].includes(family)) {
    const completed = [];
    let observedPhase = '';
    for (const line of raw.split('\n')) {
      try {
        const item = JSON.parse(line);
        if (!/^(?:[SR]0[1-6]|MC0[1-3]|WD0[1-4])/.test(item.id || '')) continue;
        if (item.event === 'progress' && item.message) observedPhase = `${item.id} · ${item.message}`;
        if (['PASS', 'FAIL', 'BLOCKED', 'UNSUPPORTED', 'EXCEEDED', 'WITHIN_OBSERVED_THRESHOLD', 'DETECTION_PASS', 'ERROR'].includes(item.status || item.latency_status)) completed.push(item);
      } catch (_) { /* non-JSON log */ }
    }
    const unique = [...new Map(completed.map((item) => [item.id, item])).values()];
    const total = job.action !== family ? 1 : ['mixed-criticality', 'watchdog'].includes(family) ? 3 : 6;
    if (unique.length) return `${unique.length}/${total} 단계 결과 수신 · ${unique.at(-1).id}: ${unique.at(-1).status || unique.at(-1).latency_status}${unique.length === total ? ' · 증거 회수 중' : ''}`;
    if (observedPhase) return observedPhase;
  }
  const phases = {'mixed-criticality': 'guest 자원 배치·ADAS 연속성 관측 중', watchdog: 'watchdog 검출·복구 증거 수집 중', health: 'guest 접속·정상 상태 검사 중', automotive: 'guest 접속·시나리오 결과 대기',
    rt: '측정·검증 및 증거 회수 중', timerlat: 'timerlat 수집·설정 복원 및 증거 회수 중',
    osnoise: 'osnoise 수집·설정 복원 및 증거 회수 중', shutdown: 'guest poweroff 및 프로세스 종료 확인 중',
    reboot: 'guest OS 재부팅 · 새 boot ID 및 SSH 연결 확인 중',
    pause: 'QEMU 실행 정지 상태 확인 중', resume: 'QEMU 실행 재개 상태 확인 중'};
  return (job.action !== family ? `${job.action.split('-').at(-1).toUpperCase()} · ` : '') + (phases[family] || '실행 결과 대기 중');
}

function featureJob(item) {
  const jobs = (state.jobs || []).filter((entry) => state.feature_session &&
    entry.feature_session === state.feature_session &&
    (entry.action === item.action || (item.children || []).some((child) => child.action === entry.action)))
    .sort((a, b) => Date.parse(b.started_at) - Date.parse(a.started_at));
  if (item.action === 'boot') return state.feature_boot;
  if (item.action === 'health') return jobs[0] || state.feature_health;
  return jobs[0];
}

function renderActionProgress() {
  for (const item of (state.catalog || []).flatMap((parent) => [parent, ...(parent.children || [])])) {
    const target = document.querySelector(`[data-progress="${item.action}"]`);
    if (!target) continue;
    const job = featureJob(item);
    const restoreFocus = target.contains(document.activeElement);
    target.replaceChildren();
    target.classList.toggle('is-running', Boolean(job && runningStatuses.includes(job.status)));
    if (!job) { target.append(el('span', item.enabled ? '준비됨 · 실행 이력 없음' : '대기 · VM/다른 작업 상태 확인', 'footnote')); continue; }
    const line = el('div', null, 'feature-status-line');
    line.append(badge(job.status), el('span', `${job.action} · ${statusLabels[job.status] || job.status} · ${elapsed(job)}`));
    const logButton = el('button', '로그 보기', 'feature-log-button');
    logButton.type = 'button';
    logButton.setAttribute('aria-label', `${item.title} 로그 보기`);
    logButton.addEventListener('click', () => openJob(job.id, true));
    target.append(line, el('p', progressText(job), 'feature-phase'));
    if (job.id && job.log_url) {
      target.append(logButton);
      if (restoreFocus) logButton.focus({preventScroll: true});
    }
    if (measurementJob(job) && job.result && !runningStatuses.includes(job.status)) {
      const resultButton = el('button', '결과 표·그래프', 'feature-log-button');
      resultButton.type = 'button';
      resultButton.setAttribute('aria-label', `${item.title} 결과 표·그래프`);
      resultButton.addEventListener('click', () => {
        selectedEvidence = `job:${job.id}`;
        renderEvidence();
        $('results').scrollIntoView({block: 'start'});
        $('evidence-select').focus({preventScroll: true});
      });
      target.append(resultButton);
    }
  }
}

function notice(message) {
  $('notice').textContent = message;
  $('notice').hidden = !message;
}

async function api(path, options = {}) {
  const response = await fetch(path, {cache: 'no-store', ...options});
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return payload;
}

function updateOptions(select, entries, selected, emptyLabel) {
  const signature = JSON.stringify(entries);
  if (select.dataset.signature !== signature) {
    select.replaceChildren();
    if (!entries.length) select.append(new Option(emptyLabel, ''));
    entries.forEach(([value, label]) => select.append(new Option(label, value)));
    select.dataset.signature = signature;
  }
  const next = entries.some(([id]) => id === selected) ? selected : entries[0]?.[0] || '';
  select.value = next;
  return next;
}

function renderActions() {
  const catalog = state.catalog || [];
  const key = JSON.stringify([catalog, pending, state.capabilities?.manual_features]);
  if (key === actionKey) return;
  actionKey = key;
  const expanded = new Set([...document.querySelectorAll('.scenario-group[open]')].map((node) => node.dataset.group));
  $('actions').replaceChildren();
  if (!catalog.length) $('actions').append(el('p', '실행 가능한 기능이 없습니다.', 'empty'));
  function actionCard(item, label) {
    const button = el('button', null, `action${item.disruptive ? ' danger' : ''}`);
    button.type = 'button';
    button.disabled = pending || item.enabled === false;
    button.dataset.action = item.action;
    button.setAttribute('aria-label', `${item.title || item.action} 실행`);
    const copy = el('span', null, 'action-copy');
    copy.append(el('strong', item.title || item.action), el('small', item.description || ''));
    button.append(el('span', label, 'action-number'), copy, el('span', '↗', 'action-arrow'));
    button.addEventListener('click', () => runAction(item));
    const wrapper = el('div', null, 'feature-item');
    const progress = el('div', null, 'feature-progress');
    progress.dataset.progress = item.action;
    wrapper.append(button, progress);
    return wrapper;
  }
  catalog.forEach((item, index) => {
    const wrapper = actionCard(item, String(index + 1).padStart(2, '0'));
    if (item.children?.length) {
      const group = el('details', null, 'scenario-group');
      group.dataset.group = item.action;
      group.open = expanded.has(item.action);
      group.append(el('summary', `시나리오별 실행 · ${item.children.length}개`));
      item.children.forEach((child) => group.append(actionCard(child, child.code || child.action.split('-').at(-1).toUpperCase())));
      wrapper.append(group);
    }
    $('actions').append(wrapper);
  });
  $('manual-features').replaceChildren();
  (state.capabilities?.manual_features || []).forEach((feature) => {
    const item = el('div', null, 'manual-feature');
    item.append(el('strong', feature.title), badge(feature.status), el('p', feature.reason));
    $('manual-features').append(item);
  });
}

function renderBackendSelector() {
  const select = $('backend-select');
  const backends = state.backends || [];
  updateOptions(select, backends.map((item) => [item.id, item.title]), state.vm?.backend || '', '백엔드 API 적용 대기');
  select.disabled = pending || !state.backend_selection_enabled;
  $('backend-note').textContent = state.vm?.running ? '실행 중에는 변경할 수 없습니다. 먼저 Power off 하세요.' :
    state.backend_selection_enabled ? '선택 후 Power on · 보존된 AutoSD 디스크로 부팅합니다.' : '진행 중 작업 또는 서버 설정을 확인하세요.';
  select.onchange = async () => {
    if (pending) return;
    pending = true;
    const backend = select.value;
    renderSystemControls();
    try {
      const response = await fetch('/api/backend', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': state.csrf_token}, body: JSON.stringify({backend})});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    } catch (error) { notice(`실행 대상 변경 실패: ${error.message}`); }
    finally { pending = false; await refresh(); }
  };
}

function renderDomainBoot() {
  const target = $('domain-boot');
  target.hidden = state.vm?.backend !== 'qbox-full';
  target.replaceChildren();
  if (target.hidden) return;
  const observed = state.domain_boot?.domains || [];
  for (const [id, title] of [['rse', 'RSE / TF-M'], ['si-cl0', 'SI CL0 / SCP'], ['si-cl1', 'SI CL1 / Zephyr'], ['ap', 'AP / TF-A → U-Boot → Linux']]) {
    const data = observed.find((item) => item.id === id);
    const card = el('article', null, 'domain-card');
    card.append(el('span', title), badge(data?.status || 'WAITING'));
    if (data?.reason) card.append(el('small', data.reason));
    else if (data?.markers) {
      const missing = Object.entries(data.markers).find(([, found]) => !found);
      if (missing) card.append(el('small', `대기: ${missing[0]}`));
    }
    target.append(card);
  }
  if (state.domain_boot?.provision) target.append(el('p', `AutoSD full-system 모듈 배포: ${state.domain_boot.provision.status}`, 'footnote'));
  target.append(el('p', '도메인별 firmware 부팅 로그 관측입니다. 물리 타이밍·전체 하드웨어 검증을 의미하지 않습니다. AP 시나리오 결과는 아래에서 별도 확인하세요.', 'footnote'));
}

function renderSystemControls() {
  if ($('backend-select')) renderBackendSelector();
  if ($('domain-boot')) renderDomainBoot();
  const target = $('system-controls');
  const controls = state.system_controls || [];
  const signature = JSON.stringify([controls, pending]);
  if (target.dataset.signature !== signature) {
    target.dataset.signature = signature;
    target.replaceChildren();
    if (!controls.length) target.append(el('p', '새 제어 API 적용을 위한 서버 재시작 대기', 'footnote'));
    for (const item of controls) {
      const button = el('button', item.title, `system-button${item.disruptive ? ' danger' : ''}`);
      button.type = 'button';
      button.disabled = pending || !item.enabled;
      button.title = item.unsupported_reason || item.description;
      button.addEventListener('click', () => runAction(item));
      target.append(button);
    }
  }
  const vm = state.vm || {};
  $('system-description').textContent = `${state.capabilities?.platform || 'AutoSD'} · 호스트 전원 제어가 아닙니다. ` +
    (vm.backend === 'qbox-full' ? 'RSE · SI CL0 · SI CL1 · AP firmware 부팅. Reboot는 새 boot ID와 도메인 상태를 확인합니다. Pause/Resume은 현재 실행의 10회 반복·HIPC·watchdog 실증 검증 후 활성화됩니다.' :
      vm.backend === 'qbox' ? 'AP 직접 부팅 · 다른 도메인은 mock. 재시작은 Power off → Power on을 사용하세요. Reboot/Pause/Resume은 미지원입니다.' :
      'Pause 상태에서는 Resume 후 종료·재부팅하세요.');
  $('system-state').textContent = vm.paused ? 'PAUSED' : vm.running ? 'POWERED ON' : 'POWERED OFF';
  const latest = [...(state.jobs || [])].reverse().find((j) => ['boot', 'shutdown', 'reboot', 'pause', 'resume'].includes(j.action));
  const progress = $('system-progress');
  progress.replaceChildren();
  if (latest) {
    progress.append(badge(latest.status), el('span', ` ${latest.action} · ${elapsed(latest)} · ${progressText(latest)} `));
    const button = el('button', '로그 보기', 'feature-log-button');
    button.type = 'button';
    button.addEventListener('click', () => openJob(latest.id, true));
    progress.append(button);
  }
}

async function runAction(item) {
  if (pending) return;
  if (item.disruptive && !window.confirm(`${item.title || item.action}\n\n${item.description || ''}\n\n실행 중인 guest에 영향을 줄 수 있습니다. 실행하시겠습니까?`)) return;
  pending = true;
  renderSystemControls();
  renderActions();
  notice('작업 실행을 요청하고 있습니다.');
  try {
    const result = await api('/api/jobs', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': state.csrf_token}, body: JSON.stringify({action: item.action, confirm_disruptive: Boolean(item.disruptive)})});
    selectedJob = result.job.id;
    if (!state.jobs.some((job) => job.id === result.job.id)) state.jobs.push(result.job);
    openJob(result.job.id);
    notice(`${item.title || item.action} 작업을 등록했습니다. 항목별 진행 상태와 ‘작업 & 실행 로그’의 Host log에서 확인하세요.`);
  } catch (error) { notice(`실행 요청 실패: ${error.message}`); }
  finally { pending = false; actionKey = ''; await refresh(); }
}

function cpuChart(samples, id) {
  const svg = svgEl('svg', {viewBox: '0 0 280 74', role: 'img', 'aria-label': `${id} CPU 사용률 추이, 0에서 100퍼센트`});
  for (const y of [8, 35, 62]) svg.append(svgEl('line', {x1: 0, x2: 280, y1: y, y2: y, stroke: '#2c3932', 'stroke-width': .6}));
  const segments = [];
  let segment = [];
  samples.forEach((sample, index) => {
    if (!finite(sample)) { if (segment.length) segments.push(segment); segment = []; return; }
    segment.push(`${index * 280 / Math.max(samples.length - 1, 1)},${62 - Math.max(0, Math.min(100, sample)) * .54}`);
  });
  if (segment.length) segments.push(segment);
  segments.forEach((points) => {
    if (points.length === 1) {
      const [cx, cy] = points[0].split(',');
      svg.append(svgEl('circle', {cx, cy, r: 2.5, fill: '#94d6b9'}));
    } else svg.append(svgEl('polyline', {points: points.join(' '), fill: 'none', stroke: '#94d6b9', 'stroke-width': 1.8, 'stroke-linejoin': 'round'}));
  });
  return svg;
}

function simulatorSeries(snapshot) {
  return (snapshot.history || []).filter(sample => sample.run_id === snapshot.run_id)
    .filter(sample => !snapshot.feature_session || sample.feature_session === snapshot.feature_session)
    .slice(-60).map(sample => sample.status === 'ONLINE' && finite(sample.speed_ratio) ? sample.speed_ratio : null);
}

function renderSimulator() {
  if (!$('simulator-status')) return;
  const sim = state.simulator || {};
  $('simulator-status').replaceWith(Object.assign(badge(sim.status || 'OFFLINE'), {id: 'simulator-status'}));
  $('simulator-time').textContent = finite(sim.sim_time_ns) ? `${fmt(sim.sim_time_ns / 1e9, 3)} s` : '—';
  $('simulator-speed').textContent = sim.status === 'ONLINE' && finite(sim.speed_ratio) ? `${fmt(sim.speed_ratio, 3)} ×` : '—';
  $('simulator-age').textContent = finite(sim.age_ms) ? `${fmt(sim.age_ms / 1000, 1)} s` : '—';
  $('simulator-note').textContent = sim.error || sim.reason || `세션 ${sim.run_id || '—'} · ${finite(sim.last_success_at) ? new Date(sim.last_success_at * 1000).toLocaleTimeString('ko-KR') : '표본 대기'} · 읽기 전용 관측`;
  const inspectorEpoch = JSON.stringify([sim.run_id, state.feature_session]);
  if ($('inspector-output') && inspectorRun !== inspectorEpoch) {
    inspectorRun = inspectorEpoch;
    inspectorRequest++;
    $('inspector-output').textContent = '새 세션 · 조회 대기';
  }
  for (const id of ['object-query', 'qmp-query']) if ($(id)) $(id).disabled = sim.status !== 'ONLINE';
  if ($('qmp-query')) {
    const capability = state.simulator_capabilities?.features?.qmp;
    $('qmp-query').disabled = sim.status !== 'ONLINE' || !capability?.available;
    $('qmp-query').title = capability?.reason || 'QMP 시작 옵션이 필요합니다.';
  }
  if ($('simulator-mcips')) $('simulator-mcips').textContent = sim.mcips_error || (sim.mcips ? JSON.stringify(sim.mcips, null, 2) : '활성 plugin 표본 없음');
  const chart = $('simulator-chart'); chart.replaceChildren();
  const samples = simulatorSeries(sim), maximum = Math.max(1, ...samples.filter(finite));
  if (samples.some(finite)) {
    const svg = cpuChart(samples.map(value => finite(value) ? value * 100 / maximum : null), 'Simulation speed');
    svg.setAttribute('aria-label', `시뮬레이션 진행 속도 최근 ${samples.length}개 표본, 세로축 0~${fmt(maximum, 3)} 배`);
    chart.append(el('span', `SIM/HOST RATIO · 0–${fmt(maximum, 3)} ×`, 'sample-note'), svg);
  }
  $('simulator-domains').replaceChildren();
  for (const domain of sim.domains || []) {
    const card = el('article', null, 'subsystem');
    const heading = el('div', null, 'subsystem-head');
    const boot = ((state.domain_boot || {}).domains || []).find(row => row.id === domain.domain_id);
    heading.append(el('h3', domain.domain_id.toUpperCase()), badge(boot ? boot.status : sim.status));
    card.append(heading, el('p', domain.qemu_instance_path || '인스턴스 미관측', 'sample-note'));
    if (boot) card.append(el('p', `BOOT EPOCH ${boot.boot_epoch || '—'} · firmware log`));
    for (const cpu of domain.cpus || []) {
      const row = el('div', null, 'simulator-cpu');
      row.append(el('span', cpu.name), badge(sim.status === 'ONLINE' ? cpu.state : sim.status),
        el('span', `local ${fmt(cpu.local_time_ns, 0)} ns · offset ${fmt(cpu.quantum_offset_ns, 0)} ns`, 'sample-note'));
      card.append(row);
    }
    if (!(domain.cpus || []).length) card.append(el('p', 'CPU 표본 미관측', 'empty'));
    $('simulator-domains').append(card);
  }
  if (!(sim.domains || []).length) $('simulator-domains').append(el('p', sim.status === 'UNSUPPORTED' ? 'QEMU는 기존 Guest CPU telemetry를 사용합니다.' : '소유한 QBox monitor와의 연결을 기다리고 있습니다.', 'empty'));
  const events = $('simulator-events'); events.replaceChildren();
  for (const event of (sim.events || []).slice(-30).reverse()) {
    events.append(el('p', `${event.observed_at} · ${event.source || 'observation'} · ${event.sim_time_ns === undefined ? '시뮬레이션 시각 미제공' : event.sim_time_ns + ' ns'} · ${event.kind} · ${JSON.stringify(event.details)}`, 'simulator-event'));
  }
}

async function inspectSimulator(qmp) {
  const run = state?.simulator?.run_id;
  const epoch = state?.feature_session;
  const request = ++inspectorRequest;
  const current = () => request === inspectorRequest && run === state?.simulator?.run_id && epoch === state?.feature_session;
  const output = $('inspector-output');
  output.textContent = '조회 중…';
  const query = qmp ? `/api/simulator/qmp?domain=${encodeURIComponent($('qmp-domain').value)}&command=${encodeURIComponent($('qmp-command').value)}`
    : `/api/simulator/objects?parent=${encodeURIComponent($('object-parent').value)}`;
  try {
    const result = await api(query);
    if (!current()) return;
    output.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    if (current()) output.textContent = `조회 불가: ${error.message}`;
  }
}

function renderMonitoring() {
  const monitor = state.monitoring || {};
  const time = monitor.collected_at ? Date.parse(monitor.collected_at) : NaN;
  const stale = finite(time) && Date.now() - time > 45000;
  const status = ['PAUSED_DURING_MEASUREMENT', 'PAUSED', 'REBOOTING', 'CONTROL_IN_PROGRESS'].includes(monitor.status) ? monitor.status
    : stale ? 'STALE' : monitor.status || 'OFFLINE';
  $('monitor-status').replaceWith(Object.assign(badge(status), {id: 'monitor-status'}));
  const online = status === 'ONLINE';
  const cpus = monitor.cpus || [];
  $('cpu-count').textContent = cpus.length ? cpus.length : '—';
  if (monitor.boot_id && lastBoot !== monitor.boot_id) {cpuHistory.clear(); lastBoot = monitor.boot_id; lastSample = '';}
  const availableHistory = (state.monitoring_history || []).filter((sample) => !monitor.boot_id || sample.boot_id === monitor.boot_id);
  const newSamples = availableHistory.length ? availableHistory.filter((sample) => !lastSample || sample.collected_at > lastSample) : [monitor];
  newSamples.forEach((sample) => {
    if (!sample.collected_at || sample.collected_at === lastSample) return;
    lastSample = sample.collected_at;
    (sample.cpus || []).forEach((cpu) => {
      const history = cpuHistory.get(cpu.id) || [];
      history.push(sample.status === 'ONLINE' && finite(cpu.utilization_pct) ? cpu.utilization_pct : null);
      cpuHistory.set(cpu.id, history.slice(-60));
    });
  });
  $('cpu-charts').replaceChildren();
  if (!cpus.length) $('cpu-charts').append(el('p', '현재 CPU 표본이 없습니다. 관리 대상 guest를 부팅하면 실제 CPU별 사용률을 표시합니다.', 'empty'));
  cpus.forEach((cpu) => {
    const card = el('article', null, 'cpu-card');
    const header = el('div', null, 'cpu-card-header');
    header.append(el('span', cpu.id.toUpperCase()), el('strong', finite(cpu.utilization_pct) ? `${fmt(cpu.utilization_pct)}%` : '대기'));
    const history = cpuHistory.get(cpu.id) || [];
    card.append(header, cpuChart(history, cpu.id), el('span', `${history.filter(finite).length} samples${online ? '' : ' · ' + status}`, 'sample-note'));
    $('cpu-charts').append(card);
  });
  $('monitor-note').textContent = monitor.error ? `수집 오류: ${monitor.error}` : `${monitor.scope || 'Guest Linux CPU와 실제 서비스 cgroup을 관측합니다.'} · ${monitor.collected_at || '수집 대기'} · 차트는 현재 부팅의 최근 최대 60개 표본입니다.`;
  $('subsystems').replaceChildren();
  const items = (monitor.subsystems || []).map((item) => ({...item, observedStatus: online ? item.status : status}));
  if (monitor.safety) items.unshift({id: 'Root / safety monitor', observedStatus: online ? monitor.safety.state || monitor.safety.status || 'OBSERVED' : status, detail: JSON.stringify(monitor.safety)});
  const unsupported = monitor.unsupported || ['RSE firmware CPU', 'Safety Island CL0/CL1', 'physical power/temperature'];
  unsupported.forEach((id) => items.push({id, observedStatus: 'UNSUPPORTED', detail: '현재 guest 계측 범위 밖 · 가상 CPU나 물리 상태를 추정하지 않습니다.'}));
  items.forEach((item) => {
    const card = el('article', null, 'subsystem');
    const header = el('div', null, 'subsystem-head');
    header.append(el('h3', item.id), badge(item.observedStatus));
    card.append(header);
    if (item.metrics) {
      const memory = Number(item.metrics['memory.current']);
      card.append(el('p', `CPU ${fmt(item.cpu_cores, 3)} cores · Memory ${item.metrics['memory.current'] && finite(memory) ? fmt(memory / 1048576) + ' MiB' : '—'}`));
      card.append(el('p', `CPU affinity ${item.metrics['cpuset.cpus.effective'] || '—'}${item.pid ? ` · PID ${item.pid}` : ''}`));
      if (item.id.startsWith('container:')) card.append(el('p', '실제 container init PID의 cgroup 계측'));
      else card.append(el('p', '서비스 cgroup · container workload와 별도'));
    }
    if (item.detail) card.append(el('p', item.detail));
    $('subsystems').append(card);
  });
}

function resultCases(result) {
  if (Array.isArray(result)) return result;
  if (!result || typeof result !== 'object') return [];
  if (Array.isArray(result.cases)) {
    const cases = [...result.cases];
    if (result.cyclictest) {
      const threads = Object.entries(result.cyclictest.threads || {});
      if (threads.length) threads.forEach(([id, thread]) => cases.push({id: `R06-cyclictest/${id}`, status: result.cyclictest.status || 'UNKNOWN', latency_status: result.cyclictest.latency_status, measurement: {count: thread.cycles, latency_us: thread.cycles > 0 ? {min: thread.min, mean: thread.avg, max: thread.max} : {}}}));
      else cases.push({id: 'R06-cyclictest', status: result.cyclictest.status || 'UNKNOWN', latency_status: result.cyclictest.latency_status});
    }
    return cases;
  }
  if (Array.isArray(result.scenarios)) return result.scenarios;
  if (Array.isArray(result.histogram?.series) && result.histogram.series.length) {
    return result.histogram.series.map((series) => ({
      id: `${result.mode}/${series.name}`, status: result.measurement_status || result.status,
      latency_status: (result.measurement_status || result.status) !== 'PASS' || result.histogram.valid === false ? 'NOT_EVALUATED' :
        series.count === 0 ? (result.mode === 'osnoise' ? 'NO_NOISE_OBSERVED' : 'NO_VALID_SAMPLES') :
        series.count > 0 && typeof series.max === 'number' && Number.isFinite(series.max) &&
          typeof result.settings?.threshold_us === 'number' && Number.isFinite(result.settings.threshold_us) ?
          (series.max > result.settings.threshold_us ? 'EXCEEDED' : 'WITHIN_OBSERVED_THRESHOLD') : 'NOT_EVALUATED',
      measurement: {count: series.count, histogram_over: series.over,
        latency_us: series.count > 0 ? {min: series.min, mean: series.avg, max: series.max} : {}},
    }));
  }
  return [{id: result.mode || '실행 결과', status: result.status || result.measurement_status || 'UNKNOWN', measurement: result}];
}

function measurementJob(job) {
  return ['rt', 'timerlat', 'osnoise', 'watchdog', 'monitor'].includes((job.action || '').split('-')[0]) || (job.action || '').startsWith('mixed-criticality');
}

function chooseEvidence(evidence, selected, session, seen, initialized) {
  const completed = evidence.filter((entry) => entry.job && measurementJob(entry.job) &&
    !runningStatuses.includes(entry.job.status)).sort((a, b) => Date.parse(b.modified_at) - Date.parse(a.modified_at));
  const current = completed.filter((entry) => session && entry.job.feature_session === session);
  const fresh = current.find((entry) => !seen.has(entry.id));
  completed.forEach((entry) => seen.add(entry.id));
  if (!initialized) return (current[0] || completed[0] || evidence[0])?.id || '';
  return fresh?.id || (evidence.some((entry) => entry.id === selected) ? selected : evidence[0]?.id || '');
}

function resultRow(item, result) {
  const measurement = item.measurement || item;
  const count = measurement.count ?? measurement.histogram?.sample_count;
  const latency = count === 0 ? {} : measurement.latency_us || {};
  return {id: item.id || item.name || '—', synthetic: Boolean(measurement.synthetic),
    measurementStatus: item.measurement_status || item.status || (item.returncode === 0 ? 'PASS' : result.measurement_status) || 'UNKNOWN',
    latencyStatus: item.latency_status || result.latency_status || 'NOT_EVALUATED',
    count, min: latency.min, mean: latency.mean ?? latency.avg, max: latency.max, p99: latency.p99,
    threshold: measurement.threshold_us ?? result.settings?.threshold_us,
    exceedances: measurement.threshold_exceedances, over: measurement.histogram_over};
}

function histogramChartData(result) {
  if (result.histogram?.valid !== true || !Array.isArray(result.histogram.series)) return [];
  const width = result.histogram.bucket_size_us || 1;
  const entries = result.histogram.entries;
  return result.histogram.series.filter((s) => Array.isArray(s.buckets)).map((s) => {
    const buckets = s.buckets.filter((b) => Number.isFinite(b.value) && b.value >= 0 && Number.isInteger(b.count) && b.count >= 0);
    return {...s, buckets, width, upper: Number.isInteger(entries) && entries > 0 ? entries * width :
      Math.max(width, ...buckets.map((b) => b.value + width)), configured: Number.isInteger(entries)};
  });
}

function noiseChartData(result, bins = 240) {
  const data = result.time_series;
  if (!data?.valid || !Array.isArray(data.samples) || data.unit !== 'us' || data.x_unit !== 's') return null;
  const samples = data.samples.filter((s) => Number.isFinite(s.time_s) && s.time_s >= 0 &&
    Number.isFinite(s.latency_us) && s.latency_us >= 0 && Number.isInteger(s.cpu) && s.cpu >= 0);
  const span = Math.max(Number.isFinite(data.end_time_s) ? data.end_time_s : 0, ...samples.map((s) => s.time_s), 0);
  const step = (span || 1) / bins;
  const groups = new Map();
  for (const sample of samples) {
    const minimum = Number.isFinite(sample.min_latency_us) && sample.min_latency_us >= 0 ? sample.min_latency_us : sample.latency_us;
    const count = Number.isInteger(sample.event_count) && sample.event_count > 0 ? sample.event_count : 1;
    const index = Math.min(bins - 1, Math.floor(sample.time_s / step));
    const key = `${sample.cpu}:${index}`;
    const old = groups.get(key);
    if (!old) groups.set(key, {cpu: sample.cpu, index, time_s: sample.time_s, min: minimum, max: sample.latency_us, count});
    else {
      old.min = Math.min(old.min, minimum); old.count += count;
      if (sample.latency_us > old.max) { old.max = sample.latency_us; old.time_s = sample.time_s; }
    }
  }
  return {samples: samples.length, span, step, points: [...groups.values()].sort((a, b) => a.cpu - b.cpu || a.index - b.index),
    partial: Boolean(data.truncated || data.dropped_events || data.status === 'PARTIAL'), source: data};
}

function plotFrame(label, xMax, yMax, xLabel, yLabel) {
  const svg = svgEl('svg', {viewBox: '0 0 640 240', role: 'img', 'aria-label': label, class: 'distribution-plot'});
  svg.append(svgEl('title', {}, label));
  const x = (value) => 66 + value / xMax * 480;
  const y = (value) => 190 - value / yMax * 156;
  for (let i = 0; i <= 4; i++) {
    svg.append(svgEl('line', {x1: 66, x2: 546, y1: y(yMax * i / 4), y2: y(yMax * i / 4), stroke: 'var(--line)'}));
    svg.append(svgEl('text', {x: 56, y: y(yMax * i / 4) + 4, 'text-anchor': 'end', class: 'plot-tick'}, fmt(yMax * i / 4, 1)));
    svg.append(svgEl('text', {x: x(xMax * i / 4), y: 208, 'text-anchor': 'middle', class: 'plot-tick'}, fmt(xMax * i / 4, 3)));
  }
  svg.append(svgEl('text', {x: 66, y: 18, class: 'plot-tick'}, yLabel));
  svg.append(svgEl('text', {x: 306, y: 232, 'text-anchor': 'middle', class: 'plot-tick'}, xLabel));
  return {svg, x, y};
}

function renderTimerlatHistogram(result, target) {
  const series = histogramChartData(result);
  if (!series.length) { target.append(el('p', 'Histogram bucket 데이터가 없습니다. 새 Timerlat 측정을 실행하세요.', 'empty')); return; }
  series.forEach((s, index) => {
    const color = ['var(--accent)', 'var(--amber)', 'var(--chart-blue)'][index % 3];
    target.append(el('h3', `${s.name} · ${fmt(s.count, 0)} samples`, 'plot-heading'));
    const top = Math.ceil(Math.max(1, s.over || 0, ...s.buckets.map((b) => b.count)) / 4) * 4;
    const {svg, x, y} = plotFrame(`${s.name} 지연 분포 histogram`, s.upper, top, 'Latency (µs)', '표본 수 (count)');
    s.buckets.forEach((b) => {
      if (!b.count) return;
      const bar = svgEl('rect', {x: x(b.value), y: y(b.count), width: Math.max(.5, 480 * s.width / s.upper - .3), height: 190 - y(b.count), fill: color});
      bar.append(svgEl('title', {}, `[${fmt(b.value)}, ${fmt(b.value + s.width)}) µs: ${fmt(b.count, 0)} samples`));
      svg.append(bar);
    });
    if (s.over > 0) {
      const over = svgEl('rect', {x: 580, y: y(s.over), width: 20, height: 190 - y(s.over), fill: 'var(--red)'});
      over.append(svgEl('title', {}, `Histogram 범위 밖: ${fmt(s.over, 0)} samples. 지연 위치와 기준 초과 횟수는 알 수 없습니다.`));
      svg.append(over);
    }
    svg.append(svgEl('text', {x: 590, y: 208, 'text-anchor': 'middle', class: 'plot-tick'}, 'over'));
    target.append(svg, el('p', `${fmt(s.width)} µs/bin · 범위 밖 ${fmt(s.over || 0, 0)}개는 별도 over 막대입니다. ` +
      (s.configured ? `수집 범위 0–${fmt(s.upper)} µs.` : '기존 결과: 출력된 bucket 범위만 표시합니다.'), 'footnote'));
  });
}

function renderOsnoiseTimeline(result, target) {
  const data = noiseChartData(result);
  if (!data) { target.append(el('p', '시간별 원시 데이터가 없는 결과입니다. 새 OS noise 측정을 실행하세요. Histogram만으로 시간 순서를 재구성하지 않습니다.', 'empty')); return; }
  if (!data.points.length) { target.append(el('p', '수집된 noise 이벤트가 없습니다. 지연 0을 의미하지 않습니다.', 'empty')); return; }
  const threshold = finite(result.settings?.threshold_us) ? result.settings.threshold_us : 0;
  const peak = Math.max(1, ...data.points.map((p) => p.max));
  const scaleStep = 10 ** Math.floor(Math.log10(peak)) / 2;
  const top = Math.ceil(peak * 1.1 / scaleStep) * scaleStep;
  const {svg, x, y} = plotFrame('OS noise 시간대별 지연: 구간 최대와 최소, CPU별', data.span || 1, top, '첫 수집 이벤트 이후 시간 (s)', 'Noise duration (µs)');
  if (threshold && threshold <= top) svg.append(svgEl('line', {x1: 66, x2: 546, y1: y(threshold), y2: y(threshold), stroke: 'var(--ink)', 'stroke-dasharray': '4 3'}));
  const cpus = [...new Set(data.points.map((p) => p.cpu))];
  cpus.forEach((cpu, index) => {
    const color = ['var(--accent)', 'var(--amber)', 'var(--chart-blue)', 'var(--red)'][index % 4];
    const points = data.points.filter((p) => p.cpu === cpu);
    let previous;
    let path = '';
    points.forEach((p) => {
      path += `${previous && p.index === previous.index + 1 ? 'L' : 'M'}${x(p.time_s)},${y(p.max)} `;
      const mark = svgEl('circle', {cx: x(p.time_s), cy: y(p.max), r: 2.1, fill: color});
      mark.append(svgEl('title', {}, `CPU ${cpu} · ${fmt(p.time_s, 6)} s · max ${fmt(p.max, 3)} µs / min ${fmt(p.min, 3)} µs · ${p.count} events`));
      svg.append(svgEl('line', {x1: x(p.time_s), x2: x(p.time_s), y1: y(p.min), y2: y(p.max), stroke: color, opacity: .25}), mark);
      previous = p;
    });
    svg.append(svgEl('path', {d: path, fill: 'none', stroke: color, 'stroke-width': 1.2}));
    target.append(el('span', `CPU ${cpu}`, `plot-key plot-color-${index % 4}`));
  });
  target.append(svg, el('p', `Y축: 관측 범위 · 실행 기준 ${fmt(threshold)} µs${threshold > top ? ' (표시 범위 밖)' : ' (흰 점선)'}. ` +
    `${data.partial ? '부분 수집 · 보존된 구간만 표시 · ' : ''}${fmt(data.samples, 0)}개 ${data.source.downsampled ? '대표점' : '이벤트'} → ${fmt(data.step * 1000, 3)} ms 구간별 최대값(점/선), 최소–최대(세로선). 빈 구간은 연결하지 않습니다. ` +
    (data.source.downsampled ? `원시 ${fmt(data.source.captured_sample_count, 0)}개는 CPU별 시간 구간 대표 peak ${fmt(data.samples, 0)}개로 축약했습니다. ` : '') +
    `trace 유실 ${fmt(data.source.dropped_events, 0)}개 · 제한/잘림 ${data.source.truncated ? '있음' : '없음'}. 원점은 첫 수집 이벤트이며 부팅 시간이 아닙니다. 커널 sampling threshold에서 생성된 이벤트만 표시합니다.`, 'footnote'));
}

function functionalRows(result) {
  const scenarios = result.scenarios || (result.kind === 'monitor-qualification' ? [
    {id: 'QUALIFICATION', status: result.status, error: result.error,
      observations: {before_boot_id: result.before_boot_id, after_boot_id: result.after_boot_id,
        health_hipc_returncode: result.health_hipc_returncode, watchdog: result.watchdog}},
    ...(result.cycles || []).map(row => ({id: `PAUSE-${row.cycle}`, status: row.pause?.status === 'PASS' && row.resume?.status === 'PASS' ? 'PASS' : 'UNCONFIRMED', observations: row})),
  ] : []);
  return scenarios.flatMap((item) => {
    const rows = [{id: item.id, status: item.status, name: '판정', value: item.reason || item.error || item.status}];
    for (const metric of (item.metrics || [])) {
      const value = typeof metric.value === 'number' ? (Number.isFinite(metric.value) ? Number(metric.value.toFixed(6)) : null) : metric.value;
      rows.push({id: item.id, status: item.status,
        name: metric.name, value: value == null ? '—' : `${value}${metric.unit ? ' ' + metric.unit : ''}`});
    }
    for (const key of ['accepted', 'reset_accepted', 'recovery_required', 'observations', 'snapshot', 'before', 'after']) {
      if (Object.hasOwn(item, key)) rows.push({id: item.id, status: item.status, name: key, value: JSON.stringify(item[key], null, 2)});
    }
    return rows;
  });
}

function renderFunctionalResult(result) {
  const target = $('functional-results');
  // Polling must not collapse evidence details or discard keyboard focus.
  const signature = JSON.stringify(result);
  if (target.dataset.signature === signature) return;
  target.dataset.signature = signature;
  target.replaceChildren();
  const table = el('table');
  table.append(el('caption', '기능 검증 결과 · 관측값 (안전 인증·물리 시간 보장 아님)'));
  const head = el('thead'); const header = el('tr');
  ['시나리오', '판정', '관측 항목', '실제 값'].forEach((name) => { const cell = el('th', name); cell.scope = 'col'; header.append(cell); });
  head.append(header); table.append(head);
  const body = el('tbody');
  functionalRows(result).forEach((item) => {
    const row = el('tr'); const status = el('td'); status.append(badge(item.status));
    const value = el('td');
    if (String(item.value).includes('\n')) {
      const details = el('details'); details.append(el('summary', '관측값 펼치기'), el('pre', item.value)); value.append(details);
    } else value.textContent = item.value;
    row.append(el('td', item.id), status, el('td', item.name), value); body.append(row);
  });
  table.append(body); target.append(table);
  if (Array.isArray(result.timeline) && result.timeline.length) {
    const timeline = el('table'); timeline.append(el('caption', '검출·복구 이벤트 · clock domain 사이 시간 차를 계산하지 않습니다.'));
    const heading = el('thead'); const row = el('tr');
    ['이벤트', 'Clock domain', '시각', '단위'].forEach((name) => { const cell = el('th', name); cell.scope = 'col'; row.append(cell); });
    heading.append(row); timeline.append(heading);
    const entries = el('tbody');
    result.timeline.forEach((item) => {
      const entry = el('tr'); [item.event, item.clock, item.value ?? '—', item.unit].forEach((value) => entry.append(el('td', value))); entries.append(entry);
    });
    timeline.append(entries); target.append(timeline);
  }
  for (const key of ['before', 'after']) {
    if (!result[key]) continue;
    const details = el('details'); details.append(el('summary', key), el('pre', JSON.stringify(result[key], null, 2)));
    target.append(details);
  }
}

function renderEvidence() {
  const evidence = [
    ...(state.jobs || []).filter((job) => job.result && (Array.isArray(job.result) || job.result.cases || job.result.mode || job.result.status)).map((job) => ({id: `job:${job.id}`, path: `${job.action} / ${job.id}`, modified_at: job.finished_at || job.started_at, result: job.result, job})),
    ...(state.evidence || [])
  ].sort((a, b) => Date.parse(b.modified_at) - Date.parse(a.modified_at));
  selectedEvidence = chooseEvidence(evidence, selectedEvidence, state.feature_session, seenCompletedMeasurements, evidenceInitialized);
  evidenceInitialized = true;
  selectedEvidence = updateOptions($('evidence-select'), evidence.map((e) => [e.id, e.path || e.id]), selectedEvidence, '결과 없음');
  const entry = evidence.find((e) => e.id === selectedEvidence);
  $('evidence-count').textContent = evidence.length;
  $('result-rows').replaceChildren();
  $('latency-chart').replaceChildren();
  const functional = ['mixed-criticality', 'watchdog', 'monitor', 'monitor-qualification'].includes(entry?.result?.kind);
  $('functional-results').hidden = !functional;
  document.querySelector('.results-grid').hidden = functional;
  if (!entry) {
    $('evidence-meta').textContent = '수집된 실행 결과가 없습니다.';
    const row = el('tr'); const cell = el('td', '결과 묶음을 선택하세요.', 'empty'); cell.colSpan = 10; row.append(cell); $('result-rows').append(row);
    $('latency-chart').append(el('p', '유효한 지연 측정값이 없습니다.', 'empty'));
    return;
  }
  const result = entry.result || {};
  $('chart-title').textContent = result.mode === 'timerlat' ? 'LATENCY HISTOGRAM' : result.mode === 'osnoise' ? 'OS NOISE / TIME' : 'MAX LATENCY';
  $('chart-unit').textContent = result.mode === 'timerlat' ? 'µs × count' : result.mode === 'osnoise' ? 'seconds × µs' : 'µs / 시나리오별';
  $('evidence-meta').textContent = [entry.path || entry.id, entry.modified_at, result.qualification, result.platform || result.settings?.platform, finite(result.settings?.threshold_us) && `실행 기준 ${fmt(result.settings.threshold_us)} µs`, result.measurement_status && `측정 ${result.measurement_status}`, result.latency_status && `지연 ${result.latency_status}`, result.threshold_stop_confirmed && '임계 초과로 trace 중지 확인'].filter(Boolean).join(' · ');
  if (entry.job) {
    const archived = ['automotive', 'rt', 'timerlat', 'osnoise'].includes(entry.job.action.split('-')[0]) || result.kind === 'mixed-criticality';
    const structured = ['watchdog', 'monitor'].includes(result.kind);
    const qualification = result.kind === 'monitor-qualification';
    const link = el('a', archived ? '원본 evidence 다운로드' : structured || qualification ? '원본 결과 JSON' : '원본 실행 로그', 'artifact-link');
    link.href = `/api/jobs/${encodeURIComponent(entry.job.id)}/artifacts/${archived ? 'evidence.tar.gz' : qualification ? 'qualification.json' : structured ? 'scenarios.json' : 'console.log'}`;
    $('evidence-meta').append(document.createTextNode(' · '), link);
  }
  if (functional) { renderFunctionalResult(result); return; }
  const cases = resultCases(result);
  const measurements = [];
  cases.forEach((item) => {
    const data = resultRow(item, result);
    const row = el('tr');
    const statusCell = el('td'); statusCell.append(badge(data.measurementStatus));
    const latencyCell = el('td'); latencyCell.append(badge(data.latencyStatus));
    row.append(el('td', `${data.id}${data.synthetic ? ' [검출용 지연 주입]' : /^R01/.test(data.id) ? ' [기준선 관측]' : ''}`), statusCell, latencyCell,
      ...[data.min, data.mean, data.max, data.p99].map((value) => el('td', fmt(value, 3))),
      el('td', fmt(data.count, 0)), el('td', fmt(data.threshold, 3)), el('td', fmt(data.exceedances, 0)));
    if (finite(data.over)) row.firstChild.append(el('small', ` · histogram 범위 초과 ${fmt(data.over, 0)}`, 'histogram-note'));
    $('result-rows').append(row);
    if (finite(data.max)) measurements.push({...data, exceeded: data.latencyStatus === 'EXCEEDED'});
  });
  if (result.mode === 'timerlat') { renderTimerlatHistogram(result, $('latency-chart')); return; }
  if (result.mode === 'osnoise') { renderOsnoiseTimeline(result, $('latency-chart')); return; }
  if (!measurements.length) { $('latency-chart').append(el('p', '이 결과에는 지연 통계가 없습니다. 판정과 원본 실행 로그를 확인하세요.', 'empty')); return; }
  const width = 420, height = measurements.length * 39 + 23;
  const max = Math.max(...measurements.map((item) => Math.max(item.max, finite(item.threshold) ? item.threshold : 0)), 1);
  const svg = svgEl('svg', {viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': '실험별 최대 지연 막대 그래프. 정확한 값은 옆 표를 참고하세요.'});
  measurements.forEach((item, index) => {
    const y = index * 39 + 10;
    svg.append(svgEl('text', {x: 0, y: y + 10, fill: '#a1ada5', 'font-family': 'monospace', 'font-size': 9}, item.id));
    svg.append(svgEl('rect', {x: 120, y, width: Math.max(item.max / max * 210, 1), height: 14, fill: item.synthetic ? '#efbc75' : item.exceeded ? '#ed9790' : '#94d6b9'}));
    if (finite(item.threshold)) svg.append(svgEl('line', {x1: 120 + item.threshold / max * 210, x2: 120 + item.threshold / max * 210, y1: y - 3, y2: y + 17, stroke: '#eeeede', 'stroke-dasharray': '3 2'}));
    svg.append(svgEl('text', {x: 415, y: y + 11, fill: '#eeeede', 'text-anchor': 'end', 'font-family': 'monospace', 'font-size': 10}, fmt(item.max)));
  });
  $('latency-chart').append(svg);
}

async function renderJobs() {
  const jobs = [...(state.jobs || [])].sort((a, b) => Date.parse(b.started_at) - Date.parse(a.started_at));
  const session = state.vm?.log_session || '';
  const groups = logGroups(jobs, session);
  if (logSession !== session) {
    logSession = session;
    selectedJob = groups.current[0]?.id || '';
    displayedJob = '';
    $('log-output').textContent = '현재 세션 작업을 기다리고 있습니다.';
    $('guest-log-output').textContent = '현재 부팅의 Guest 출력을 불러오는 중입니다.';
    $('guest-log-output').scrollTop = 0;
  }
  if (selectedJob && !jobs.some((job) => job.id === selectedJob)) selectedJob = groups.current[0]?.id || '';
  const select = $('job-select');
  const signature = JSON.stringify([session, jobs.map((job) => [job.id, job.action, job.status, job.started_at, job.log_session])]);
  if (select.dataset.signature !== signature) {
    select.replaceChildren(new Option('작업 선택 · 현재 세션 / 이전 실행 이력', ''));
    for (const [name, entries] of [['현재 세션', groups.current], ['이전 세션 · 실행 이력', groups.history]]) {
      if (!entries.length) continue;
      const group = el('optgroup');
      group.label = name;
      for (const job of entries) {
        const stamp = new Date(job.started_at).toLocaleString('ko-KR', {hour12: false});
        group.append(new Option(`${job.action} · ${job.status} · ${stamp} · ${job.id.slice(0, 8)}`, job.id));
      }
      select.append(group);
    }
    select.dataset.signature = signature;
  }
  select.value = selectedJob;
  const job = jobs.find((item) => item.id === selectedJob);
  const activeCount = jobs.filter((item) => runningStatuses.includes(item.status)).length;
  $('active-count').textContent = activeCount;
  $('running-tab-count').textContent = activeCount ? `(${activeCount} 실행 중)` : '';
  if (!job) {
    displayedJob = '';
    $('job-meta').textContent = '현재 세션 작업 없음 · 이전 로그는 드롭다운의 실행 이력에서 선택하세요.';
    $('log-output').textContent = '표시할 Host 작업을 선택하세요.';
    return;
  }
  if (displayedJob !== job.id) {
    if (displayedJob) jobScroll.set(displayedJob, $('log-output').scrollTop);
    displayedJob = job.id;
    $('log-output').textContent = progressLog.get(job.id) || '선택한 작업의 로그를 불러오는 중입니다.';
    $('log-output').scrollTop = jobScroll.get(job.id) || 0;
  }
  $('job-meta').replaceChildren(badge(job.status), el('span', `  ${job.action} · ${job.started_at || '—'}${job.finished_at ? ' → ' + job.finished_at : ''} · exit ${job.returncode ?? '—'}`));
  $('job-meta').append(el('p', `${statusLabels[job.status] || job.status} · ${elapsed(job)} · ${progressText(job)}`, 'job-progress'));
  const requestedId = job.id;
  try {
    const payload = await api(`/api/jobs/${encodeURIComponent(job.id)}/log`);
    progressLog.set(job.id, payload.text || '');
    renderActionProgress();
    if (selectedJob !== requestedId) return;
    const pre = $('log-output');
    const atBottom = pre.scrollHeight - pre.scrollTop - pre.clientHeight < 35;
    const value = `${payload.truncated ? '[로그가 표시 한도로 잘렸습니다. 원본 파일을 확인하세요.]\n' : ''}${payload.text || '아직 출력된 로그가 없습니다.'}`;
    if (pre.textContent !== value) { pre.textContent = value; if (atBottom) pre.scrollTop = pre.scrollHeight; }
  } catch (error) { if (selectedJob === requestedId) $('log-output').textContent = `로그 조회 실패: ${error.message}`; }
}

async function renderGuestLog() {
  const session = state.vm?.log_session || '';
  const request = ++guestLogRequest;
  const sources = state.guest_log_sources || [{id: 'uart', title: 'Boot UART'}];
  guestSource = updateOptions($('guest-source'), sources.map((source) => [source.id, source.title]), guestSource, 'Boot UART');
  const source = guestSource;
  const url = state.vm?.guest_log_url && `${state.vm.guest_log_url}?source=${encodeURIComponent(source)}`;
  if (!url) {
    $('guest-log-meta').textContent = '현재 Guest UART 출력 · 관리되는 부팅 세션 없음';
    $('guest-log-output').textContent = 'Guest 부팅을 기다리고 있습니다.';
    return;
  }
  try {
    const payload = await api(url);
    if (request !== guestLogRequest || source !== guestSource || session !== (state.vm?.log_session || '') || (payload.log_session || '') !== session) return;
    const pre = $('guest-log-output');
    const atBottom = pre.scrollHeight - pre.scrollTop - pre.clientHeight < 35;
    $('guest-log-meta').textContent = `${sources.find((item) => item.id === source)?.title || source} · ${session || '세션 대기'} · ${payload.status || (state.vm?.paused ? 'PAUSED' : state.vm?.running ? 'LIVE' : 'OFFLINE')}${payload.collected_at ? ' · 수집 ' + payload.collected_at : ''} · Host 작업 선택과 독립${source === 'uart' ? '' : ' · 15초 갱신 간격, 배타적 시나리오 실행 중 수집 중단'}`;
    const value = `${payload.truncated ? '[표시 한도를 초과하여 최근 Guest 출력만 표시합니다.]\n' : ''}${payload.text || '아직 출력된 Guest 로그가 없습니다.'}`;
    if (pre.textContent !== value) { pre.textContent = value; if (atBottom) pre.scrollTop = pre.scrollHeight; }
  } catch (error) {
    if (request === guestLogRequest && session === (state.vm?.log_session || '')) $('guest-log-output').textContent = `Guest 로그 조회 실패: ${error.message}`;
  }
}

async function refresh() {
  if (refreshing) return;
  refreshing = true;
  try {
    state = await api('/api/state');
    $('connection-status').textContent = '로컬 연결됨';
    $('connection-dot').className = 'dot live';
    const vm = state.vm || {};
    $('simulation-status').textContent = vm.pause_state_unknown ? 'PAUSE STATE UNKNOWN' : vm.paused ? 'SIMULATION PAUSED' : vm.running ? 'SIMULATION LIVE' : 'OFFLINE';
    $('simulation-detail').textContent = vm.running ? `${vm.owned ? '대시보드 관리 guest' : '외부 guest'} · SSH ${vm.ssh_port || '—'}` : '시뮬레이션은 정지 상태입니다. 이전 결과는 계속 확인할 수 있습니다.';
    $('updated-at').textContent = `UPDATED ${new Date().toLocaleTimeString('ko-KR', {hour12: false})}`;
    renderSystemControls(); renderActions(); renderActionProgress(); renderMonitoring(); renderSimulator(); renderEvidence(); await Promise.all([renderJobs(), renderGuestLog()]);
    // Follow the active non-boot demo even when another job's log is selected.
    const active = state.jobs.find((job) => job.action !== 'boot' && runningStatuses.includes(job.status));
    if (active && active.id !== selectedJob) {
      try { const log = await api(active.log_url); progressLog.set(active.id, log.text || ''); renderActionProgress(); } catch (_) { /* next poll retries */ }
    }
  } catch (error) {
    actionKey = '';
    document.querySelectorAll('#actions button, #system-controls button').forEach((button) => { button.disabled = true; });
    $('system-controls').dataset.signature = '';
    $('system-state').textContent = 'UNKNOWN';
    $('connection-status').textContent = '연결 끊김';
    $('connection-dot').className = 'dot error';
    $('simulation-status').textContent = 'UNKNOWN';
    $('simulation-detail').textContent = '백엔드 연결이 끊겨 현재 실행 상태를 확인할 수 없습니다.';
    $('monitor-status').replaceWith(Object.assign(badge('STALE'), {id: 'monitor-status'}));
    if ($('simulator-status')) $('simulator-status').textContent = 'STALE';
    notice(`상태 조회 실패: ${error.message}. 표시된 이전 값은 현재 상태가 아닐 수 있습니다.`);
  } finally { refreshing = false; }
}

$('evidence-select').addEventListener('change', (event) => { selectedEvidence = event.target.value; renderEvidence(); });
$('job-select').addEventListener('change', (event) => openJob(event.target.value));
$('guest-source').addEventListener('change', (event) => {
  guestSource = event.target.value;
  $('guest-log-output').textContent = '선택한 Guest 로그 수집 중…';
  $('guest-log-output').scrollTop = 0;
  renderGuestLog();
});
if (new URLSearchParams(location.search).get('view') === 'guest') document.body.classList.add('guest-only');
$('refresh').addEventListener('click', refresh);
if ($('object-query')) $('object-query').addEventListener('click', () => inspectSimulator(false));
if ($('qmp-query')) $('qmp-query').addEventListener('click', () => inspectSimulator(true));
refresh();
setInterval(refresh, 3000);
