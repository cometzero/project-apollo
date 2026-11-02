'use strict';
const PROCESS_DEFINITIONS = [
 {id:'qbox',host:'qvp-host',executable:'QBox + in-process libqemu',role:'simulation',evidence:'STATIC_SOURCE',description:'SystemC modules와 QEMU instances가 공유하는 host address space. domain은 PID 경계가 아닙니다.'},
 {id:'http',host:'qvp-host',executable:'python3 -m http.server',role:'support',evidence:'STATIC_CONFIG',description:'문서만 제공하는 HTTP process. QVP memory/IRQ 경로에 참여하지 않습니다.'},
 {id:'browser',host:'macbook',executable:'Browser',role:'support',evidence:'ILLUSTRATIVE',description:'MacBook browser의 논리 process. browser 내부 renderer/network process 구성과 PID는 UNKNOWN입니다.'},
 {id:'launcher',host:'qvp-host',executable:'QVP launcher',role:'support',evidence:'NOT_RUN',description:'실행 시 확인할 지원 process. launcher가 이미 종료되었을 수 있습니다.'}
];
const INSTANCE_NAMES={ap:'platform.ap_qemu_inst',rse:'platform.rse_cpu_pass.qemu_inst',si_cl0:'platform.si_cl0_qemu_inst',si_cl1:'platform.si_cl1_qemu_inst'};
const CONTEXT_NAMES={setup:'Elaboration / configuration',qemu:'QEMU callback / vCPU execution',systemc:'SystemC kernel / transport',guest:'GUEST execution (host thread UNKNOWN)',unknown:'Execution context UNKNOWN'};
const NODE_CONTEXTS=[
 {},
 {cpu:'qemu',bridge:'qemu',return:'qemu',payload:'qemu',policy:'setup'},
 {access:'qemu',hint:'qemu',alias:'qemu',mapping:'qemu',backing:'qemu',invalidate:'unknown'},
 {gic:'unknown',cpu:'qemu',isr:'guest',eoi:'guest'},
 {apdata:'qemu',sidata:'qemu',irq:'unknown',reverse:'guest'}
];
function nodeContext(index,node){
 let context=NODE_CONTEXTS[index][node.id] || 'systemc';
 let instance=null,scProcess=null;
 if(index===0){
  context=/mgr$|inst$|outer$/.test(node.id)?'setup':/cpu$/.test(node.id)?'qemu':'systemc';
  const domain=['si_cl0','si_cl1','rse','ap'].find(d=>node.id.startsWith(d));
  if(domain&&/mgr$|inst$|cpu$|gic$/.test(node.id))instance=INSTANCE_NAMES[domain];
  if(node.id==='si0gic')instance=INSTANCE_NAMES.si_cl0;
  if(node.id==='si1gic')instance=INSTANCE_NAMES.si_cl1;
  if(node.id==='rseouter')instance='platform.qemu_inst';
 }else if(index===1||index===2){if(['qemu','guest'].includes(context))instance=INSTANCE_NAMES.ap;}
 else if(index===3){if(['qemu','guest'].includes(context)||node.id==='gic')instance=INSTANCE_NAMES.si_cl1;}
 else if(index===4){if(node.id==='apdata')instance=INSTANCE_NAMES.ap;if(['sidata','irq','reverse'].includes(node.id))instance=INSTANCE_NAMES.si_cl1;}
 if(index===3&&node.id==='emit')scProcess='SC_METHOD(emit_combined_irq)';
 return {process:'qbox',instance,context,scProcess,evidence:context==='guest'?'ILLUSTRATIVE':'STATIC_SOURCE'};
}
function validateSnapshot(raw){
 const fail=message=>{throw Error(message);};
 const str=(v,name)=>{if(typeof v!=='string'||!v.length||v.length>4096)fail(name+' must be a nonempty string');};
 const int=(v,name)=>{if(!Number.isSafeInteger(v)||v<1)fail(name+' must be a positive integer');};
 if(!raw||raw.schema_version!==1)fail('Unsupported snapshot schema');
 str(raw.collected_at,'collected_at');if(!Number.isFinite(Date.parse(raw.collected_at)))fail('Invalid collected_at');
 if(!Array.isArray(raw.processes)||raw.processes.length>64)fail('Invalid processes');
 const ids=new Set(),identities=new Set(),hostPids=new Set();
 for(const p of raw.processes){
  str(p.id,'process.id');str(p.host,'process.host');str(p.executable,'executable');str(p.evidence,'evidence');
  if(ids.has(p.id))fail('Duplicate process ID');ids.add(p.id);
  if(!['OBSERVED','UNKNOWN','EXITED','ERROR'].includes(p.status))fail('Invalid process status');
  if(p.status==='OBSERVED'){
   int(p.pid,'pid');if(!Number.isSafeInteger(p.ppid)||p.ppid<0)fail('Invalid ppid');str(p.start_time,'start_time');
   const hostPid=`${p.host}/${p.pid}`;if(hostPids.has(hostPid))fail('Conflicting PID identities in one snapshot');hostPids.add(hostPid);
   const identity=`${p.host}/${p.pid}/${p.start_time}`;if(identities.has(identity))fail('Duplicate process identity');identities.add(identity);
   str(p.binary_revision,'binary_revision');str(p.tcg_mode,'tcg_mode');
  } else if(p.pid!==null||p.ppid!==null||p.start_time!==null)fail('Unobserved process cannot claim PID identity');
  if(!Array.isArray(p.threads)||p.threads.length>4096)fail('Invalid threads');
  if(p.status!=='OBSERVED'&&p.threads.length)fail('Unobserved process cannot claim TIDs');
  const tids=new Set(),cpuIds=new Set();
  for(const t of p.threads){int(t.tid,'tid');str(t.name,'thread name');str(t.start_time,'thread start_time');str(t.role,'thread role');
   if(tids.has(t.tid))fail('Duplicate thread ID');tids.add(t.tid);
   if(!Array.isArray(t.cpus)||t.cpus.length>256)fail('Invalid CPU mappings');
   for(const cpu of t.cpus){str(cpu.instance,'instance');if(!Object.values(INSTANCE_NAMES).includes(cpu.instance))fail('Unknown CPU instance');if(!Number.isSafeInteger(cpu.index)||cpu.index<0)fail('Invalid CPU index');const cpuKey=cpu.instance+'/'+cpu.index;if(cpuIds.has(cpuKey))fail('Conflicting CPU mapping');cpuIds.add(cpuKey);if(cpu.evidence!=='QMP query-cpus-fast')fail('CPU mapping requires QMP evidence');}
  }
 }
 if(!Array.isArray(raw.links)||raw.links.length>256)fail('Invalid links');
 for(const l of raw.links){if(!ids.has(l.from)||!ids.has(l.to)||l.from===l.to)fail('Invalid IPC endpoints');str(l.transport,'transport');str(l.endpoint,'endpoint');str(l.evidence,'link evidence');}
 return raw;
}
function processRecords(snapshot){
 const records=PROCESS_DEFINITIONS.map(p=>({...p,pid:null,ppid:null,start_time:null,status:'UNKNOWN',threads:[],binary_revision:'UNKNOWN',tcg_mode:'UNKNOWN'}));
 if(snapshot)for(const p of snapshot.processes){const i=records.findIndex(r=>r.id===p.id);if(i<0)records.push({role:'support',description:'Imported process',...p});else records[i]={...records[i],...p};}
 return records;
}
function processIdentity(p){return p.status==='OBSERVED'?`${p.host} / PID ${p.pid} / start ${p.start_time}`:`${p.host} / ${p.id} / PID UNKNOWN (${p.status})`;}
function edgeBoundary(a,b){return a.process===b.process?'SAME_PROCESS':'IPC';}
if(typeof module!=='undefined')module.exports={validateSnapshot,processRecords,processIdentity,nodeContext,edgeBoundary};
