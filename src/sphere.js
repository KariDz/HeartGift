import * as THREE from "three";
import { assetUrl } from "./config.js";

/**
 * Self-contained photo galaxy; images are set in public/config.json.
 * WebGL is optional: the caller can fall back to a CSS photo gallery.
 */
export class PhotoSphere {
  constructor(container, photos, onTap) {
    this.host=container;this.onTap=onTap;this.photos=photos;
    this.scene=new THREE.Scene();
    this.camera=new THREE.PerspectiveCamera(49,1,.1,100);
    this.camera.position.z=14;
    this.group=new THREE.Group();this.scene.add(this.group);
    this.renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:"low-power"});
    this.renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));
    this.renderer.setClearColor(0,0);
    this.renderer.outputColorSpace=THREE.SRGBColorSpace;
    this.renderer.domElement.className="sphere-canvas";
    this.renderer.domElement.setAttribute("aria-label","Drag or tap the memory sphere");
    container.appendChild(this.renderer.domElement);
    this.meshes=[];this.phase="sphere";this.progress=0;this.zoom=14;
    this.drag=false;this.origin=null;this.raf=0;this.dead=false;this.lastTime=0;
    this.resize=this.resize.bind(this);this.animate=this.animate.bind(this);
    this.handleDown=this.handleDown.bind(this);
    this.handleMove=this.handleMove.bind(this);
    this.handleUp=this.handleUp.bind(this);
    window.addEventListener("resize",this.resize);
    const canvas=this.renderer.domElement;
    canvas.addEventListener("pointerdown",this.handleDown);
    canvas.addEventListener("pointermove",this.handleMove);
    canvas.addEventListener("pointerup",this.handleUp);
    canvas.addEventListener("pointercancel",this.handleUp);
    this.createPhotos();
    this.resize();this.raf=requestAnimationFrame(this.animate);
  }
  createPhotos() {
    const total=this.photos.length;
    const loader=new THREE.TextureLoader();
    const r=4.3;
    this.photos.forEach((src,i)=>{
      // A Fibonacci sphere distributes portraits evenly without overlap clusters.
      const y=1-2*(i+.5)/total;
      const radius=Math.sqrt(1-y*y);
      const theta=i*Math.PI*(3-Math.sqrt(5));
      const point=new THREE.Vector3(Math.cos(theta)*radius*r,y*r,Math.sin(theta)*radius*r);
      const frame=new THREE.Group();
      const backing=new THREE.Mesh(new THREE.PlaneGeometry(2.55,3.08),new THREE.MeshBasicMaterial({color:0xffecf5,transparent:true,opacity:.94,side:THREE.DoubleSide}));
      const imageMaterial=new THREE.MeshBasicMaterial({color:0xd9a4c8,side:THREE.DoubleSide,transparent:true});
      const image=new THREE.Mesh(new THREE.PlaneGeometry(2.38,2.9),imageMaterial);
      image.position.z=.018;
      frame.add(backing,image);
      frame.position.copy(point);
      frame.lookAt(point.clone().multiplyScalar(2));
      this.group.add(frame);
      const outward=point.clone().normalize();
      this.meshes.push({frame,point:point.clone(),outward});
      loader.load(assetUrl(src),texture=>{
        if(this.dead){texture.dispose();return;}
        texture.colorSpace=THREE.SRGBColorSpace;
        imageMaterial.map=texture;imageMaterial.color.set(0xffffff);imageMaterial.needsUpdate=true;
      },undefined,()=>{/* a missing image uses a pleasant colored placeholder */});
    });
  }
  resize(){
    if(this.dead)return;
    const w=this.host.clientWidth||innerWidth,h=this.host.clientHeight||innerHeight;
    this.camera.aspect=w/Math.max(h,1);
    this.camera.fov=w<600?65:49;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w,h,false);
    this.renderer.domElement.style.width="100%";
    this.renderer.domElement.style.height="100%";
  }
  handleDown(e){
    if(this.phase==="burst")return;
    this.origin={x:e.clientX,y:e.clientY,lastX:e.clientX,lastY:e.clientY};
    this.drag=false;
    try{this.renderer.domElement.setPointerCapture(e.pointerId);}catch(_){}
  }
  handleMove(e){
    if(!this.origin || this.phase==="burst")return;
    const dx=e.clientX-this.origin.lastX,dy=e.clientY-this.origin.lastY;
    if(Math.hypot(e.clientX-this.origin.x,e.clientY-this.origin.y)>6)this.drag=true;
    if(this.drag){this.group.rotation.y+=dx*.005;this.group.rotation.x=Math.max(-.6,Math.min(.6,this.group.rotation.x+dy*.003));}
    this.origin.lastX=e.clientX;this.origin.lastY=e.clientY;
  }
  handleUp(e){
    if(!this.origin)return;
    const wasDrag=this.drag;
    this.origin=null;this.drag=false;
    if(!wasDrag && e.type==="pointerup" && this.phase!=="burst")this.onTap();
  }
  focus(){if(this.phase==="sphere"){this.phase="focused";this.zoom=11;}}
  explode(){
    if(this.phase==="burst")return;
    this.phase="burst";this.progress=0;
    this.meshes.forEach((mesh,i)=>{
      const jitter=new THREE.Vector3(Math.sin(i*13.4)*1.7,Math.cos(i*9.3)*1.7,Math.sin(i*3.8)*1.5);
      mesh.target=mesh.point.clone().add(mesh.outward.clone().multiplyScalar(4.2)).add(jitter);
    });
  }
  animate(time){
    if(this.dead)return;
    const dt=Math.min((time-this.lastTime)/16.67||1,2.1);this.lastTime=time;
    if(this.phase!=="burst"){this.group.rotation.y+=.0016*dt;}
    if(this.phase==="focused")this.camera.position.z+=(this.zoom-this.camera.position.z)*.055*dt;
    if(this.phase==="burst"){
      this.progress=Math.min(1,this.progress+.018*dt);
      const t=1-Math.pow(1-this.progress,3);
      for(const m of this.meshes){
        m.frame.position.lerpVectors(m.point,m.target,t);
        m.frame.scale.setScalar(1-.22*t);
      }
      this.group.rotation.y+=.0004*dt;
    }
    this.renderer.render(this.scene,this.camera);
    this.raf=requestAnimationFrame(this.animate);
  }
  destroy(){
    if(this.dead)return;this.dead=true;cancelAnimationFrame(this.raf);
    window.removeEventListener("resize",this.resize);
    const canvas=this.renderer.domElement;
    canvas.removeEventListener("pointerdown",this.handleDown);
    canvas.removeEventListener("pointermove",this.handleMove);
    canvas.removeEventListener("pointerup",this.handleUp);
    canvas.removeEventListener("pointercancel",this.handleUp);
    this.group.traverse(object=>{
      if(object.geometry)object.geometry.dispose();
      if(object.material){
        const materials=Array.isArray(object.material)?object.material:[object.material];
        for(const material of materials){material.map?.dispose();material.dispose();}
      }
    });
    this.renderer.dispose();canvas.remove();
  }
}
