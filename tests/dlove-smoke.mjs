import { chromium } from '@playwright/test';
import {spawn} from 'node:child_process';
import {createServer} from 'node:net';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
const base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const logs=process.env.HEARTGIFT_LOG_DIR || path.join(os.tmpdir(),'heartgift-dlove-smoke');
mkdirSync(logs,{recursive:true});
const cfg=JSON.parse(readFileSync(path.join(base,'site/gift-config.json')));
const wish='19.11 làm sao em để anh iu của em thiệt thòi được. Món quà nhỏ gửi đến anh, mong rằng mỗi ngày của anh đều ngập tràn hạnh phúc. Cảm ơn anh vì đã xuất hiện trong cuộc đời em.';
const details=[],errors=[];
function record(stage,more={}){const row={stage,...more};details.push(row);console.log(JSON.stringify(row))}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function freePort(){return new Promise((resolve,reject)=>{
 const s=createServer();s.on('error',reject);s.listen(0,'127.0.0.1',()=>{const port=s.address().port;s.close(()=>resolve(port))});
})}
let server,browser,port;
const externalApiCalls=[];
try{
 let url=process.env.HEARTGIFT_BASE_URL||'';
 if(url){
  if(!/^https:\/\//.test(url))throw Error('Live test URL must be HTTPS');
  url=url.endsWith('/')?url:url+'/';
  record('test-target',{url,kind:'public GitHub Pages'});
 }else{
  port=await freePort();
  server=spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1','--directory',path.join(base,'site')],{cwd:base,stdio:['ignore','pipe','pipe']});
  writeFileSync(path.join(logs,'resource-registry.json'),JSON.stringify({task_id:'dlove-original-1911-smoke',owner:'TASK-OWNED',pid:server.pid,port,created:new Date().toISOString(),cwd:base},null,2));
  url='http://127.0.0.1:'+port+'/';
  for(let i=0;i<70;i++){if(server.exitCode!==null)throw Error('server exited');
   try{if((await fetch(url)).ok)break;}catch(_){/* retry */} await sleep(120);
  }
 }
 browser=await chromium.launch({headless:true,...(process.env.CHROME_BINARY?{executablePath:process.env.CHROME_BINARY}:{}),args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:900,height:780}});
 // Capture real Audio elements created by the original DLove viewer; do not mock playback.
 await page.addInitScript(()=>{
   const NativeAudio=window.Audio;
   window.__heartgiftAudioInstances=[];
   function AuditedAudio(...args){
     const element=new NativeAudio(...args);
     window.__heartgiftAudioInstances.push(element);
     return element;
   }
   AuditedAudio.prototype=NativeAudio.prototype;
   window.Audio=AuditedAudio;
 });
 const openingPhotoResponses=[];
 page.on('response',r=>{if(r.url().includes('/images/photos/01.webp')&&r.ok())openingPhotoResponses.push(r.url())});
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',req=>{if(req.url().includes('apiv2.deargift.online'))externalApiCalls.push(req.url())});
 page.on('response',r=>{if(r.status()>=400 && r.url().startsWith(url))errors.push('HTTP '+r.status()+' '+r.url())});
 page.on('requestfailed',r=>{if(r.url().startsWith(url))errors.push('request failed '+r.url())});
 // Test full experience with the actual published config and real images (no mocked assets).
 await page.goto(url,{waitUntil:'domcontentloaded',timeout:25000});
 await page.locator('#start-wrap').waitFor({state:'visible',timeout:25000});
 await page.waitForFunction(()=>getComputedStyle(document.getElementById('loading')).display==='none',undefined,{timeout:30000});
 if(cfg.particleImage!=='images/photos/01.webp')throw Error('Wrong particle image config: '+cfg.particleImage);
 if(!openingPhotoResponses.length)throw Error('Opening particle photo 01.webp was not fetched before start screen');
 record('opening-particle-image-is-01',{photo:cfg.particleImage,requests:openingPhotoResponses.length});
 record('start-visible',{title:await page.title()});
 const start=await page.locator('#start-wrap').boundingBox();
 await page.mouse.move(start.x+start.width/2,start.y+start.height/2);await page.mouse.down();await sleep(1450);await page.mouse.up();
 record('held-start');
 // Verify the authorized original MP3 is really loaded and playback has begun.
 await page.waitForFunction((track)=>window.__heartgiftAudioInstances?.some(audio=>
   audio.src.includes(track) && audio.readyState>=1 && !audio.paused && audio.currentTime>0
 ),'noinaycoanh.mp3',{timeout:12000,polling:300});
 const musicState=await page.evaluate(()=>{
   const audio=window.__heartgiftAudioInstances.find(a=>a.src.includes('noinaycoanh.mp3'));
   return {src:audio.src,readyState:audio.readyState,paused:audio.paused,position:audio.currentTime,duration:audio.duration};
 });
 if(!Number.isFinite(musicState.duration)||musicState.duration<30)throw Error('Original soundtrack duration invalid: '+JSON.stringify(musicState));
 record('original-music-playing',musicState);
 await page.locator('#sphere-click-hint').waitFor({state:'attached',timeout:8000});
 // Wait for the actual 3D gallery rather than assuming fixed morph duration.
 await page.waitForFunction(()=>Number(document.documentElement.dataset.heartgiftSphereTiles)>0,undefined,{timeout:75000,polling:300});
 const tileCount=Number(await page.locator('html').getAttribute('data-heartgift-sphere-tiles'));
 if(tileCount!==cfg.sphereImages.length)throw Error('Sphere repeated photos: '+tileCount+' tiles for '+cfg.sphereImages.length+' images');
 record('sphere-has-unique-tiles',{tileCount});
 await sleep(4900); // Wait for the incoming sphere's intro animation before tapping.
 await page.screenshot({path:path.join(logs,'original-sphere-with-user-photos.png')});
 await page.mouse.click(450,390);await sleep(2200);await page.mouse.click(450,390);
 const fly=page.locator('#btn-flying-corner');
 await fly.waitFor({state:'visible',timeout:12000});
 const flyingCount=Number(await page.locator('html').getAttribute('data-heartgift-flying-cards'));
 if(flyingCount!==cfg.sphereImages.length)throw Error('Flying cards repeated photos: '+flyingCount+' for '+cfg.sphereImages.length);
 record('sphere-two-clicks',{flyingCount});
 await fly.click();
 await page.locator('#letter-envelope-img.visible').waitFor({timeout:12000});
 record('cupid-envelope-visible');
 await page.screenshot({path:path.join(logs,'original-envelope.png')});
 await page.locator('#letter-envelope-img').click();
 await page.locator('#cupid-letter-frame.visible').waitFor({timeout:10000});
 await page.locator('.letter-content.typing-complete').waitFor({timeout:20000});
 await sleep(800);
 const received=await page.locator('.letter-content').innerText();
 if(received!==wish)throw Error('The letter text does not match exactly');
 if(!(await page.locator('#letterImageWrap').isVisible()))throw Error('Letter photo missing');
 await page.locator('#letterInlineImage').evaluate(async img=>{if(!img.complete)await new Promise(r=>{img.onload=r;img.onerror=r});if(!img.naturalWidth)throw Error('Letter image did not load')});
 const finalSrc=await page.locator('#letterInlineImage').getAttribute('src');
 if(!finalSrc?.includes(cfg.letter.image))throw Error('Unexpected letter image '+finalSrc+' expected '+cfg.letter.image);
 await page.screenshot({path:path.join(logs,'original-letter-with-user-photos.png')});
 record('exact-letter-and-final-photo',{length:received.length,finalSrc});
 if(externalApiCalls.length)throw Error('Original API called: '+externalApiCalls.join('; '));
 if(errors.length)throw Error('Browser errors: '+errors.join('; '));
 record('passed');
}catch(e){errors.push(String(e.stack||e));record('failed',{error:String(e.message||e)});process.exitCode=1;}
finally{
 if(browser)await browser.close();
 if(server && server.exitCode===null){server.kill('SIGTERM');await Promise.race([new Promise(r=>server.once('exit',r)),sleep(2000)]);if(server.exitCode===null){server.kill('SIGKILL');await Promise.race([new Promise(r=>server.once('exit',r)),sleep(600)]);}}
 writeFileSync(path.join(logs,'test-report.json'),JSON.stringify({details,errors,serverStopped:!server || server.exitCode!==null || server.signalCode!==null},null,2));
 record('cleanup',{serverStopped:!server || server.exitCode!==null || server.signalCode!==null,errors:errors.length});
}
