import {optimize} from 'https://cdn.jsdelivr.net/npm/svgo/+esm';
import * as utils from './utils.js';
const style=document.createElement("style");
style.textContent=`
html,body{
    width:100%;
    height:100%;
    margin:0;
}
body{
    overflow:hidden;
}
#da_box{
    width:100%;
    height:100%;
}
#editor{
    display:flex;
    width:100%;
    height:100%;
}
#sidebar_left{
    width:180px;
    height:100%;
    flex-shrink:0;
    box-sizing:border-box;
    padding:10px;
    background:#fff;
    border-right:1px solid #aaa;
}
#toolbar{
    display:flex;
    flex-direction:column;
    gap:6px;
}
#toolbar button{
    width:100%;
    padding:10px;
    box-sizing:border-box;
    border:1px solid #bbb;
    border-radius:4px;
    background:#eee;
    color:#000;
    cursor:pointer;
}
#toolbar button:hover{
    background: #ddd;
}
#toolbar button:active {
    background: #ccc;
}
#toolbar button.active {
    background: #bbb;
    border-color: #aaa;
}
#workspace{
    display:flex;
    flex:1;
    min-width:0;
    min-height:0;
}
#canvas_container{
    flex:1;
    min-width:0;
    min-height:0;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#aaa;
    position:relative;
}
#canvas {
    width:80%;
    height:80%;
    background:#fff;
}
#layers {
    width: 180px;
    flex-shrink:0;
    background:#aaa;
    border-right:1px solid #aaa;
}
#properties {
    width:220px;
    flex-shrink:0;
    background:#aaa;
    border-left:1px solid #aaa;
}
#canvas,
#overlay{
    position:absolute;
    width:80%;
    height:80%;
}
#overlay{
    pointer-events:none;
}`
document.head.appendChild(style);
const default_toolbar=`
<div id="toolbar">
<button data-tool="main-tools">T̲ools</button>
<button data-tool="main-shape">S̲hape</button>
<button data-tool="main-fileoptions">F̲ile</button>
</div>
`;
const tools=`
<button data-tool="tool-select">S͟elect</button>
<button data-tool="tool-reshape">R͟eshape</button>
<button data-tool="tool-vecna">V͟ector Node Tool</button>
<button data-tool="tool-text">T͟ext</button>
<button data-tool="tool-zoom">Z͟oom</button>
<button data-tool="tool-fill">F͟ill</button>
<button data-tool="tool-colorset">C͟olor Set</button>
<button data-tool="tool-colorpick">Color P͟icker</button>
`;
const shapes=`
<button data-tool="shape-rectangle">R͟ectangle</button>
<button data-tool="shape-ellipse">E̲llipse</button>
<button data-tool="shape-compass">C̲ompass</button>
<button data-tool="shape-polygon">P̲olygon</button>
<button data-tool="shape-line">L̲ine</button>
`;
const fileoptions=`
<button data-tool="file-new">N̲ew</button>
<button data-tool="file-resize">R̲esize Canvas</button>
<button data-tool="file-open">O̲pen</button>
<button data-tool="file-save">S̲ave</button>
`;
let current_tool="tool-select";
let current_color="#000000";
let size=[480,360];
const da_box=document.getElementById("da_box");
da_box.innerHTML=`
    <div id="editor">
        <div id="sidebar_left">
            ${default_toolbar}
        </div>
        <div id="workspace">
            <aside id="layers"></aside>
            <main id="canvas_container">
                <svg id="canvas"
                    xmlns="http://www.w3.org/2000/svg"
                    width="${size[0]}"
                    height="${size[1]}"
                    viewBox="0 0 ${size[0]} ${size[1]}">
                </svg>
                <svg id="overlay"
                    width="${size[0]}"
                    height="${size[1]}"
                    viewBox="0 0 ${size[0]} ${size[1]}">
                </svg>
            </main>
            <aside id="properties"></aside>
        </div>
    </div>
`;
const canvas=document.getElementById("canvas");
const overlay=document.getElementById("overlay");
const toolbar=document.getElementById("toolbar");
let drawing=false;
let start_point=null;
let current_shape=null;
let selected_element=null;
let translating=false;
let resizing=false;
let resize_handle=null;
let resize_box=null;
let resize_transform="";
let active_pointer_id=null;
function select_element(element){
    selected_element=element;
    utils.select_element(overlay,element);
}
function deselect_element(){
    utils.deselect_element(overlay);
    selected_element=null;
    canvas.style.cursor="default";
}
function reset_interaction(event=null,cancelDrawing=false){
    if(cancelDrawing&&current_shape?.parentNode===canvas){
        canvas.removeChild(current_shape);
    }
    drawing=false;
    start_point=null;
    current_shape=null;
    translating=false;
    resizing=false;
    resize_handle=null;
    resize_box=null;
    resize_transform="";
    if(active_pointer_id!==null&&canvas.hasPointerCapture(active_pointer_id)){
        canvas.releasePointerCapture(active_pointer_id);
    }
    active_pointer_id=null;
    utils.set_resize_handles_visible(overlay,true);
    canvas.style.cursor="default";
}
function is_editable_target(target){
    return target instanceof HTMLElement&&(
        target.isContentEditable||
        ["INPUT","TEXTAREA","SELECT"].includes(target.tagName)
    );
}
function update_active_tool(){
    toolbar.querySelectorAll("[data-tool]").forEach((button)=>{
        button.classList.toggle("active",button.dataset.tool===current_tool);
    });
}
function update_cursor(point,event){
    if(!selected_element||resizing||translating){
        return;
    }
    const box=selected_element.getBBox();
    const handle=utils.get_resize_handle(point,box);
    if(handle){
        canvas.style.cursor=utils.get_resize_cursor(handle);
    }else if(event.target===selected_element||selected_element.contains(event.target)){
        canvas.style.cursor="grab";
    }else{
        canvas.style.cursor="default";
    }
}
async function save_svg(svg){
    const rawSvg=new XMLSerializer().serializeToString(svg);
    const result=optimize(rawSvg,{multipass:true,plugins:['preset-default',{name:'cleanupNumericValues',params:{floatPrecision:3}}]});
    const svgData=result.data;
    if("showSaveFilePicker" in window){
        try{
            const handle=await window.showSaveFilePicker({suggestedName:"my_drawing.svg",types:[{description:"SVG Image",accept:{"image/svg+xml":[".svg"]}}]});
            const writable=await handle.createWritable();
            await writable.write(svgData);
            await writable.close();
        }catch(error){
            if(error.name!=="AbortError") {
                console.error(error);
            }
        }
    }else{
        const blob=new Blob([svgData],{type:"image/svg+xml"});
        const url=URL.createObjectURL(blob);
        const a=document.createElement("a");
        a.href=url;
        a.download="my_drawing.svg";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}
function show_toolbar(content){
    toolbar.innerHTML=`${content}<button data-tool="main-return">B͟ack</button>`;
    update_active_tool();
}
const toolbar_actions={
    "main-tools":()=>show_toolbar(tools),
    "main-shape":()=>show_toolbar(shapes),
    "main-fileoptions":()=>show_toolbar(fileoptions),
    "main-return":()=>{
        toolbar.innerHTML=default_toolbar;
        update_active_tool();
    },
    "tool-colorset":()=>{
        show_toolbar(`<input type="color" id="color_picker" value="${current_color}">`);
        document.getElementById("color_picker").addEventListener("input",(event)=>{
            current_color=event.target.value;
        });
    },
    "file-new":()=>{
        if(!confirm("This will clear the entire canvas. Okay to proceed?")){return;}
        reset_interaction(null,true);
        canvas.innerHTML="";
        deselect_element();
    },
    "file-resize":()=>{
        const newWidth=parseFloat(prompt("Enter new width:",size[0]));
        const newHeight=parseFloat(prompt("Enter new height:",size[1]));
        if(Number.isFinite(newWidth)&&Number.isFinite(newHeight)&&newWidth>0&&newHeight>0){
            size=[newWidth,newHeight];
            canvas.setAttribute("width",size[0]);
            canvas.setAttribute("height",size[1]);
            canvas.setAttribute("viewBox",`0 0 ${size[0]} ${size[1]}`);
            overlay.setAttribute("width",size[0]);
            overlay.setAttribute("height",size[1]);
            overlay.setAttribute("viewBox",`0 0 ${size[0]} ${size[1]}`);
        }
    },
    "file-open":()=>{
        if(!confirm("This will clear the entire canvas. Okay to proceed?")){return;}
        reset_interaction(null,true);
        const input=document.createElement("input");
        input.type="file";
        input.accept=".svg";
        input.addEventListener("change",(event)=>{
            const file=event.target.files[0];
            if(!file){return;}
            const reader=new FileReader();
            reader.onload=(e)=>{
                const parser=new DOMParser();
                const doc=parser.parseFromString(e.target.result,"image/svg+xml");
                const loadedSvg=doc.documentElement;
                if(loadedSvg.nodeName!=="svg"){
                    alert("That isn't a valid SVG file.");
                    return;
                }
                canvas.innerHTML=loadedSvg.innerHTML;
                const viewBox=loadedSvg.getAttribute("viewBox");
                const viewBoxValues=viewBox?.trim().split(/[\s,]+/).map(Number);
                const viewBoxWidth=viewBoxValues?.length===4&&Number.isFinite(viewBoxValues[2])?viewBoxValues[2]:null;
                const viewBoxHeight=viewBoxValues?.length===4&&Number.isFinite(viewBoxValues[3])?viewBoxValues[3]:null;
                const width=parseFloat(loadedSvg.getAttribute("width")||"");
                const height=parseFloat(loadedSvg.getAttribute("height")||"");
                size=[Number.isFinite(width)&&width>0?width:viewBoxWidth||480,Number.isFinite(height)&&height>0?height:viewBoxHeight||360];
                canvas.setAttribute("width",loadedSvg.getAttribute("width")||size[0]);
                canvas.setAttribute("height",loadedSvg.getAttribute("height")||size[1]);
                canvas.setAttribute("viewBox",viewBox||`0 0 ${size[0]} ${size[1]}`);
                overlay.setAttribute("width",canvas.getAttribute("width"));
                overlay.setAttribute("height",canvas.getAttribute("height"));
                overlay.setAttribute("viewBox",canvas.getAttribute("viewBox"));
                deselect_element();
            };
            reader.readAsText(file);
        });
        input.click();
    },
    "file-save":()=>save_svg(canvas)
};
async function resolve_toolbar(tool){
    const action=toolbar_actions[tool];
    if(action){
        await action();
    }else{
        current_tool=tool;
        update_active_tool();
    }
}
const toolbar_shortcuts={
    b:["main-return"],
    c:["tool-colorset","shape-compass"],
    e:["shape-ellipse"],
    f:["main-fileoptions","tool-fill"],
    l:["shape-line"],
    n:["file-new"],
    o:["file-open"],
    p:["tool-colorpick","shape-polygon"],
    r:["tool-reshape","shape-rectangle","file-resize"],
    s:["main-shape","tool-select","file-save"],
    t:["main-tools","tool-text"],
    v:["tool-vecna"],
    z:["tool-zoom"]
};
async function resolve_toolbar_shortcut(key){
    const tools=toolbar_shortcuts[key]||[];
    const tool=tools.find((name)=>toolbar.querySelector(`[data-tool="${name}"]`));
    if(tool){await resolve_toolbar(tool);}
}
document.addEventListener("keydown",async (event)=>{
    if(is_editable_target(event.target)){return;}
    if(event.key==="Escape"){
        reset_interaction(null,true);
        deselect_element();
    }else if(event.key==="Delete"||event.key==="Backspace"){
        if(selected_element){
            canvas.removeChild(selected_element);
            deselect_element();
        }
    }else if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(event.key)){
        if(selected_element){
            let moveAmount=10;
            if(event.shiftKey){moveAmount=1;}
            if(selected_element.localName==="rect"){
                const dx=event.key==="ArrowRight"?moveAmount:event.key==="ArrowLeft"?-moveAmount:0;
                const dy=event.key==="ArrowDown"?moveAmount:event.key==="ArrowUp"?-moveAmount:0;
                const x=parseFloat(selected_element.getAttribute("x")||"0");
                const y=parseFloat(selected_element.getAttribute("y")||"0");
                selected_element.setAttribute("x",x+dx);
                selected_element.setAttribute("y",y+dy);
            }else if(selected_element.localName==="circle"||selected_element.localName==="ellipse"){
                const dx=event.key==="ArrowRight"?moveAmount:event.key==="ArrowLeft"?-moveAmount:0;
                const dy=event.key==="ArrowDown"?moveAmount:event.key==="ArrowUp"?-moveAmount:0;
                const cx=parseFloat(selected_element.getAttribute("cx")||"0");
                const cy=parseFloat(selected_element.getAttribute("cy")||"0");
                selected_element.setAttribute("cx",cx+dx);
                selected_element.setAttribute("cy",cy+dy);
            }else if(selected_element.localName==="line"){
                const dx=event.key==="ArrowRight"?moveAmount:event.key==="ArrowLeft"?-moveAmount:0;
                const dy=event.key==="ArrowDown"?moveAmount:event.key==="ArrowUp"?-moveAmount:0;
                const x1=parseFloat(selected_element.getAttribute("x1")||"0");
                const y1=parseFloat(selected_element.getAttribute("y1")||"0");
                const x2=parseFloat(selected_element.getAttribute("x2")||"0");
                const y2=parseFloat(selected_element.getAttribute("y2")||"0");
                selected_element.setAttribute("x1",x1+dx);
                selected_element.setAttribute("y1",y1+dy);
                selected_element.setAttribute("x2",x2+dx);
                selected_element.setAttribute("y2",y2+dy);
            }else{
                const dx=event.key==="ArrowRight"?moveAmount:event.key==="ArrowLeft"?-moveAmount:0;
                const dy=event.key==="ArrowDown"?moveAmount:event.key==="ArrowUp"?-moveAmount:0;
                utils.translate_element(selected_element,dx,dy);
            }
            select_element(selected_element);
        }
    }else{
        await resolve_toolbar_shortcut(event.key);
    }
});
canvas.addEventListener("pointerdown",(event)=>{
    if(active_pointer_id!==null){return;}
    if(current_tool==="tool-select"){
        const point=utils.get_svg_point(canvas,event);
        const existingHandle=selected_element?utils.get_resize_handle(point,selected_element.getBBox()):null;
        if(event.target===canvas&&!existingHandle){
            deselect_element();
            return;
        }
        if(event.target!==canvas&&selected_element!==event.target){
            select_element(event.target);
        }
        resize_handle=selected_element?utils.get_resize_handle(point,selected_element.getBBox()):null;
        if(resize_handle){
            resizing=true;
            resize_box=selected_element.getBBox();
            resize_transform=selected_element.getAttribute("transform")||"";
        }else{
            translating=true;
        }
        start_point=point;
        utils.set_resize_handles_visible(overlay,false);
        canvas.style.cursor=resizing?utils.get_resize_cursor(resize_handle):"grabbing";
        active_pointer_id=event.pointerId;
        canvas.setPointerCapture(event.pointerId);
    }else{
        active_pointer_id=event.pointerId;
        drawing=true;
        start_point=utils.get_svg_point(canvas,event);
        if(current_tool==="shape-rectangle"){
            current_shape=document.createElementNS("http://www.w3.org/2000/svg","rect");
            current_shape.setAttribute("x",start_point.x);
            current_shape.setAttribute("y",start_point.y);
            current_shape.setAttribute("width",0);
            current_shape.setAttribute("height",0);
            current_shape.setAttribute("fill",current_color);
            canvas.appendChild(current_shape);
            canvas.setPointerCapture(event.pointerId);
        }else if(current_tool==="shape-compass"){
            current_shape=document.createElementNS("http://www.w3.org/2000/svg","circle");
            current_shape.setAttribute("cx",start_point.x);
            current_shape.setAttribute("cy",start_point.y);
            current_shape.setAttribute("r",0);
            current_shape.setAttribute("fill",current_color);
            canvas.appendChild(current_shape);
            canvas.setPointerCapture(event.pointerId);
        }else if(current_tool==="shape-ellipse"){
            current_shape=document.createElementNS("http://www.w3.org/2000/svg","ellipse");
            current_shape.setAttribute("cx",start_point.x);
            current_shape.setAttribute("cy",start_point.y);
            current_shape.setAttribute("rx",0);
            current_shape.setAttribute("ry",0);
            current_shape.setAttribute("fill",current_color);
            canvas.appendChild(current_shape);
            canvas.setPointerCapture(event.pointerId);
        }
    }
});
canvas.addEventListener("pointermove",(event)=>{
    const point=utils.get_svg_point(canvas,event);
    update_cursor(point,event);
    if(drawing&&current_shape){
        if(current_shape.localName==="rect"){
            if(event.shiftKey){
                const dx=point.x-start_point.x;
                const dy=point.y-start_point.y;
                const size=Math.max(Math.abs(dx),Math.abs(dy));
                const x=dx<0 ? start_point.x-size:start_point.x;
                const y=dy<0 ? start_point.y-size:start_point.y;
                current_shape.setAttribute("x",x);
                current_shape.setAttribute("y",y);
                current_shape.setAttribute("width",size);
                current_shape.setAttribute("height",size);
            }else{
                const x=Math.min(start_point.x,point.x);
                const y=Math.min(start_point.y,point.y);
                const width=Math.abs(point.x-start_point.x);
                const height=Math.abs(point.y-start_point.y);
                current_shape.setAttribute("x",x);
                current_shape.setAttribute("y",y);
                current_shape.setAttribute("width",width);
                current_shape.setAttribute("height",height);
            }
        }else if(current_shape.localName==="circle"){
            const dx=point.x-start_point.x;
            const dy=point.y-start_point.y;
            const radius=Math.sqrt(dx*dx+dy*dy);
            current_shape.setAttribute("r",radius);
        }else if(current_shape.localName==="ellipse"){
            if(event.shiftKey){
                const dx=point.x-start_point.x;
                const dy=point.y-start_point.y;
                const size=Math.max(Math.abs(dx),Math.abs(dy));
                const x=dx<0?start_point.x-size:start_point.x;
                const y=dy<0?start_point.y-size:start_point.y;
                current_shape.setAttribute("cx",x+size/2);
                current_shape.setAttribute("cy",y+size/2);
                current_shape.setAttribute("rx",size/2);
                current_shape.setAttribute("ry",size/2);
            }else{
                const x=Math.min(start_point.x,point.x);
                const y=Math.min(start_point.y,point.y);
                const width=Math.abs(point.x-start_point.x);
                const height=Math.abs(point.y-start_point.y);
                current_shape.setAttribute("cx",x+width/2);
                current_shape.setAttribute("cy",y+height/2);
                current_shape.setAttribute("rx",width/2);
                current_shape.setAttribute("ry",height/2);
            }
        }
    }else if(resizing&&selected_element){
        const dx=point.x-start_point.x;
        const dy=point.y-start_point.y;
        utils.resize_element(selected_element,resize_handle,resize_box,dx,dy,resize_transform,event.shiftKey);
        select_element(selected_element);
        utils.set_resize_handles_visible(overlay,false);
    }else if(translating&&selected_element){
        const dx=point.x-start_point.x;
        const dy=point.y-start_point.y;
        const box=selected_element.getBBox();
        if(selected_element.localName==="rect"||selected_element.localName==="image"||selected_element.localName==="text"){
            selected_element.setAttribute("x",box.x+dx);
            selected_element.setAttribute("y",box.y+dy);
        }else if(selected_element.localName==="circle"||selected_element.localName==="ellipse"){
            selected_element.setAttribute("cx",box.x+box.width/2+dx);
            selected_element.setAttribute("cy",box.y+box.height/2+dy);
        }else if(selected_element.localName==="line"){
            const x1=parseFloat(selected_element.getAttribute("x1"))+dx;
            selected_element.setAttribute("x1",x1);
            const y1=parseFloat(selected_element.getAttribute("y1"))+dy;
            selected_element.setAttribute("y1",y1);
            const x2=parseFloat(selected_element.getAttribute("x2"))+dx;
            selected_element.setAttribute("x2",x2);
            const y2=parseFloat(selected_element.getAttribute("y2"))+dy;
            selected_element.setAttribute("y2",y2);
        }else{
            utils.translate_element(selected_element,dx,dy);
        }
        start_point=point;
        select_element(selected_element);
        utils.set_resize_handles_visible(overlay,false);
    }
});
canvas.addEventListener("pointerup",(event)=>{
    if(active_pointer_id!==null&&event.pointerId!==active_pointer_id){return;}
    if(drawing){utils.stop_drawing(canvas,current_shape,event);}
    reset_interaction(event);
    if(selected_element){select_element(selected_element);}
});
canvas.addEventListener("pointercancel",(event)=>{
    if(active_pointer_id!==null&&event.pointerId!==active_pointer_id){return;}
    reset_interaction(event,true);
    if(selected_element){select_element(selected_element);}
});
toolbar.addEventListener("click",async (event)=>{
    const button=event.target.closest("[data-tool]");
    if(!button||!toolbar.contains(button)){return;}
    try{
        await resolve_toolbar(button.dataset.tool);
    }catch(error){
        console.error("Toolbar action failed:",error);
    }
});