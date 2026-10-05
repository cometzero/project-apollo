/* Native presentation contracts; these tests do not launch a board or send jobs. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ui = require('../scripts/autosd_dashboard/web/board.js');
const topology = require('../scripts/autosd_dashboard/web/topology.js');
const source = fs.readFileSync(path.join(__dirname, '../scripts/autosd_dashboard/web/board.js'), 'utf8');
const html = fs.readFileSync(path.join(__dirname, '../scripts/autosd_dashboard/web/board.html'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, '../scripts/autosd_dashboard/web/board.css'), 'utf8');
const graph = {
  groups: [{id: 'ap_compute', label: 'AP'}, {id: 'board', label: 'Board'}],
  nodes: [
    {id: 'platform.core0', group: 'ap_compute', kind: 'cpu', label: 'core0', moduletype: 'cpu'},
    {id: 'platform.pmic', group: 'board', label: 'PMIC', moduletype: 'i2c-device'},
    {id: 'platform.new_device', group: 'future_subsystem', label: 'new', moduletype: 'new-model'},
  ],
  edges: [
    {id: 'one', source: 'platform.core0', target: 'platform.pmic', kind: 'tlm', binding: {reference: 'actual'}},
    {id: 'two', source: 'platform.pmic', target: 'platform.new_device', kind: 'signal'},
    {id: 'missing', source: 'platform.core0', target: 'external.tc397', kind: 'uart'},
  ],
};
test('PCB and block views have identical actual membership and bindings', () => {
  const board = ui.graphView(graph, '', 'board'), block = ui.graphView(graph, '', 'block');
  const members = view => view.nodes.flatMap(n => n.members.map(m => m.id)).sort();
  assert.deepEqual(members(board), graph.nodes.map(n => n.id).sort());
  assert.deepEqual(members(board), members(block));
  assert.deepEqual(board.edges.map(e => e.members.map(m => m.id)), block.edges.map(e => e.members.map(m => m.id)));
  assert.equal(board.edges.length, 2);
  assert.equal(board.nodes.some(n => n.group === 'external'), false, 'no fabricated MCU');
  assert.ok(board.nodes.some(n => n.group === 'future_subsystem'), 'unknown Lua component remains visible');
  assert.notDeepEqual(board.nodes.map(n => [n.x, n.y]), block.nodes.map(n => [n.x, n.y]));
});
test('node removal and real attachment updates propagate to both views', () => {
  const modified = structuredClone(graph);
  modified.nodes = modified.nodes.filter(n => n.id !== 'platform.pmic');
  modified.nodes.push({id: 'external.tc397', group: 'external', label: 'MCU', moduletype: 'QEMU'});
  for (const mode of ['board', 'block']) {
    const view = ui.graphView(modified, '', mode);
    assert.equal(view.nodes.some(n => n.members.some(m => m.id === 'platform.pmic')), false);
    assert.equal(view.edges.length, 1);
    assert.equal(view.edges[0].members[0].id, 'missing');
  }
});
test('group details and kind filters preserve original node and edge IDs', () => {
  const detail = ui.graphView(graph, 'ap_compute');
  assert.deepEqual(detail.nodes.map(n => n.id), ['platform.core0']);
  assert.equal(detail.overview, false);
  assert.deepEqual(ui.graphView(graph, '', 'board', 'signal').edges.flatMap(e => e.members.map(m => m.id)), ['two']);
  const duplicate = {...graph, edges: [...graph.edges, {...graph.edges[0], id: 'parallel'}]};
  assert.equal(ui.graphView(duplicate).edges[0].members.length, 2, 'aggregates real bindings, not invented links');
});
test('64-bit addresses and zero use shared BigInt topology contract', () => {
  const regions = topology.memoryRegions({parameters: {mem: {address: '0', size: '0'}, high: {address: '0x1000000000000000', size: '0x20', mapped_base_addr: '0'}}});
  assert.equal(regions[0].address, '0x00000000');
  assert.equal(regions[0].end, '—');
  assert.equal(regions[1].end, '0x100000000000001F');
  assert.equal(regions[1].mapped, '0x00000000');
  assert.match(source, /topo\.memoryRegions\(node\)/);
});
test('stats retain >100% actual host values, separate domains, and last 120 samples', () => {
  const samples = Array.from({length: 130}, (_, seq) => ({run_id: 'live', sample_monotonic: seq * 5, status: 'OK', cpu_pct: 240 + seq, domain_vcpu_pct: {ap: 220}}));
  samples.unshift({run_id: 'old', sample_monotonic: 0, cpu_pct: 9999});
  const result = ui.sampleSeries(samples, 'cpu_pct', 'live');
  assert.equal(result.length, 120); assert.equal(result[0].value, 250); assert.equal(result.at(-1).value, 369);
  assert.equal(ui.sampleSeries(samples, 'domain_vcpu_pct.ap', 'live')[0].value, 220);
  assert.equal(ui.chartPath(result).max, 369);
});
test('missing, stale, warmup and barrier values create chart gaps, never zero', () => {
  const samples = ['OK', 'STALE', 'OK', 'WARMING_UP', 'BARRIER', 'OK'].map((status, i) => ({run_id: 'x', status, sample_monotonic: i * 3, cpu_pct: i === 2 ? null : 0}));
  const series = ui.sampleSeries(samples, 'cpu_pct', 'x');
  assert.deepEqual(series.map(p => p.value), [0, null, null, null, null, 0]);
  assert.equal((ui.chartPath(series).path.match(/M/g) || []).length, 2);
  assert.deepEqual(ui.sampleSeries([{run_id: 'x', cpu_pct: '100', sample_monotonic: 1}], 'cpu_pct', 'x')[0].value, null);
  assert.equal(ui.chartPath([{time: null, value: 90}]).max, null);
});
test('current metric rejects previous-run cached samples and preserves real zero', () => {
  const sample = {run_id: 'old', status: 'OK', cpu_pct: 0};
  assert.equal(ui.sampleValue(sample, 'cpu_pct', 'new'), null);
  assert.equal(ui.sampleValue(sample, 'cpu_pct', 'old'), 0);
  assert.equal(ui.sampleValue({...sample, status: 'STALE'}, 'cpu_pct', 'old'), null);
});
test('chart uses host timestamps rather than uniform fabricated spacing', () => {
  const chart = ui.chartPath([{time: 10, value: 1}, {time: 11, value: 1}, {time: 20, value: 1}], 106, 65);
  assert.match(chart.path, /M3\.00/); assert.match(chart.path, /L13\.00/); assert.match(chart.path, /L103\.00/);
});
test('logs reject old run, preserve cursors/gap, bound retained text and strip ANSI', () => {
  const old = {cursor: 'a', text: '기존\n'};
  assert.strictEqual(ui.mergeLog(old, {run_id: 'old', next_cursor: 'bad', text: 'old'}, 'current'), old);
  const next = ui.mergeLog(old, {run_id: 'current', next_cursor: 'b', gap: true, text: '\x1b[31m새 로그\x1b[0m\r\n<script>alert(1)</script>'}, 'current');
  assert.equal(next.cursor, 'b'); assert.equal(next.gap, true); assert.match(next.text, /로그 간격/); assert.match(next.text, /<script>/);
  assert.doesNotMatch(next.text, /\x1b|\r/);
  assert.equal(ui.mergeLog({text: '', cursor: ''}, {text: 'x'.repeat(300000)}, 'current').text.length, 200000);
  assert.doesNotMatch(source, /\.innerHTML\s*=|insertAdjacentHTML|eval\(/, 'log content must remain text');
});
test('typed job payload requires current session, capability and explicit disruptive consent', () => {
  const state = {run_id: 'one', csrf_token: 'token'}, descriptor = {id: 'vmcu.power.off', available: true, disruptive: true};
  assert.throws(() => ui.jobPayload(descriptor, {}, state, 'req'), /확인/);
  assert.deepEqual(ui.jobPayload(descriptor, {arg: 0}, state, 'req', true), {action: descriptor.id, args: {arg: 0}, run_id: 'one', request_id: 'req', confirm_disruptive: true});
  assert.throws(() => ui.jobPayload({...descriptor, available: false, reason: 'MCU off'}, {}, state, 'req', true), /MCU off/);
  assert.throws(() => ui.jobPayload(descriptor, {}, {...state, active_job: {status: 'RUNNING'}}, 'req', true), /작업/);
  assert.throws(() => ui.jobPayload(descriptor, {}, {run_id: 'one'}, 'req', true), /인증/);
  assert.equal(ui.busy({active_job: {status: 'FAIL'}}), false);
  assert.equal(ui.busy({active_job: 'job-id'}), true);
});
test('UART sources follow actual enabled descriptors and keep host logs separate', () => {
  assert.equal(ui.uartSource({id: 'tc397'}, false), false);
  assert.equal(ui.uartSource({id: 'tc397'}, true), true);
  assert.equal(ui.uartSource({id: 'new-console', kind: 'uart'}, true), true);
  assert.equal(ui.uartSource({id: 'si-cl0', enabled: false}, true), false);
  assert.equal(ui.uartSource({id: 'platform'}, true), false);
});
test('only discovered action descriptors determine scenario/control placement', () => {
  assert.equal(ui.scenarioAction({id: 'qvp.future-profile'}), true);
  assert.equal(ui.scenarioAction({id: 'future-check', mode: 'scenario'}), true);
  assert.equal(ui.scenarioAction({id: 'vmcu.pfdi.fault-recover'}), true);
  assert.equal(ui.scenarioAction({id: 'vmcu.power.off', mode: 'live'}), false);
});
test('independent CSP-compatible Korean surface includes mobile/keyboard controls', () => {
  assert.match(html, /<html lang="ko">/);
  assert.doesNotMatch(html, /<script(?![^>]*src=)|\sonclick=|<style/i);
  for (const page of ['board', 'uart', 'scenarios', 'control', 'evidence']) assert.match(html, new RegExp(`id="page-${page}"`));
  assert.match(html, /QVP 논리 보드 · 실물 배치 UNVERIFIED/);
  assert.match(source, /'X-CSRF-Token'/);
  assert.match(source, /getRandomValues/, 'request IDs also work on HTTP LAN origins');
  assert.match(source, /'keydown'/); assert.match(css, /max-width:700px/);
  assert.match(css, /prefers-reduced-motion/); assert.match(css, /:focus-visible/);
  assert.doesNotMatch(html, /https?:\/\//, 'offline assets only');
});
