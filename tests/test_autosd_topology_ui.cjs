const {test} = require('node:test');
const assert = require('node:assert/strict');
const {diagram, filteredNodes} = require('../scripts/autosd_dashboard/web/topology.js');
const graph = {
  groups: [{id: 'ap', label: 'AP'}, {id: 'fabric', label: 'Fabric'}],
  nodes: [
    {id: 'cpu', label: 'CPU', kind: 'cpu', group: 'ap', moduletype: 'cpu'},
    {id: 'router', label: 'router', kind: 'router', group: 'ap', moduletype: 'router'},
    {id: 'uart', label: 'uart', kind: 'component', group: 'ap', moduletype: 'uart', parameters: {address: '0xff00'}},
    {id: 'mem', label: 'memory', kind: 'component', group: 'fabric', moduletype: 'ram'},
  ],
  edges: [
    {id: '1', source: 'cpu', target: 'router', kind: 'tlm'},
    {id: '2', source: 'router', target: 'uart', kind: 'tlm'},
    {id: '3', source: 'router', target: 'mem', kind: 'tlm'},
    {id: '4', source: 'uart', target: 'cpu', kind: 'signal'},
  ],
};
test('overview aggregates actual bindings without inventing an edge', () => {
  const view = diagram(graph);
  assert.equal(view.nodes.length, 4);
  assert.equal(view.edges.length, 3);
  assert.equal(view.edges[2].target, 'fabric:2');
  assert.ok(view.nodes.every(n => n.aggregate));
});
test('subsystem shows individual CPU-router-component nodes and signals opt in', () => {
  const view = diagram(graph, 'ap');
  assert.deepEqual(view.nodes.map(n => n.id), ['cpu', 'router', 'uart']);
  assert.equal(view.edges.length, 2);
  assert.equal(diagram(graph, 'ap', true).edges.length, 3);
  assert.ok(view.nodes[0].x < view.nodes[1].x && view.nodes[1].x < view.nodes[2].x);
});
test('search includes model, CCI path and configuration, scoped by subsystem', () => {
  assert.equal(filteredNodes(graph, '', 'FF00')[0].id, 'uart');
  assert.equal(filteredNodes(graph, 'ap', 'ram').length, 0);
  assert.equal(filteredNodes(graph, '', 'ram')[0].id, 'mem');
});
test('layout has unique cells even with many components', () => {
  const expanded = {...graph, nodes: [...graph.nodes, ...Array.from({length: 100}, (_, i) =>
    ({id: `c${i}`, group: 'ap', kind: 'component', label: `c${i}`, moduletype: 'stub'}))]};
  const view = diagram(expanded, 'ap');
  assert.equal(new Set(view.nodes.map(n => `${n.x},${n.y}`)).size, view.nodes.length);
  assert.ok(view.nodes.every(n => n.y + n.height < view.height));
});
test('unknown group and empty source graph are represented without fabricated nodes', () => {
  assert.equal(diagram(graph, 'missing').nodes.length, 0);
  assert.equal(diagram({nodes: [], edges: [], groups: []}).edges.length, 0);
});
