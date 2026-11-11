import "./styles.css";
import { loadConfig, assetUrl } from "./config.js";
import { createStarfield } from "./particles.js";
import { PhotoSphere } from "./sphere.js";
import { createLetterScene } from "./letter.js";

const $=id=>document.getElementById(id);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;
createStarfield($("ambientCanvas"));
let cfg,sphere,letter,playing=false,stage="intro",audio=null;
function showStage(id) {
  for(const el of document.querySelectorAll(".stage"))el.classList.toggle("is-active",el.id===id);
  stage=id;
}
function applyConfig(c) {
  document.title=(c.pageTitle||"HeartGift")+" · HeartGift";
  $("topbarNote").textContent=c.topbarNote||"Made with love";
  $("introTitle").replaceChildren(document.createTextNode(c.intro?.title||"A small gift,"), document.createElement("br"));
  const emphasis=document.createElement("em");emphasis.textContent=c.intro?.emphasis||"a whole lot of love.";
  $("introTitle").appendChild(emphasis);
  $("introCopy").textContent=c.intro?.subtitle||"Something special for you.";
  $("startLabel").textContent=c.intro?.button||"Hold to begin";
  letter=createLetterScene(c,()=>location.reload());
  $("openLetterButton").addEventListener("click",()=>{showStage("letter");letter.start();});
  if(c.music?.src) {
    audio=new Audio(assetUrl(c.music.src));
    audio.loop=true;audio.volume=Math.min(1,Math.max(0,c.music.volume??.4));
  }
}
async function morphWords() {
  showStage("morph");
  for(const word of cfg.morphTexts||["YOU","ARE","LOVED"]) {
    $("morphWord").classList.remove("is-shown");
    await sleep(reduced?80:320);
    $("morphWord").textContent=word;
    $("morphWord").classList.add("is-shown");
    await sleep(reduced?220:1680);
  }
}
function galleryFallback() {
  const root=$("sphereRoot");
  root.classList.add("sphere-fallback");
  for(const path of cfg.photos) {
    const img=new Image();img.src=assetUrl(path);img.alt="A cherished memory";
    root.appendChild(img);
  }
  $("galleryHint").textContent="Your memories are here ♡";
  $("openLetterButton").classList.remove("is-hidden");
}
function gallery() {
  showStage("gallery");
  const button=$("openLetterButton");
  button.classList.add("is-hidden");
  let taps=0;
  try{
    sphere=new PhotoSphere($("sphereRoot"),cfg.photos,()=>{
      taps++;
      if(taps===1){sphere.focus();$("galleryHint").textContent="One more tap to set them free ✨";}
      else if(taps===2){sphere.explode();$("galleryHint").textContent="Every little moment matters";button.classList.remove("is-hidden");}
    });
  }catch(e){console.warn("WebGL not available. Falling back to the photo grid.",e);sphere?.destroy();galleryFallback();}
}
async function begin() {
  if(playing)return;playing=true;
  if(audio)audio.play().catch(()=>{/* autoplay permission is optional */});
  $("startButton").classList.remove("is-holding");
  await morphWords();
  gallery();
}
function holdToStart() {
  const btn=$("startButton");
  let timer=null,started=false;
  function down(e){
    if(playing)return;
    if(e.pointerType==="mouse" && e.button!==0)return;
    e.preventDefault();
    btn.classList.add("is-holding");started=false;
    timer=setTimeout(()=>{started=true;timer=null;begin();},900);
  }
  function up(){
    if(timer!==null){clearTimeout(timer);timer=null;}
    btn.classList.remove("is-holding");
  }
  btn.addEventListener("pointerdown",down);
  for(const event of ["pointerup","pointercancel","pointerleave"])btn.addEventListener(event,up);
  btn.addEventListener("keydown",e=>{
    if((e.key==="Enter"||e.key===" ")&&!playing){e.preventDefault();begin();}
  });
}
async function boot(){
  try{cfg=await loadConfig();applyConfig(cfg);holdToStart();}
  catch(e){
    console.error("HeartGift initialization failed",e);
    $("introCopy").textContent="Unable to load the gift configuration. Please check public/config.json.";
    $("startButton").disabled=true;
  }
}
boot();
// A minimal, internal readiness signal for automated acceptance tests.
window.addEventListener("pagehide",()=>sphere?.destroy(),{once:true});
