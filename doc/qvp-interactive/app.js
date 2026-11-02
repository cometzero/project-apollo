'use strict';
const P = 'hsoc-stack/tools/qbox-platform/';
const Q = 'hsoc-stack/tools/qbox/';
const scenarios = [
 {name:'01 / 구조',title:'Instance는 CPU의 실행 소속입니다.',intro:'QBox 안에서 Lua가 SystemC wrapper를 구성하고, AP CPU들은 동일한 AP QemuInstance를 참조합니다.',caveat:'생성 관계를 보여주는 화면입니다. host thread 수와 실행 순서는 runtime policy 확인이 필요합니다.',steps:[
 ['CONFIG','Lua / platform','moduletype, args, bind로 instance와 component를 구성합니다.',P+'platforms/apollo/soc/hw-block/ap_compute/cpu.lua:89'],
 ['OWNERSHIP','QemuInstance','ap_qemu_inst_mgr와 AARCH64 ap_qemu_inst가 생성됩니다.',P+'platforms/apollo/soc/hw-block/ap_compute/cpu.lua:91'],
 ['OWNERSHIP','AP CPU wrappers','ap_cpu_i의 args={ctx.instances.ap}로 같은 instance를 참조합니다. vCPU마다 instance 하나를 만드는 구조가 아닙니다.',P+'platforms/apollo/soc/hw-block/ap_compute/cpu.lua:27'],
 ['BINDING','SystemC sockets','최종 connect 단계에서 CPU mem은 ap_router.target_socket으로 연결됩니다. irq_in은 ap_gic 출력과 연결됩니다.',P+'platforms/apollo/soc/hw-block/ap_compute/interconnect.lua:202'] ]},
 {name:'02 / Memory',title:'DRAM과 SRAM은 gs_memory backing에 도달합니다.',intro:'예시: AP CPU의 일반 memory access. SystemC bus master도 initiator socket에서 router를 통해 memory target에 접근합니다.',caveat:'주소 변환과 보호 정책은 해당 initiator 경로에 따라 다릅니다. 그림의 단계는 일반 접근을 단순화한 것입니다.',steps:[
 ['DATA','AP vCPU access','QEMU memory callback에서 주소, command, data_length를 가진 TLM payload를 구성합니다.',Q+'qemu-components/common/include/ports/initiator.h'],
 ['DATA','run_on_sysc','do_regular_access는 SystemC 실행 문맥에서 b_transport를 호출합니다. 지연과 response를 반환받습니다.',Q+'qemu-components/common/include/ports/initiator.h:658'],
 ['DATA','ap_router','최종 binding된 memory target으로 전달합니다. CPU mem → router target, router initiator → memory target 방향입니다.',P+'platforms/apollo/soc/hw-block/ap_compute/interconnect.lua:158'],
 ['DATA','gs_memory','target 주소를 backing offset으로 해석하여 read/write합니다. DRAM1은 base 0x80000000, size 0x7f000000입니다. SRAM도 gs_memory지만 여러 객체로 나뉩니다.',Q+'systemc-components/gs_memory/include/gs_memory.h:301'] ]},
 {name:'03 / DMI',title:'같은 backing, 다른 접근 경로.',intro:'DMI 허용 경로의 예시입니다. get_direct_mem_ptr는 pointer뿐 아니라 유효 주소 범위와 권한을 반환합니다.',caveat:'DMI 허용 여부는 Lua/CCI override와 전체 경로 정책에 의존합니다. DMI hit rate와 성능은 측정하지 않았습니다.',steps:[
 ['NEGOTIATION','일반 접근 / hint','일반 transaction의 dmi_allowed hint를 확인한 후 DMI를 요청합니다. 거절되면 일반 transport를 유지합니다.',Q+'qemu-components/common/include/ports/initiator.h:658'],
 ['DMI','get_direct_mem_ptr','gs_memory가 dmi_allow, 주소 범위, ROM 여부를 검사하고 host pointer와 read/write 권한을 제공합니다.',Q+'systemc-components/gs_memory/include/gs_memory.h:247'],
 ['DMI','QEMU memory alias','instance DMI manager가 backing의 alias를 생성합니다. 별도의 DRAM 복사본을 만드는 설명이 아닙니다.',Q+'qemu-components/common/include/ports/initiator.h:620'],
 ['DMI','직접 접근 / invalidate','매핑된 범위의 후속 접근은 매번 일반 b_transport를 거치지 않을 수 있습니다. 무효화가 발생하면 해당 mapping을 폐기해야 합니다.',Q+'qemu-components/common/include/ports/initiator.h'] ]},
 {name:'04 / Interrupt',title:'IRQ는 상태와 signal의 경로입니다.',intro:'SI CL1 mailbox interrupt 예시. 데이터 transaction과 IRQ signal을 분리해서 봅니다.',caveat:'GIC enable, routing, priority와 CPU mask 조건이 충족되어야 handler가 실행됩니다. 실제 guest ISR 실행은 NOT_RUN입니다.',steps:[
 ['CONTROL','MHU status','mailbox 상태와 mask에서 combined IRQ level을 계산합니다.',P+'systemc-components/mhu320ae/include/mhu320ae.h:1059'],
 ['CONTROL','SystemC event','pending IRQ update를 event로 전달하고 emit_combined_irq가 irq signal을 갱신합니다. deassert에는 별도 처리도 있습니다.',P+'systemc-components/mhu320ae/include/mhu320ae.h:1101'],
 ['CONTROL','SI CL1 GIC','si_cl1_hipc_mhu_mbx.irq → si_cl1_gic.spi_in_41. 여기서 SPI index 41은 architectural INTID 73에 해당합니다.',P+'platforms/apollo/soc/hw-block/si_cl1/mailbox.lua:73'],
 ['CONDITIONAL','vCPU / guest handler','interrupt controller와 CPU 조건에 따라 예외를 처리합니다. device status clear와 GIC EOI를 별도 단계로 상세화할 예정입니다.',P+'platforms/apollo/soc/hw-block/si_cl1/cpu.lua'] ]},
 {name:'05 / Mailbox',title:'Payload와 doorbell을 나누어 봅니다.',intro:'AP → SI CL1의 doorbell-bridge를 따라갑니다. 같은 pair 이름이 QBox 내부 PBX/MBX를 연결합니다.',caveat:'이 시안은 notification 경로입니다. shared-memory/vring payload와 firmware barrier/ack 순서는 다음 구현에서 별도 추적합니다.',steps:[
 ['CONTROL','AP PBX write','AP가 host_ap_si_cl1_mhu_pbx register에 접근합니다. pair는 apollo_ap_to_si_cl1, protocol은 doorbell-bridge입니다.',P+'platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua:145'],
 ['INTERNAL CALL','paired_mbx()','write_postbox_doorbell이 paired_mbx의 signal_doorbell_channel을 호출합니다. peer 알림은 C++ 호출이며 DRAM payload 복사 자체가 아닙니다.',P+'systemc-components/mhu320ae/include/mhu320ae.h:2183'],
 ['CONTROL','SI CL1 MBX / IRQ','동일 pair의 si_cl1_hipc_mhu_mbx가 수신 측입니다. 상태 변화와 combined IRQ가 SI CL1 GIC로 전달됩니다.',P+'platforms/apollo/soc/hw-block/si_cl1/mailbox.lua:54'],
 ['CONDITIONAL','수신 / clear / reply','수신 firmware의 payload 처리와 clear, 역방향 pair apollo_si_cl1_to_ap를 이용한 reply를 별도 sequence로 상세화할 예정입니다.',P+'platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua:167'] ]}
];
let chapter = 0, step = 0, timer = null;
const el = id => document.getElementById(id);
function pause(){clearInterval(timer);timer=null;el('play').textContent='자동 재생';}
function render(){
 const scene=scenarios[chapter];
 el('title').textContent=scene.title;el('intro').textContent=scene.intro;
 el('count').textContent=`${String(step+1).padStart(2,'0')} / ${scene.steps.length}`;
 el('chapters').replaceChildren(...scenarios.map((s,i)=>{const b=document.createElement('button');b.textContent=s.name;b.setAttribute('aria-pressed',i===chapter);b.onclick=()=>{pause();chapter=i;step=0;render();};return b;}));
 drawDiagram(chapter,step);
 el('path').replaceChildren(...scene.steps.map((s,i)=>{const b=document.createElement('button');b.className='node';b.setAttribute('aria-current',i===step?'step':'false');const small=document.createElement('small');small.textContent=`0${i+1} / ${s[0]}`;b.append(small,document.createTextNode(s[1]));b.onclick=()=>{pause();step=i;render();};return b;}));
 const s=scene.steps[step];el('kind').textContent=s[0];el('stepTitle').textContent=s[1];el('detail').textContent=s[2];el('source').textContent=s[3];el('caveat').textContent=scene.caveat;
 el('progress').style.width=`${(step+1)/scene.steps.length*100}%`;el('prev').disabled=step===0;el('next').disabled=step===scene.steps.length-1;
}
el('prev').onclick=()=>{pause();step=Math.max(0,step-1);render();};
el('next').onclick=()=>{pause();step=Math.min(scenarios[chapter].steps.length-1,step+1);render();};
el('reset').onclick=()=>{pause();step=0;render();};
el('play').onclick=()=>{if(timer){pause();return;}if(step===scenarios[chapter].steps.length-1){step=0;render();}el('play').textContent='일시 정지';timer=setInterval(()=>{step++;if(step===scenarios[chapter].steps.length-1)pause();render();},2400);};
initProcessUI();
render();
