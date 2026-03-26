"""CSS + libreria Canvas con soporte de tooltips hover."""

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#f0f4ff;color:#1a1a2e;padding:14px}
h1{font-size:21px}h2{font-size:14px;color:#1a1a2e}h3{font-size:12px;color:#374151}
.hdr{background:#0053e2;color:#fff;padding:14px 18px;border-radius:12px;margin-bottom:14px;
     display:flex;align-items:center;gap:12px}
.hdr h1{color:#fff;font-size:20px}
.hdr-sub{font-size:11px;color:#b3c9ff;margin-top:2px}
.badge{padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700}
.badge-es{background:#fff;color:#0053e2}
.badge-fds{background:#ffc220;color:#1a1a1a}
.card{background:#fff;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.07);padding:18px;margin-bottom:14px}
.tabs{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px}
.tab-btn{padding:7px 15px;border:1.5px solid #d1d5db;border-radius:8px;cursor:pointer;
  background:#fff;color:#374151;font-size:12px;font-weight:600;transition:all .15s}
.tab-btn:hover{border-color:#0053e2;color:#0053e2}
.tab-btn.active{background:#0053e2;color:#fff;border-color:#0053e2}
.tab-pane{display:none}.tab-pane.active{display:block}
.filters{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;padding:14px;background:#fff;
  border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.07);margin-bottom:14px}
.flt-group{display:flex;flex-direction:column;gap:4px}
.flt-label{font-size:11px;font-weight:700;color:#374151}
select{border:1.5px solid #d1d5db;border-radius:7px;padding:6px 10px;font-size:13px;
  background:#fff;color:#1a1a2e;cursor:pointer;min-width:150px}
select:focus{outline:none;border-color:#0053e2}
.btn-reset{background:#f3f4f6;border:1.5px solid #d1d5db;border-radius:7px;
  padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer;color:#374151}
.btn-reset:hover{background:#e5e7eb}
.btn-export{background:#2a8703;color:#fff;border:none;border-radius:7px;
  padding:6px 13px;font-size:12px;font-weight:600;cursor:pointer}
.btn-export:hover{background:#1f6502}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
.cv-wrap{position:relative;width:100%}
.cc {width:100%;height:350px;display:block;cursor:crosshair}
.cc-lg{width:100%;height:430px;display:block;cursor:crosshair}
.cc-sm{width:100%;height:280px;display:block;cursor:crosshair}
.sec-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.tbl-wrap{overflow-x:auto;max-height:380px}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:#0053e2;color:#fff;padding:7px 9px;text-align:left;white-space:nowrap;position:sticky;top:0}
td{padding:5px 9px;border-bottom:1px solid #f0f4ff}
tr:hover td{background:#f0f4ff}
.tr{text-align:right}
.pill{display:inline-block;padding:1px 8px;border-radius:99px;font-size:11px;font-weight:600}
.pos{color:#2a8703;font-weight:700}.neg{color:#ea1100;font-weight:700}.neu{color:#6b7280;font-weight:700}
.info-bar{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;
  padding:8px 14px;font-size:11px;color:#1d4ed8;margin-bottom:10px}
.filter-pills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.fpill{padding:4px 12px;border-radius:99px;font-size:11px;font-weight:600;cursor:pointer;
  border:1.5px solid #0053e2;color:#0053e2;background:#fff;transition:all .12s}
.fpill.on{background:#0053e2;color:#fff}
#total-info{font-size:11px;color:#6b7280;margin-left:auto;align-self:center}
#vc-tip{position:fixed;pointer-events:none;z-index:9999;display:none;
  background:rgba(15,23,42,.92);color:#fff;padding:8px 12px;border-radius:8px;
  font-size:12px;line-height:1.6;max-width:240px;box-shadow:0 4px 16px rgba(0,0,0,.3);
  border:1px solid rgba(255,255,255,.1)}
#vc-tip b{color:#ffc220}
.kpi-val{font-size:22px;font-weight:800;color:#0053e2}
.kpi-val.pos{color:#2a8703}
.kpi-val.neg{color:#ea1100}
"""

JS_LIB = r"""
// ==============================================================
// VC — Vanilla Canvas mini-chart library with hover tooltips
// ==============================================================
const VC = (function(){
  const PAL=['#0053e2','#ea1100','#2a8703','#7c3aed','#f97316',
    '#10b981','#e11d48','#3b82f6','#84cc16','#f59e0b',
    '#06b6d4','#8b5cf6','#ec4899','#14b8a6','#fb923c',
    '#ffc220','#00b0b9','#a855f7','#22c55e','#374151'];

  // Tooltip element
  const tip = document.createElement('div');
  tip.id = 'vc-tip';
  document.body.appendChild(tip);

  function showTip(html, ex, ey){
    tip.innerHTML = html;
    tip.style.display = 'block';
    const vw = window.innerWidth, vh = window.innerHeight;
    let tx = ex + 16, ty = ey - 10;
    if(tx + 250 > vw) tx = ex - 250;
    if(ty + 120 > vh) ty = ey - 130;
    tip.style.left = tx + 'px';
    tip.style.top  = ty + 'px';
  }
  function hideTip(){ tip.style.display = 'none'; }

  // Registry: canvasId -> {type, hits[]}
  const REG = {};

  function attachHover(cv, type){
    cv.onmousemove = function(e){
      const rect = cv.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const entry = REG[cv.id];
      if(!entry){ hideTip(); return; }
      if(type === 'bar'){
        let found = null;
        for(const h of entry.hits){
          if(mx >= h.x && mx <= h.x+h.w && my >= h.y && my <= h.y+h.h){ found=h; break; }
        }
        if(found){
          const val = found.v >= 1000 ? found.v.toLocaleString() : found.v;
          showTip(`<b>${found.ds}</b><br>${found.lbl}<br>Valor: <b>${val}</b>`, e.clientX, e.clientY);
        } else hideTip();
      } else if(type === 'line'){
        let best = null, bestD = 22;
        for(const h of entry.hits){
          const d = Math.sqrt((mx-h.x)**2 + (my-h.y)**2);
          if(d < bestD){ bestD=d; best=h; }
        }
        if(best){
          const val = best.v >= 1000 ? best.v.toLocaleString() : best.v;
          showTip(`<b>${best.ds}</b><br>${best.lbl}<br>Valor: <b>${val}</b>`, e.clientX, e.clientY);
        } else hideTip();
      }
    };
    cv.onmouseleave = hideTip;
  }

  function setup(cv){
    const dpr = window.devicePixelRatio||1;
    const W = cv.parentElement ? cv.parentElement.offsetWidth||600 : 600;
    const H = cv.offsetHeight||350;
    cv.width = W*dpr; cv.height = H*dpr;
    const ctx = cv.getContext('2d');
    ctx.scale(dpr, dpr);
    return {ctx, W, H};
  }

  function niceMax(v){ if(!v||v<=0) return 10; const e=Math.pow(10,Math.floor(Math.log10(v))); return Math.ceil(v/e)*e||10; }
  function yW(max){ return Math.max(52, String(Math.round(max)).length*7+12); }
  function fmtV(v){ return v>=1000000?(v/1000000).toFixed(1)+'M':v>=1000?(v/1000).toFixed(1)+'K':v.toLocaleString(); }

  function drawGrid(ctx,pad,W,H,maxV,nG=5){
    const {t,b,l,r}=pad, pH=H-t-b;
    ctx.save(); ctx.strokeStyle='#e5e7eb'; ctx.lineWidth=0.8;
    ctx.fillStyle='#9ca3af'; ctx.font='10px sans-serif'; ctx.textAlign='right';
    for(let i=0;i<=nG;i++){
      const y=t+pH-(i/nG)*pH;
      ctx.beginPath();ctx.moveTo(l,y);ctx.lineTo(W-r,y);ctx.stroke();
      ctx.fillText(fmtV(Math.round(maxV*i/nG)), l-5, y+3);
    }
    ctx.restore();
  }

  function drawXLabels(ctx,labels,pad,W,H,rotate){
    const {t,b,l,r}=pad, pH=H-t-b, pW=W-l-r;
    ctx.save(); ctx.fillStyle='#6b7280'; ctx.font='9px sans-serif';
    const step=pW/labels.length;
    labels.forEach((lbl,i)=>{
      const x=l+(i+.5)*step;
      ctx.save(); ctx.translate(x, t+pH+(rotate?8:14));
      if(rotate) ctx.rotate(-Math.PI*0.38);
      ctx.textAlign=rotate?'right':'center';
      ctx.fillText(lbl,0,0);
      ctx.restore();
    });
    ctx.restore();
  }

  function drawLegend(ctx,datasets,pad,W){
    const rx=W-pad.r+10; let ry=pad.t+2;
    const mxW=pad.r-16;
    ctx.save();
    datasets.forEach((ds,i)=>{
      const c=ds.color||PAL[i%PAL.length];
      if(ds.dashed){
        ctx.strokeStyle=c;ctx.lineWidth=2;ctx.setLineDash([5,3]);ctx.globalAlpha=.8;
        ctx.beginPath();ctx.moveTo(rx,ry+5);ctx.lineTo(rx+14,ry+5);ctx.stroke();
        ctx.setLineDash([]);
      } else {
        ctx.fillStyle=c;ctx.globalAlpha=.85;ctx.fillRect(rx,ry,14,10);
      }
      ctx.globalAlpha=1;ctx.fillStyle='#374151';ctx.font='9px sans-serif';ctx.textAlign='left';
      const words=(ds.label||'').split(' ');
      let line='',ly=ry+9;
      words.forEach(w=>{
        const t2=line+(line?' ':'')+w;
        if(ctx.measureText(t2).width>mxW&&line){ctx.fillText(line,rx+17,ly);line=w;ly+=10;}
        else line=t2;
      });
      ctx.fillText(line,rx+17,ly);
      ry=ly+10;
    });
    ctx.restore();
  }

  function drawTitle(ctx,txt,W,padR){
    ctx.save();ctx.fillStyle='#1a1a2e';ctx.font='bold 12px sans-serif';
    ctx.textAlign='center';ctx.fillText(txt,(W-padR)/2,16);ctx.restore();
  }

  return {
    bar(cv, {labels, datasets, ttl='', grouped=true}){
      if(!cv||!datasets||!datasets.length) return;
      const {ctx,W,H} = setup(cv);
      ctx.clearRect(0,0,cv.width,cv.height);
      const legW = Math.min(200,W*.32);
      const rotate = labels.length > 7;
      const allVals = datasets.flatMap(d=>d.data||[0]);
      const maxV = niceMax(Math.max(...allVals, 0));
      const pad = {t:34, b:rotate?92:52, l:yW(maxV), r:legW};
      drawGrid(ctx,pad,W,H,maxV);
      drawXLabels(ctx,labels,pad,W,H,rotate);
      const pH=H-pad.t-pad.b, pW=W-pad.l-pad.r;
      const nG=labels.length, nS=datasets.length;
      const gW=pW/nG;
      const bW=Math.max(3, Math.min(grouped?gW*.82/nS:gW*.72, grouped?36:64));
      const hits=[];
      datasets.forEach((ds,di)=>{
        const c=ds.color||PAL[di%PAL.length];
        ctx.fillStyle=c; ctx.globalAlpha=.86;
        (ds.data||[]).forEach((v,i)=>{
          let bx;
          if(grouped) bx=pad.l+i*gW+(di-(nS-1)/2)*bW+gW/2-bW/2;
          else        bx=pad.l+i*gW+(gW-bW)/2;
          const bH=v/maxV*pH;
          const by=pad.t+pH-bH;
          ctx.fillRect(bx, by, bW-1, bH);
          hits.push({x:bx, y:by, w:bW-1, h:bH, v, lbl:labels[i]||'', ds:ds.label||''});
        });
      });
      ctx.globalAlpha=1;
      drawTitle(ctx,ttl,W,pad.r);
      drawLegend(ctx,datasets,pad,W);
      if(!cv.id) cv.id='vc_'+(Math.random()*1e6|0);
      REG[cv.id]={hits};
      attachHover(cv,'bar');
    },

    line(cv, {labels, datasets, ttl=''}){
      if(!cv||!datasets||!datasets.length) return;
      const {ctx,W,H} = setup(cv);
      ctx.clearRect(0,0,cv.width,cv.height);
      const legW = Math.min(200,W*.32);
      const rotate = labels.length > 6;
      const allV = datasets.flatMap(d=>d.data||[0]).filter(Number.isFinite);
      const maxV = niceMax(Math.max(...allV,1));
      const pad = {t:34, b:rotate?88:52, l:yW(maxV), r:legW};
      drawGrid(ctx,pad,W,H,maxV);
      drawXLabels(ctx,labels,pad,W,H,rotate);
      const pH=H-pad.t-pad.b, pW=W-pad.l-pad.r;
      const step = labels.length>1 ? pW/(labels.length-1) : pW;
      const hits=[];
      datasets.forEach((ds,di)=>{
        const c=ds.color||PAL[di%PAL.length];
        ctx.save();
        ctx.strokeStyle=c; ctx.lineWidth=2;
        ctx.setLineDash(ds.dashed?[6,4]:[]);
        ctx.globalAlpha=ds.dashed?.7:.9;
        ctx.beginPath();
        (ds.data||[]).forEach((v,i)=>{
          const x=pad.l+i*step, y=pad.t+pH-v/maxV*pH;
          i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
        });
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle=c;
        (ds.data||[]).forEach((v,i)=>{
          const x=pad.l+i*step, y=pad.t+pH-v/maxV*pH;
          ctx.beginPath();ctx.arc(x,y,ds.dashed?3:4.5,0,Math.PI*2);ctx.fill();
          hits.push({x,y,v,lbl:labels[i]||'',ds:ds.label||''});
        });
        ctx.restore();
      });
      drawTitle(ctx,ttl,W,pad.r);
      drawLegend(ctx,datasets,pad,W);
      if(!cv.id) cv.id='vc_'+(Math.random()*1e6|0);
      REG[cv.id]={hits};
      attachHover(cv,'line');
    },

    donut(cv, {labels, data, colors=[], ttl=''}){
      if(!cv||!data||!data.length) return;
      const {ctx,W,H} = setup(cv);
      ctx.clearRect(0,0,cv.width,cv.height);
      const total=data.reduce((a,b)=>a+b,0)||1;
      const cx=W*.46, cy=H*.5+4, r=Math.min(W*.36,H*.36,110);
      let ang=-Math.PI/2;
      data.forEach((v,i)=>{
        const sl=v/total*Math.PI*2;
        ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,r,ang,ang+sl);ctx.closePath();
        ctx.fillStyle=colors[i]||PAL[i%PAL.length];ctx.globalAlpha=.9;ctx.fill();
        ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.globalAlpha=1;ctx.stroke();
        const mid=ang+sl/2, px=cx+Math.cos(mid)*r*.64, py=cy+Math.sin(mid)*r*.64;
        const pct=Math.round(v/total*100);
        if(pct>5){ctx.fillStyle='#fff';ctx.font='bold 12px sans-serif';
          ctx.textAlign='center';ctx.fillText(pct+'%',px,py+4);}
        ang+=sl;
      });
      ctx.beginPath();ctx.arc(cx,cy,r*.47,0,Math.PI*2);
      ctx.fillStyle='#fff';ctx.globalAlpha=1;ctx.fill();
      ctx.fillStyle='#1a1a2e';ctx.font='bold 13px sans-serif';ctx.textAlign='center';
      ctx.fillText(fmtV(total),cx,cy+4);
      ctx.fillStyle='#6b7280';ctx.font='9px sans-serif';ctx.fillText('Total',cx,cy+15);
      ctx.fillStyle='#1a1a2e';ctx.font='bold 11px sans-serif';ctx.fillText(ttl,W*.46,14);
      let lx=6, ly=H-18;
      data.forEach((v,i)=>{
        ctx.fillStyle=colors[i]||PAL[i%PAL.length];ctx.globalAlpha=.9;ctx.fillRect(lx,ly,10,10);
        ctx.globalAlpha=1;ctx.fillStyle='#374151';ctx.font='9px sans-serif';ctx.textAlign='left';
        const lbl=labels[i]+(v>0?' ('+Math.round(v/total*100)+'%)':'');
        ctx.fillText(lbl,lx+13,ly+9); lx+=ctx.measureText(lbl).width+30;
      });
      // Donut hover: sectors
      if(!cv.id) cv.id='vc_'+(Math.random()*1e6|0);
      REG[cv.id]={hits:[],cx,cy,r,data,labels,colors,total};
      cv.onmousemove=function(e){
        const rect=cv.getBoundingClientRect();
        const mx=e.clientX-rect.left-cx, my=e.clientY-rect.top-cy;
        const dist=Math.sqrt(mx*mx+my*my);
        if(dist<r*.47||dist>r){hideTip();return;}
        let ang2=-Math.PI/2;
        let theta=Math.atan2(my,mx);
        if(theta<ang2) theta+=Math.PI*2;
        let found=null;
        for(let i=0;i<data.length;i++){
          const sl=data[i]/total*Math.PI*2;
          let end=ang2+sl; if(end<-Math.PI/2) end+=Math.PI*2;
          if(theta>=ang2&&theta<ang2+sl){found=i;break;}
          ang2+=sl;
        }
        if(found!==null){
          const pct=Math.round(data[found]/total*100);
          showTip(`<b>${labels[found]}</b><br>Valor: <b>${fmtV(data[found])}</b><br>${pct}% del total`,e.clientX,e.clientY);
        } else hideTip();
      };
      cv.onmouseleave=hideTip;
    }
  };
}());
"""
