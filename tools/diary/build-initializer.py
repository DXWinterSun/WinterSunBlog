#!/usr/bin/env python3
"""Build self-contained HTTPS/offline initializers; never takes a real password."""
import base64,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def digest(text):
    return "'sha256-"+base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()+"'"
def build(reference,test_mode=False):
    html=(HERE/'initialize.template.html').read_text()
    crypto=(ROOT/'diary/crypto.js').read_text()
    initializer=(HERE/'initialize.js').read_text().replace('/*REFERENCE*/',json.dumps(reference,ensure_ascii=False)).replace('/*TEST_MODE*/','true' if test_mode else 'false')
    html=html.replace('/*STYLE*/',(ROOT/'diary/style.css').read_text()).replace('/*CRYPTO*/',crypto).replace('/*INITIALIZER*/',initializer)
    if test_mode:
        html=html.replace('装好冬的日记 · 本机初始化','日记浏览器合成测试').replace('装好冬的<span>日记</span>','合成数据<span>测试</span>').replace('只初始化一次，以后可以让 dot 帮你记。','仅测试浏览器，不使用真实密码或私人内容。').replace('「雪地」的原密码','公开测试口令：diary-browser-self-test-only').replace('我确认创建一套日记专用密钥，用现有密码加密私钥，并下载加密备份包。该包用于以后持续解锁日记，我会妥善保管。此操作不自动上传，也不会给 dot 密码或明文私钥。','我确认仅使用页面上显示的公开测试口令进行合成测试，不输入真实密码。测试包不能用于启用日记。').replace('下载加密备份包','下载合成测试包')
    style=html.split('<style>',1)[1].split('</style>',1)[0]
    policy="default-src 'none'; script-src "+digest(crypto)+' '+digest(initializer)+"; style-src "+digest(style)+"; connect-src 'none'; img-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'"
    return html.replace('<!--CSP-->','<meta http-equiv="Content-Security-Policy" content="'+policy+'">')
reference=json.loads((HERE/'reference-vault.json').read_text())
html=build(reference)
(HERE/'winter-diary-initialize-offline.html').write_text(html)
out=ROOT/'diary/setup';out.mkdir(exist_ok=True)
(out/'index.html').write_text(html)
synthetic=json.loads((HERE/'synthetic-reference.json').read_text())
(out/'self-test.html').write_text(build(synthetic,True))
print('Built isolated initializers. No real password or private content used.')
