#!/usr/bin/env node
'use strict';
// Prepare, never publish. A publisher must compare baseManifestSha256 against
// the latest remote manifest and atomically commit the entry plus new manifest.
const fs=require('node:fs'),nodeCrypto=require('node:crypto'),diary=require('../../diary/crypto.js');
try{
  const args=process.argv.slice(2),opts={};
  for(let i=0;i<args.length;i+=2){if(!['--manifest','--entry','--expected-key-id'].includes(args[i])||!args[i+1]||opts[args[i]])throw Error();opts[args[i]]=args[i+1];}
  if(!opts['--manifest']||!opts['--entry']||!opts['--expected-key-id'])throw Error();
  const raw=fs.readFileSync(opts['--manifest'],'utf8'),encrypted=fs.readFileSync(opts['--entry'],'utf8');if(raw.length>400000||encrypted.length>180000)throw Error();
  const manifest=diary.validateManifest(JSON.parse(raw),opts['--expected-key-id']);
  const entry=diary.inspectEntry(JSON.parse(encrypted));if(entry.keyId!==manifest.keyId)throw Error();
  const alreadyIndexed=manifest.entries.includes(entry.id);if(!alreadyIndexed)manifest.entries.push(entry.id);
  diary.validateManifest(manifest,manifest.keyId);
  process.stdout.write(JSON.stringify({baseManifestSha256:nodeCrypto.createHash('sha256').update(raw).digest('hex'),entryId:entry.id,keyId:entry.keyId,alreadyIndexed,manifest},null,2)+'\n');
}catch(_){process.stderr.write('未准备追加。请核对索引、密文条目和可信公钥指纹。\n');process.exitCode=1;}
