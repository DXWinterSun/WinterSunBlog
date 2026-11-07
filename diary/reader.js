(function(){
  'use strict';
  const $=id=>document.getElementById(id),PAGE=20;
  let entries=[],ids=[],loaded=0,key=null,keyId=null,generation=0,controller=null,busy=false,setupAvailable=false;
  function lock(message){
    generation++;if(controller)controller.abort();controller=null;entries=[];ids=[];loaded=0;key=null;keyId=null;busy=false;
    $('password').value='';$('search').value='';$('entries').replaceChildren();$('count').textContent='';$('load-status').textContent='';
    $('diary').hidden=true;$('lock').hidden=false;$('lock-now').hidden=true;$('more').hidden=true;$('empty').hidden=true;$('unlock').disabled=!setupAvailable;$('password').disabled=!setupAvailable;$('unlock-form').hidden=!setupAvailable;$('check-setup').hidden=setupAvailable;$('check-setup').disabled=false;$('status').textContent=message||'';
  }
  async function getJSON(url,limit,signal){
    const local=new AbortController(),abort=()=>local.abort();signal.addEventListener('abort',abort,{once:true});if(signal.aborted)local.abort();const timer=setTimeout(abort,20000);
    try{
    const response=await fetch(url,{cache:'no-store',credentials:'omit',referrerPolicy:'no-referrer',signal:local.signal});
    if(response.status===404)throw Error('MISSING');if(!response.ok)throw Error('NETWORK');
    const length=response.headers.get('content-length');if(length&&Number(length)>limit)throw Error('SIZE');
    const reader=response.body.getReader(),parts=[];let size=0;
    try{for(;;){const next=await reader.read();if(next.done)break;size+=next.value.byteLength;if(size>limit){await reader.cancel();throw Error('SIZE');}parts.push(next.value);}}
    finally{reader.releaseLock();}
    const bytes=new Uint8Array(size);let at=0;for(const part of parts){bytes.set(part,at);at+=part.length;}
    return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
    }finally{clearTimeout(timer);signal.removeEventListener('abort',abort);}
  }
  async function readSetup(signal){
    const pub=await getJSON('./public.json',4096,signal);await DiaryCrypto.validatePublic(pub);
    const vault=await getJSON('./vault.json',20000,signal),header=DiaryCrypto.inspectVault(vault);
    if(header.keyId!==pub.keyId)throw Error('KEY');
    const manifest=DiaryCrypto.validateManifest(await getJSON('./manifest.json',400000,signal),pub.keyId);
    return {pub,vault,manifest};
  }
  async function checkSetup(){
    if(busy)return;
    if(!window.isSecureContext||!window.crypto||!window.crypto.subtle){lock('当前浏览器不支持安全解锁，请使用支持 Web Crypto 的 HTTPS 浏览器。');return;}
    busy=true;const attempt=++generation;controller=new AbortController();$('check-setup').disabled=true;$('status').textContent='正在检查日记是否准备好……';
    try{await readSetup(controller.signal);if(attempt!==generation)return;setupAvailable=true;lock('日记已准备好。密码只在当前页面使用。');}
    catch(error){if(attempt===generation){setupAvailable=false;lock(error.message==='MISSING'?'这本日记还没有完成首次设置，现在不用输入密码。尚未保存任何日记。':'日记资料暂时未能通过检查，现在不用输入密码。可以稍后再检查。');}}
  }
  function render(){
    const q=$('search').value.trim().toLocaleLowerCase(),visible=entries.filter(e=>!q||[e.title,e.body,...e.tags].join('\n').toLocaleLowerCase().includes(q));
    $('entries').replaceChildren();$('count').textContent='已打开 '+loaded+' / '+ids.length+' 小段';$('empty').hidden=visible.length>0;
    $('empty').textContent=q?'已打开的日记里没有找到这几个字。':'这一页还空着。日子慢慢来，想写时再记。';
    for(const entry of visible.slice().sort((a,b)=>b.date.localeCompare(a.date))){
      const article=document.createElement('article');article.className='entry';const time=document.createElement('time');time.dateTime=entry.date;time.textContent=entry.date.replace(/-/g,' · ');article.append(time);
      if(entry.title.trim()){const h=document.createElement('h2');h.textContent=entry.title;article.append(h);}
      const body=document.createElement('p');body.className='body';body.textContent=entry.body;article.append(body);
      if(entry.tags.length){const tags=document.createElement('div');tags.className='tags';for(const text of entry.tags){const tag=document.createElement('span');tag.className='tag';tag.textContent=text;tags.append(tag);}article.append(tags);}
      $('entries').append(article);
    }
    $('more').hidden=loaded>=ids.length;$('more').disabled=busy;
  }
  async function loadMore(){
    if(busy||!key)return;busy=true;$('more').disabled=true;const attempt=generation,start=loaded;
    const pageIds=ids.slice(start,start+PAGE),page=[],privateKey=key,expectedKeyId=keyId,signal=controller.signal;
    $('load-status').textContent=pageIds.length?'正在打开下一小叠……':'';
    try{
      // At most four fetch/decrypt operations in flight, with no silent skipping.
      for(let i=0;i<pageIds.length;i+=4){
        const batch=await Promise.allSettled(pageIds.slice(i,i+4).map(async id=>{const encrypted=await getJSON('./entries/'+id+'.json',180000,signal);return DiaryCrypto.decryptEntry(encrypted,privateKey,expectedKeyId,id);}));
        if(attempt!==generation)return;if(batch.some(item=>item.status!=='fulfilled'))throw Error('ENTRY');page.push(...batch.map(item=>item.value));
      }
      if(attempt!==generation)return;entries.push(...page);loaded=start+pageIds.length;$('load-status').textContent='';
    }catch(_){if(attempt===generation)$('load-status').textContent='这一叠有条目未能读取或通过校验，没有跳过或计入。可以重试；已打开的内容仍在。';}
    finally{if(attempt===generation){busy=false;render();}}
  }
  $('unlock-form').addEventListener('submit',async event=>{
    event.preventDefault();if(busy||!setupAvailable||document.hidden)return;busy=true;const attempt=++generation;let setupChecked=false,password=$('password').value;$('password').value='';$('unlock').disabled=true;$('status').textContent='正在翻开……';controller=new AbortController();const signal=controller.signal;
    try{
      const {pub,vault,manifest}=await readSetup(signal);setupChecked=true;
      const privateKey=await DiaryCrypto.unlock(vault,pub,password);password='';if(attempt!==generation)return;
      key=privateKey;keyId=pub.keyId;ids=manifest.entries.slice().reverse();loaded=0;entries=[];busy=false;$('lock').hidden=true;$('diary').hidden=false;$('lock-now').hidden=false;$('status').textContent='';render();await loadMore();
    }catch(error){if(attempt===generation){if(!setupChecked)setupAvailable=false;lock(!setupChecked?'日记资料暂时不齐或未能通过检查，现在不用输入密码。请稍后重新检查。':'没有打开。请检查密码或稍后重试；没有改动任何日记。');}}
    finally{password='';if(attempt===generation){busy=false;$('unlock').disabled=false;}}
  });
  $('check-setup').addEventListener('click',checkSetup);
  $('more').addEventListener('click',loadMore);$('search').addEventListener('input',render);$('lock-now').addEventListener('click',()=>lock('本子锁好了。'));
  window.addEventListener('pagehide',()=>lock());window.addEventListener('pageshow',event=>{if(event.persisted)lock();});document.addEventListener('visibilitychange',()=>{if(document.hidden)lock();});
  checkSetup();
})();
