/** Lightweight accessible ambient particles (no remote assets). */
export function createStarfield(canvas) {
  const ctx=canvas.getContext("2d"); if (!ctx) return ()=>{};
  const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;
  let w=0,h=0,raf=0,dots=[];
  function resize() {
    w=innerWidth;h=innerHeight;
    const d=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.round(w*d);canvas.height=Math.round(h*d);
    canvas.style.width=w+"px";canvas.style.height=h+"px";ctx.setTransform(d,0,0,d,0,0);
    dots=Array.from({length:Math.min(110,Math.max(32,Math.round(w*h/10500)))},()=>({x:Math.random()*w,y:Math.random()*h,r:Math.random()*1.25+.4,phase:Math.random()*6.283,speed:Math.random()*.6+.16}));
  }
  function frame(t) {
    ctx.clearRect(0,0,w,h);ctx.fillStyle="#ffc7e6";
    for(const p of dots){ctx.globalAlpha=reduced?.33:.2+.4*(.5+.5*Math.sin(t*.001*p.speed+p.phase));ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}
    ctx.globalAlpha=1;if(!reduced)raf=requestAnimationFrame(frame);
  }
  resize();addEventListener("resize",resize);frame(0);
  return ()=>{cancelAnimationFrame(raf);removeEventListener("resize",resize);};
}
