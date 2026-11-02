'use strict';
const SVG_NS='http://www.w3.org/2000/svg';
const edgeColors={tlm:'#65dfc4',dmi:'#c7a0ff',irq:'#f5bd68',call:'#84b9ff',own:'#94a4aa',return:'#eaa3bd',ipc:'#ff9a9a'};
let diagramZoom=1;
function svgElement(name,attrs={},text){const e=document.createElementNS(SVG_NS,name);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;return e;}
function inspectNode(n){
 document.querySelectorAll('.diagram-node').forEach(e=>e.classList.toggle('selected',e.dataset.id===n.id));
 el('objectTitle').textContent=n.title;el('objectDetail').textContent=n.detail;
 el('objectSource').textContent=n.source?`${n.source}:${n.line}`:'Process metadata / snapshot evidence';el('excerpt').textContent=n.excerpt||n.detail;
 el('objectContext').textContent=describeContext(n);
 const jump=el('openProcess');jump.textContent=n.navigate?'이 process로 이동':'소속 process 확대';jump.onclick=()=>switchProcess(n.navigate||n.process||'qbox');
}
function drawDiagram(index,activeStep){
 const graph=visualGraph(index,activeStep),svg=el('diagram');svg.replaceChildren();svg.setAttribute('viewBox',`0 0 ${graph.width} ${graph.height}`);svg.setAttribute('aria-label',graph.title);
 el('diagramTitle').textContent=graph.title;el('diagramSubtitle').textContent=graph.subtitle;
 const defs=svgElement('defs');for(const [kind,color] of Object.entries(edgeColors)){const marker=svgElement('marker',{id:`arrow-${kind}`,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:7,markerHeight:7,orient:'auto-start-reverse'});marker.append(svgElement('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:color}));defs.append(marker);}svg.append(defs);
 for(const box of graph.groups){svg.append(svgElement('rect',{x:box.x,y:box.y,width:box.w,height:box.h,rx:12,class:`diagram-group ${box.kind||''}`}),svgElement('text',{x:box.x+18,y:box.y+28,class:'group-title'},box.label));}
 const nodes=new Map(graph.nodes.map(n=>[n.id,n]));
 for(const edge of graph.edges){const a=nodes.get(edge.a),b=nodes.get(edge.b);let points=edge.route;
 if(!points){if(Math.abs(a.x-b.x)<30){const down=b.y>a.y;points=[[a.x+a.w/2,down?a.y+a.h:a.y],[b.x+b.w/2,down?b.y:b.y+b.h]];}else{const right=b.x>a.x;const start=[right?a.x+a.w:a.x,a.y+a.h/2],end=[right?b.x:b.x+b.w,b.y+b.h/2];const mid=(start[0]+end[0])/2;points=[start,[mid,start[1]],[mid,end[1]],end];}}
 const color=edgeColors[edge.kind],active=edge.stage===activeStep;
 const g=svgElement('g',{class:`diagram-edge ${active?'active':''}`,'data-kind':edge.kind});
 if(edge.detail)g.append(svgElement('title',{},edge.detail));
 g.append(svgElement('path',{d:points.map((p,i)=>`${i?'L':'M'} ${p.join(' ')}`).join(' '),fill:'none',stroke:color,'stroke-width':active?3:1.7,'stroke-dasharray':edge.kind==='own'?'3 6':edge.kind==='dmi'?'9 5':edge.kind==='return'?'4 4':'none','marker-end':`url(#arrow-${edge.kind})`}));
 const p=points[Math.floor((points.length-1)/2)],q=points[Math.ceil((points.length-1)/2)];
 g.append(svgElement('text',{x:(p[0]+q[0])/2,y:a.y===b.y?a.y-12:(p[1]+q[1])/2-9,'text-anchor':'middle',class:'edge-label',fill:color},edge.label));svg.append(g);
 }
 for(const n of graph.nodes){const g=svgElement('g',{class:`diagram-node ${n.stage===activeStep?'active':''}`,tabindex:0,role:'button','aria-label':`${n.title}: 소스 보기`,'data-id':n.id});g.append(svgElement('title',{},n.title+' / '+n.lines.join(' / ')));g.append(svgElement('rect',{x:n.x,y:n.y,width:n.w,height:n.h,rx:7}));g.append(svgElement('circle',{cx:n.x,cy:n.y+n.h/2,r:4,class:'socket-dot'}),svgElement('circle',{cx:n.x+n.w,cy:n.y+n.h/2,r:4,class:'socket-dot'}));g.append(svgElement('text',{x:n.x+13,y:n.y+27,class:'node-title','font-size':n.title.length>32?13:15},n.title.length>Math.floor((n.w-26)/7)?n.title.slice(0,Math.floor((n.w-26)/7)-1)+'…':n.title));n.lines.forEach((line,i)=>g.append(svgElement('text',{x:n.x+13,y:n.y+51+i*20,class:'node-detail'},line.length>Math.floor((n.w-26)/7)?line.slice(0,Math.floor((n.w-26)/7)-1)+'…':line)));g.onclick=()=>{if(n.navigate&&(processMode==='map'||n.remoteProcess))switchProcess(n.navigate);else inspectNode(n);};g.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();g.onclick();}};svg.append(g);}
 updateProcessUI(index,activeStep);
 setDiagramZoom(diagramZoom);inspectNode(graph.nodes.find(n=>n.stage===activeStep)||graph.nodes[0]);
 el('graphStats').textContent=`${graph.nodes.length} objects · ${graph.edges.length} connections`;
}
function setDiagramZoom(z){diagramZoom=Math.max(.75,Math.min(2,z));el('diagram').style.width=`${diagramZoom*100}%`;el('zoomValue').textContent=`${Math.round(diagramZoom*100)}%`;}
document.getElementById('zoomIn').onclick=()=>setDiagramZoom(diagramZoom+.25);
document.getElementById('zoomOut').onclick=()=>setDiagramZoom(diagramZoom-.25);
document.getElementById('zoomFit').onclick=()=>setDiagramZoom(1);
