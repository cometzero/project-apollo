const assert=require('node:assert/strict');
const {validateSnapshot,processRecords,processIdentity,nodeContext,edgeBoundary}=require('./process-model.js');
const sample=()=>({schema_version:1,collected_at:'2026-11-01T00:00:00Z',processes:[{id:'qbox',host:'fixture-host',executable:'TEST_FIXTURE',status:'OBSERVED',pid:101,ppid:1,start_time:'test-boot:900',evidence:'TEST_ONLY',binary_revision:'UNKNOWN',tcg_mode:'UNKNOWN',threads:[{tid:102,name:'fixture',start_time:'test-boot:901',role:'UNKNOWN',cpus:[]}]}],links:[]});
assert(validateSnapshot(sample()));
for(const mutate of [s=>s.schema_version=2,s=>s.processes[0].pid=-1,s=>s.processes[0].start_time=null,s=>s.processes[0].threads[0].tid='102',s=>s.processes[0].threads.push(s.processes[0].threads[0]),s=>s.processes.push(s.processes[0]),s=>s.links.push({from:'qbox',to:'missing'}),s=>s.processes[0].status='EXITED']){
 const s=sample();mutate(s);assert.throws(()=>validateSnapshot(s));
}
const conflict=sample();conflict.processes.push({...conflict.processes[0],id:'other',start_time:'test-boot:999'});assert.throws(()=>validateSnapshot(conflict));
const exited=sample();Object.assign(exited.processes[0],{status:'EXITED',pid:null,ppid:null,start_time:null,threads:[]});assert(validateSnapshot(exited));
assert(processIdentity(processRecords(null)[0]).includes('PID UNKNOWN'));
assert.notEqual(processIdentity(sample().processes[0]),processIdentity({...sample().processes[0],start_time:'test-boot:999'}));
assert.equal(edgeBoundary(nodeContext(4,{id:'pbx'}),nodeContext(4,{id:'mbx'})),'SAME_PROCESS');
assert.equal(edgeBoundary({process:'qbox'},{process:'http'}),'IPC');
assert.equal(nodeContext(0,{id:'aprouter'}).instance,null);
assert.equal(nodeContext(3,{id:'emit'}).scProcess,'SC_METHOD(emit_combined_irq)');
assert.equal(nodeContext(3,{id:'isr'}).evidence,'ILLUSTRATIVE');
console.log('PASS snapshot validation, identity, context and boundary tests');
