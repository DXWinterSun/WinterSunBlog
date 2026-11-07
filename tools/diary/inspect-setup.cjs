#!/usr/bin/env node
'use strict';
// Validate an encrypted initialization package without requesting a password.
// This command does not decrypt, install, upload, or publish any file.
const fs=require('node:fs'),diary=require('../../diary/crypto.js');
(async()=>{
  const args=process.argv.slice(2);if(args.length!==4||args[0]!=='--setup'||args[2]!=='--expected-key-id')throw Error();
  const raw=fs.readFileSync(args[1],'utf8');if(Buffer.byteLength(raw)>30000)throw Error();
  const bundle=JSON.parse(raw);
  if(!bundle||Object.keys(bundle).sort().join('|')!=='format|manifest|public|vault|version'||bundle.format!=='winter-diary-setup'||bundle.version!==1)throw Error();
  await diary.validatePublic(bundle.public,args[3]);const header=diary.inspectVault(bundle.vault);
  if(header.keyId!==bundle.public.keyId)throw Error();
  const manifest=diary.validateManifest(bundle.manifest,bundle.public.keyId);if(manifest.entries.length!==0)throw Error();
  process.stdout.write(JSON.stringify({validStructure:true,keyId:bundle.public.keyId,entries:0,encryptedPrivateKey:true,decryptionVerified:false})+'\n');
})().catch(()=>{process.stderr.write('加密包或可信指纹未通过检查。没有解密、安装或上传任何文件。\n');process.exitCode=1;});
