const {test,before,after}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),nodeCrypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const diary=require('../../../diary/crypto.js');
const PASSWORD='SYNTHETIC TEST ONLY — never a real user password';
const CHECK='SYNTHETIC REFERENCE';
const ID='b2dbd9b0-180c-4b43-8277-93f00a895bc7',ID2='a603d372-46a7-44af-8f7a-eefea4d4ed35';
const CONTENT={date:'2026-11-07',title:'纯属演示',body:'这段文字只用于合成测试。\n<script>literal text</script>',tags:['测试']};
let reference,setup,privateKey,entry,temp;
before(async()=>{
  temp=fs.mkdtempSync(path.join(os.tmpdir(),'diary-publickey-tests-'));
  const salt=nodeCrypto.randomBytes(16),iv=nodeCrypto.randomBytes(12),key=nodeCrypto.pbkdf2Sync(PASSWORD,salt,310000,32,'sha256'),cipher=nodeCrypto.createCipheriv('aes-256-gcm',key,iv);
  const ciphertext=Buffer.concat([cipher.update(JSON.stringify(CHECK),'utf8'),cipher.final(),cipher.getAuthTag()]);key.fill(0);
  reference={kdf:'PBKDF2-SHA256',iter:310000,salt:salt.toString('base64'),check:{iv:iv.toString('base64'),ct:ciphertext.toString('base64')}};
  setup=await diary.createSetup(PASSWORD,reference,CHECK);
  privateKey=await diary.unlock(setup.vault,setup.public,PASSWORD);
  entry=await diary.encryptEntry(setup.public,setup.public.keyId,ID,CONTENT);
});
after(()=>{if(temp)fs.rmSync(temp,{recursive:true,force:true});});
test('one-time setup contains public key and only password-encrypted private key',()=>{
  assert.equal(setup.public.jwk.kty,'RSA');assert.equal(Buffer.from(setup.public.jwk.n,'base64url').length,384);
  assert.deepEqual(Object.keys(setup.public.jwk).sort(),['e','kty','n']);assert.notEqual(setup.vault.kdf.salt,reference.salt);
  assert.equal(setup.vault.kdf.iterations,600000);assert.equal(privateKey.extractable,false);assert.deepEqual(privateKey.usages,['decrypt']);
  const json=JSON.stringify(setup);assert.ok(!json.includes(PASSWORD));assert.ok(!json.includes(CHECK));assert.ok(!json.includes('PRIVATE KEY'));assert.ok(!/"(?:d|p|q|dp|dq|qi)":/.test(json));
  assert.deepEqual(setup.manifest.entries,[]);
});
test('wrong original password cannot initialize',async()=>{await assert.rejects(diary.createSetup('wrong synthetic password',reference,CHECK));});
test('RSA key thumbprint is deterministic canonical e,kty,n SHA256',async()=>{
  const p=setup.public.jwk,canonical=JSON.stringify({e:p.e,kty:p.kty,n:p.n});
  assert.equal(await diary.fingerprint(p),nodeCrypto.createHash('sha256').update(canonical).digest('base64url'));
  assert.equal(await diary.fingerprint({n:p.n,kty:p.kty,e:p.e}),setup.public.keyId);
});
test('agent public-key encryption round-trip preserves approved plaintext',async()=>{
  assert.deepEqual(await diary.decryptEntry(entry,privateKey,setup.public.keyId,ID),{id:ID,...CONTENT});
  const s=JSON.stringify(entry);for(const value of [PASSWORD,CONTENT.date,CONTENT.title,CONTENT.body])assert.ok(!s.includes(value));
  assert.equal(Buffer.from(entry.wrappedKey,'base64').length,384);assert.equal(Buffer.from(entry.iv,'base64').length,12);
});
test('missing or changed trusted fingerprint blocks encryption',async()=>{
  await assert.rejects(diary.encryptEntry(setup.public,undefined,ID,CONTENT));
  await assert.rejects(diary.encryptEntry(setup.public,'A'.repeat(43),ID,CONTENT));
  const fake=structuredClone(setup.public);fake.keyId='B'.repeat(43);await assert.rejects(diary.validatePublic(fake));
});
test('private JWK fields and invalid RSA parameters rejected',async()=>{
  for(const changes of [{d:'secret'},{e:'Aw'},{n:'AA'}]){const p=structuredClone(setup.public);Object.assign(p.jwk,changes);await assert.rejects(diary.validatePublic(p));}
});
test('wrong password, tampered wrapper, salt and key identity fail closed',async()=>{
  await assert.rejects(diary.unlock(setup.vault,setup.public,'wrong'));
  for(const field of ['ct','iv']){const v=structuredClone(setup.vault);const b=Buffer.from(v.cipher[field],'base64');b[0]^=1;v.cipher[field]=b.toString('base64');await assert.rejects(diary.unlock(v,setup.public,PASSWORD));}
  const v=structuredClone(setup.vault);v.kdf.salt=nodeCrypto.randomBytes(16).toString('base64');await assert.rejects(diary.unlock(v,setup.public,PASSWORD));
  const wrongId=structuredClone(setup.vault);wrongId.keyId='C'.repeat(43);await assert.rejects(diary.unlock(wrongId,setup.public,PASSWORD));
});
test('entry ciphertext, wrapped key and IV tampering rejected',async()=>{
  for(const field of ['ct','wrappedKey','iv']){const e=structuredClone(entry),b=Buffer.from(e[field],'base64');b[0]^=1;e[field]=b.toString('base64');await assert.rejects(diary.decryptEntry(e,privateKey,setup.public.keyId,ID));}
});
test('wrapped private key must match the advertised public key',async()=>{
  const other=await globalThis.crypto.subtle.generateKey({name:'RSA-OAEP',modulusLength:3072,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['encrypt','decrypt']);
  const raw=new Uint8Array(await globalThis.crypto.subtle.exportKey('pkcs8',other.privateKey));
  const v=structuredClone(setup.vault),header={format:v.format,version:1,keyId:v.keyId,kdf:v.kdf};
  const salt=Buffer.from(v.kdf.salt,'base64'),key=nodeCrypto.pbkdf2Sync(PASSWORD,salt,600000,32,'sha256'),iv=nodeCrypto.randomBytes(12),cipher=nodeCrypto.createCipheriv('aes-256-gcm',key,iv);cipher.setAAD(Buffer.from(JSON.stringify(header)));
  const ct=Buffer.concat([cipher.update(raw),cipher.final(),cipher.getAuthTag()]);raw.fill(0);key.fill(0);v.cipher.iv=iv.toString('base64');v.cipher.ct=ct.toString('base64');
  await assert.rejects(diary.unlock(v,setup.public,PASSWORD));
});
test('envelopes interoperate with the independent Node crypto API',()=>{
  const v=setup.vault,header={format:v.format,version:1,keyId:v.keyId,kdf:v.kdf};
  const pwKey=nodeCrypto.pbkdf2Sync(PASSWORD,Buffer.from(v.kdf.salt,'base64'),600000,32,'sha256');
  const box=Buffer.from(v.cipher.ct,'base64'),decipher=nodeCrypto.createDecipheriv('aes-256-gcm',pwKey,Buffer.from(v.cipher.iv,'base64'));decipher.setAAD(Buffer.from(JSON.stringify(header)));decipher.setAuthTag(box.subarray(-16));
  const pkcs8=Buffer.concat([decipher.update(box.subarray(0,-16)),decipher.final()]);pwKey.fill(0);
  const rsa=nodeCrypto.createPrivateKey({key:pkcs8,format:'der',type:'pkcs8'});pkcs8.fill(0);
  const eHeader={format:entry.format,version:1,suite:entry.suite,keyId:entry.keyId,id:entry.id},label=Buffer.from(JSON.stringify(eHeader));
  const dataKey=nodeCrypto.privateDecrypt({key:rsa,oaepHash:'sha256',oaepLabel:label,padding:nodeCrypto.constants.RSA_PKCS1_OAEP_PADDING},Buffer.from(entry.wrappedKey,'base64'));
  const ct=Buffer.from(entry.ct,'base64'),aes=nodeCrypto.createDecipheriv('aes-256-gcm',dataKey,Buffer.from(entry.iv,'base64'));aes.setAAD(label);aes.setAuthTag(ct.subarray(-16));
  const plain=Buffer.concat([aes.update(ct.subarray(0,-16)),aes.final()]);dataKey.fill(0);assert.deepEqual(JSON.parse(plain.toString('utf8')),CONTENT);plain.fill(0);
});
test('entry cannot be relabelled, moved to another UUID or key identity',async()=>{
  await assert.rejects(diary.decryptEntry(entry,privateKey,setup.public.keyId,ID2));
  const changed={...entry,id:ID2};await assert.rejects(diary.decryptEntry(changed,privateKey,setup.public.keyId,ID2));
  await assert.rejects(diary.decryptEntry({...entry,keyId:'D'.repeat(43)},privateKey,'D'.repeat(43),ID));
  await assert.rejects(diary.decryptEntry({...entry,suite:'RSA-OTHER'},privateKey,setup.public.keyId,ID));
});
test('each encryption uses a new key and IV, including stable-ID retries',async()=>{
  const next=await diary.encryptEntry(setup.public,setup.public.keyId,ID,CONTENT);
  assert.notEqual(next.iv,entry.iv);assert.notEqual(next.wrappedKey,entry.wrappedKey);assert.notEqual(next.ct,entry.ct);
});
test('content validation rejects invalid dates, extra fields, excessive text and tags',()=>{
  for(const change of [{date:'2026-02-30'},{body:''},{body:'x'.repeat(20001)},{tags:Array(9).fill('a')},{extra:'not permitted'}])assert.throws(()=>diary.validateContent({...CONTENT,...change}));
});
test('manifest rejects traversal, duplicate IDs, foreign key and excessive entries',()=>{
  const good={...setup.manifest,entries:[ID]};assert.deepEqual(diary.validateManifest(good,setup.public.keyId),good);
  for(const ids of [[ID,ID],['../vault'],Array(5001).fill(ID)])assert.throws(()=>diary.validateManifest({...good,entries:ids},setup.public.keyId));
  assert.throws(()=>diary.validateManifest(good,'wrong'));
});
test('public key does not authenticate author: any holder can encrypt',async()=>{
  const outsider=JSON.parse(JSON.stringify(setup.public));const e=await diary.encryptEntry(outsider,outsider.keyId,ID2,CONTENT);
  assert.equal((await diary.decryptEntry(e,privateKey,outsider.keyId,ID2)).body,CONTENT.body);
});
test('CLI encrypts stdin with public key only and refuses overwrite and changed pin',async()=>{
  const publicFile=path.join(temp,'public.json'),out=path.join(temp,ID+'.json');fs.writeFileSync(publicFile,JSON.stringify(setup.public));
  const command=path.resolve(__dirname,'../encrypt-entry.cjs'),args=[command,'--public',publicFile,'--expected-key-id',setup.public.keyId,'--id',ID,'--out',out];
  const first=spawnSync(process.execPath,args,{input:JSON.stringify(CONTENT),encoding:'utf8'});assert.equal(first.status,0,first.stderr);
  assert.ok(!first.stdout.includes(CONTENT.body));assert.ok(!first.stderr.includes(CONTENT.body));
  const before=fs.readFileSync(out,'utf8');assert.equal((await diary.decryptEntry(JSON.parse(before),privateKey,setup.public.keyId,ID)).body,CONTENT.body);
  const repeat=spawnSync(process.execPath,args,{input:JSON.stringify(CONTENT),encoding:'utf8'});assert.notEqual(repeat.status,0);assert.equal(fs.readFileSync(out,'utf8'),before);
  const wrong=args.slice();wrong[wrong.indexOf('--expected-key-id')+1]='E'.repeat(43);wrong[wrong.indexOf('--out')+1]=path.join(temp,'bad.json');assert.notEqual(spawnSync(process.execPath,wrong,{input:JSON.stringify(CONTENT)}).status,0);assert.ok(!fs.existsSync(path.join(temp,'bad.json')));
  assert.ok(!fs.readdirSync(temp).some(n=>n.includes('ciphertext-tmp')));
});
test('manifest proposal preserves previous IDs, detects repeats and records base hash',()=>{
  const file=path.join(temp,'manifest.json'),entryFile=path.join(temp,ID+'.json'),raw=JSON.stringify({...setup.manifest,entries:[ID2]});fs.writeFileSync(file,raw);
  const args=[path.resolve(__dirname,'../prepare-manifest.cjs'),'--manifest',file,'--entry',entryFile,'--expected-key-id',setup.public.keyId];
  const result=spawnSync(process.execPath,args,{encoding:'utf8'});assert.equal(result.status,0,result.stderr);const proposal=JSON.parse(result.stdout);
  assert.deepEqual(proposal.manifest.entries,[ID2,ID]);assert.equal(proposal.baseManifestSha256,nodeCrypto.createHash('sha256').update(raw).digest('hex'));assert.equal(fs.readFileSync(file,'utf8'),raw);
  fs.writeFileSync(file,JSON.stringify(proposal.manifest));const repeat=JSON.parse(spawnSync(process.execPath,args,{encoding:'utf8'}).stdout);assert.equal(repeat.alreadyIndexed,true);assert.equal(repeat.manifest.entries.length,2);
});
test('browser source has no secret storage, plaintext HTML rendering or logging',()=>{
  for(const file of ['diary/reader.js','diary/crypto.js','tools/diary/initialize.js']){const s=fs.readFileSync(path.resolve(__dirname,'../../..',file),'utf8');assert.ok(!/localStorage|sessionStorage|indexedDB|innerHTML|console\./.test(s),file);}
  const html=fs.readFileSync(path.resolve(__dirname,'../winter-diary-initialize-offline.html'),'utf8');assert.ok(html.includes("connect-src 'none'"));assert.ok(html.includes("form-action 'none'"));assert.ok(!/<(?:script|link)[^>]+(?:src|href)=/.test(html));
  for(const match of html.matchAll(/<script>([\s\S]*?)<\/script>/g)){const hash=nodeCrypto.createHash('sha256').update(match[1]).digest('base64');assert.ok(html.includes("'sha256-"+hash+"'"));}
});
test('setup inspector requires the trusted fingerprint and rejects synthetic packages',()=>{
  const file=path.join(temp,'setup.json'),cmd=path.resolve(__dirname,'../inspect-setup.cjs');fs.writeFileSync(file,JSON.stringify(setup));
  const run=pin=>spawnSync(process.execPath,[cmd,'--setup',file,'--expected-key-id',pin],{encoding:'utf8'});
  const good=run(setup.public.keyId);assert.equal(good.status,0,good.stderr);const receipt=JSON.parse(good.stdout);assert.equal(receipt.decryptionVerified,false);assert.equal(receipt.encryptedPrivateKey,true);
  assert.notEqual(run('X'.repeat(43)).status,0);
  fs.writeFileSync(file,JSON.stringify({...setup,format:'winter-diary-self-test'}));assert.notEqual(run(setup.public.keyId).status,0);
});
test('both online initializers are self-contained and every inline script is hash-bound',()=>{
  for(const file of ['diary/setup/index.html','diary/setup/self-test.html']){
    const s=fs.readFileSync(path.resolve(__dirname,'../../..',file),'utf8');assert.ok(s.includes("connect-src 'none'"));assert.ok(s.includes("form-action 'none'"));assert.ok(!/<(?:script|link|img)[^>]+(?:src|href)=/.test(s));assert.ok(!/\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket/.test(s));
    for(const m of s.matchAll(/<script>([\s\S]*?)<\/script>/g)){assert.ok(s.includes("'sha256-"+nodeCrypto.createHash('sha256').update(m[1]).digest('base64')+"'"));}
    for(const m of s.matchAll(/<style>([\s\S]*?)<\/style>/g)){assert.ok(s.includes("'sha256-"+nodeCrypto.createHash('sha256').update(m[1]).digest('base64')+"'"));}
  }
});
