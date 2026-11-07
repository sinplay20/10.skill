'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const typeNames = {statement:'叙述',definition:'定义',notation:'记号',axiom:'公理',assumption:'假设',theorem:'定理',proposition:'命题',lemma:'引理',corollary:'推论',conjecture:'猜想',example:'例子',remark:'注记',exercise:'练习',problem:'问题'};
  const colors = {statement:'#99a5b2',definition:'#bc914f',notation:'#bd9b68',axiom:'#a582a8',assumption:'#a7a088',theorem:'#5383b8',proposition:'#9179ae',lemma:'#5c968c',corollary:'#6a91b7',conjecture:'#ad7d98',example:'#a19a6b',remark:'#9aa5a8',exercise:'#a38f79',problem:'#a38f79'};
  const relationNames = {depends_on:'依赖',implies:'蕴含',equivalent_to:'等价',special_case_of:'特例',example_of:'例子',counterexample_to:'反例',related_to:'相关'};
  const symmetric = new Set(['equivalent_to','related_to']);
  const state = {doc:null,selected:4,filter:'all',query:'',limit:100,info:null,etag:null,fingerprint:'',dirty:false,showLabels:false,nodes:[],edges:[],positions:new Map(),raf:0,transform:{x:0,y:0,k:1}};
  function el(tag, attrs={}, ...children) {
    const element = document.createElement(tag);
    for (const [key,value] of Object.entries(attrs)) {
      if (key==='class') element.className=value;
      else if (key==='style') for(const [property,setting] of Object.entries(value)){if(property.startsWith('--'))element.style.setProperty(property,setting);else element.style[property]=setting;}
      else if (key.startsWith('on')) element.addEventListener(key.slice(2),value);
      else element.setAttribute(key,value);
    }
    for (const child of children.flat()) if(child!==null&&child!==undefined) element.append(typeof child==='string'?document.createTextNode(child):child);
    return element;
  }
  function svg(tag, attrs={}) {
    const element=document.createElementNS('http://www.w3.org/2000/svg',tag);
    for(const [key,value] of Object.entries(attrs)) element.setAttribute(key,value);
    return element;
  }
  function toast(message) { $('toast').textContent=message; $('toast').classList.add('show'); clearTimeout(toast.timer); toast.timer=setTimeout(()=>$('toast').classList.remove('show'),3600); }
  function math(element) {
    if(window.renderMathInElement) renderMathInElement(element,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false},{left:'$',right:'$',display:false}],throwOnError:false,trust:false,strict:'ignore',maxExpand:500});
  }
  const content = item => item.Original.content;
  const designation = item => item.Original.indexing.identifier || `${typeNames[content(item).type]} · ${item.index}`;
  const dot = kind => el('i',{class:'dot',style:{'--color':colors[kind]||colors.statement}});
  function allEdges() {return state.doc.items.flatMap(item=>item.Original.relations.map(relation=>({source:item.index,...relation})));}
  function get(index) {return state.doc.items.find(item=>item.index===index);}
  function plain(text) {return text.replace(/\\label\{[^}]*\}/g,'').replace(/\$/g,'').replace(/\\[a-zA-Z]+/g,'').replace(/[{}]/g,'').trim();}
  function displayText(text) {
    const labels=new Map();
    for(const anchor of state.doc.anchors||[]) for(const label of anchor.labels||[]) labels.set(label,anchor.index);
    return text.replace(/\\label\{[^}]*\}/g,'').replace(/\\(?:ref|autoref|eqref)\{([^}]+)\}/g,(match,label)=>labels.has(label)?designation(get(labels.get(label))):match).trim();
  }
  function matches(item) {return (state.filter==='all'||content(item).type===state.filter)&&(!state.query||`${item.Original.indexing.identifier}\n${content(item).body}\n${content(item).proof}`.toLocaleLowerCase().includes(state.query));}
  function basicValidate(data) {
    if(data?.format!=='math-document-indexed'||data.format_version!=='1.0'||!Array.isArray(data.items)||!Array.isArray(data.reading_order)||!data.source||!data.review) throw Error('需要 math-document-indexed 1.0 格式的文献 JSON');
    if(typeof data.source.title!=='string'||typeof data.source.document!=='string'||!Array.isArray(data.source.authors)||!Array.isArray(data.unresolved)||!Array.isArray(data.anchors))throw Error('来源信息、unresolved 或 anchors 格式不完整');
    const map=new Map(),expected=new Set(),seen=new Set(),bodies=[];
    for(const item of data.items) {
      if(!Number.isInteger(item.index)||item.index<1||map.has(item.index)||Object.hasOwn(item,'id')) throw Error('条目应使用唯一的正整数 index');
      const c=item.Original?.content;
      if(!c||!typeNames[c.type]||typeof c.body!=='string'||!c.body.trim()||typeof c.proof!=='string'||!Array.isArray(item.Original.relations)) throw Error(`index ${item.index} 内容格式错误`);
      if(!item.Original.indexing?.location||typeof item.Original.indexing.identifier!=='string'||item.Original.indexing.location.document!==data.source.document)throw Error(`index ${item.index} 来源或编号格式错误`);
      map.set(item.index,item); expected.add(`${item.index}:body`); if(c.proof)expected.add(`${item.index}:proof`);
    }
    for(let i=1;i<=map.size;i++)if(!map.has(i))throw Error('index 需连续编号为 1..N');
    for(const item of data.items) for(const relation of item.Original.relations) {
      if(!map.has(relation.target)||!relationNames[relation.type]||!['explicit','inferred'].includes(relation.basis)) throw Error(`index ${item.index} 含无效关系`);
    }
    for(const entry of data.reading_order) {
      const key=`${entry.index}:${entry.part}`;
      if(!expected.has(key)||seen.has(key))throw Error('阅读顺序含重复或无效的正文／证明引用');
      seen.add(key); if(entry.part==='body') bodies.push(entry.index);
    }
    if(seen.size!==expected.size||bodies.some((value,i)=>value!==i+1))throw Error('阅读顺序未完整覆盖条目，或 index 不是正文首次出现顺序');
  }
  function load(data,{dirty=false}={}) {
    basicValidate(data); state.doc=data; state.dirty=dirty; state.limit=100;
    if(!get(state.selected))state.selected=data.items[0]?.index||null;
    state.fingerprint=JSON.stringify(data);
    renderHeader(); renderFilters(); renderReader(); drawGraph(); renderSelection();
  }
  function renderHeader() {
    const source=state.doc.source, edges=allEdges();
    $('docTitle').textContent=source.title;
    $('docMeta').replaceChildren(el('span',{},source.kind==='latex'?'LATEX DOCUMENT':source.kind==='scan_pdf'?'SCANNED PDF':'PDF DOCUMENT'),el('span',{class:'badge'},'INDEXED JSON'),...(source.synthetic?[el('span',{class:'badge demo'},'虚构演示')]:[]));
    $('docSubtitle').textContent=(source.authors.length?source.authors.join(' · ')+'  /  ':'')+source.document;
    $('docStats').replaceChildren(...[[state.doc.items.length,'数学条目'],[edges.length,'条关系'],[state.doc.reading_order.filter(x=>x.part==='proof').length,'份证明']].map(([n,label])=>el('span',{},el('b',{},String(n)),label)));
    const status={draft:'结构草稿 · 待 Agent 对照原文核对',agent_checked:'文档标注：Agent 已核对',human_checked:'文档标注：人工已核对'}[state.doc.review.status]||'待核对';
    $('scopeBanner').textContent=`${status}。${source.complete?'记录范围：完整文献。':'记录范围：部分文献。'} ${state.doc.unresolved.length?'另有 '+state.doc.unresolved.length+' 项待处理。':'结构校验不代表数学内容准确，图谱不保证覆盖全部隐含上下文。'}`;
    $('saveBtn').textContent=state.dirty?'保存改动 ●':'保存到工作区';
  }
  function renderFilters() {
    const counts=new Map(); for(const item of state.doc.items) counts.set(content(item).type,(counts.get(content(item).type)||0)+1);
    const filters=[['all','全部条目',state.doc.items.length],...Object.keys(typeNames).filter(type=>counts.has(type)).map(type=>[type,typeNames[type],counts.get(type)])];
    $('typeFilters').replaceChildren(...filters.map(([type,label,count])=>el('button',{class:'filter'+(state.filter===type?' active':''),onclick:()=>{state.filter=type;state.limit=100;renderFilters();renderReader();drawGraph();}},type==='all'?el('span',{class:'dot',style:{'--color':'#8b9daf'}}):dot(type),el('span',{},label),el('span',{class:'count'},String(count)))));
  }
  function renderReader() {
    const matchesItems=state.doc.items.filter(matches), keep=new Set(matchesItems.map(item=>item.index));
    const order=state.doc.reading_order.filter(entry=>keep.has(entry.index));
    const proofPositions=new Map(state.doc.reading_order.filter(entry=>entry.part==='proof').map(entry=>[entry.index,entry]));
    $('outlineCount').textContent=String(matchesItems.length);
    $('outline').replaceChildren(...matchesItems.slice(0,250).map(item=>el('button',{class:'outline-item'+(item.index===state.selected?' active':''),onclick:()=>select(item.index)},el('span',{class:'index'},String(item.index).padStart(2,'0')),designation(item))));
    const cards=order.slice(0,state.limit).map(entry=>{
      const item=get(entry.index),c=content(item),proof=entry.part==='proof';
      const header=el('div',{class:'entry-header'},el('span',{class:'entry-type',style:{'--color':proof?'#8998a8':colors[c.type]}},dot(proof?'statement':c.type),proof?'证明':typeNames[c.type]),el('span',{class:'entry-id'},proof?`Proof of ${designation(item)}`:item.Original.indexing.identifier),el('span',{class:'entry-index'},`#${item.index}`));
      const page=entry.page||(proof?'':item.Original.indexing.location.page);
      if(page)header.append(el('span',{class:'page'},'p. '+page));
      const body=el('div',{class:'entry-body'},displayText(proof?c.proof:c.body));
      const card=el('article',{class:`entry ${proof?'proof':c.type}`+(item.index===state.selected?' selected':''),'data-index':item.index,'data-key':`${item.index}:${entry.part}`,style:{'--color':colors[c.type]},onclick:()=>select(item.index,false)},header,body);
      if(!proof&&(item.Original.relations.length||proofPositions.has(item.index))) {
        const footer=el('div',{class:'entry-footer'});
        const related=item.Original.relations.slice(0,3);
        for(const relation of related)footer.append(el('button',{onclick:event=>{event.stopPropagation();select(relation.target);}},`${relationNames[relation.type]} #${relation.target}`));
        if(proofPositions.has(item.index)) {
          const position=proofPositions.get(item.index);
          footer.append(el('button',{class:'proof-jump',onclick:event=>{event.stopPropagation();select(item.index,true,'proof');}},`查看证明${position.page?' · p.'+position.page:''} ↗`));
        }
        card.append(footer);
      }
      math(body); return card;
    });
    $('items').replaceChildren(...(cards.length?cards:[el('div',{class:'empty'},'没有匹配的条目。试试修改关键词或类型。')]));
    $('moreBtn').hidden=order.length<=state.limit;
  }
  function select(index,scroll=true,part='body') {
    const item=get(index); if(!item)return;
    state.selected=index;
    if(!matches(item)) {state.filter='all';state.query='';$('search').value='';renderFilters();}
    const order=state.doc.reading_order.filter(entry=>matches(get(entry.index)));
    const position=order.findIndex(entry=>entry.index===index&&entry.part===part);
    if(position>=state.limit)state.limit=position+20;
    renderReader(); renderSelection();
    if($('focusToggle').checked||!state.nodes.some(node=>node.id===index))drawGraph();else updateGraphSelection();
    if(scroll)document.querySelector(`[data-key="${index}:${part}"]`)?.scrollIntoView({behavior:'smooth',block:'center'});
  }
  function renderSelection() {
    const item=get(state.selected); if(!item){$('selection').replaceChildren(el('div',{class:'empty'},'选择条目以查看关系'));return;}
    const incident=allEdges().filter(edge=>edge.source===item.index||edge.target===item.index);
    const snippet=el('div',{class:'selection-snippet'},displayText(content(item).body)); math(snippet);
    $('selection').replaceChildren(el('div',{class:'selection-label'},'SELECTED ENTRY · #'+item.index),el('div',{class:'selection-title'},dot(content(item).type),designation(item)),snippet,...(incident.length?incident.slice(0,30).map(edge=>{
      const outgoing=edge.source===item.index,other=outgoing?edge.target:edge.source;
      const direction=symmetric.has(edge.type)?'↔':outgoing?'→':'←';
      return el('button',{class:'relation-row',title:edge.explanation||'',onclick:()=>select(other)},el('span',{},direction),el('span',{class:'relation-name'},relationNames[edge.type]),el('span',{},designation(get(other))),el('small',{},edge.basis==='inferred'?'推断':'明确'));
    }):[el('div',{class:'selection-snippet'},'尚未记录条目间关系。')]));
  }
  function drawGraph() {
    cancelAnimationFrame(state.raf);
    const area=$('graph'),w=$('graphArea').clientWidth,h=$('graphArea').clientHeight;
    area.setAttribute('viewBox',`0 0 ${w} ${h}`); area.replaceChildren();
    const defs=svg('defs'),marker=svg('marker',{id:'arrow',viewBox:'0 0 10 10',refX:8,refY:5,markerWidth:5,markerHeight:5,orient:'auto-start-reverse'});
    marker.append(svg('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#a2b5c8'}));defs.append(marker);area.append(defs);
    let items=state.doc.items.filter(matches),edges=allEdges();
    if($('focusToggle').checked) {const keep=new Set([state.selected]);for(const edge of edges)if(edge.source===state.selected||edge.target===state.selected){keep.add(edge.source);keep.add(edge.target);}items=items.filter(item=>keep.has(item.index));}
    const total=items.length;
    if(items.length>200) {const neighborhood=new Set([state.selected]);for(const edge of edges)if(edge.source===state.selected||edge.target===state.selected){neighborhood.add(edge.source);neighborhood.add(edge.target);}items=[...items.filter(item=>neighborhood.has(item.index)),...items.filter(item=>!neighborhood.has(item.index))].slice(0,200);}
    const ids=new Set(items.map(item=>item.index));edges=edges.filter(edge=>ids.has(edge.source)&&ids.has(edge.target));
    $('graphCount').textContent=total>200?`${items.length} / ${total} 节点`:`${items.length} 节点`;
    const group=svg('g');area.append(group);state.graphGroup=group;
    const edgeGroup=svg('g'),nodeGroup=svg('g');group.append(edgeGroup,nodeGroup);
    const degree=new Map();for(const edge of edges){degree.set(edge.source,(degree.get(edge.source)||0)+1);degree.set(edge.target,(degree.get(edge.target)||0)+1);}
    state.nodes=items.map((item,i)=>{const p=state.positions.get(item.index),a=2*Math.PI*i/Math.max(1,items.length)-Math.PI/2;return{id:item.index,item,x:p?.x??w/2+Math.cos(a)*w*.32,y:p?.y??h/2+Math.sin(a)*h*.32,vx:0,vy:0,r:13+Math.min(8,(degree.get(item.index)||0)*2)};});
    const map=new Map(state.nodes.map(node=>[node.id,node]));
    state.edges=edges.map(edge=>{const line=svg('path',{class:'graph-edge '+edge.basis,...(!symmetric.has(edge.type)?{'marker-end':'url(#arrow)'}:{})});const title=svg('title');title.textContent=`#${edge.source} ${relationNames[edge.type]} #${edge.target} · ${edge.basis==='explicit'?'原文明确':'分析推断'}\n${edge.explanation||''}`;line.append(title);edgeGroup.append(line);const label=svg('text',{class:'edge-label'});label.textContent=relationNames[edge.type];label.style.display=state.showLabels?'':'none';edgeGroup.append(label);return{...edge,a:map.get(edge.source),b:map.get(edge.target),line,label};});
    for(const node of state.nodes){
      const g=svg('g',{class:'graph-node',tabindex:0,role:'button','aria-label':`${designation(node.item)} index ${node.id}`});g.style.setProperty('--color',colors[content(node.item).type]);
      const title=svg('title');title.textContent=designation(node.item)+'\n'+plain(content(node.item).body);g.append(title,svg('circle',{class:'node-ring',r:node.r+5}),svg('circle',{class:'node-core',r:node.r}));
      const number=svg('text',{class:'node-index',y:.4});number.textContent=String(node.id);g.append(number);
      const label=svg('text',{y:node.r+17});label.textContent=node.item.Original.indexing.identifier||`${typeNames[content(node.item).type]} ${node.id}`;g.append(label);
      g.addEventListener('click',()=>{if(!node.moved)select(node.id);});g.addEventListener('keydown',event=>{if(event.key==='Enter')select(node.id);});
      g.addEventListener('pointerdown',event=>{event.stopPropagation();node.dragging=true;node.moved=false;g.setPointerCapture(event.pointerId);});
      g.addEventListener('pointermove',event=>{if(!node.dragging)return;node.moved=true;const rect=area.getBoundingClientRect(),t=state.transform;node.x=(event.clientX-rect.left-t.x)/t.k;node.y=(event.clientY-rect.top-t.y)/t.k;paintGraph();});
      g.addEventListener('pointerup',()=>{node.dragging=false;state.positions.set(node.id,{x:node.x,y:node.y});});node.element=g;nodeGroup.append(g);
    }
    state.transform={x:0,y:0,k:1};state.userMoved=false;updateGraphSelection();
    let tick=0;
    function step(){
      tick++; const nodes=state.nodes,alpha=Math.max(.05,1-tick/180);
      for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){const a=nodes[i],b=nodes[j],dx=b.x-a.x||.1,dy=b.y-a.y||.1,d=Math.hypot(dx,dy),force=Math.min(4,4300/(d*d))+(d<78?(78-d)*.035:0);const fx=dx/d*force*alpha,fy=dy/d*force*alpha;a.vx-=fx;a.vy-=fy;b.vx+=fx;b.vy+=fy;}
      for(const edge of state.edges){const dx=edge.b.x-edge.a.x,dy=edge.b.y-edge.a.y,d=Math.hypot(dx,dy)||1,force=(d-112)*.009*alpha;edge.a.vx+=dx/d*force;edge.a.vy+=dy/d*force;edge.b.vx-=dx/d*force;edge.b.vy-=dy/d*force;}
      for(const node of nodes){node.vx+=(w/2-node.x)*.0015*alpha;node.vy+=(h/2-node.y)*.0015*alpha;if(!node.dragging){node.vx*=.77;node.vy*=.77;node.x+=node.vx;node.y+=node.vy;}state.positions.set(node.id,{x:node.x,y:node.y});}
      paintGraph();if(tick===120&&!state.userMoved)fitGraph();if(tick<180)state.raf=requestAnimationFrame(step);
    }
    step();
  }
  function paintGraph() {
    for(const node of state.nodes)node.element.setAttribute('transform',`translate(${node.x},${node.y})`);
    for(const edge of state.edges){const dx=edge.b.x-edge.a.x,dy=edge.b.y-edge.a.y,d=Math.hypot(dx,dy)||1;const sx=edge.a.x+dx/d*(edge.a.r+2),sy=edge.a.y+dy/d*(edge.a.r+2),tx=edge.b.x-dx/d*(edge.b.r+5),ty=edge.b.y-dy/d*(edge.b.r+5);edge.line.setAttribute('d',`M${sx},${sy} L${tx},${ty}`);edge.label.setAttribute('x',(sx+tx)/2);edge.label.setAttribute('y',(sy+ty)/2-4);}
    applyTransform();
  }
  function updateGraphSelection() {for(const node of state.nodes)node.element.classList.toggle('selected',node.id===state.selected);for(const edge of state.edges){const active=edge.source===state.selected||edge.target===state.selected;edge.line.classList.toggle('highlighted',active);edge.line.classList.toggle('dimmed',!active);}}
  function applyTransform(){const t=state.transform;state.graphGroup?.setAttribute('transform',`translate(${t.x},${t.y}) scale(${t.k})`);}
  function fitGraph(){if(!state.nodes.length)return;const w=$('graphArea').clientWidth,h=$('graphArea').clientHeight;const minX=Math.min(...state.nodes.map(n=>n.x))-65,maxX=Math.max(...state.nodes.map(n=>n.x))+65,minY=Math.min(...state.nodes.map(n=>n.y))-50,maxY=Math.max(...state.nodes.map(n=>n.y))+55;const k=Math.min(1.3,(w-25)/(maxX-minX),(h-50)/(maxY-minY));state.transform={k,x:(w-(maxX-minX)*k)/2-minX*k,y:(h-(maxY-minY)*k)/2-minY*k};applyTransform();}
  function download(data,name,type='application/json'){const url=URL.createObjectURL(new Blob([data],{type})),a=el('a',{href:url,download:name});a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  async function post(route,data){const response=await fetch(route,{method:'POST',headers:{'Content-Type':'application/json',...(state.etag?{'If-Match':state.etag}:{})},body:JSON.stringify(data)});if(!response.ok){let message='请求未完成';try{message=(await response.json()).error||message;}catch{}throw Error(message);}return response;}
  $('search').addEventListener('input',event=>{state.query=event.target.value.trim().toLocaleLowerCase();state.limit=100;renderReader();drawGraph();});
  $('clearFilters').onclick=()=>{state.filter='all';state.query='';$('search').value='';state.limit=100;renderFilters();renderReader();drawGraph();};
  $('moreBtn').onclick=()=>{state.limit+=100;renderReader();};
  $('focusToggle').onchange=drawGraph;
  $('fitBtn').onclick=fitGraph;
  $('labelsBtn').onclick=()=>{state.showLabels=!state.showLabels;$('labelsBtn').textContent=state.showLabels?'隐藏关系名':'显示关系名';for(const edge of state.edges)edge.label.style.display=state.showLabels?'':'none';};
  $('openBtn').onclick=()=>$('fileInput').click();
  $('fileInput').onchange=async event=>{const file=event.target.files[0];if(!file)return;try{load(JSON.parse(await file.text()),{dirty:true});toast('文档已载入；可导出或保存到当前工作区。');}catch(error){toast(error.message);}event.target.value='';};
  $('exportBtn').onclick=()=>download(JSON.stringify(state.doc,null,2)+'\n','document.indexed.json');
  $('saveBtn').onclick=async()=>{try{const response=await post('/api/save',state.doc);state.etag=response.headers.get('ETag');state.dirty=false;state.fingerprint=JSON.stringify(state.doc);renderHeader();toast('已校验并保存到本地工作区。');}catch(error){toast(error.message);}};
  $('submitBtn').onclick=async()=>{try{$('submitBtn').disabled=true;const response=await post('/api/submission',state.doc);download(await response.blob(),'mathdoc-submission.zip','application/zip');toast('已导出仓库待导入包：包含 index JSON 与实际结构校验记录。');}catch(error){toast(error.message);}finally{$('submitBtn').disabled=false;}};
  $('jsonBtn').onclick=()=>{$('jsonEditor').value=JSON.stringify(state.doc,null,2);$('jsonError').textContent='';$('jsonDialog').showModal();};
  $('closeJson').onclick=()=>$('jsonDialog').close();
  $('applyJson').onclick=()=>{try{load(JSON.parse($('jsonEditor').value),{dirty:true});$('jsonDialog').close();toast('改动已载入；保存或导出前将再次校验。');}catch(error){$('jsonError').textContent=error.message;}};
  $('sourceBtn').onclick=async()=>{if(!state.info?.source_available){toast('当前没有关联原文件；启动 view 时可用 --source 指定 PDF／TeX。');return;}if(state.info.source_sha256&&state.info.source_sha256!==state.doc.source.sha256){toast('当前 JSON 与关联原文件的 SHA-256 不一致，请用 --source 关联正确文献。');return;}try{$('sourceContent').replaceChildren();if(state.info.source_path.toLowerCase().endsWith('.pdf'))$('sourceContent').append(el('iframe',{src:'/source',title:'来源 PDF'}));else $('sourceContent').append(el('pre',{},await (await fetch('/source')).text()));$('sourceDialog').showModal();}catch(error){toast(error.message);}};
  $('closeSource').onclick=()=>$('sourceDialog').close();
  $('agentBtn').onclick=async()=>{const info=state.info;const text=`使用 math-document-indexer skill：${info?.skill_path||''}\n对照来源：${info?.source_path||state.doc.source.document}\n核对并完善 index 文档：${info?.document_path||'document.indexed.json'}\n保持 id + Original 的 Original 结构，条目标识使用 index；证明附属于条目，reading_order 保留原文位置。核对类型、原文编号和 explicit/inferred 关系，不编造缺失内容。完成后运行 validate 并刷新网页。需要提交仓库时先导出待导入稿；正式入库使用独立 plan-import 步骤。`;
    try{await navigator.clipboard.writeText(text);toast('Agent 任务已复制，粘贴到当前 Agent 对话即可。');}catch{toast('剪贴板不可用；请按 SKILL.md 中的流程处理。');}
  };
  let pan=null;
  $('graph').addEventListener('pointerdown',event=>{if(event.target.closest('.graph-node'))return;pan={x:event.clientX,y:event.clientY,tx:state.transform.x,ty:state.transform.y};$('graph').setPointerCapture(event.pointerId);});
  $('graph').addEventListener('pointermove',event=>{if(!pan)return;state.userMoved=true;state.transform.x=pan.tx+event.clientX-pan.x;state.transform.y=pan.ty+event.clientY-pan.y;applyTransform();});
  $('graph').addEventListener('pointerup',()=>{pan=null;});
  $('graph').addEventListener('wheel',event=>{event.preventDefault();const rect=$('graph').getBoundingClientRect(),t=state.transform,x=event.clientX-rect.left,y=event.clientY-rect.top,k=Math.max(.15,Math.min(4,t.k*Math.exp(-event.deltaY*.0015)));state.transform={k,x:x-(x-t.x)*k/t.k,y:y-(y-t.y)*k/t.k};state.userMoved=true;applyTransform();},{passive:false});
  let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(state.doc)drawGraph();},200);});
  async function refresh(){try{const response=await fetch('/api/document');if(!response.ok)throw Error((await response.json()).error);const data=await response.json(),fingerprint=JSON.stringify(data);if(!state.doc){state.etag=response.headers.get('ETag');load(data);}else if(fingerprint!==state.fingerprint&&!state.dirty){state.etag=response.headers.get('ETag');load(data);toast('已载入 Agent 更新后的文档。');}}catch(error){if(!state.doc){$('docTitle').textContent='文档载入失败';$('scopeBanner').textContent=error.message;toast(error.message);}}}
  fetch('/api/info').then(r=>r.json()).then(info=>{state.info=info;}).catch(()=>{});
  refresh();setInterval(refresh,4500);
  window.mathdocWorkbench={getDocument:()=>structuredClone(state.doc),select,validate:basicValidate};
})();
