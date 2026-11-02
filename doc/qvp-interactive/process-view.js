'use strict';
let processMode='component',selectedProcess='qbox',importedSnapshot=null,useSnapshot=false;
function currentProcesses(){return processRecords(useSnapshot?importedSnapshot:null);}
function processById(id){return currentProcesses().find(p=>p.id===id);}
function switchProcess(id){selectedProcess=id;processMode='detail';document.getElementById('viewMode').value='detail';render();}
function infoNode(id,x,y,title,lines,process,detail,navigate=null){return {id,x,y,w:440,h:96,title,lines,stage:-1,process,context:'unknown',instance:null,scProcess:null,evidence:'STATIC_SOURCE',detail,source:null,excerpt:'',navigate};}
function runtimeThreads(p){
 const group={label:'HOST THREADS / snapshot only · SC processes ≠ OS threads',x:20,y:0,w:1560,h:0,kind:'threads'};
 const nodes=[],lanes=[];
 p.threads.forEach((t,i)=>{
  const y=50+i*170;
  lanes.push({label:`HOST THREAD · TID ${t.tid} · collected identity (not live)`,x:35,y,w:1530,h:155,kind:'context'});
  nodes.push(infoNode(`thread-${t.tid}`,55,y+40,`TID ${t.tid} · ${t.name}`,[t.role,`start ${t.start_time}`],p.id,JSON.stringify(t,null,2)));
  const mapping=infoNode(`thread-map-${t.tid}`,565,y+40,'QMP guest vCPU → host thread mapping',[
   t.cpus.length?t.cpus.map(c=>`${c.instance} / CPU ${c.index}`).join(' ; '):'UNKNOWN / no QMP mapping',
   'This does not assign every instance component to this TID'],p.id,JSON.stringify(t.cpus,null,2));mapping.w=950;nodes.push(mapping);
 });
 if(!nodes.length)nodes.push(infoNode('no-threads',55,50,'HOST THREAD / TID UNKNOWN',['runtime snapshot unavailable','No inferred one-vCPU : one-thread mapping'],p.id,'실제 thread 목록과 QMP CPU index 매핑은 snapshot이 있을 때만 표시합니다.'));
 group.h=70+Math.max(1,p.threads.length)*170;return {group,nodes,lanes};
}
function processMap(){
 const support=document.getElementById('showSupport').checked;
 const records=currentProcesses().filter(p=>support||p.id==='qbox');
 const hosts=[...new Set(records.map(p=>p.host))];
 const graph={title:'Process Map / Host → OS process → execution objects',subtitle:'굵은 테두리 = OS address space · 점선 = instance/논리 구획 · PID는 snapshot에서만 표시',width:1600,height:0,groups:[],nodes:[],edges:[]};
 let y=70;
 for(const host of hosts){
  const list=records.filter(p=>p.host===host),start=y;
  const hostBox={label:`HOST: ${host}`,x:12,y,w:1576,h:0,kind:'host'};graph.groups.push(hostBox);y+=50;
  for(const p of list){
   const height=p.id==='qbox'?420:180;
   graph.groups.push({label:`OS PROCESS · ${processIdentity(p)}`,x:30,y,w:1540,h:height,kind:'process'});
   graph.nodes.push(infoNode(`proc-${p.id}`,55,y+50,p.executable,[`PPID ${p.ppid??'UNKNOWN'} · ${p.status}`,`${p.evidence} · 클릭: process 상세`],p.id,p.description||'Snapshot process',p.id));
   if(p.id==='qbox'){
    const instances=[...Object.values(INSTANCE_NAMES),'platform.qemu_inst'];
    instances.forEach((inst,i)=>{const n=infoNode(`instance-${i}`,55+(i%3)*510,y+190+Math.floor(i/3)*110,inst,['QEMU INSTANCE · same OS process','reference grouping, not a separate PID'],p.id,'모든 QEMU instance는 QBox process 내부 libqemu 상태입니다. RSE outer instance와 Container-local CPU instance는 서로 다릅니다.',p.id);n.instance=inst;graph.nodes.push(n);});
   }
   y+=height+30;
  }
  hostBox.h=y-start;y+=35;
 }
 const links=useSnapshot?importedSnapshot.links:[];
 for(const link of links){if(records.some(p=>p.id===link.from)&&records.some(p=>p.id===link.to))graph.edges.push({a:`proc-${link.from}`,b:`proc-${link.to}`,kind:'ipc',stage:-2,label:`IPC · ${link.transport}`,detail:`${link.endpoint} · ${link.evidence}`});}
 if(!useSnapshot&&support){graph.subtitle+=' · HTTP(browser ↔ server)는 설계 경로이며 IPC runtime 미확인';}
 graph.height=y+20;return graph;
}
function processDetail(index,activeStep){
 const p=processById(selectedProcess)||processById('qbox');
 const graph={title:`Process detail / ${p.executable}`,subtitle:processIdentity(p)+' · lanes describe execution contexts, not exclusive thread ownership',width:1600,height:0,groups:[],nodes:[],edges:[]};
 let y=95;
 if(p.id==='qbox'){
  const original=QVP_DIAGRAMS[index];
  const contexts=['setup','qemu','systemc','guest','unknown'];
  for(const context of contexts){
   const items=original.nodes.map(n=>({...n,...nodeContext(index,n)})).filter(n=>n.context===context);
   if(!items.length)continue;
   const height=80+Math.ceil(items.length/3)*140;
   graph.groups.push({label:`${CONTEXT_NAMES[context]} · host TID UNKNOWN until matched evidence`,x:30,y,w:1540,h:height,kind:'context'});
   items.forEach((n,i)=>graph.nodes.push({...n,x:55+(i%3)*510,y:y+55+Math.floor(i/3)*140,w:440}));
   y+=height+25;
  }
  graph.edges=original.edges.filter(e=>e.stage===activeStep).map(e=>({...e,route:null}));
 }else{
  graph.nodes.push(infoNode(`proc-${p.id}`,55,y+40,p.executable,[p.status,p.evidence],p.id,p.description||'Imported process'));
  y+=180;
 }
 const links=(useSnapshot?importedSnapshot.links:[]).filter(l=>l.from===p.id||l.to===p.id);
 if(links.length){
  const height=70+Math.ceil(links.length/3)*140;
  graph.groups.push({label:'BOUNDARY PORTS / remote endpoints · click to switch process',x:30,y,w:1540,h:height,kind:'ports'});
  links.forEach((l,i)=>{
   const remote=l.from===p.id?l.to:l.from;
   const n=infoNode(`endpoint-${i+1}`,55+(i%3)*510,y+50+Math.floor(i/3)*140,`BOUNDARY PORT → ${remote}`,[`IPC: ${l.transport}`,l.endpoint],p.id,`${l.endpoint}\n${l.evidence}`,remote);
   n.remoteProcess=remote;graph.nodes.push(n);
  });y+=height+25;
 }
 if(p.id==='qbox'){
  const entries=index>=3?SYSTEMC_PROCESSES:SYSTEMC_PROCESSES.filter(n=>n.id==='sc-cpu');
  graph.groups.push({label:'SYSTEMC PROCESSES / source registration · not OS process or exclusive TID',x:30,y,w:1540,h:200,kind:'context'});
  entries.forEach((entry,i)=>graph.nodes.push({...infoNode(entry.id,55+i*510,y+55,entry.title,['STATIC_SOURCE · current execution UNKNOWN','SC kernel scheduling ≠ host thread ownership'],p.id,entry.detail),...entry,context:'systemc',scProcess:entry.title}));
  y+=225;
 }
 const threads=runtimeThreads(p);threads.group.y=y;threads.nodes.forEach(n=>n.y+=y);threads.lanes.forEach(l=>l.y+=y);graph.groups.push(threads.group,...threads.lanes);graph.nodes.push(...threads.nodes);y+=threads.group.h+20;
 graph.groups.unshift({label:`OS PROCESS · ${processIdentity(p)} · same address space`,x:12,y:55,w:1576,h:y-55,kind:'process'});
 graph.height=y+20;return graph;
}
function visualGraph(index,activeStep){
 if(processMode==='map')return processMap();
 if(processMode==='detail')return processDetail(index,activeStep);
 const g=QVP_DIAGRAMS[index],p=processById('qbox');
 return {...g,title:g.title+' / PROCESS BOUNDARY',height:g.height+20,
  groups:[{label:`OS PROCESS · ${processIdentity(p)} · 동일 address space`,x:5,y:8,w:1590,h:g.height,kind:'process'},...g.groups],
  nodes:g.nodes.map(n=>({...n,...nodeContext(index,n)}))};
}
function describeContext(n){
 const p=processById(n.process||'qbox');
 const tids=p.threads.filter(t=>n.instance&&t.cpus.some(c=>c.instance===n.instance)).map(t=>t.tid);
 return [processIdentity(p),`evidence: ${n.evidence||p.evidence} · ${useSnapshot?'SNAPSHOT (not live)':'STATIC'}`,
  `instance: ${n.instance||'not assigned / UNKNOWN'}`,`context: ${CONTEXT_NAMES[n.context]||n.context||'UNKNOWN'}`,
  `candidate TIDs for instance: ${tids.length?tids.join(', '):'UNKNOWN'} (현재 실행 TID 아님)`,
  `SYSTEMC PROCESS: ${n.scProcess||'UNKNOWN / not applicable'}`,`guest PID: UNKNOWN`].join('\n');
}
function updateProcessUI(index,activeStep){
 if(!processById(selectedProcess))selectedProcess='qbox';
 const select=document.getElementById('processSelect');select.replaceChildren(...currentProcesses().map(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=`${p.id} · PID ${p.pid??'UNKNOWN'}`;return o;}));select.value=selectedProcess;
 const snapshot=useSnapshot?importedSnapshot:null;
 document.getElementById('snapshotStatus').textContent=snapshot?`SNAPSHOT ${snapshot.collected_at} · ${snapshot.processes.length} processes · NOT LIVE`:'STATIC_SOURCE · PID/TID UNKNOWN · runtime NOT_RUN';
 document.getElementById('snapshotMode').value=useSnapshot?'snapshot':'static';
 const selected=processById(selectedProcess)||processById('qbox');
 document.getElementById('processEvidence').textContent=[processIdentity(selected),`PPID: ${selected.ppid??'UNKNOWN'} · status: ${selected.status} (snapshot time only)`,`binary revision: ${selected.binary_revision} · TCG mode: ${selected.tcg_mode}`,`evidence: ${selected.evidence}`, ...(selected.errors||[]).map(e=>'PARTIAL / ERROR: '+e), snapshot?'source revisions: '+JSON.stringify(snapshot.source_revisions||'UNKNOWN'):'runtime snapshot NOT_RUN'].join('\n');
 const nodes=QVP_DIAGRAMS[index].nodes.filter(n=>n.stage===activeStep).map(n=>({...n,...nodeContext(index,n)}));
 const p=processById('qbox');
 const contexts=[...new Set(nodes.map(n=>CONTEXT_NAMES[n.context]))];
 const previous=QVP_DIAGRAMS[index].nodes.filter(n=>n.stage===activeStep-1).map(n=>nodeContext(index,n).context);
 const changed=activeStep>0&&nodes.some(n=>!previous.includes(n.context));
 document.getElementById('stepContext').textContent=`${processIdentity(p)}\n동일 process 내부 · IPC 없음 · ${changed?'실행 문맥 전환 (thread handoff runtime 미확인)':'thread handoff UNKNOWN / 해당 없음'}\n문맥: ${contexts.join(' / ')}\ninstance: ${[...new Set(nodes.map(n=>n.instance).filter(Boolean))].join(', ')||'UNKNOWN / not assigned'}\nSYSTEMC PROCESS: ${[...new Set(nodes.map(n=>n.scProcess).filter(Boolean))].join(', ')||'UNKNOWN / not applicable'} · host TID / guest PID: UNKNOWN`;
}
function initProcessUI(){
 document.getElementById('viewMode').onchange=e=>{pause();processMode=e.target.value;render();};
 document.getElementById('processSelect').onchange=e=>{pause();switchProcess(e.target.value);};
 document.getElementById('showSupport').onchange=()=>render();
 document.getElementById('snapshotMode').onchange=e=>{useSnapshot=e.target.value==='snapshot'&&!!importedSnapshot;render();};
 document.getElementById('snapshotFile').onchange=async e=>{
  const file=e.target.files[0];if(!file)return;
  try{if(file.size>4*1024*1024)throw Error('Snapshot exceeds 4 MiB');const parsed=validateSnapshot(JSON.parse(await file.text()));importedSnapshot=parsed;useSnapshot=true;document.getElementById('snapshotError').textContent='';document.querySelector('#snapshotMode option[value=snapshot]').disabled=false;render();}
  catch(error){document.getElementById('snapshotError').textContent=`Import rejected: ${error.message} · 이전 view 유지`;}
  e.target.value='';
 };
}
