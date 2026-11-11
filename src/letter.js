import {assetUrl} from "./config.js";
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
export function createLetterScene(config,onRestart){
  const envelope=document.getElementById("envelope");
  const scene=document.querySelector(".letter-scene");
  const card=document.getElementById("letterCard");
  const content=document.getElementById("letterContent");
  const imageWrap=document.getElementById("letterPhotoWrap");
  const image=document.getElementById("letterPhoto");
  const caption=document.getElementById("letterCaption");
  const signature=document.getElementById("letterSignature");
  let opened=false,generation=0;
  document.getElementById("letterGreeting").textContent=config.letter.greeting||"Dear you,";
  document.getElementById("restartButton").addEventListener("click",onRestart);
  async function open(){
    if(opened)return;opened=true;scene.classList.add("has-opened");
    envelope.disabled=true;await sleep(650);card.classList.add("is-visible");
    const current=++generation;
    const characters=Array.from(config.letter.message);
    const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;
    content.classList.add("is-typing");content.textContent="";
    if(reduced)content.textContent=characters.join("");
    else for(const char of characters){
      if(generation!==current)return;content.textContent+=char;
      if(content.scrollHeight>content.clientHeight)content.scrollTop=content.scrollHeight;
      await sleep(char==="\n"?200:30);
    }
    if(generation!==current)return;content.classList.remove("is-typing");
    if(config.letter.image){image.src=assetUrl(config.letter.image);caption.textContent=config.letter.caption||"";imageWrap.classList.remove("is-hidden");}
    signature.textContent=config.letter.signature||"";card.classList.add("is-complete");
  }
  envelope.addEventListener("click",open);
  return {
    start(){scene.classList.remove("has-opened");scene.classList.add("is-arriving");setTimeout(()=>scene.classList.add("is-ready"),1600);},
    reset(){generation++;opened=false;scene.className="letter-scene";card.className="letter-card";content.textContent="";imageWrap.classList.add("is-hidden");signature.textContent="";envelope.disabled=false;}
  };
}
