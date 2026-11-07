(function(){
  'use strict';
  const REFERENCE=/*REFERENCE*/,TEST_MODE=/*TEST_MODE*/;
  const $=id=>document.getElementById(id);
  let generation=0,busy=false,setup=null;const urls=new Set();
  function clear(message){generation++;$('password').value='';busy=false;$('fields').disabled=!!setup;$('create').disabled=!!setup;$('status').textContent=message||'';}
  $('cancel').addEventListener('click',()=>clear('密码输入已清空。'));
  $('setup-form').addEventListener('submit',async event=>{
    event.preventDefault();if(busy||setup||!$('consent').checked||document.hidden)return;
    if(!window.isSecureContext||!window.crypto||!window.crypto.subtle){clear('需要支持 Web Crypto 的可信 HTTPS 浏览器。');return;}
    const attempt=++generation;let password=$('password').value;$('password').value='';busy=true;$('fields').disabled=true;$('create').disabled=true;$('status').textContent='正在本机创建钥匙并自检，可能需要一小会儿……';
    try{const result=await DiaryCrypto.createSetup(password,REFERENCE,'冬的私人档案');password='';if(attempt!==generation)return;setup=result;$('fingerprint').textContent=result.public.keyId;$('ready').hidden=false;$('status').textContent=TEST_MODE?'合成数据测试通过。这不是你的日记钥匙。':'检查完成。请下载并妥善保留加密备份包。';}
    catch(_){if(attempt===generation)$('status').textContent='没有完成。请检查原密码和浏览器支持；没有上传或改动任何日记。';}
    finally{password='';if(attempt===generation){busy=false;$('fields').disabled=!!setup;$('create').disabled=!!setup;}}
  });
  $('download').addEventListener('click',()=>{
    if(!setup)return;
    const output=TEST_MODE?{...setup,format:'winter-diary-self-test'}:setup;
    const url=URL.createObjectURL(new Blob([JSON.stringify(output,null,2)+'\n'],{type:'application/json'}));urls.add(url);
    const a=document.createElement('a');a.href=url;a.download=TEST_MODE?'winter-diary-synthetic-test.json':'winter-diary-encrypted-setup.json';document.body.append(a);a.click();a.remove();
    $('status').textContent=TEST_MODE?'测试文件已交给浏览器下载，不能用于启用日记。':'已交给浏览器下载。请确认文件已保存；再次点击会下载同一份，不会重新生成钥匙。';
    setTimeout(()=>{URL.revokeObjectURL(url);urls.delete(url);},60000);
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&busy)clear('已暂停这次创建并清空输入，请回来后重试。');});
  window.addEventListener('pagehide',()=>{clear();setup=null;for(const url of urls)URL.revokeObjectURL(url);urls.clear();$('ready').hidden=true;$('fingerprint').textContent='';});
  window.addEventListener('pageshow',event=>{if(event.persisted)clear();});
})();
