import { chromium } from '@playwright/test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifacts=process.env.HEARTGIFT_TEST_OUTPUT || path.join(os.tmpdir(),'heartgift-smoke-output');
fs.mkdirSync(artifacts,{recursive:true});
const executable=process.env.CHROME_BINARY;
const errors=[],stages=[];
let server=null,browser=null,serverClosed=false;
function status(s){stages.push({name:s,time:new Date().toISOString()}); console.log('OK',s);}
async function reservePort(){
  return await new Promise((resolve,reject)=>{
    const s=net.createServer();s.on('error',reject);
    s.listen(0,'127.0.0.1',()=>{const port=s.address().port;s.close(()=>resolve(port));});
  });
}
async function waitReady(url){
  for(let i=0;i<50;i++){
    if(server.exitCode!==null)throw new Error('Preview exited unexpectedly');
    try{const r=await fetch(url,{signal:AbortSignal.timeout(900)});if(r.ok)return;}catch(_){}
    await new Promise(r=>setTimeout(r,160));
  }
  throw new Error('Preview failed to start');
}
try{
  const port=await reservePort();
  const url='http://127.0.0.1:'+port+'/';
  server=spawn(process.execPath,['node_modules/vite/bin/vite.js','preview','--host','127.0.0.1','--port',String(port),'--strictPort'],{
    cwd:dir,stdio:['ignore','pipe','pipe']
  });
  fs.writeFileSync(path.join(artifacts,'resource-registry.json'),JSON.stringify({task:'heartgift-smoke',pid:server.pid,port,cwd:dir,startUtc:new Date().toISOString(),owner:'TASK-OWNED'},null,2));
  server.stdout.on('data',d=>{});
  server.stderr.on('data',d=>{console.error(String(d).slice(0,250))});
  await waitReady(url);status('preview ready');
  browser=await chromium.launch({headless:true,...(executable?{executablePath:executable}:{}),args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl']});
  const page=await browser.newPage({viewport:{width:1100,height:820}});
  page.on('pageerror',e=>errors.push(e.message));
  page.on('requestfailed',req=>{if(req.url().startsWith(url))errors.push(req.url()+': '+req.failure()?.errorText)});
  await page.goto(url,{waitUntil:'networkidle',timeout:25000});
  await page.waitForFunction(()=>document.querySelector('#introCopy')?.textContent.includes('Dành cho anh'));
  assert.match(await page.title(),/19\.11/);status('intro and config');
  await page.screenshot({path:path.join(artifacts,'intro.png')});
  const btn=page.locator('#startButton');
  const rect=await btn.boundingBox();
  assert.ok(rect);
  await page.mouse.move(rect.x+rect.width/2,rect.y+rect.height/2);
  await page.mouse.down();await page.waitForTimeout(1050);await page.mouse.up();
  await page.locator('#gallery.is-active').waitFor({timeout:18000});
  status('hold -> words -> gallery');
  await page.screenshot({path:path.join(artifacts,'sphere.png')});
  const sphere=page.locator('.sphere-canvas');
  if(await sphere.count()){
    await sphere.click({position:{x:440,y:400}});
    await sphere.click({position:{x:440,y:400}});
  }
  await page.locator('#openLetterButton:not(.is-hidden)').waitFor({timeout:5000});
  status('sphere clicks/burst');
  await page.locator('#openLetterButton').click();
  await page.locator('.letter-scene.is-ready').waitFor({timeout:6000});
  status('envelope ready');
  await page.locator('#envelope').click();
  await page.locator('#letterCard.is-complete').waitFor({timeout:17000});
  const wish='19.11 làm sao em để anh iu của em thiệt thòi được. Món quà nhỏ gửi đến anh, mong rằng mỗi ngày của anh đều ngập tràn hạnh phúc. Cảm ơn anh vì đã xuất hiện trong cuộc đời em.';
  assert.equal(await page.locator('#letterContent').innerText(),wish);
  assert.equal(await page.locator('#letterPhotoWrap').isVisible(),true);
  status('full letter and image');
  await page.screenshot({path:path.join(artifacts,'letter.png')});
  await page.locator('#restartButton').click();
  await page.locator('#intro.is-active').waitFor({timeout:10000});
  status('restart');
  const mobile=await browser.newPage({viewport:{width:390,height:844}});
  mobile.on('pageerror',e=>errors.push('mobile: '+e.message));
  await mobile.goto(url,{waitUntil:'networkidle',timeout:20000});
  assert.equal(await mobile.locator('#startButton').isVisible(),true);
  status('mobile');
  await mobile.screenshot({path:path.join(artifacts,'mobile.png')});
  assert.equal(errors.length,0,errors.join('\n'));
}catch(e){errors.push(e.stack||String(e)); console.error('FAILED',e);process.exitCode=1;}
finally{
  if(browser)await browser.close();
  if(server && server.exitCode===null){
    server.kill('SIGTERM');
    await Promise.race([new Promise(r=>server.once('exit',r)),new Promise(r=>setTimeout(r,1600))]);
    if(server.exitCode===null){server.kill('SIGKILL');await Promise.race([new Promise(r=>server.once('exit',r)),new Promise(r=>setTimeout(r,1000))]);}
  }
  serverClosed=!server || server.exitCode!==null;
  fs.writeFileSync(path.join(artifacts,'smoke.json'),JSON.stringify({stages,errors,serverClosed},null,2));
  console.log('FINAL',JSON.stringify({stages:stages.length,errors:errors.length,serverClosed,artifacts}));
}
