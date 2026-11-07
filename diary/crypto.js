(function (root) {
  'use strict';
  const SUITE = 'RSA-OAEP-3072-SHA256+A256GCM';
  const ITER = 600000, MAX_ENTRY = 65536;
  const ID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
  const FP = /^[A-Za-z0-9_-]{43}$/;
  const enc = new TextEncoder(), dec = new TextDecoder('utf-8',{fatal:true});
  const fail = () => { throw new Error('日记资料未通过安全检查。'); };
  function exact(o, keys) { if (!o || typeof o !== 'object' || Array.isArray(o) || Object.keys(o).sort().join('|') !== keys.slice().sort().join('|')) fail(); }
  function subtle() { if (!root.crypto || !root.crypto.subtle) throw new Error('当前浏览器不支持安全加密。'); return root.crypto.subtle; }
  function b64(a) { let s=''; for(const b of a) s+=String.fromCharCode(b); return btoa(s); }
  function bytes(s, length, max=MAX_ENTRY+2048) {
    if (typeof s!=='string' || s.length>max*2 || !/^[A-Za-z0-9+/]*={0,2}$/.test(s)) fail();
    let a; try { a=Uint8Array.from(atob(s),c=>c.charCodeAt(0)); } catch (_) { fail(); }
    if (a.length>max || (length && a.length!==length) || b64(a)!==s) fail(); return a;
  }
  function b64url(a) { return b64(a).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''); }
  function unurl(s) { if(typeof s!=='string'||!s||!/^[A-Za-z0-9_-]+$/.test(s)) fail(); const a=bytes(s.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-s.length%4)%4),null,4096);if(b64url(a)!==s)fail();return a; }
  function random(n) { return root.crypto.getRandomValues(new Uint8Array(n)); }
  function aad(o) { return enc.encode(JSON.stringify(o)); }
  function validateJwk(jwk) {
    exact(jwk,['e','kty','n']); if(jwk.kty!=='RSA'||jwk.e!=='AQAB')fail();
    const n=unurl(jwk.n); if(n.length!==384||n[0]<128)fail();
    return {e:jwk.e,kty:'RSA',n:jwk.n};
  }
  async function fingerprint(jwk) { return b64url(new Uint8Array(await subtle().digest('SHA-256',aad(validateJwk(jwk))))); }
  async function validatePublic(pub, expected) {
    exact(pub,['format','version','suite','keyId','jwk']);
    if(pub.format!=='winter-diary-public'||pub.version!==1||pub.suite!==SUITE||!FP.test(pub.keyId))fail();
    const computed=await fingerprint(pub.jwk); if(computed!==pub.keyId||(expected!==undefined&&computed!==expected))fail();
    return pub;
  }
  async function passwordKey(password,salt,iterations,usages) {
    if(typeof password!=='string'||!password||password.length>1024)fail();
    const raw=enc.encode(password); let material;
    try { material=await subtle().importKey('raw',raw,'PBKDF2',false,['deriveKey']); } finally {raw.fill(0);}
    return subtle().deriveKey({name:'PBKDF2',salt,iterations,hash:'SHA-256'},material,{name:'AES-GCM',length:256},false,usages);
  }
  async function verifyExistingPassword(password,reference,expected) {
    if(!reference||reference.kdf!=='PBKDF2-SHA256'||reference.iter!==310000||!reference.check)fail();
    const key=await passwordKey(password,bytes(reference.salt,16),310000,['decrypt']);
    const plain=new Uint8Array(await subtle().decrypt({name:'AES-GCM',iv:bytes(reference.check.iv,12),tagLength:128},key,bytes(reference.check.ct,null,4096)));
    try {if(JSON.parse(dec.decode(plain))!==expected)fail();}finally{plain.fill(0);} return true;
  }
  function vaultHeader(vault) {
    exact(vault,['format','version','keyId','kdf','cipher']); exact(vault.kdf,['name','iterations','salt']); exact(vault.cipher,['name','iv','ct']);
    if(vault.format!=='winter-diary-key-vault'||vault.version!==1||!FP.test(vault.keyId)||vault.kdf.name!=='PBKDF2-SHA256'||vault.kdf.iterations!==ITER||vault.cipher.name!=='A256GCM')fail();
    bytes(vault.kdf.salt,16); bytes(vault.cipher.iv,12); bytes(vault.cipher.ct,null,8192);
    return {format:vault.format,version:1,keyId:vault.keyId,kdf:{name:vault.kdf.name,iterations:ITER,salt:vault.kdf.salt}};
  }
  async function createSetup(password,reference,expected) {
    // Only call from the user's local initializer after its explicit confirmation.
    await verifyExistingPassword(password,reference,expected);
    const pair=await subtle().generateKey({name:'RSA-OAEP',modulusLength:3072,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['encrypt','decrypt']);
    const exported=await subtle().exportKey('jwk',pair.publicKey);
    const jwk={e:exported.e,kty:exported.kty,n:exported.n}; const keyId=await fingerprint(jwk);
    const pub={format:'winter-diary-public',version:1,suite:SUITE,keyId,jwk};
    const header={format:'winter-diary-key-vault',version:1,keyId,kdf:{name:'PBKDF2-SHA256',iterations:ITER,salt:b64(random(16))}};
    const iv=random(12),privateBytes=new Uint8Array(await subtle().exportKey('pkcs8',pair.privateKey));
    try {
      const key=await passwordKey(password,bytes(header.kdf.salt,16),ITER,['encrypt']);
      const ct=await subtle().encrypt({name:'AES-GCM',iv,additionalData:aad(header),tagLength:128},key,privateBytes);
      const vault={...header,cipher:{name:'A256GCM',iv:b64(iv),ct:b64(new Uint8Array(ct))}};
      const setup={format:'winter-diary-setup',version:1,public:pub,vault,manifest:{format:'winter-diary-manifest',version:1,keyId,entries:[]}};
      const testKey=await unlock(vault,pub,password),testId='00000000-0000-4000-8000-000000000001';
      const testContent={date:'2000-01-01',title:'初始化自检',body:'这条自检不会保存到日记。',tags:[]};
      const testEntry=await encryptEntry(pub,keyId,testId,testContent),testResult=await decryptEntry(testEntry,testKey,keyId,testId);
      if(testResult.body!==testContent.body)fail();
      return setup;
    }finally{privateBytes.fill(0);}
  }
  async function unlock(vault,pub,password) {
    await validatePublic(pub); const header=vaultHeader(vault); if(header.keyId!==pub.keyId)fail();
    const key=await passwordKey(password,bytes(vault.kdf.salt,16),ITER,['decrypt']);
    const plain=new Uint8Array(await subtle().decrypt({name:'AES-GCM',iv:bytes(vault.cipher.iv,12),additionalData:aad(header),tagLength:128},key,bytes(vault.cipher.ct,null,8192)));
    try {
      const privateKey=await subtle().importKey('pkcs8',plain,{name:'RSA-OAEP',hash:'SHA-256'},false,['decrypt']);
      if(privateKey.algorithm.modulusLength!==3072)fail();
      const publicKey=await subtle().importKey('jwk',validateJwk(pub.jwk),{name:'RSA-OAEP',hash:'SHA-256'},false,['encrypt']);
      const challenge=random(32),label=enc.encode('winter-diary-key-pair:'+pub.keyId);
      const proof=await subtle().encrypt({name:'RSA-OAEP',label},publicKey,challenge);
      const check=new Uint8Array(await subtle().decrypt({name:'RSA-OAEP',label},privateKey,proof));
      const matched=check.length===challenge.length&&check.every((v,i)=>v===challenge[i]);check.fill(0);challenge.fill(0);if(!matched)fail();
      return privateKey;
    }finally{plain.fill(0);}
  }
  function validateContent(value) {
    exact(value,['date','title','body','tags']);
    if(typeof value.date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value.date)||!Number.isFinite(Date.parse(value.date+'T12:00:00Z'))||new Date(value.date+'T12:00:00Z').toISOString().slice(0,10)!==value.date)fail();
    if(typeof value.title!=='string'||value.title.length>160||typeof value.body!=='string'||!value.body.trim()||value.body.length>20000)fail();
    if(!Array.isArray(value.tags)||value.tags.length>8||value.tags.some(t=>typeof t!=='string'||t.length>24))fail();
    const content={date:value.date,title:value.title,body:value.body,tags:value.tags.slice()};if(aad(content).length>MAX_ENTRY)fail();return content;
  }
  function entryHeader(entry) {
    exact(entry,['format','version','suite','keyId','id','wrappedKey','iv','ct']);
    if(entry.format!=='winter-diary-entry'||entry.version!==1||entry.suite!==SUITE||!FP.test(entry.keyId)||!ID.test(entry.id))fail();
    bytes(entry.wrappedKey,384);bytes(entry.iv,12);bytes(entry.ct,null,MAX_ENTRY+16);
    return {format:entry.format,version:1,suite:SUITE,keyId:entry.keyId,id:entry.id};
  }
  async function encryptEntry(pub,expectedKeyId,id,content) {
    if(typeof expectedKeyId!=='string'||!FP.test(expectedKeyId)||!ID.test(id))fail();
    await validatePublic(pub,expectedKeyId);
    const clean=validateContent(content),raw=aad(clean);
    const header={format:'winter-diary-entry',version:1,suite:SUITE,keyId:pub.keyId,id};
    const label=aad(header),secret=random(32),iv=random(12);
    try {
      const publicKey=await subtle().importKey('jwk',validateJwk(pub.jwk),{name:'RSA-OAEP',hash:'SHA-256'},false,['encrypt']);
      const dataKey=await subtle().importKey('raw',secret,{name:'AES-GCM'},false,['encrypt']);
      const wrapped=await subtle().encrypt({name:'RSA-OAEP',label},publicKey,secret);
      const ciphertext=await subtle().encrypt({name:'AES-GCM',iv,additionalData:label,tagLength:128},dataKey,raw);
      return {...header,wrappedKey:b64(new Uint8Array(wrapped)),iv:b64(iv),ct:b64(new Uint8Array(ciphertext))};
    }finally{secret.fill(0);raw.fill(0);}
  }
  async function decryptEntry(entry,privateKey,expectedKeyId,expectedId) {
    const header=entryHeader(entry);if(header.keyId!==expectedKeyId||header.id!==expectedId)fail();
    const label=aad(header),rawKey=new Uint8Array(await subtle().decrypt({name:'RSA-OAEP',label},privateKey,bytes(entry.wrappedKey,384)));
    let plain;
    try {
      if(rawKey.length!==32)fail();const key=await subtle().importKey('raw',rawKey,{name:'AES-GCM'},false,['decrypt']);
      plain=new Uint8Array(await subtle().decrypt({name:'AES-GCM',iv:bytes(entry.iv,12),additionalData:label,tagLength:128},key,bytes(entry.ct,null,MAX_ENTRY+16)));
      return {id:header.id,...validateContent(JSON.parse(dec.decode(plain)))};
    }finally{rawKey.fill(0);if(plain)plain.fill(0);}
  }
  function validateManifest(value,keyId) {
    exact(value,['format','version','keyId','entries']);if(value.format!=='winter-diary-manifest'||value.version!==1||value.keyId!==keyId||!Array.isArray(value.entries)||value.entries.length>5000||value.entries.some(id=>typeof id!=='string'||!ID.test(id))||new Set(value.entries).size!==value.entries.length)fail();
    return {format:value.format,version:1,keyId,entries:value.entries.slice()};
  }
  const api=Object.freeze({createSetup,unlock,encryptEntry,decryptEntry,validateContent,validateManifest,validatePublic,inspectEntry:entryHeader,inspectVault:vaultHeader,fingerprint,verifyExistingPassword,maxEntryBytes:MAX_ENTRY});
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.DiaryCrypto=api;
})(globalThis);
