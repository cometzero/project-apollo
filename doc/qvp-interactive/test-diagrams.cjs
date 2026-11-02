// Run from any directory: node doc/qvp-interactive/test-diagrams.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
const graphs = vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'diagrams.js'), 'utf8') + '\nQVP_DIAGRAMS');
assert.equal(graphs.length, 5);
for (const graph of graphs) {
  const ids = new Set(graph.nodes.map(n => n.id));
  assert.equal(ids.size, graph.nodes.length, 'duplicate node ID');
  for (const n of graph.nodes) {
    assert(n.x >= 0 && n.y >= 0 && n.x+n.w <= graph.width && n.y+n.h <= graph.height, n.id);
    assert(n.stage >= 0 && n.stage < 4);
    const source = fs.readFileSync(path.join(root, n.source), 'utf8').split('\n');
    assert(n.line > 0 && n.line <= source.length);
    assert.equal(n.excerpt.split('\n')[0], String(n.line).padStart(4) + '  ' + source[n.line-1], 'stale excerpt');
  }
  for (const e of graph.edges) {
    assert(ids.has(e.a) && ids.has(e.b), 'dangling edge');
    assert(['tlm','dmi','irq','call','own','return'].includes(e.kind));
  }
}
const mailbox=graphs[4];
assert(mailbox.edges.some(e=>e.a==='pbx' && e.b==='mbx' && e.kind==='call'));
assert(mailbox.edges.some(e=>e.a==='sib' && e.b==='shared' && e.kind==='tlm'));
console.log('PASS: five graphs, source excerpts, bounds, references and mailbox path types');
