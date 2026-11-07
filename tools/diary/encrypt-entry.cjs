#!/usr/bin/env node
'use strict';
// Encrypt only. Never reads a password, private-key vault, credential, or network.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('../../diary/crypto.js');
let outputPath=null,committed=false,failureReported=false;
function reportFailure(){
  if(failureReported)return;failureReported=true;
  let exists=committed;try{exists=exists||!!(outputPath&&fs.existsSync(outputPath));}catch(_){exists=true;}
  process.stderr.write(exists?'输出路径已有密文，或写入结果需核对。不要覆盖或盲目重试；请先检查该文件与条目编号。\n':'未生成新条目。请核对可信公钥指纹、输入格式和输出路径；不会覆盖已有文件。\n');
  process.exitCode=exists?2:1;
}
process.stdout.on('error',reportFailure);
async function main() {
  const args=process.argv.slice(2),options={};
  for(let i=0;i<args.length;i+=2) {
    if(!['--public','--expected-key-id','--id','--out'].includes(args[i])||!args[i+1]||options[args[i]])throw new Error();
    options[args[i]]=args[i+1];
  }
  for(const key of ['--public','--expected-key-id','--id','--out'])if(!options[key])throw new Error();
  // The expected fingerprint must come from the trusted initialization handoff,
  // not from this mutable public-key file itself.
  const output=path.resolve(options['--out']);outputPath=output;
  if(fs.existsSync(output))throw new Error();
  const pubRaw=fs.readFileSync(options['--public'],'utf8');if(pubRaw.length>4096)throw new Error();
  const pub=JSON.parse(pubRaw);await crypto.validatePublic(pub,options['--expected-key-id']);
  let chunks=[],size=0;
  for await (const chunk of process.stdin) {size+=chunk.length;if(size>crypto.maxEntryBytes+2048)throw new Error();chunks.push(chunk);}
  const buffer=Buffer.concat(chunks);for(const chunk of chunks)chunk.fill(0);chunks=[];
  let input;
  try{input=JSON.parse(buffer.toString('utf8'));}finally{buffer.fill(0);}
  const result=await crypto.encryptEntry(pub,options['--expected-key-id'],options['--id'],input);input=null;
  const encoded=JSON.stringify(result,null,2)+'\n';
  // Ciphertext-only temporary file, then atomic exclusive link. A retry cannot
  // replace an existing entry or leave a partial final file.
  const temporary=output+'.ciphertext-tmp-'+globalThis.crypto.randomUUID();
  let fd;
  try {
    fd=fs.openSync(temporary,'wx',0o600);fs.writeFileSync(fd,encoded,'utf8');fs.fsyncSync(fd);fs.closeSync(fd);fd=undefined;
    fs.linkSync(temporary,output);committed=true;
  }finally{if(fd!==undefined)fs.closeSync(fd);if(fs.existsSync(temporary))fs.unlinkSync(temporary);}
  process.stdout.write(JSON.stringify({id:result.id,keyId:result.keyId,ciphertextBytes:Buffer.byteLength(encoded)})+'\n');
}
main().catch(reportFailure);
