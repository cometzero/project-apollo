'use strict';
function currentViewDrawio(){
 const graph=visualGraph(chapter,step),doc=document.implementation.createDocument('', 'mxfile');
 const add=(parent,name,attrs)=>{const e=doc.createElement(name);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));parent.appendChild(e);return e;};
 const page=add(doc.documentElement,'diagram',{id:'current',name:graph.title});
 const model=add(page,'mxGraphModel',{}),root=add(model,'root',{});
 add(root,'mxCell',{id:'0'});add(root,'mxCell',{id:'1',parent:'0'});
 graph.groups.forEach((g,i)=>{const c=add(root,'mxCell',{id:'group-'+i,parent:'1',vertex:'1',value:g.label,style:'rounded=1;whiteSpace=wrap;verticalAlign=top;fillColor=none;strokeColor=#547587;strokeWidth='+(g.kind==='process'?3:1)+';'});add(c,'mxGeometry',{x:g.x,y:g.y,width:g.w,height:g.h,as:'geometry'});});
 graph.nodes.forEach(n=>{const c=add(root,'mxCell',{id:'node-'+n.id,parent:'1',vertex:'1',value:[n.title,...n.lines,'OS process: '+(n.process||'qbox')].join('\n'),style:'rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;'});add(c,'mxGeometry',{x:n.x,y:n.y,width:n.w,height:n.h,as:'geometry'});});
 graph.edges.forEach((e,i)=>{const c=add(root,'mxCell',{id:'edge-'+i,parent:'1',edge:'1',source:'node-'+e.a,target:'node-'+e.b,value:e.label,style:'edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor='+edgeColors[e.kind]+';'});add(c,'mxGeometry',{relative:'1',as:'geometry'});});
 return new XMLSerializer().serializeToString(doc);
}
document.getElementById('exportView').onclick=()=>{
 const url=URL.createObjectURL(new Blob([currentViewDrawio()],{type:'application/xml'}));
 const a=document.createElement('a');a.href=url;a.download='qvp-'+processMode+'.drawio';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
