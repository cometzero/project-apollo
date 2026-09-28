// Pure progress presentation contracts; no browser or VM writes.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../scripts/autosd_dashboard/web/app.js'), 'utf8');
function context() {
  const scope = {runningStatuses: ['RUNNING', 'QUEUED', 'STARTING'], state: {monitoring: {status: 'OFFLINE'}}, progressLog: new Map(), Date};
  vm.createContext(scope);
  vm.runInContext(source.slice(source.indexOf('function elapsed('), source.indexOf('function renderActionProgress(')), scope);
  return scope;
}
test('boot process existence is not guest readiness', () => {
  const scope = context();
  const job = {action: 'boot', status: 'RUNNING'};
  assert.match(scope.progressText(job), /연결 대기/);
  scope.state.monitoring.status = 'ONLINE';
  assert.match(scope.progressText(job), /guest 연결됨/);
});
test('automotive progress uses observed unique JSON results only', () => {
  const scope = context();
  const line = JSON.stringify({id: 'S01-coldboot', status: 'PASS'});
  scope.progressLog.set('test', 'noise\n' + line + '\n' + line + '\n{partial');
  assert.match(scope.progressText({id: 'test', action: 'automotive', status: 'RUNNING'}), /^1\/6/);
});
test('RT does not invent completion percentage', () => {
  const scope = context();
  assert.doesNotMatch(scope.progressText({action: 'rt', status: 'RUNNING'}), /%/);
  assert.match(scope.progressText({status: 'EXCEEDED', result: {latency_status: 'EXCEEDED'}}), /EXCEEDED/);
  assert.equal(scope.progressText({status: 'FAIL', error: 'SSH unavailable'}), 'SSH unavailable');
});
test('finished duration freezes at finish timestamp', () => {
  assert.equal(context().elapsed({started_at: '2026-09-27T00:00:00Z', finished_at: '2026-09-27T00:01:05Z'}), '1분 5초');
});
test('individual scenario progress ignores start events', () => {
  const scope = context();
  scope.progressLog.set('single', JSON.stringify({id: 'S01-coldboot', status: 'RUNNING'}) + '\n');
  assert.doesNotMatch(scope.progressText({id: 'single', action: 'automotive-s01', status: 'RUNNING'}), /^1\/1/);
  scope.progressLog.set('single', JSON.stringify({id: 'S01-coldboot', status: 'PASS'}) + '\n');
  assert.match(scope.progressText({id: 'single', action: 'automotive-s01', status: 'RUNNING'}), /^1\/1/);
});
test('blocked scenario exposes prerequisite reason', () => {
  assert.match(context().progressText({action: 'automotive-s05', status: 'BLOCKED', result: [{status: 'BLOCKED', reason: 'Requires FAULT_LATCHED'}]}), /Requires FAULT_LATCHED/);
});
test('feature statuses only show the current power lifecycle', () => {
  const scope = context();
  scope.state.jobs = [
    {id: 'old', action: 'automotive-s02', feature_session: 'old', status: 'PASS'},
    {id: 'legacy', action: 'rt', status: 'PASS'},
  ];
  scope.state.feature_session = 'off';
  assert.equal(scope.featureJob({action: 'automotive', children: [{action: 'automotive-s02'}]}), undefined);
  assert.equal(scope.featureJob({action: 'rt'}), undefined);
  scope.state.feature_session = 'new';
  scope.state.jobs.push({id: 'new-job', action: 'automotive-s02', feature_session: 'new', status: 'RUNNING'});
  assert.equal(scope.featureJob({action: 'automotive', children: [{action: 'automotive-s02'}]}).id, 'new-job');
});
test('boot and queued health follow lifecycle rather than launcher lifetime', () => {
  const scope = context();
  scope.state.feature_session = 'boot';
  scope.state.jobs = [{id: 'boot', action: 'boot', feature_session: 'boot', status: 'RUNNING'}];
  scope.state.feature_boot = {action: 'boot', status: 'PASS', phase: 'Guest boot ID 확인 완료'};
  scope.state.feature_health = {action: 'health', status: 'QUEUED', phase: '서비스 준비 대기'};
  assert.equal(scope.featureJob({action: 'boot'}).status, 'PASS');
  assert.equal(scope.progressText(scope.featureJob({action: 'health'})), '서비스 준비 대기');
  scope.state.jobs.push({id: 'health', action: 'health', feature_session: 'boot', status: 'PASS'});
  assert.equal(scope.featureJob({action: 'health'}).id, 'health');
});
test('paused VM is not presented as booting or live guest', () => {
  const scope = context();
  scope.state.vm = {paused: true};
  assert.match(scope.progressText({action: 'boot', status: 'RUNNING'}), /일시정지/);
  assert.match(scope.progressText({action: 'reboot', status: 'RUNNING'}), /boot ID/);
});
test('QBox system controls label AP-only scope and unsupported operations', () => {
  const nodes = Object.fromEntries(['system-controls', 'system-description', 'system-state', 'system-progress'].map((id) => [id, {
    dataset: {}, replaceChildren() {}, append() {}, textContent: '',
  }]));
  const scope = {state: {vm: {backend: 'qbox', running: true}, capabilities: {platform: 'QBox AP direct'}},
    pending: false, $: (id) => nodes[id], el: () => ({})};
  vm.createContext(scope);
  vm.runInContext(source.slice(source.indexOf('function renderSystemControls('), source.indexOf('async function runAction(')), scope);
  scope.renderSystemControls();
  assert.match(nodes['system-description'].textContent, /QBox AP direct/);
  assert.match(nodes['system-description'].textContent, /다른 도메인은 mock/);
  assert.match(nodes['system-description'].textContent, /Reboot\/Pause\/Resume은 미지원/);
  assert.equal(nodes['system-state'].textContent, 'POWERED ON');
});
test('backend selector is server-gated and supports the three explicit choices', async () => {
  const nodes = {'backend-select': {}, 'backend-note': {}};
  const calls = [];
  const scope = {state: {vm: {backend: 'qbox-full', running: false}, backend_selection_enabled: true, csrf_token: 'token',
    backends: [{id: 'qemu', title: 'QEMU'}, {id: 'qbox', title: 'QBox (AP only)'}, {id: 'qbox-full', title: 'QBox (full)'}]},
    pending: false, $: (id) => nodes[id], updateOptions: (node, rows, selected) => {node.rows = rows; node.value = selected;},
    renderSystemControls() {}, refresh: async () => {}, notice() {},
    fetch: async (...args) => {calls.push(args); return {ok: true, json: async () => ({backend: 'qemu'})};}};
  vm.createContext(scope);
  vm.runInContext(source.slice(source.indexOf('function renderBackendSelector('), source.indexOf('function renderDomainBoot(')), scope);
  scope.renderBackendSelector();
  assert.equal(nodes['backend-select'].rows.length, 3);
  assert.equal(nodes['backend-select'].disabled, false);
  nodes['backend-select'].value = 'qemu'; await nodes['backend-select'].onchange();
  assert.equal(calls[0][0], '/api/backend');
  assert.equal(calls[0][1].headers['X-CSRF-Token'], 'token');
  assert.deepEqual(JSON.parse(calls[0][1].body), {backend: 'qemu'});
  scope.state.vm.running = true; scope.state.backend_selection_enabled = false;
  scope.renderBackendSelector();
  assert.equal(nodes['backend-select'].disabled, true);
});
test('full domain cards never infer firmware PASS from guest login', () => {
  const target = {children: [], replaceChildren() {this.children = [];}, append(n) {this.children.push(n);}};
  const scope = {state: {vm: {backend: 'qbox-full'}, feature_boot: {status: 'PASS'}, domain_boot: {domains: [{id: 'ap', status: 'PASS'}]}},
    $: () => target, badge: (status) => ({status}), el: (tag, text) => ({tag, text, children: [], append(...items) {this.children.push(...items);}})};
  vm.createContext(scope);
  vm.runInContext(source.slice(source.indexOf('function renderDomainBoot('), source.indexOf('function renderSystemControls(')), scope);
  scope.renderDomainBoot();
  assert.equal(target.children[0].children[1].status, 'WAITING');
  assert.equal(target.children[3].children[1].status, 'PASS');
  scope.state.vm.backend = 'qbox'; scope.renderDomainBoot();
  assert.equal(target.hidden, true);
});

