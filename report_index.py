"""JS del Tab de Index ES vs FdS - Etapa 2.

Formula del volumen (correcta):
  Vol = SUM(precio_dia_i) x rotaciones_upc
  Index = (SUM_Vol_FdS - SUM_Vol_ES) / SUM_Vol_ES
  Donde SUM_Vol es la suma de volumenes de todos los UPCs comparables.
"""

JS_INDEX = r"""
// ==============================================================
// TAB INDEX  Etapa 2: Index FdS vs Entre Semana
// var (no const) -> evita TDZ cuando renderAll se llama antes
// de que este modulo termine de ejecutarse
// ==============================================================
var IDX = (function(){
  'use strict';

  // ============================================================
  // UTILIDADES
  // ============================================================
  function safeNum(v){
    return (v !== null && v !== undefined && v !== '' && isFinite(+v)) ? +v : null;
  }
  function capIdx(v, lo, hi){
    const n = safeNum(v);
    if(n === null) return null;
    return (n < lo || n > hi) ? null : n;
  }

  // ============================================================
  // FILTRADO Y MAPEO DE DATOS
  // ============================================================
  function fqIdx(){
    return RAW_IDX
      .filter(r =>{
        if(fPais && r.pais !== fPais)       return false;
        if(fComp && r.competidor !== fComp) return false;
        return true;
      })
      .map(r =>({
        pais:        r.pais,
        competidor:  r.competidor,
        ano:         +r.ano,
        sw:          +r.sw,

        upcs_comparables: +(r.upcs_comparables || 0),
        total_rotaciones: +(r.total_rotaciones || 0),

        // Precios promedio de referencia
        p_normal_es:  safeNum(r.avg_precio_normal_es),
        p_normal_fds: safeNum(r.avg_precio_normal_fds),
        p_oferta_es:  safeNum(r.avg_precio_oferta_es),
        p_oferta_fds: safeNum(r.avg_precio_oferta_fds),
        p_mayoreo_es: safeNum(r.avg_precio_mayoreo_es),
        p_mayoreo_fds:safeNum(r.avg_precio_mayoreo_fds),

        // Cobertura: dias promedio con precio por segmento
        dias_normal_es:   safeNum(r.avg_dias_normal_es)  || 0,
        dias_normal_fds:  safeNum(r.avg_dias_normal_fds) || 0,
        dias_oferta_es:   safeNum(r.avg_dias_oferta_es)  || 0,
        dias_oferta_fds:  safeNum(r.avg_dias_oferta_fds) || 0,
        dias_mayoreo_es:  safeNum(r.avg_dias_mayoreo_es) || 0,
        dias_mayoreo_fds: safeNum(r.avg_dias_mayoreo_fds)|| 0,

        // Volumenes agregados
        vol_normal_es:  safeNum(r.vol_normal_es),
        vol_normal_fds: safeNum(r.vol_normal_fds),
        vol_oferta_es:  safeNum(r.vol_oferta_es),
        vol_oferta_fds: safeNum(r.vol_oferta_fds),
        vol_mayoreo_es: safeNum(r.vol_mayoreo_es),
        vol_mayoreo_fds:safeNum(r.vol_mayoreo_fds),

        // INDEX = (Vol_FdS - Vol_ES) / Vol_ES
        index_normal:  capIdx(r.index_normal,  -2, 2),
        index_oferta:  capIdx(r.index_oferta,  -2, 2),
        index_mayoreo: capIdx(r.index_mayoreo, -2, 2),

        // Clasificacion de UPCs
        upcs_fds_barato_normal:  +(r.upcs_fds_barato_normal  || 0),
        upcs_fds_caro_normal:    +(r.upcs_fds_caro_normal    || 0),
        upcs_fds_barato_oferta:  +(r.upcs_fds_barato_oferta  || 0),
        upcs_fds_caro_oferta:    +(r.upcs_fds_caro_oferta    || 0),
        upcs_fds_barato_mayoreo: +(r.upcs_fds_barato_mayoreo || 0),
        upcs_fds_caro_mayoreo:   +(r.upcs_fds_caro_mayoreo   || 0)
      }));
  }

  // ============================================================
  // HELPERS DE PRESENTACION
  // ============================================================
  function swLabel(ano, sw){
    return 'SW' + String(sw).padStart(2,'0') + "'" + String(ano).slice(2);
  }
  function sortBySW(rows){
    return [...rows].sort((a,b) => a.ano !== b.ano ? a.ano - b.ano : a.sw - b.sw);
  }
  function topComps(rows, n){
    if(fComp) return [fComp];
    const m = {};
    rows.forEach(r =>{ m[r.competidor] = (m[r.competidor]||0) + r.upcs_comparables; });
    return Object.entries(m).sort((a,b)=>b[1]-a[1]).slice(0,n).map(x=>x[0]);
  }
  function listSWs(rows){
    return [...new Set(sortBySW(rows).map(r => r.ano+'-'+r.sw))];
  }
  function fieldAvg(rows, field){
    const v = rows.map(r=>r[field]).filter(v=>v!==null&&isFinite(v));
    return v.length ? v.reduce((a,b)=>a+b,0)/v.length : null;
  }
  function fieldSum(rows, field){
    return rows.reduce((s,r)=>s+(r[field]||0),0);
  }

  const PAL = ['#0053e2','#ea1100','#2a8703','#7c3aed','#f97316','#10b981',
               '#e11d48','#3b82f6','#84cc16','#f59e0b','#06b6d4','#8b5cf6'];

  // ============================================================
  // MOTOR DE GRAFICAS BIPOLAR (soporta valores negativos)
  // Eje Y en % (valores vienen como fraccion: -0.05 = -5%)
  // ============================================================
  function getCanvas(id){
    const cv = document.getElementById(id);
    if(!cv) return null;
    const dpr = window.devicePixelRatio || 1;
    const W   = (cv.parentElement ? cv.parentElement.offsetWidth : 0) || 700;
    const H   = cv.offsetHeight || 320;
    cv.width  = W * dpr;  cv.height = H * dpr;
    cv.style.width = W+'px'; cv.style.height = H+'px';
    const ctx = cv.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.clearRect(0,0,W,H);
    return {cv, ctx, W, H};
  }

  function niceBound(vals){
    const hi0 = Math.max(...vals.filter(isFinite), 0.02);
    const lo0 = Math.min(...vals.filter(isFinite), -0.02);
    const round5 = v => Math.ceil(Math.abs(v)/0.05)*0.05*(v<0?-1:1);
    return {lo: round5(lo0), hi: round5(hi0)};
  }

  function bipolarAxes(ctx, pad, W, H, lo, hi){
    const pH = H - pad.t - pad.b, pW = W - pad.l - pad.r;
    const range = hi - lo;
    const zero_y = pad.t + pH * (hi / range);
    const steps = [-0.30,-0.25,-0.20,-0.15,-0.10,-0.05,0,0.05,0.10,0.15,0.20,0.25,0.30]
      .filter(v => v >= lo*1.05 && v <= hi*1.05);
    ctx.save();
    ctx.font = '9px sans-serif'; ctx.textAlign = 'right'; ctx.fillStyle='#6b7280';
    steps.forEach(v =>{
      const y = pad.t + pH*((hi-v)/range);
      ctx.strokeStyle = v===0 ? '#374151' : '#e5e7eb';
      ctx.lineWidth   = v===0 ? 1.5 : 0.7;
      ctx.beginPath(); ctx.moveTo(pad.l,y); ctx.lineTo(W-pad.r,y); ctx.stroke();
      ctx.fillStyle = v===0 ? '#374151' : '#6b7280';
      ctx.fillText((v*100).toFixed(0)+'%', pad.l-4, y+3);
    });
    ctx.restore();
    return {pH, pW, zero_y, range};
  }

  function bipolarXLabels(ctx, labels, pad, W, H){
    const pW = W-pad.l-pad.r;
    const step = labels.length>1 ? pW/(labels.length-1) : pW;
    const rot  = labels.length > 8;
    ctx.save(); ctx.font='9px sans-serif'; ctx.fillStyle='#6b7280';
    labels.forEach((lbl,i)=>{
      const x = pad.l + i*step, y = H-pad.b+12;
      ctx.save();
      if(rot){ ctx.translate(x,y); ctx.rotate(Math.PI/4); ctx.textAlign='left'; }
      else   { ctx.textAlign='center'; ctx.translate(x,y); }
      ctx.fillText(lbl,0,0); ctx.restore();
    });
    ctx.restore();
  }

  function bipolarLegend(ctx, datasets, W, H, padR){
    const legX = W-padR+8; let ly = 30;
    ctx.save(); ctx.font='10px sans-serif'; ctx.textAlign='left';
    datasets.forEach((ds,i)=>{
      const c = ds.color||PAL[i%PAL.length];
      ctx.fillStyle=c; ctx.globalAlpha=0.9;
      ctx.fillRect(legX, ly-8, 14, 10);
      ctx.globalAlpha=1; ctx.fillStyle='#374151';
      const lbl = ds.label.length>18 ? ds.label.slice(0,16)+'..' : ds.label;
      ctx.fillText(lbl, legX+17, ly); ly+=16;
    });
    ctx.restore();
  }

  function bipolarTitle(ctx, ttl, W, padR){
    ctx.save(); ctx.fillStyle='#1a1a2e'; ctx.font='bold 12px sans-serif';
    ctx.textAlign='center'; ctx.fillText(ttl,(W-padR)/2,14); ctx.restore();
  }

  // ── Tooltip global compartido (reutiliza el de VC si existe) ──────
  function showTipIDX(html, ex, ey){
    let t = document.getElementById('vc-tip');
    if(!t){ t=document.createElement('div'); t.id='vc-tip'; document.body.appendChild(t); }
    t.innerHTML = html;
    t.style.display = 'block';
    const vw=window.innerWidth, vh=window.innerHeight;
    let tx=ex+18, ty=ey-12;
    if(tx+260>vw) tx=ex-268;
    if(ty+180>vh) ty=ey-190;
    t.style.left=tx+'px'; t.style.top=ty+'px';
  }
  function hideTipIDX(){
    const t=document.getElementById('vc-tip'); if(t) t.style.display='none';
  }

  // ── Barras bipolares con hover-band + multi-serie tooltip + labels ───
  function biBar(id, {labels, datasets, ttl}){
    const cv = document.getElementById(id); if(!cv) return;
    const dpr = window.devicePixelRatio||1;
    const W   = (cv.parentElement?cv.parentElement.offsetWidth:0)||700;
    const H   = cv.offsetHeight||320;
    cv.width=W*dpr; cv.height=H*dpr;
    cv.style.width=W+'px'; cv.style.height=H+'px';
    const ctx = cv.getContext('2d'); ctx.scale(dpr,dpr);
    const legW = Math.min(180,W*0.28);
    const pad  = {t:22, b:labels.length>7?90:52, l:42, r:legW};
    const allV = datasets.flatMap(d=>d.data||[]).filter(v=>v!==null&&isFinite(v));
    if(!allV.length) return;
    const {lo,hi} = niceBound(allV);
    const pH  = H-pad.t-pad.b, pW = W-pad.l-pad.r;
    const nG=labels.length, nS=datasets.length;
    const gW=pW/nG;
    const bW=Math.max(3, Math.min(nS>1?gW*0.8/nS:gW*0.6, 30));

    // Precompute rects by group index
    const byIdx = labels.map(()=>[]);
    datasets.forEach((ds,di)=>{
      const c = ds.color||PAL[di%PAL.length];
      (ds.data||[]).forEach((v,i)=>{
        if(v===null||!isFinite(v)) return;
        const bx = nS>1
          ? pad.l+i*gW+(di-(nS-1)/2)*bW+gW/2-bW/2
          : pad.l+i*gW+(gW-bW)/2;
        byIdx[i].push({bx, c, v, ds:ds.label||''});
      });
    });

    function paint(hovIdx){
      ctx.clearRect(0,0,W,H);
      const {zero_y,range} = bipolarAxes(ctx,pad,W,H,lo,hi);

      // Hover band
      if(hovIdx!==null){
        ctx.save();
        ctx.fillStyle='rgba(0,83,226,0.07)';
        ctx.fillRect(pad.l+hovIdx*gW, pad.t, gW, pH);
        ctx.restore();
      }

      byIdx.forEach((grp,gi)=>{
        grp.forEach(h=>{
          const bh = Math.abs((h.v/range)*pH);
          const by = h.v>=0 ? zero_y-bh : zero_y;
          ctx.fillStyle=h.c;
          ctx.globalAlpha = hovIdx===null||hovIdx===gi ? 0.87 : 0.28;
          ctx.fillRect(h.bx, by, bW-1, bh);

          // Value label on hover
          if(hovIdx===gi){
            ctx.globalAlpha=1;
            ctx.fillStyle='#1a1a2e'; ctx.font='bold 9px sans-serif'; ctx.textAlign='center';
            const pct = (h.v*100).toFixed(1)+'%';
            const ly2 = h.v>=0 ? by-3 : by+bh+11;
            ctx.fillText(pct, h.bx+bW/2, ly2);
          }
        });
      });
      ctx.globalAlpha=1;
      bipolarXLabels(ctx,labels,pad,W,H);
      bipolarTitle(ctx,ttl,W,legW);
      bipolarLegend(ctx,datasets,W,H,legW);
    }

    paint(null);

    cv.style.cursor='crosshair';
    cv.onmousemove=function(e){
      const rect=cv.getBoundingClientRect();
      const mx=e.clientX-rect.left;
      const idx=Math.floor((mx-pad.l)/gW);
      if(idx<0||idx>=labels.length){ paint(null); hideTipIDX(); return; }
      paint(idx);
      let html=`<b style="color:#ffc220">${labels[idx]}</b>`;
      byIdx[idx].forEach(h=>{
        const c=h.c;
        const pct=(h.v>=0?'+':''+(h.v*100).toFixed(2)+'%');
        html+=`<br><span style="color:${c}">&#9632;</span> ${h.ds}: <b>${(h.v*100).toFixed(2)}%</b>`;
      });
      showTipIDX(html, e.clientX, e.clientY);
    };
    cv.onmouseleave=()=>{ paint(null); hideTipIDX(); };
  }

  // ── Lineas bipolares con crosshair + multi-serie tooltip + labels en puntos ───
  function biLine(id, {labels, datasets, ttl}){
    const cv = document.getElementById(id); if(!cv) return;
    const dpr = window.devicePixelRatio||1;
    const W   = (cv.parentElement?cv.parentElement.offsetWidth:0)||700;
    const H   = cv.offsetHeight||320;
    cv.width=W*dpr; cv.height=H*dpr;
    cv.style.width=W+'px'; cv.style.height=H+'px';
    const ctx = cv.getContext('2d'); ctx.scale(dpr,dpr);
    const legW = Math.min(180,W*0.28);
    const pad  = {t:22, b:labels.length>8?90:52, l:42, r:legW};
    const allV = datasets.flatMap(d=>d.data||[]).filter(v=>v!==null&&isFinite(v));
    if(!allV.length) return;
    const {lo,hi} = niceBound(allV);
    const pH  = H-pad.t-pad.b, pW = W-pad.l-pad.r;
    const step = labels.length>1 ? pW/(labels.length-1) : pW;

    // Mostrar labels en puntos cuando hay pocos puntos y pocas series
    const showLabels = labels.length <= 14 && datasets.length <= 5;

    // Precompute puntos por dataset
    const ptsByDs = datasets.map((ds,di)=>{
      const c = ds.color||PAL[di%PAL.length];
      return (ds.data||[]).map((v,i)=>{
        const {zero_y, range} = (() => {
          // mini-calc zero_y sin ctx (solo necesitamos los coords)
          const r2 = hi-lo; const zy = pad.t+pH*(hi/r2);
          return {zero_y:zy, range:r2};
        })();
        return {
          x: pad.l+i*step,
          y: (v!==null&&isFinite(v)) ? pad.t+pH*((hi-v)/(hi-lo)) : null,
          v, lbl:labels[i]||'', c, ds:ds.label||''
        };
      });
    });

    function paint(hovIdx){
      ctx.clearRect(0,0,W,H);
      bipolarAxes(ctx,pad,W,H,lo,hi);

      // Crosshair vertical
      if(hovIdx!==null){
        const hx = pad.l+hovIdx*step;
        ctx.save();
        ctx.strokeStyle='rgba(55,65,81,0.30)'; ctx.lineWidth=1.2;
        ctx.setLineDash([5,4]);
        ctx.beginPath(); ctx.moveTo(hx,pad.t); ctx.lineTo(hx,pad.t+pH); ctx.stroke();
        ctx.setLineDash([]);
        ctx.restore();
      }

      datasets.forEach((ds,di)=>{
        const pts = ptsByDs[di];
        const c   = ds.color||PAL[di%PAL.length];
        ctx.save();
        ctx.strokeStyle=c; ctx.lineWidth=2; ctx.globalAlpha=0.9;
        ctx.beginPath();
        let started=false;
        pts.forEach(p=>{
          if(!p.y||!isFinite(p.y)){ started=false; return; }
          if(!started){ ctx.moveTo(p.x,p.y); started=true; }
          else ctx.lineTo(p.x,p.y);
        });
        ctx.stroke();
        ctx.fillStyle=c;
        pts.forEach((p,i)=>{
          if(!p.y||!isFinite(p.y)) return;
          const isHov = hovIdx===i;
          const r2 = isHov ? 7 : 4;
          ctx.globalAlpha=1;
          ctx.beginPath(); ctx.arc(p.x,p.y,r2,0,Math.PI*2); ctx.fill();

          // Anillo blanco en hover
          if(isHov){
            ctx.save();
            ctx.strokeStyle='#fff'; ctx.lineWidth=2;
            ctx.beginPath(); ctx.arc(p.x,p.y,r2,0,Math.PI*2); ctx.stroke();
            ctx.restore();
          }

          // Data label en punto
          if(showLabels && p.v!==null && isFinite(p.v)){
            const lbl = (p.v*100).toFixed(1)+'%';
            ctx.save();
            ctx.font = isHov?'bold 10px sans-serif':'bold 9px sans-serif';
            const tw = ctx.measureText(lbl).width;
            // Fondo semitransparente para legibilidad
            ctx.fillStyle='rgba(255,255,255,0.85)';
            ctx.fillRect(p.x-tw/2-2, p.y-20, tw+4, 13);
            ctx.fillStyle = isHov?'#1a1a2e':c;
            ctx.textAlign='center';
            ctx.fillText(lbl, p.x, p.y-10);
            ctx.restore();
          }
        });
        ctx.restore();
      });
      ctx.globalAlpha=1;
      bipolarXLabels(ctx,labels,pad,W,H);
      bipolarTitle(ctx,ttl,W,legW);
      bipolarLegend(ctx,datasets,W,H,legW);
    }

    paint(null);
    cv.style.cursor='crosshair';

    cv.onmousemove=function(e){
      const rect=cv.getBoundingClientRect();
      const mx=e.clientX-rect.left;
      if(mx<pad.l-15||mx>W-pad.r+15){ paint(null); hideTipIDX(); return; }
      const raw=(mx-pad.l)/(step||1);
      const idx=Math.max(0,Math.min(labels.length-1, Math.round(raw)));
      paint(idx);
      // Tooltip multi-serie
      let html=`<b style="color:#ffc220">${labels[idx]||''}</b>`;
      datasets.forEach((ds,di)=>{
        const c = ds.color||PAL[di%PAL.length];
        const v = (ds.data||[])[idx];
        if(v!==null&&v!==undefined&&isFinite(v)){
          const pct=(v*100).toFixed(2)+'%';
          const arr=v<-0.001?'\u25bc':v>0.001?'\u25b2':'—';
          html+=`<br><span style="color:${c}">&#9679;</span> ${ds.label||''}: <b>${arr} ${pct}</b>`;
        }
      });
      showTipIDX(html, e.clientX, e.clientY);
    };
    cv.onmouseleave=()=>{ paint(null); hideTipIDX(); };
  }

  // ============================================================
  // RENDERIZADORES
  // ============================================================

  function renderKPIs(data){
    const vN = data.filter(r=>r.index_normal!==null);
    const vO = data.filter(r=>r.index_oferta!==null);
    const vM = data.filter(r=>r.index_mayoreo!==null);
    const avgN = vN.length ? fieldSum(vN,'index_normal') /vN.length*100 : 0;
    const avgO = vO.length ? fieldSum(vO,'index_oferta') /vO.length*100 : 0;
    const avgM = vM.length ? fieldSum(vM,'index_mayoreo')/vM.length*100 : 0;
    const totUPC = fieldSum(data,'upcs_comparables');
    const totRot = fieldSum(data,'total_rotaciones');
    const bajaN  = [...new Set(data.filter(r=>r.index_normal!==null&&r.index_normal<-0.02).map(r=>r.competidor))];

    const set  = (id,txt)=>{ const e=document.getElementById(id); if(e) e.textContent=txt; };
    const setC = (id,c)  =>{ const e=document.getElementById(id); if(e) e.className=c; };

    set('kpi_idx_n', (avgN>0?'+':'')+avgN.toFixed(2)+'%');
    setC('kpi_idx_n','kpi-val '+(avgN<0?'pos':'neg'));
    set('kpi_idx_o', (avgO>0?'+':'')+avgO.toFixed(2)+'%');
    setC('kpi_idx_o','kpi-val '+(avgO<0?'pos':'neg'));
    set('kpi_idx_m', (avgM>0?'+':'')+avgM.toFixed(2)+'%');
    setC('kpi_idx_m','kpi-val '+(avgM<0?'pos':'neg'));
    set('kpi_upcs',           totUPC.toLocaleString());
    set('kpi_rot',            (totRot/1e6).toFixed(2)+'M');
    set('kpi_comps_baja',     bajaN.length+' competidores');
    set('kpi_comps_baja_list',bajaN.slice(0,5).join(', ')+(bajaN.length>5?'...':''));
  }

  // G1: Index Normal por semana (lineas bipolares)
  function renderIdxNormal(data){
    const sws    = listSWs(data);
    const labels = sws.map(s=>{ const[a,w]=s.split('-').map(Number); return swLabel(a,w); });
    const comps  = topComps(data,12);
    biLine('c_idx_normal',{
      labels, ttl:'Index Normal FdS vs ES por Semana  (- = FdS mas barato)',
      datasets: comps.map((c,i)=>({
        label:c, color:PAL[i%PAL.length],
        data: sws.map(s=>{
          const[a,w]=s.split('-').map(Number);
          const row=data.find(r=>r.competidor===c&&r.ano===a&&r.sw===w);
          return row&&row.index_normal!==null?row.index_normal:0;
        })
      }))
    });
  }

  // G2: Index Oferta por semana
  function renderIdxOferta(data){
    const sws    = listSWs(data);
    const labels = sws.map(s=>{ const[a,w]=s.split('-').map(Number); return swLabel(a,w); });
    const comps  = topComps(data,12);
    biLine('c_idx_oferta',{
      labels, ttl:'Index Oferta FdS vs ES por Semana',
      datasets: comps.map((c,i)=>({
        label:c, color:PAL[i%PAL.length],
        data: sws.map(s=>{
          const[a,w]=s.split('-').map(Number);
          const row=data.find(r=>r.competidor===c&&r.ano===a&&r.sw===w);
          return row&&row.index_oferta!==null?row.index_oferta:0;
        })
      }))
    });
  }

  // G3: Index Mayoreo por semana
  function renderIdxMayoreo(data){
    const withM  = data.filter(r=>r.index_mayoreo!==null);
    if(!withM.length) return;
    const sws    = listSWs(withM);
    const labels = sws.map(s=>{ const[a,w]=s.split('-').map(Number); return swLabel(a,w); });
    const comps  = topComps(withM,12);
    biLine('c_idx_mayoreo',{
      labels, ttl:'Index Mayoreo FdS vs ES por Semana',
      datasets: comps.map((c,i)=>({
        label:c, color:PAL[i%PAL.length],
        data: sws.map(s=>{
          const[a,w]=s.split('-').map(Number);
          const row=withM.find(r=>r.competidor===c&&r.ano===a&&r.sw===w);
          return row&&row.index_mayoreo!==null?row.index_mayoreo:0;
        })
      }))
    });
  }

  // G4: Cobertura de dias de checkeo ES vs FdS (clave para detectar ausencia de precios FdS)
  function renderCobertura(data){
    const comps  = topComps(data,14);
    const esN    = comps.map(c=>fieldAvg(data.filter(r=>r.competidor===c),'dias_normal_es')  ||0);
    const fdsN   = comps.map(c=>fieldAvg(data.filter(r=>r.competidor===c),'dias_normal_fds') ||0);
    const esO    = comps.map(c=>fieldAvg(data.filter(r=>r.competidor===c),'dias_oferta_es')  ||0);
    const fdsO   = comps.map(c=>fieldAvg(data.filter(r=>r.competidor===c),'dias_oferta_fds') ||0);
    // Barras agrupadas: dias checkeo ES vs FdS por tipo de precio
    VC.bar(document.getElementById('c_idx_cobertura'),{
      labels:comps,
      datasets:[
        {label:'Normal ES (dias prom)',  color:'#0053e2', data:esN},
        {label:'Normal FdS (dias prom)', color:'#60a5fa', data:fdsN},
        {label:'Oferta ES (dias prom)',  color:'#f97316', data:esO},
        {label:'Oferta FdS (dias prom)', color:'#fcd34d', data:fdsO}
      ],
      ttl:'Cobertura de Checkeos: dias con precio ES vs FdS por Competidor'
    });
  }

  // G5: Precios promedios ES vs FdS por competidor (siempre positivos)
  function renderPrecioESFdS(data){
    const comps = topComps(data,12);
    VC.bar(document.getElementById('c_idx_precio'),{
      labels:comps,
      datasets:[
        {label:'Normal ES',  color:'#0053e2', data:comps.map(c=>fieldAvg(data.filter(r=>r.competidor===c),'p_normal_es')  ||0)},
        {label:'Normal FdS', color:'#ffc220', data:comps.map(c=>fieldAvg(data.filter(r=>r.competidor===c),'p_normal_fds') ||0)}
      ],
      ttl:'Precio Normal Promedio: Entre Semana vs Fin de Semana'
    });
  }

  // G6: Distribucion de UPCs barato/igual/caro
  function renderUpcDist(data){
    const comps  = topComps(data,12);
    const bN     = comps.map(c=>fieldSum(data.filter(r=>r.competidor===c),'upcs_fds_barato_normal'));
    const cN     = comps.map(c=>fieldSum(data.filter(r=>r.competidor===c),'upcs_fds_caro_normal'));
    const igual  = comps.map((c,i)=>Math.max(0,
      fieldSum(data.filter(r=>r.competidor===c),'upcs_comparables') - bN[i] - cN[i]));
    VC.bar(document.getElementById('c_idx_upcs'),{
      labels:comps,
      datasets:[
        {label:'FdS mas barato (<-1%)', color:'#2a8703', data:bN},
        {label:'Precio igual (+-1%)',   color:'#6b7280', data:igual},
        {label:'FdS mas caro  (>+1%)', color:'#ea1100', data:cN}
      ],
      ttl:'UPCs: FdS mas barato / igual / mas caro en Normal (acumulado)'
    });
  }

  // G7: Index por pais (barras bipolares)
  function renderIdxPais(data){
    const paises = fPais?[fPais]:[...new Set(data.map(r=>r.pais))].sort();
    biBar('c_idx_pais',{
      labels:paises,
      ttl:'Index Promedio por Pais  (- = FdS mas barato)',
      datasets:[
        {label:'Index Normal',  color:'#0053e2', data:paises.map(p=>fieldAvg(data.filter(r=>r.pais===p),'index_normal') ||0)},
        {label:'Index Oferta',  color:'#f97316', data:paises.map(p=>fieldAvg(data.filter(r=>r.pais===p&&r.index_oferta!==null),'index_oferta') ||0)},
        {label:'Index Mayoreo', color:'#2a8703', data:paises.map(p=>fieldAvg(data.filter(r=>r.pais===p&&r.index_mayoreo!==null),'index_mayoreo')||0)}
      ]
    });
  }

  // Tabla detalle
  function renderTablaIdx(data){
    const tbody = document.getElementById('tb_idx_body');
    if(!tbody) return;
    tbody.innerHTML = '';

    const fmtIdx = v=>{
      if(v===null||v===undefined) return "<span style='color:#9ca3af'>N/D</span>";
      const pct=(v*100).toFixed(2);
      const cls=v<-0.01?'neg':v>0.01?'pos':'neu';
      const arr=v<-0.01?'\u25bc':v>0.01?'\u25b2':'';
      return `<span class='${cls}'>${arr} ${pct}%</span>`;
    };
    const fmtP=(es,fds)=>{
      if(!es||!fds) return '-';
      const d=((fds-es)/es*100).toFixed(1);
      const cls=fds<es*0.99?'pos':fds>es*1.01?'neg':'neu';
      return `${fds.toLocaleString(undefined,{maximumFractionDigits:2})} <span class='${cls}'>(${+d>0?'+':''}${d}%)</span>`;
    };
    const fmt2=v=>v!==null?v.toLocaleString(undefined,{maximumFractionDigits:2}):'-';
    const fmtD=v=>v?v.toFixed(1):'-';

    sortBySW(data).forEach(r=>{
      const tr = document.createElement('tr');
      tr.innerHTML=[
        `<td>${r.pais}</td>`,
        `<td><b>${r.competidor}</b></td>`,
        `<td>${swLabel(r.ano,r.sw)}</td>`,
        `<td class='tr'>${r.upcs_comparables.toLocaleString()}</td>`,
        `<td class='tr'>${r.total_rotaciones.toLocaleString(undefined,{maximumFractionDigits:0})}</td>`,
        // Cobertura dias
        `<td class='tr'>${fmtD(r.dias_normal_es)}</td>`,
        `<td class='tr'>${fmtD(r.dias_normal_fds)}</td>`,
        // Normal
        `<td class='tr'>${fmt2(r.p_normal_es)}</td>`,
        `<td class='tr'>${fmtP(r.p_normal_es,r.p_normal_fds)}</td>`,
        `<td class='tr'>${fmtIdx(r.index_normal)}</td>`,
        // Oferta
        `<td class='tr'>${fmt2(r.p_oferta_es)}</td>`,
        `<td class='tr'>${fmtP(r.p_oferta_es,r.p_oferta_fds)}</td>`,
        `<td class='tr'>${fmtIdx(r.index_oferta)}</td>`,
        // Mayoreo
        `<td class='tr'>${fmt2(r.p_mayoreo_es)}</td>`,
        `<td class='tr'>${fmtP(r.p_mayoreo_es,r.p_mayoreo_fds)}</td>`,
        `<td class='tr'>${fmtIdx(r.index_mayoreo)}</td>`,
        // UPCs clasificados
        `<td class='tr' style='color:#2a8703'>${r.upcs_fds_barato_normal.toLocaleString()}</td>`,
        `<td class='tr' style='color:#ea1100'>${r.upcs_fds_caro_normal.toLocaleString()}</td>`
      ].join('');
      tbody.appendChild(tr);
    });
  }

  // ============================================================
  // PUNTO DE ENTRADA
  // ============================================================
  return {
    render(){
      try{
        const data = fqIdx();
        if(!data.length){
          console.warn('[IDX] Sin datos. RAW_IDX.length=',RAW_IDX.length,'fPais=',fPais,'fComp=',fComp);
          return;
        }
        console.log('[IDX] OK -', data.length,'filas,',
          [...new Set(data.map(r=>r.competidor))].length,'competidores,',
          'index_normal samples:',data.slice(0,3).map(r=>r.index_normal));
        renderKPIs(data);
        renderIdxNormal(data);
        renderIdxOferta(data);
        renderIdxMayoreo(data);
        renderCobertura(data);
        renderPrecioESFdS(data);
        renderUpcDist(data);
        renderIdxPais(data);
        renderTablaIdx(data);
      }catch(err){
        console.error('[IDX] Error en render:',err);
      }
    }
  };

}());
"""
