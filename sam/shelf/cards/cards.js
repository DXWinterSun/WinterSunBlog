/* Winter's card catalogue. Counts live here; the shelf keeps its original records.
   Always fetch the latest GitHub object before editing; update only the chosen item.
   Public PNGs deliberately omit quantities, acquisition status and private notes. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const API = 'https://api.github.com/repos/DXWinterSun/WinterSunBlog/contents/sam/shelf/cards/';
  const KEY = 'ws-sam-shelf-key';
  let data, scope = 'owned', selected = new Set(), busy = false, editing = null, savedURLs = [];
  const token = () => { try { return localStorage.getItem(KEY) || ''; } catch (_) { return ''; } };
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const cardById = id => data.cards.find(c => c.id === id);
  const known = c => Number.isInteger(c.quantity) && c.quantity >= 0;
  const qtyText = c => known(c) ? '×' + c.quantity : '数量待核对';
  function cardState(c) {
    if (c.status === '已到手') return {label:'已到手',tone:'arrived'};
    if (c.status === '想收') return {label:'想收',tone:'wanted'};
    if (c.quantity > 0) return {label:'已购·含在途',tone:'transit'};
    return {label:'待核对',tone:'unknown'};
  }
  function statusBadge(c) { const s=cardState(c); return '<span class="card-status" data-state="'+s.tone+'">'+esc(s.label)+'</span>'; }
  function countBadge(c) { return '<span class="qty '+(!known(c)?'unknown':'')+'"><small>'+ (known(c)?'已购数量':'持有数量')+'</small><b>'+ (known(c)?'×'+c.quantity:'待核对')+'</b></span>'; }
  function notice(s) { $('notice').textContent = s; $('notice').hidden = !s; }
  function current() {
    const q = $('search').value.trim().toLowerCase();
    return data.cards.filter(c => (scope === 'all' || (scope === 'owned' ? c.quantity > 0 : !(c.quantity > 0))) && (!$('series').value || c.series === $('series').value) && (!$('kind').value || c.kind === $('kind').value) && (!q || [c.name,c.number,c.series,c.variant,c.kind].join(' ').toLowerCase().includes(q)));
  }
  function paintOptions() {
    for (const [id, field, label] of [['series','series','全部系列'],['kind','kind','全部卡种']]) {
      const old = $(id).value;
      $(id).innerHTML = '<option value="">'+label+'</option>' + [...new Set(data.cards.map(c => c[field]))].map(s => '<option>'+esc(s)+'</option>').join('');
      if ([...$(id).options].some(o => o.value === old)) $(id).value = old;
    }
    $('series-names').innerHTML = [...new Set(data.cards.map(c=>c.series))].map(s=>'<option value="'+esc(s)+'">').join('');
  }
  function badges(c) { return '<span class="badge" data-kind="'+esc(c.kind)+'">'+esc(c.kind)+'</span><span class="badge">'+esc(c.variant || '版本待核对')+'</span>' + (c.number ? '<span class="badge">#'+esc(c.number)+'</span>' : ''); }
  function render() {
    const owned = data.cards.filter(c => c.quantity > 0), list = current(), owner = !!token();
    $('styles').textContent = owned.length;
    $('copies').textContent = owned.reduce((n,c) => n+c.quantity,0);
    $('series-count').textContent = new Set(owned.map(c=>c.series)).size;
    $('curator').textContent = owner ? '馆长模式 · 已开门' : '馆长入口';
    $('add').hidden = !owner;
    $('result').textContent = list.length+' 款卡面'+(selected.size ? ' · 已选 '+selected.size+' 款' : '');
    $('clear-selection').hidden = !selected.size;
    $('export-public').disabled = $('export-private').disabled = !list.length && !selected.size;
    $('updated').textContent = '最近登记 '+data.updated;
    $('grid').innerHTML = list.length ? list.map(c => '<article class="card'+(selected.has(c.id)?' selected':'')+'" data-id="'+esc(c.id)+'"><div class="card-top">'+statusBadge(c)+countBadge(c)+'</div><button class="art" data-detail="'+esc(c.id)+'" aria-label="查看'+esc(c.name)+'详情"><img loading="lazy" src="'+esc(c.image)+'" alt="'+esc(c.name+' · '+c.variant)+'"></button><div class="card-body"><p class="card-series">'+esc(c.series)+'</p><h2>'+esc(c.name)+'</h2><div class="badges">'+badges(c)+'</div><p class="photo-source">'+esc(c.photo || '卡面图')+'</p><div class="card-foot"><label class="select-card"><input type="checkbox" data-select="'+esc(c.id)+'" '+(selected.has(c.id)?'checked':'')+'>选入拼图</label><button data-save="'+esc(c.id)+'">保存单张</button></div>'+(owner?'<div class="quantity-edit"><button data-minus="'+esc(c.id)+'" aria-label="数量减一" '+(!c.quantity || busy?'disabled':'')+'>−</button><button data-plus="'+esc(c.id)+'" aria-label="数量加一" '+(busy?'disabled':'')+'>＋</button><button class="edit" data-edit="'+esc(c.id)+'" '+(busy?'disabled':'')+'>编辑</button></div>':'')+'</div></article>').join('') : '<p class="empty">这一页暂时没有卡，换个筛选看看。</p>';
    $('legacy-list').innerHTML = data.legacy.map(c => '<article class="legacy-item"><h3>'+esc(c.name)+'</h3><p>'+esc(c.spec)+'</p><p><strong>原记录 '+c.quantity+' 张</strong> · 待补卡面'+(c.shelfId==='seed-topps'?'；2/5是限编，不是两张。':'')+'</p></article>').join('');
  }
  function openDetail(c) {
    $('detail-content').innerHTML = '<div class="detail-collection">'+statusBadge(c)+countBadge(c)+'</div><img src="'+esc(c.image)+'" alt="'+esc(c.name)+'"><div class="eyebrow">'+esc(c.series)+'</div><h2>'+esc(c.name)+'</h2><div class="badges">'+badges(c)+'</div><p>'+esc(c.note)+'</p><p class="hint">'+esc(c.photo || '卡面图')+'</p><div class="detail-actions"><button data-detail-save="'+esc(c.id)+'">保存卡面图片</button>'+(token()?'<button data-detail-edit="'+esc(c.id)+'">修改记录</button>':'')+'</div>';
    $('detail').showModal();
  }
  async function getRepo() {
    const r = await fetch(API+'data.json?ref=main&t='+Date.now(), {headers:{Accept:'application/vnd.github+json',Authorization:'Bearer '+token()},cache:'no-store'});
    if (!r.ok) throw Error(r.status === 401 || r.status === 403 ? '馆长钥匙未通过验证，请回藏品架检查权限。' : '读取收藏记录失败（'+r.status+'），请稍后重试。');
    const obj = await r.json();
    const bytes = Uint8Array.from(atob(obj.content.replace(/\s/g,'')),c=>c.charCodeAt(0));
    return {value:JSON.parse(new TextDecoder().decode(bytes)),sha:obj.sha};
  }
  function encode(s) {
    const bytes = new TextEncoder().encode(s); let binary='';
    for (let i=0;i<bytes.length;i++) binary+=String.fromCharCode(bytes[i]);
    return btoa(binary);
  }
  async function update(change, message) {
    if (!token()) throw Error('请先从藏品架打开馆长模式。');
    for (let attempt=0;attempt<3;attempt++) {
      const remote = await getRepo();
      change(remote.value);
      remote.value.updated = new Date().toLocaleDateString('sv-SE',{timeZone:'Asia/Shanghai'});
      const r = await fetch(API+'data.json', {method:'PUT',headers:{Accept:'application/vnd.github+json',Authorization:'Bearer '+token(),'Content-Type':'application/json'},body:JSON.stringify({message,content:encode(JSON.stringify(remote.value,null,2)+'\n'),sha:remote.sha,branch:'main'})});
      if (r.status===409 || r.status===422) continue;
      if (!r.ok) throw Error('未能发布（'+r.status+'）。本次改动未确认，请重试。');
      data=remote.value; paintOptions(); render(); notice('已保存到收藏馆，站点更新后其他设备也能看到。'); return;
    }
    throw Error('记录刚被更新，请刷新后重试，避免覆盖其他改动。');
  }
  async function increment(id,delta) {
    if (busy) return;
    busy=true; render(); notice('正在保存数量…');
    try { await update(d => {
      const c=d.cards.find(c=>c.id===id); if (!c) throw Error('这张卡已被移走，请刷新。');
      const n=known(c)?c.quantity:0; if (n+delta<0) throw Error('数量不能小于零。');
      c.quantity=n+delta;
      if (delta>0 && ['待核对','想收'].includes(c.status)) c.status='已购·含在途';
    },'Update card quantity: '+id+' '+(delta>0?'+1':'-1')); }
    catch(e) { notice(e.message+' 数量没有在本页提前增加。'); }
    finally { busy=false; render(); }
  }
  function edit(c) {
    editing=c?.id || null;
    const f=$('edit-form'); f.reset(); $('edit-error').textContent='';
    for(const k of ['name','series','number','kind','variant','quantity','status','note']) if(c && c[k]!=null) f.elements[k].value=c[k];
    $('editor-title').textContent=c?'修改卡牌记录':'收录新卡';
    $('editor').showModal();
  }
  async function preparePhoto(file) {
    if (file.size > 24*1024*1024) throw Error('照片大于24MB，请换一张稍小的。');
    const url=URL.createObjectURL(file);
    try {
      const im=await loadImage(url), cv=document.createElement('canvas');
      const scale=Math.min(1,1600/Math.max(im.width,im.height)); cv.width=Math.round(im.width*scale);cv.height=Math.round(im.height*scale);
      const ctx=cv.getContext('2d');ctx.fillStyle='#f5f0e7';ctx.fillRect(0,0,cv.width,cv.height);ctx.drawImage(im,0,0,cv.width,cv.height);
      return cv.toDataURL('image/jpeg',.9).split(',')[1];
    } finally {URL.revokeObjectURL(url);}
  }
  $('edit-form').addEventListener('submit',async e=>{
    e.preventDefault(); if(busy)return;
    const f=e.currentTarget, n=f.elements.quantity.value.trim(), quantity=n===''?null:Number(n);
    if(quantity!==null && (!Number.isInteger(quantity)||quantity<0)) { $('edit-error').textContent='数量请填写零或正整数。';return; }
    busy=true; $('edit-submit').disabled=true; $('edit-error').textContent='正在保存…';
    const id=editing || 'card-'+Date.now().toString(36)+'-'+crypto.getRandomValues(new Uint32Array(1))[0].toString(36);
    try {
      let image=null;const file=f.elements.picture.files[0];
      if(file){
        const content=await preparePhoto(file),path='images/'+id+'-'+Date.now()+'.jpg';
        const r=await fetch(API+path,{method:'PUT',headers:{Authorization:'Bearer '+token(),'Content-Type':'application/json'},body:JSON.stringify({message:'Add card photo: '+id,content,branch:'main'})});
        if(!r.ok)throw Error('照片未能保存（'+r.status+'），记录尚未修改。'); image=path;
      }
      const fields={quantity};for(const k of ['name','series','number','kind','variant','status','note'])fields[k]=f.elements[k].value.trim();
      if(!editing && !image)throw Error('新卡请附一张卡面照片，方便以后识别。');
      if(image) {fields.image=image;fields.photo='Winter 实拍';}
      await update(d=>{
        let c=d.cards.find(c=>c.id===id);
        if(editing&&!c)throw Error('这条记录已被移走，请刷新。');
        if(!c){c={id};d.cards.unshift(c);}Object.assign(c,fields);
      },(editing?'Edit card: ':'Collect card: ')+id);
      $('editor').close();
    }catch(err){$('edit-error').textContent=err.message;}
    finally{busy=false;$('edit-submit').disabled=false;render();}
  });
  function loadImage(url) {
    return new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('卡面图片未加载，暂时无法保存拼图。请刷新重试。'));im.src=url;});
  }
  function drawFit(ctx,im,x,y,w,h){const scale=Math.min(w/im.width,h/im.height);ctx.drawImage(im,x+(w-im.width*scale)/2,y+(h-im.height*scale)/2,im.width*scale,im.height*scale);}
  function drawText(ctx,s,x,y,max,font=26,color='#302c29') {
    ctx.fillStyle=color;let size=font;ctx.font=size+'px sans-serif';while(ctx.measureText(s).width>max&&size>15){size--;ctx.font=size+'px sans-serif';}ctx.fillText(s,x,y,max);
  }
  async function exportImages(list, counts=false, single=false) {
    if(!list.length)return;
    const buttons=[$('export-public'),$('export-private')];buttons.forEach(b=>b.disabled=true);notice('正在整理卡面图片…');
    try {
      const ims=await Promise.all(list.map(c=>loadImage(c.image)));
      savedURLs.forEach(URL.revokeObjectURL);savedURLs=[];$('saved-images').replaceChildren();$('saved-actions').replaceChildren();
      const pages=Math.ceil(list.length/9);
      for(let page=0;page<pages;page++) {
        const entries=list.slice(page*9,page*9+9), images=ims.slice(page*9,page*9+9), cols=single?1:3, rows=Math.ceil(entries.length/cols), W=single?1080:1440, cell=single?(counts?1250:1180):(counts?600:525);
        const cv=document.createElement('canvas');cv.width=W;cv.height=240+rows*cell+85;
        const ctx=cv.getContext('2d');ctx.fillStyle='#f5f0e7';ctx.fillRect(0,0,W,cv.height);
        ctx.fillStyle='#965e37';ctx.fillRect(54,58,42,3);drawText(ctx,'WINTER SUN / THE CARD COLLECTION',112,68,W-170,19,'#965e37');
        drawText(ctx,counts?'Justin Hammer · 收藏数量':'Justin Hammer · 卡牌图鉴',54,138,W-108,42);
        drawText(ctx,counts?'逐款已购数量（含在途） · '+new Date().toLocaleDateString('zh-CN',{timeZone:'Asia/Shanghai'}):'系列 · 卡号 · 版本',54,188,W-108,24,'#726d65');
        const pad=single?54:42,cw=(W-pad*2)/cols;
        entries.forEach((c,i)=>{
          const x=pad+(i%cols)*cw,y=230+Math.floor(i/cols)*cell;
          ctx.fillStyle='#fffdf8';ctx.fillRect(x+8,y,cw-16,cell-20);
          if(counts) {
            const state=cardState(c), stateColor=state.tone==='arrived'?'#42614e':state.tone==='transit'?'#965e37':'#726d65';
            ctx.fillStyle=state.tone==='arrived'?'#e8f0e9':state.tone==='transit'?'#f4e8d4':'#eeeae2';
            ctx.fillRect(x+24,y+20,Math.min(205,cw-170),44);
            drawText(ctx,state.label,x+35,y+49,Math.min(182,cw-192),21,stateColor);
            ctx.textAlign='right';
            drawText(ctx,known(c)?'已购 ×'+c.quantity:'待核对',x+cw-28,y+51,135,25,'#365c73');
            ctx.textAlign='left';
          }
          drawFit(ctx,images[i],x+30,y+(counts?92:20),cw-60,single?900:335);
          const ty=y+(single?(counts?1030:960):(counts?450:380));
          drawText(ctx,c.name,x+25,ty,cw-50,single?33:25);
          drawText(ctx,c.series,x+25,ty+37,cw-50,20,'#726d65');
          drawText(ctx,[c.number?'#'+c.number:'',c.kind,c.variant].filter(Boolean).join(' · '),x+25,ty+71,cw-50,20,'#965e37');
        });
        ctx.strokeStyle='#ddd5c7';ctx.beginPath();ctx.moveTo(54,cv.height-66);ctx.lineTo(W-54,cv.height-66);ctx.stroke();
        drawText(ctx,'Winter 的收藏馆 · 卡面版权归各发行方所有',54,cv.height-30,W-210,18,'#726d65');
        drawText(ctx,(page+1)+' / '+pages,W-130,cv.height-30,90,18,'#726d65');
        const blob=await new Promise(resolve=>cv.toBlob(resolve,'image/png'));if(!blob)throw Error('图片生成失败，请重试。');
        const url=URL.createObjectURL(blob);savedURLs.push(url);
        const img=document.createElement('img');img.alt=(counts?'收藏数量图':'卡面图')+' 第'+(page+1)+'页';img.src=url;$('saved-images').append(img);
        const filename='Winter-Cards-'+(counts?'Inventory':'Gallery')+'-'+(page+1)+'.png';
        const a=document.createElement('a');a.href=url;a.download=filename;a.textContent='下载第 '+(page+1)+' 张';$('saved-actions').append(a);
        const file=new File([blob],filename,{type:'image/png'});
        if(navigator.canShare?.({files:[file]})){
          const share=document.createElement('button');share.textContent='分享图片 '+(page+1);share.onclick=async()=>{try{await navigator.share({files:[file]});}catch(e){if(e.name!=='AbortError')notice('分享未完成，请长按图片或点下载。');}};$('saved-actions').append(share);
        }
      }
      notice('');$('saved').showModal();
    }catch(e){notice(e.message);}
    finally{render();}
  }
  const forExport=()=>selected.size?data.cards.filter(c=>selected.has(c.id)):current();
  $('export-public').onclick=()=>exportImages(forExport());
  $('export-private').onclick=()=>exportImages(forExport(),true);
  $('clear-selection').onclick=()=>{selected.clear();render();};
  $('search').oninput=render;$('series').onchange=render;$('kind').onchange=render;
  document.querySelectorAll('[data-scope]').forEach(b=>b.onclick=()=>{scope=b.dataset.scope;document.querySelectorAll('[data-scope]').forEach(t=>t.classList.toggle('on',t===b));render();});
  $('grid').addEventListener('change',e=>{const id=e.target.dataset.select;if(!id)return;e.target.checked?selected.add(id):selected.delete(id);render();});
  $('grid').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;for(const [action,id]of Object.entries(b.dataset)){if(action==='detail')openDetail(cardById(id));if(action==='save')exportImages([cardById(id)],false,true);if(action==='edit')edit(cardById(id));if(action==='plus')increment(id,1);if(action==='minus')increment(id,-1);}});
  $('detail').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.detailSave){$('detail').close();exportImages([cardById(b.dataset.detailSave)],false,true);}if(b.dataset.detailEdit){$('detail').close();edit(cardById(b.dataset.detailEdit));}});
  document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>{if(busy&&b.closest('dialog')===$('editor'))return;b.closest('dialog').close();});
  $('editor').addEventListener('cancel',e=>{if(busy)e.preventDefault();});
  $('add').onclick=()=>edit(null);
  $('curator').onclick=()=>{if(token())notice('馆长模式已开启。卡片下方可以加减数量或编辑；「收录新卡」可以补照片。钥匙沿用藏品架的本机设置。');else location.href='../#door';};
  async function init(){
    try{let authError='';
      if(token())try{data=(await getRepo()).value;}catch(e){authError=e.message;}
      if(!data){const r=await fetch('./data.json',{cache:'no-cache'});if(!r.ok)throw Error('卡册暂时没打开，请稍后刷新。');data=await r.json();}
      paintOptions();render();if(authError)notice(authError+' 当前显示公开版记录。');
    }catch(e){notice(e.message);$('grid').innerHTML='<p class="empty">卡册暂时无法加载，请刷新重试。</p>';}
  }
  init();
})();