function logContext() {
  const scope = {Date};
  vm.createContext(scope);
  vm.runInContext(source.slice(source.indexOf('function logGroups('), source.indexOf('function openJob(')), scope);
  return scope;
}
test('only matching boot epoch belongs to current log session', () => {
  const jobs = [
    {id: 'old', log_session: 'boot:0', started_at: '2026-09-27T00:00:00Z'},
    {id: 'new', log_session: 'boot:1', started_at: '2026-09-27T01:00:00Z'},
    {id: 'legacy', started_at: '2026-09-26T00:00:00Z'},
  ];
  const groups = logContext().logGroups(jobs, 'boot:1');
  assert.equal(groups.current.map((job) => job.id).join(','), 'new');
  assert.equal(groups.history.map((job) => job.id).join(','), 'old,legacy');
  const powerCycle = logContext().logGroups(jobs, 'new-boot:0');
  assert.equal(powerCycle.current.length, 0);
  assert.equal(powerCycle.history.length, 3);
});
test('missing session never promotes legacy jobs into current session', () => {
  const groups = logContext().logGroups([{id: 'legacy'}], '');
  assert.equal(groups.current.length, 0);
  assert.equal(groups.history.length, 1);
});
test('Host and Guest are separate visible panels with independent selectors', () => {
  const html = fs.readFileSync(path.join(__dirname, '../scripts/autosd_dashboard/web/index.html'), 'utf8');
  assert.match(html, /section[^>]+id="guest-logs"/);
  assert.doesNotMatch(html, /id="guest-log-panel"[^>]*hidden/);
  assert.match(html, /href="\/\?view=guest" target="_blank"/);
  assert.match(html, /select id="guest-source"/);
  assert.match(html, /select id="job-select"/);
  assert.doesNotMatch(source, /job-tab-/);
});
test('Guest polling is independent of host selection and guarded against old sessions', () => {
  const guest = source.slice(source.indexOf('async function renderGuestLog('), source.indexOf('async function refresh('));
  assert.match(guest, /state\.vm\?\.guest_log_url/);
  assert.doesNotMatch(guest, /selectedJob/);
  assert.match(guest, /session !== \(state\.vm\?\.log_session/);
  assert.match(source, /Promise\.all\(\[renderJobs\(\), renderGuestLog\(\)\]\)/);
});

function guestLogContext(api) {
  const nodes = new Map([
    ['guest-log-output', {textContent: 'current UART', scrollHeight: 100, scrollTop: 0, clientHeight: 100}],
    ['guest-log-meta', {textContent: 'current session'}],
  ]);
  const scope = {
    state: {vm: {log_session: 'current', guest_log_url: '/api/guest/log', running: true}},
    guestLogRequest: 0, guestSource: 'uart', updateOptions: (_, entries, selected) => selected,
    api, $: (id) => nodes.get(id),
  };
  vm.createContext(scope);
  vm.runInContext(source.slice(source.indexOf('async function renderGuestLog('), source.indexOf('async function refresh(')), scope);
  return {scope, nodes};
}
test('Guest response from backend epoch different from last state is not displayed', async () => {
  const {scope, nodes} = guestLogContext(async () => ({log_session: 'next', text: 'different epoch UART'}));
  await scope.renderGuestLog();
  assert.equal(nodes.get('guest-log-output').textContent, 'current UART');
  assert.equal(nodes.get('guest-log-meta').textContent, 'current session');
});
test('late Guest request cannot overwrite a newer request for the same epoch', async () => {
  const responses = [];
  const {scope, nodes} = guestLogContext(() => new Promise((resolve) => responses.push(resolve)));
  const first = scope.renderGuestLog();
  const second = scope.renderGuestLog();
  responses[1]({log_session: 'current', text: 'newest UART'});
  await second;
  responses[0]({log_session: 'current', text: 'older UART'});
  await first;
  assert.equal(nodes.get('guest-log-output').textContent, 'newest UART');
});

function resultContext() {
  const scope = {Date, runningStatuses: ['RUNNING', 'QUEUED', 'STARTING']};
  vm.createContext(scope);
  vm.runInContext(source.slice(source.indexOf('function resultCases('), source.indexOf('function renderEvidence(')), scope);
  return scope;
}
const resultEntry = (id, epoch, time, status = 'PASS', action = 'rt') => ({
  id, modified_at: `2026-09-27T${time}:00Z`, job: {action, feature_session: epoch, status},
});
test('mixed criticality parent counts three cases and child counts one', () => {
  const scope = context();
  scope.progressLog.set('mc', JSON.stringify({event: 'case-complete', id: 'MC01', status: 'PASS'}));
  assert.match(scope.progressText({id: 'mc', action: 'mixed-criticality', status: 'RUNNING'}), /^1\/3/);
  assert.match(scope.progressText({id: 'mc', action: 'mixed-criticality-mc01', status: 'RUNNING'}), /^1\/1/);
});
test('functional metrics preserve zero, missing values, and observed evidence', () => {
  const scope = resultContext();
  const rows = scope.functionalRows({scenarios: [{id: 'MC01', status: 'PASS', metrics: [
    {name: 'zero', value: 0, unit: 'count'}, {name: 'missing'}], observations: {cpus: '1'}}]});
  assert.equal(rows[1].value, '0 count');
  assert.equal(rows[2].value, '—');
  assert.match(rows[3].value, /cpus/);
  assert.equal(scope.measurementJob({action: 'watchdog-wd04'}), true);
  assert.equal(scope.measurementJob({action: 'mixed-criticality-mc03'}), true);
});
test('unchanged functional results preserve expanded details during polling', () => {
  const result = {kind: 'watchdog', scenarios: [{id: 'WD01', status: 'PASS'}]};
  const scope = resultContext();
  scope.$ = () => ({dataset: {signature: JSON.stringify(result)}, replaceChildren() {throw new Error('must not rebuild');}});
  assert.doesNotThrow(() => scope.renderFunctionalResult(result));
});
test('first result selection prefers the latest completed measurement in this power epoch', () => {
  const scope = resultContext();
  const entries = [resultEntry('old', 'old', '12:00'), resultEntry('new', 'current', '11:00'), resultEntry('running', 'current', '13:00', 'RUNNING')];
  assert.equal(scope.chooseEvidence(entries, '', 'current', new Set(), false), 'new');
  assert.equal(scope.chooseEvidence(entries, '', 'off', new Set(), false), 'old');
});
test('manual result selection persists until a new current-epoch measurement completes', () => {
  const scope = resultContext();
  const seen = new Set();
  const entries = [resultEntry('one', 'current', '10:00'), resultEntry('two', 'current', '11:00')];
  assert.equal(scope.chooseEvidence(entries, '', 'current', seen, false), 'two');
  assert.equal(scope.chooseEvidence(entries, 'one', 'current', seen, true), 'one');
  entries.push(resultEntry('health', 'current', '12:00', 'PASS', 'health'));
  entries.push(resultEntry('legacy', 'old', '13:00'));
  assert.equal(scope.chooseEvidence(entries, 'one', 'current', seen, true), 'one');
  entries.push(resultEntry('three', 'current', '14:00', 'RUNNING', 'timerlat'));
  assert.equal(scope.chooseEvidence(entries, 'one', 'current', seen, true), 'one');
  entries.at(-1).job.status = 'EXCEEDED';
  assert.equal(scope.chooseEvidence(entries, 'one', 'current', seen, true), 'three');
});
test('RTLA series preserve CPU/IRQ identity and do not invent stats for zero samples', () => {
  const scope = resultContext();
  const result = {mode: 'timerlat', measurement_status: 'PASS', latency_status: 'EXCEEDED', settings: {threshold_us: 5000}, histogram: {series: [
    {name: 'IRQ-001', count: 100, min: 1, avg: 3, max: 9, over: 2},
    {name: 'Thread-002', count: 0, min: 0, avg: 0, max: 0, over: 0},
  ]}};
  const rows = scope.resultCases(result).map((item) => scope.resultRow(item, result));
  assert.equal(rows[0].id, 'timerlat/IRQ-001');
  assert.equal(rows[0].measurementStatus, 'PASS');
  assert.equal(rows[0].latencyStatus, 'WITHIN_OBSERVED_THRESHOLD');
  assert.equal(rows[0].mean, 3);
  assert.equal(rows[0].threshold, 5000);
  assert.equal(rows[0].over, 2);
  assert.equal(rows[0].exceedances, undefined);
  assert.equal(rows[0].p99, undefined);
  assert.equal(rows[1].count, 0);
  assert.equal(rows[1].max, undefined);
  assert.equal(rows[1].latencyStatus, 'NO_VALID_SAMPLES');
});
test('RTLA row comparisons do not inherit overall trace stop verdict', () => {
  const scope = resultContext();
  const result = {mode: 'timerlat', measurement_status: 'PASS', latency_status: 'EXCEEDED', settings: {threshold_us: 1000}, histogram: {valid: true, series: [
    {name: 'IRQ', count: 10, max: 324}, {name: 'Thread', count: 10, max: 804}, {name: 'User', count: 10, max: 1034},
  ]}};
  const rows = () => scope.resultCases(result).map((row) => row.latency_status).join(',');
  assert.equal(rows(), 'WITHIN_OBSERVED_THRESHOLD,WITHIN_OBSERVED_THRESHOLD,EXCEEDED');
  delete result.settings.threshold_us;
  assert.equal(rows(), 'NOT_EVALUATED,NOT_EVALUATED,NOT_EVALUATED');
  result.settings.threshold_us = 1000;
  result.measurement_status = 'FAIL';
  assert.equal(rows(), 'NOT_EVALUATED,NOT_EVALUATED,NOT_EVALUATED');
  result.measurement_status = 'PASS';
  result.histogram.valid = false;
  assert.equal(rows(), 'NOT_EVALUATED,NOT_EVALUATED,NOT_EVALUATED');
  result.mode = 'osnoise';
  result.histogram = {valid: true, series: [{name: 'CPU001', count: 0, max: 0}]};
  assert.equal(rows(), 'NO_NOISE_OBSERVED');
});
test('legacy RTLA result shows collected sample count without fabricated latency', () => {
  const scope = resultContext();
  const result = {mode: 'osnoise', status: 'PASS', histogram: {sample_count: 15}};
  const row = scope.resultRow(scope.resultCases(result)[0], result);
  assert.equal(row.count, 15);
  assert.equal(row.max, undefined);
});
test('RT suite and cyclictest preserve recorded thresholds and measurement statistics', () => {
  const scope = resultContext();
  const result = {settings: {threshold_us: 1000}, cases: [
    {id: 'R05-inject', returncode: 0, latency_status: 'DETECTION_PASS', measurement: {synthetic: true, count: 2, threshold_exceedances: 1, latency_us: {min: 1, mean: 2000, max: 3999, p99: 3999}}},
  ], cyclictest: {status: 'PASS', latency_status: 'EXCEEDED', threads: {'0': {cycles: 50, min: 1, avg: 3, max: 2000}}}};
  const rows = scope.resultCases(result).map((item) => scope.resultRow(item, result));
  assert.equal(rows[0].measurementStatus, 'PASS');
  assert.equal(rows[0].synthetic, true);
  assert.equal(rows[0].threshold, 1000);
  assert.equal(rows[0].exceedances, 1);
  assert.equal(rows[1].id, 'R06-cyclictest/0');
  assert.equal(rows[1].mean, 3);
  assert.equal(rows[1].count, 50);
});
test('result presentation exposes measurement and latency status separately with threshold legend', () => {
  const html = fs.readFileSync(path.join(__dirname, '../scripts/autosd_dashboard/web/index.html'), 'utf8');
  assert.match(html, /측정<\/th><th scope="col">지연 판정/);
  assert.match(html, /최소 µs/);
  assert.match(html, /평균 µs/);
  assert.match(html, /기준 초과 횟수/);
  assert.match(html, /흰 점선: 실행 당시 기준/);
  assert.match(source, /결과 표·그래프/);
  assert.match(source, /stroke-dasharray/);
});

test('Timerlat histogram preserves bucket counts and separates overflow', () => {
  const data = resultContext().histogramChartData({histogram: {valid: true, bucket_size_us: 50, entries: 100,
    series: [{name: 'IRQ-001', count: 12, over: 3, buckets: [{value: 100, count: 9}]}]}});
  assert.equal(data[0].width, 50);
  assert.equal(data[0].upper, 5000);
  assert.equal(data[0].buckets[0].count, 9);
  assert.equal(data[0].over, 3);
  assert.equal(resultContext().histogramChartData({histogram: {valid: false, series: [{}]}}).length, 0);
});
test('OS noise cannot manufacture a timeline from a histogram', () => {
  assert.equal(resultContext().noiseChartData({mode: 'osnoise', histogram: {series: [{count: 100, max: 10}]}}), null);
  assert.equal(resultContext().noiseChartData({time_series: {valid: true, unit: 'ns', x_unit: 's', samples: []}}), null);
});
test('OS noise time aggregation preserves peaks, gaps and CPU identity', () => {
  const data = resultContext().noiseChartData({time_series: {valid: true, unit: 'us', x_unit: 's', truncated: true, dropped_events: 2,
    samples: [{time_s: 0, latency_us: 3, cpu: 1}, {time_s: .01, latency_us: 900, cpu: 1},
      {time_s: .02, latency_us: 5, cpu: 1}, {time_s: .01, latency_us: 6, cpu: 2},
      {time_s: 1, latency_us: 7, cpu: 1}, {time_s: -1, latency_us: 20, cpu: 1}]}} , 10);
  assert.equal(data.samples, 5);
  assert.equal(data.points.length, 3);
  assert.equal(data.points[0].min, 3);
  assert.equal(data.points[0].max, 900);
  assert.equal(data.points[0].time_s, .01);
  assert.equal(data.points[0].count, 3);
  assert.equal(data.points[1].index, 9);
  assert.equal(data.points[2].cpu, 2);
  assert.equal(data.partial, true);
});
test('OS noise representative peaks retain raw minima, counts and full time span', () => {
  const data = resultContext().noiseChartData({time_series: {valid: true, unit: 'us', x_unit: 's', end_time_s: 5,
    samples: [{time_s: .1, latency_us: 10, min_latency_us: 1, event_count: 200, cpu: 1},
      {time_s: .2, latency_us: 20, min_latency_us: 2, event_count: 300, cpu: 1}]}} , 10);
  assert.equal(data.span, 5);
  assert.equal(data.points[0].min, 1);
  assert.equal(data.points[0].max, 20);
  assert.equal(data.points[0].count, 500);
});
function chartContext() {
  const scope = resultContext();
  function node(tag, attrs, text) { return {tag, attrs, text, children: [], append(...items) {this.children.push(...items);}}; }
  Object.assign(scope, {finite: Number.isFinite, fmt: (v) => String(v),
    el: (tag, text, className) => node(tag, {className}, text), svgEl: node});
  return {scope, target: node('div')};
}
test('trace renderers produce histogram bars and time axes, not max comparison bars', () => {
  let {scope, target} = chartContext();
  scope.renderTimerlatHistogram({histogram: {valid: true, series: [{name: 'Thr-001', count: 5, over: 2, buckets: [{value: 12, count: 3}]}]}}, target);
  const svg = target.children.find((n) => n.tag === 'svg');
  assert.equal(svg.children.filter((n) => n.tag === 'rect').length, 2);
  assert.match(JSON.stringify(svg), /Latency \(µs\)/);
  ({scope, target} = chartContext());
  scope.renderOsnoiseTimeline({settings: {threshold_us: 1000}, time_series: {valid: true, unit: 'us', x_unit: 's', samples: [
    {time_s: 0, latency_us: 5, cpu: 1}, {time_s: 1, latency_us: 10, cpu: 1}]}}, target);
  const timeline = target.children.find((n) => n.tag === 'svg');
  assert.match(JSON.stringify(timeline), /첫 수집 이벤트 이후 시간/);
  assert.equal(timeline.children.find((n) => n.tag === 'path').attrs.d.includes('L'), false);
});
