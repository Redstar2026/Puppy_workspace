"""Logica de la app CAM: filtros, renders y exports."""

JS_APP = r"""
// ==============================================================
// APP — Datos, filtros, renders
// ==============================================================
// FIX: excluir datos fuera del rango Ago-2025 a Mar-2026
function validPeriodo(r){
  if(r.ano < 2025 || r.ano > 2026) return false;
  if(r.ano === 2025 && r.mes < 8)  return false;
  if(r.ano === 2026 && r.mes > 3)  return false;
  return true;
}

const Q1 = RAW_Q1.filter(validPeriodo);
const Q3 = RAW_Q3.filter(validPeriodo);

const MES_N={1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'};
function mesKey(a,m){ return a*100+m; }
function mesLabel(a,m){ return (MES_N[m]||m)+' '+String(a).slice(2); }

let fPais='', fComp='', fMes='';
let dailyType='normal', caidaType='normal', trendSeg='ambos', trendType='normal';

function fq1(){ return Q1.filter(r=>(!fPais||r.pais===fPais)&&(!fComp||r.competidor===fComp)&&(!fMes||r.ano+'-'+r.mes===fMes)); }
function fq3(){ return Q3.filter(r=>(!fPais||r.pais===fPais)&&(!fComp||r.competidor===fComp)&&(!fMes||r.ano+'-'+r.mes===fMes)); }

function sum(rows,field){ return rows.reduce((s,r)=>s+(r[field]||0),0); }
function topN(rows,key,n=12,field='cnt_precio_normal'){
  const m={}; rows.forEach(r=>{ m[r[key]]=(m[r[key]]||0)+(r[field]||0); });
  return Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,n).map(x=>x[0]);
}

function sortPeriodos(data){
  return [...new Set(data.map(r=>r.ano+'-'+r.mes))]
    .sort((a,b)=>{ const[ay,am]=a.split('-').map(Number),[by,bm]=b.split('-').map(Number);
      return mesKey(ay,am)-mesKey(by,bm); });
}
function sortSemanas(data){
  return [...new Set(data.map(r=>r.ano+'-'+r.mes+'-'+r.semana))]
    .sort((a,b)=>{ const p=a.split('-').map(Number),q=b.split('-').map(Number);
      return (mesKey(p[0],p[1])*100+p[2])-(mesKey(q[0],q[1])*100+q[2]); });
}

// ---------- FILTROS ----------
function initFilters(){
  const paises=[...new Set(Q3.map(r=>r.pais))].sort();
  const comps=[...new Set(Q3.map(r=>r.competidor))].sort();
  const sp=document.getElementById('flt-pais'), sc=document.getElementById('flt-comp');
  paises.forEach(p=>{const o=document.createElement('option');o.value=p;o.textContent=p;sp.appendChild(o);});
  comps.forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=c;sc.appendChild(o);});
}

function applyFilters(){
  fPais=document.getElementById('flt-pais').value;
  fComp=document.getElementById('flt-comp').value;
  fMes=document.getElementById('flt-mes').value;
  renderAll();
}
function resetFilters(){
  fPais='';fComp='';fMes='';
  ['flt-pais','flt-comp','flt-mes'].forEach(id=>document.getElementById(id).value='');
  renderAll();
}

// ---------- TABS ----------
function showTab(id,btn){
  document.querySelectorAll('.tab-pane').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}

// ---------- PILLS ----------
function setPill(el){ el.parentElement.querySelectorAll('.fpill').forEach(p=>p.classList.remove('on')); el.classList.add('on'); }
function setDailyType(v,el){ dailyType=v; setPill(el); renderTab2(); }
function setCaidaType(v,el){ caidaType=v; setPill(el); renderTab4(); }
function setTrendSeg(v,el){ trendSeg=v; setPill(el); renderTab6(); }
function setTrendType(v,el){ trendType=v; setPill(el); renderTab6(); }

// ---------- CSV EXPORT ----------
function exportCSV(tid,fname){
  const t=document.getElementById(tid); if(!t) return;
  const csv=[...t.querySelectorAll('tr')].map(r=>[...r.querySelectorAll('th,td')].map(c=>'"'+c.innerText.replace(/"/g,'""')+'"').join(',')).join('\n');
  const a=document.createElement('a'); a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv); a.download=fname; a.click();
}

// ==============================================================
// TAB 1 – Conteos Semanales
// ==============================================================
function renderTab1(){
  const data=fq1();
  const sws=sortSemanas(data);
  const labels=sws.map(s=>{const[a,m,w]=s.split('-').map(Number);return mesLabel(a,m)+' W'+w;});

  function swVals(seg,field){
    return sws.map(s=>{
      const[a,m,w]=s.split('-').map(Number);
      return sum(data.filter(r=>r.ano===a&&r.mes===m&&r.semana===w&&r.segmento===seg),field);
    });
  }

  VC.bar(document.getElementById('c_sw_n'),{labels,datasets:[
    {label:'Entre Semana',color:'#0053e2',data:swVals('Entre Semana','cnt_precio_normal')},
    {label:'Fin de Semana',color:'#ffc220',data:swVals('Fin de Semana','cnt_precio_normal')}],
    ttl:'Precio Normal por Semana'});
  VC.bar(document.getElementById('c_sw_o'),{labels,datasets:[
    {label:'Oferta ES', color:'#0053e2',data:swVals('Entre Semana','cnt_precio_oferta')},
    {label:'Oferta FdS',color:'#ffc220',data:swVals('Fin de Semana','cnt_precio_oferta')}],
    ttl:'Precio Oferta por Semana'});
  VC.bar(document.getElementById('c_sw_m'),{labels,datasets:[
    {label:'Mayoreo ES', color:'#2a8703',data:swVals('Entre Semana','cnt_mayoreo')},
    {label:'Mayoreo FdS',color:'#f97316',data:swVals('Fin de Semana','cnt_mayoreo')}],
    ttl:'Precio Mayoreo por Semana'});

  const tbody=document.getElementById('tb_sw_body'); tbody.innerHTML='';
  data.slice(0,600).forEach(r=>{
    const sc=r.segmento==='Entre Semana'?'#0053e2':'#ffc220', st=r.segmento==='Entre Semana'?'#fff':'#1a1a1a';
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${mesLabel(r.ano,r.mes)}</td><td>W${r.semana}</td><td>${r.pais}</td>
      <td><b>${r.competidor}</b></td>
      <td><span class='pill' style='background:${sc};color:${st}'>${r.segmento==='Entre Semana'?'ES':'FdS'}</span></td>
      <td>${r.dia_semana||''}</td>
      <td class='tr'>${(r.cnt_precio_normal||0).toLocaleString()}</td>
      <td class='tr'>${(r.cnt_precio_oferta||0).toLocaleString()}</td>
      <td class='tr'>${(r.cnt_mayoreo||0).toLocaleString()}</td>`;
    tbody.appendChild(tr);
  });
  const el=document.getElementById('total-info');
  if(el) el.textContent='Filas: '+data.length.toLocaleString()+' | Total Normal: '+sum(data,'cnt_precio_normal').toLocaleString();
}

// ==============================================================
// TAB 2 – Tendencia Diaria (canvas manual con colores por barra)
// ==============================================================
const DIAS=['Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo'];
const DIA_COLORS=['#0053e2','#0053e2','#0053e2','#0053e2','#ffc220','#ffc220','#ffc220'];

function renderTab2(){
  const data=fq1();
  const field={normal:'cnt_precio_normal',oferta:'cnt_precio_oferta',mayoreo:'cnt_mayoreo'}[dailyType]||'cnt_precio_normal';
  const vals=DIAS.map(d=>sum(data.filter(r=>r.dia_semana===d),field));
  const cv=document.getElementById('c_day'); if(!cv) return;
  const dpr=window.devicePixelRatio||1;
  const W=cv.parentElement.offsetWidth||600, H=cv.offsetHeight||350;
  cv.width=W*dpr; cv.height=H*dpr;
  const ctx=cv.getContext('2d'); ctx.scale(dpr,dpr);
  ctx.clearRect(0,0,W,H);
  const maxV=Math.max(...vals,1);
  const pad={t:34,b:50,l:65,r:22};
  const pH=H-pad.t-pad.b, pW=W-pad.l-pad.r;
  // grid
  ctx.strokeStyle='#e5e7eb'; ctx.lineWidth=.8;
  for(let i=0;i<=5;i++){ const y=pad.t+pH-(i/5)*pH; ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(W-pad.r,y);ctx.stroke(); }
  // y-axis labels
  ctx.fillStyle='#9ca3af';ctx.font='10px sans-serif';ctx.textAlign='right';
  for(let i=0;i<=5;i++){ const y=pad.t+pH-(i/5)*pH; const v=Math.round(maxV*i/5); ctx.fillText(v>=1000?(v/1000).toFixed(1)+'K':v,pad.l-5,y+3); }
  // bars + hit areas
  const gW=pW/DIAS.length, bW=gW*.68, hits=[];
  vals.forEach((v,i)=>{
    ctx.fillStyle=DIA_COLORS[i];ctx.globalAlpha=.87;
    const bx=pad.l+i*gW+(gW-bW)/2, bH=v/maxV*pH, by=pad.t+pH-bH;
    ctx.fillRect(bx,by,bW,bH);
    ctx.globalAlpha=1;ctx.fillStyle='#374151';ctx.font='bold 9px sans-serif';ctx.textAlign='center';
    if(v>0) ctx.fillText(v>=1000?(v/1000).toFixed(1)+'K':v,bx+bW/2,by-4);
    hits.push({x:bx,y:by,w:bW,h:bH,v,lbl:DIAS[i],ds:'Conteo '+dailyType});
  });
  ctx.fillStyle='#6b7280';ctx.font='10px sans-serif';ctx.textAlign='center';
  DIAS.forEach((d,i)=>ctx.fillText(d,pad.l+(i+.5)*gW,H-pad.b+16));
  ctx.fillStyle='#1a1a2e';ctx.font='bold 12px sans-serif';ctx.textAlign='center';
  ctx.fillText('Conteo '+dailyType.toUpperCase()+' por Dia (Azul=ES, Amarillo=FdS)',W/2,16);
  ctx.fillStyle='#0053e2';ctx.fillRect(W-185,H-20,11,11);
  ctx.fillStyle='#374151';ctx.font='10px sans-serif';ctx.textAlign='left';ctx.fillText('Entre Semana',W-171,H-11);
  ctx.fillStyle='#ffc220';ctx.fillRect(W-80,H-20,11,11);
  ctx.fillText('Fin de Semana',W-66,H-11);
  if(!cv.id) cv.id='c_day';
  VC['_REG']||Object.defineProperty(VC,'_REG',{value:{}}); // not needed
  // attach tooltip via same REG in VC closure
  cv._vc_hits=hits;
  cv.onmousemove=function(e){
    const rect=cv.getBoundingClientRect(), mx=e.clientX-rect.left, my=e.clientY-rect.top;
    let found=null;
    for(const h of hits){ if(mx>=h.x&&mx<=h.x+h.w&&my>=h.y&&my<=h.y+h.h){found=h;break;} }
    if(found){
      const tip=document.getElementById('vc-tip');
      tip.innerHTML=`<b>${found.lbl}</b><br>Tipo: <b>${dailyType.toUpperCase()}</b><br>Valor: <b>${found.v.toLocaleString()}</b>`;
      tip.style.display='block';
      let tx=e.clientX+16, ty=e.clientY-10;
      if(tx+250>window.innerWidth) tx=e.clientX-255;
      tip.style.left=tx+'px'; tip.style.top=ty+'px';
    } else { document.getElementById('vc-tip').style.display='none'; }
  };
  cv.onmouseleave=()=>{ document.getElementById('vc-tip').style.display='none'; };

  const esT=sum(data.filter(r=>r.segmento==='Entre Semana'),field);
  const fdT=sum(data.filter(r=>r.segmento==='Fin de Semana'),field);
  VC.donut(document.getElementById('c_day_pie'),{labels:['Entre Semana','Fin de Semana'],data:[esT,fdT],colors:['#0053e2','#ffc220'],ttl:'Distribucion ES vs FdS'});
}

// ==============================================================
// TAB 3 – Por Mes / Pais / Competidor
// ==============================================================
const CPAL=['#0053e2','#ea1100','#2a8703','#7c3aed','#f97316','#10b981','#e11d48','#3b82f6','#84cc16','#f59e0b'];

function renderTab3(){
  const data=fq3();
  const ps=sortPeriodos(data);
  const labels=ps.map(p=>{const[a,m]=p.split('-').map(Number);return mesLabel(a,m);});
  const comps=fComp?[fComp]:topN(data,'competidor',10,'cnt_precio_normal');

  function mkDS(field){
    return comps.flatMap((c,i)=>[
      {label:c+' ES',color:CPAL[i%CPAL.length],dashed:false,
        data:ps.map(p=>{const[a,m]=p.split('-').map(Number);return sum(data.filter(r=>r.competidor===c&&r.ano===a&&r.mes===m&&r.segmento==='Entre Semana'),field);})},
      {label:c+' FdS',color:CPAL[i%CPAL.length],dashed:true,
        data:ps.map(p=>{const[a,m]=p.split('-').map(Number);return sum(data.filter(r=>r.competidor===c&&r.ano===a&&r.mes===m&&r.segmento==='Fin de Semana'),field);})}
    ]);
  }
  VC.line(document.getElementById('c_mes_n'),{labels,datasets:mkDS('cnt_precio_normal'),ttl:'Precio Normal por Mes (solida=ES, discontinua=FdS)'});
  VC.line(document.getElementById('c_mes_o'),{labels,datasets:mkDS('cnt_precio_oferta'),ttl:'Precio Oferta por Mes'});
  VC.line(document.getElementById('c_mes_m'),{labels,datasets:mkDS('cnt_mayoreo'),ttl:'Precio Mayoreo por Mes'});
}

// ==============================================================
// TAB 4 – Caida FdS
// ==============================================================
function renderTab4(){
  const data=fq3();
  const ps=sortPeriodos(data);
  const labels=ps.map(p=>{const[a,m]=p.split('-').map(Number);return mesLabel(a,m);});
  const field={normal:'cnt_precio_normal',oferta:'cnt_precio_oferta',mayoreo:'cnt_mayoreo'}[caidaType]||'cnt_precio_normal';
  const comps=fComp?[fComp]:topN(data.filter(r=>r.segmento==='Fin de Semana'),'competidor',15,field);
  const CPAL2=['#0053e2','#ea1100','#2a8703','#7c3aed','#f97316','#10b981','#e11d48','#3b82f6','#84cc16','#f59e0b','#06b6d4','#8b5cf6','#ec4899','#14b8a6','#fb923c'];
  VC.line(document.getElementById('c_caida'),{labels,
    datasets:comps.map((c,i)=>({
      label:c, color:CPAL2[i%CPAL2.length],
      data:ps.map(p=>{const[a,m]=p.split('-').map(Number);return sum(data.filter(r=>r.competidor===c&&r.ano===a&&r.mes===m&&r.segmento==='Fin de Semana'),field);})
    })),ttl:'Conteo FdS '+caidaType.toUpperCase()+' por Mes (Top 15)'});

  const q1=fq1(), allSws=sortSemanas(q1);
  const pairs=[...new Set(q1.map(r=>r.pais+'||'+r.competidor))].sort();
  const tbody=document.getElementById('tb_caida_body'); tbody.innerHTML='';
  pairs.forEach(pair=>{
    const[pais,comp]=pair.split('||');
    let zN=0,zO=0,zM=0,total=0;
    allSws.forEach(s=>{
      const[a,m,w]=s.split('-').map(Number);
      const es=q1.filter(r=>r.pais===pais&&r.competidor===comp&&r.ano===a&&r.mes===m&&r.semana===w&&r.segmento==='Entre Semana');
      const fd=q1.filter(r=>r.pais===pais&&r.competidor===comp&&r.ano===a&&r.mes===m&&r.semana===w&&r.segmento==='Fin de Semana');
      if(!es.length&&!fd.length) return;
      total++;
      if(!sum(fd,'cnt_precio_normal')) zN++;
      if(!sum(fd,'cnt_precio_oferta')) zO++;
      if(!sum(fd,'cnt_mayoreo'))       zM++;
    });
    if(!total) return;
    const pct=Math.round(zN/total*100), cls=pct>70?'neg':pct>30?'neu':'pos';
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${pais}</td><td><b>${comp}</b></td>
      <td class='tr ${pct>50?"neg":""}'>${zN}/${total}</td>
      <td class='tr'>${zO}/${total}</td><td class='tr'>${zM}/${total}</td>
      <td class='tr'>${total}</td><td class='tr ${cls}'>${pct}%</td>`;
    tbody.appendChild(tr);
  });
}

// ==============================================================
// TAB 5 – Deltas MoM
// ==============================================================
function renderTab5(){
  const data=fq3();
  const ps=sortPeriodos(data);
  const labels=ps.map(p=>{const[a,m]=p.split('-').map(Number);return mesLabel(a,m);});
  const comps=fComp?[fComp]:topN(data,'competidor',8,'cnt_precio_normal');
  VC.line(document.getElementById('c_mom'),{labels,
    datasets:comps.map((c,i)=>({
      label:c, color:CPAL[i%CPAL.length],
      data:ps.map(p=>{const[a,m]=p.split('-').map(Number);return sum(data.filter(r=>r.competidor===c&&r.ano===a&&r.mes===m),'cnt_precio_normal');})
    })),ttl:'Evolucion Mensual Precio Normal (Top 8)'});

  const pairs=[...new Set(data.map(r=>r.pais+'||'+r.competidor))].sort();
  const tbody=document.getElementById('tb_mom_body'); tbody.innerHTML='';
  pairs.forEach(pair=>{
    const[pais,comp]=pair.split('||');
    ['Entre Semana','Fin de Semana'].forEach(seg=>{
      let prev=null;
      ps.forEach(p=>{
        const[a,m]=p.split('-').map(Number);
        const rows=data.filter(r=>r.pais===pais&&r.competidor===comp&&r.ano===a&&r.mes===m&&r.segmento===seg);
        const cN=sum(rows,'cnt_precio_normal'), cO=sum(rows,'cnt_precio_oferta'), cM=sum(rows,'cnt_mayoreo');
        const d=(cur,prv)=>prv&&prv>0?{t:((cur-prv)/prv*100).toFixed(1),c:cur>prv?'pos':cur<prv?'neg':'neu'}:{t:null,c:'neu'};
        const dN=d(cN,prev?.cN), dO=d(cO,prev?.cO), dM=d(cM,prev?.cM);
        const fmt=x=>x.t!==null?(x.t>0?'+':'')+x.t+'%':'&mdash;';
        const sc=seg==='Entre Semana'?'#0053e2':'#ffc220', st=seg==='Entre Semana'?'#fff':'#1a1a1a';
        const tr=document.createElement('tr');
        tr.innerHTML=`<td>${pais}</td><td><b>${comp}</b></td><td>${mesLabel(a,m)}</td>
          <td><span class='pill' style='background:${sc};color:${st}'>${seg==='Entre Semana'?'ES':'FdS'}</span></td>
          <td class='tr'>${cN.toLocaleString()}</td><td class='tr ${dN.c}'>${fmt(dN)}</td>
          <td class='tr'>${cO.toLocaleString()}</td><td class='tr ${dO.c}'>${fmt(dO)}</td>
          <td class='tr'>${cM.toLocaleString()}</td><td class='tr ${dM.c}'>${fmt(dM)}</td>`;
        tbody.appendChild(tr); prev={cN,cO,cM};
      });
    });
  });
}

// ==============================================================
// TAB 6 – Tendencias por Competidor
// ==============================================================
function renderTab6(){
  const data=fq3();
  const ps=sortPeriodos(data);
  const labels=ps.map(p=>{const[a,m]=p.split('-').map(Number);return mesLabel(a,m);});
  const field={normal:'cnt_precio_normal',oferta:'cnt_precio_oferta',mayoreo:'cnt_mayoreo'}[trendType]||'cnt_precio_normal';
  const comps=fComp?[fComp]:topN(data,'competidor',12,field);
  const CPAL3=['#0053e2','#ea1100','#2a8703','#7c3aed','#f97316','#10b981','#e11d48','#3b82f6','#84cc16','#f59e0b','#06b6d4','#8b5cf6'];

  function segF(r){ if(trendSeg==='es') return r.segmento==='Entre Semana'; if(trendSeg==='fds') return r.segmento==='Fin de Semana'; return true; }

  VC.line(document.getElementById('c_trend'),{labels,
    datasets:comps.map((c,i)=>({
      label:c+' '+(trendSeg==='es'?'ES':trendSeg==='fds'?'FdS':'ES+FdS'), color:CPAL3[i%CPAL3.length],
      data:ps.map(p=>{const[a,m]=p.split('-').map(Number);return sum(data.filter(r=>r.competidor===c&&r.ano===a&&r.mes===m&&segF(r)),field);})
    })),ttl:'Tendencia '+trendType.toUpperCase()+' - '+(trendSeg==='ambos'?'ES+FdS':trendSeg==='es'?'Entre Semana':'Fin de Semana')});

  const lastP=ps[ps.length-1];
  if(lastP){
    const[la,lm]=lastP.split('-').map(Number);
    VC.bar(document.getElementById('c_trend_esfd'),{labels:comps,
      datasets:[
        {label:'Entre Semana',color:'#0053e2',data:comps.map(c=>sum(data.filter(r=>r.competidor===c&&r.ano===la&&r.mes===lm&&r.segmento==='Entre Semana'),field))},
        {label:'Fin de Semana',color:'#ffc220',data:comps.map(c=>sum(data.filter(r=>r.competidor===c&&r.ano===la&&r.mes===lm&&r.segmento==='Fin de Semana'),field))}
      ],ttl:'ES vs FdS en '+mesLabel(la,lm)+' - '+trendType.toUpperCase()});
  }
}

// ==============================================================
// RENDER ALL
// ==============================================================
function renderAll(){
  renderTab1(); renderTab2(); renderTab3();
  renderTab4(); renderTab5(); renderTab6();
  // IDX se define despues en JS_INDEX; var+try-catch evita TDZ ReferenceError
  try { if(typeof IDX !== 'undefined' && IDX) IDX.render(); } catch(e) {}
}

initFilters();
renderAll();
"""
