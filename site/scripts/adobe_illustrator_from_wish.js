import {optimize} from 'https://cdn.jsdelivr.net/npm/svgo/+esm';
const default_toolbar=`
<div id="toolbar">
<button data-tool="main-tools">Tools</button>
<button data-tool="main-shape">Shape</button>
<button data-tool="main-fileoptions">File</button>
</div>
`;
const tools=`
<button data-tool="tool-select">Select</button>
<button data-tool="tool-reshape">Reshape</button>
<button data-tool="tool-vecna">Vector Node Tool</button>
<button data-tool="tool-text">Text</button>
<button data-tool="tool-zoom">Zoom</button>
<button data-tool="tool-fill">Fill</button>
<button data-tool="tool-colorset">Color Set</button>
<button data-tool="tool-colorpick">Color Picker</button>
`;
const shapes=`
<button data-tool="shape-rectangle">Rectangle</button>
<button data-tool="shape-circle">Circle</button>
<button data-tool="shape-ellipse">Ellipse</button>
<button data-tool="shape-polygon">Polygon</button>
<button data-tool="shape-line">Line</button>
<button data-tool="shape-star4">Star(4-point)</button>
<button data-tool="shape-star5">Star(5-point)</button>
`;
const fileoptions=`
<button data-tool="file-new">New</button>
<button data-tool="file-resize">Resize Canvas</button>
<button data-tool="file-open">Open</button>
<button data-tool="file-save">Save</button>
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
function get_svg_point(event){
    const point=canvas.createSVGPoint();
    point.x=event.clientX;
    point.y=event.clientY;
    return point.matrixTransform(canvas.getScreenCTM().inverse());
}
function stop_drawing(event){
    if(!drawing){return;}
    if(current_shape.width.baseVal.value===0||current_shape.height.baseVal.value===0){canvas.removeChild(current_shape);}
    drawing=false;
    start_point=null;
    current_shape=null;
    if(canvas.hasPointerCapture(event.pointerId)){canvas.releasePointerCapture(event.pointerId);}
}
function select_element(element){
    selected_element=element;
    const box=element.getBBox();
    const x=box.x;
    const y=box.y;
    const width=box.width;
    const height=box.height;
    const mid_x=x+width/2;
    const mid_y=y+height/2;
    overlay.innerHTML=`<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="none" stroke="#5af" stroke-width="1"/><circle cx="${mid_x}" cy="${y}" r="1.5" fill="#5af"/><circle cx="${mid_x}" cy="${y+height}" r="1.5" fill="#5af"/><circle cx="${x}" cy="${mid_y}" r="1.5" fill="#5af"/><circle cx="${x+width}" cy="${mid_y}" r="1.5" fill="#5af"/><circle cx="${x}" cy="${y}" r="1.5" fill="#5af"/><circle cx="${x+width}" cy="${y}" r="1.5" fill="#5af"/><circle cx="${x}" cy="${y+height}" r="1.5" fill="#5af"/><circle cx="${x+width}" cy="${y+height}" r="1.5" fill="#5af"/><line x1="${mid_x-1.5}" y1="${mid_y-1.5}" x2="${mid_x+1.5}" y2="${mid_y+1.5}" stroke="#5af" stroke-width="1.5" stroke-linecap="round"/><line x1="${mid_x-1.5}" y1="${mid_y+1.5}" x2="${mid_x+1.5}" y2="${mid_y-1.5}" stroke="#5af" stroke-width="1.5" stroke-linecap="round"/>`
}
function deselect_element(){
    overlay.innerHTML="";
    selected_element=null;
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
canvas.addEventListener("pointerdown",(event)=>{
    if(current_tool==="tool-select"){
        if(event.target===canvas){
            deselect_element();
            return;
        }
        if(selected_element!==event.target){
            select_element(event.target);
        }
        translating=true;
        start_point=get_svg_point(event);
        canvas.setPointerCapture(event.pointerId);
    }else if(current_tool==="shape-rectangle"){
        drawing=true;
        start_point=get_svg_point(event);
        current_shape=document.createElementNS("http://www.w3.org/2000/svg","rect");
        current_shape.setAttribute("x",start_point.x);
        current_shape.setAttribute("y",start_point.y);
        current_shape.setAttribute("width",0);
        current_shape.setAttribute("height",0);
        current_shape.setAttribute("fill",current_color);
        canvas.appendChild(current_shape);
        canvas.setPointerCapture(event.pointerId);
    }else{
        return;
    }
});
canvas.addEventListener("pointermove",(event)=>{
    const point=get_svg_point(event);
    if(drawing&&current_shape){
        const x=Math.min(start_point.x,point.x);
        const y=Math.min(start_point.y,point.y);
        const width=Math.abs(point.x-start_point.x);
        const height=Math.abs(point.y-start_point.y);
        current_shape.setAttribute("x",x);
        current_shape.setAttribute("y",y);
        current_shape.setAttribute("width",width);
        current_shape.setAttribute("height",height);
    }else if(translating&&selected_element){
        const dx=point.x-start_point.x;
        const dy=point.y-start_point.y;
        const box=selected_element.getBBox();
        selected_element.setAttribute("x",box.x+dx);
        selected_element.setAttribute("y",box.y+dy);
        start_point=point;
        select_element(selected_element);
    }
});
canvas.addEventListener("pointerup",(event)=>{
    translating=false;
    stop_drawing(event);
    if(canvas.hasPointerCapture(event.pointerId)){
        canvas.releasePointerCapture(event.pointerId);
    }
});
canvas.addEventListener("pointercancel",(event)=>{stop_drawing(event);});
toolbar.addEventListener("click",async (event)=>{
    const tool=event.target.dataset.tool;
    switch(tool){
        case "main-tools":
            toolbar.innerHTML=`
                ${tools}
                <button data-tool="main-return">Back</button>
            `;
            break;
        case "main-shape":
            toolbar.innerHTML=`
                ${shapes}
                <button data-tool="main-return">Back</button>
            `;
            break;
        case "main-fileoptions":
            toolbar.innerHTML=`
                ${fileoptions}
                <button data-tool="main-return">Back</button>
            `;
            break;
        case "main-return":
            toolbar.innerHTML=default_toolbar;
            break;
        case "tool-colorset":
            toolbar.innerHTML=`
                <input type="color" id="color_picker" value="${current_color}">
                <button data-tool="main-return">Done</button>
            `;
            const colorPicker=document.getElementById("color_picker");
            colorPicker.addEventListener("input",(event)=>{
                current_color=event.target.value;
            });
            break;
        case "file-new":
            if(!confirm("This will clear the entire canvas. Okay to proceed?")){break;}
            canvas.innerHTML="";
            deselect_element();
            break;
        case "file-resize":
            const newWidth=parseInt(prompt("Enter new width:",size[0]));
            const newHeight=parseInt(prompt("Enter new height:",size[1]));
            if(Number.isFinite(newWidth)&&Number.isFinite(newHeight)&&newWidth>0&&newHeight>0){
                size=[newWidth,newHeight];
                canvas.setAttribute("width",size[0]);
                canvas.setAttribute("height",size[1]);
                canvas.setAttribute("viewBox",`0 0 ${size[0]} ${size[1]}`);
                overlay.setAttribute("width",size[0]);
                overlay.setAttribute("height",size[1]);
                overlay.setAttribute("viewBox",`0 0 ${size[0]} ${size[1]}`);
            }
            break;
        case "file-open":
            if(!confirm("This will clear the entire canvas. Okay to proceed?")){break;}
            const input=document.createElement("input");
            input.type="file";
            input.accept=".svg";
            input.addEventListener("change",(event)=>{
                const file=event.target.files[0];
                if(file){
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
                        if(loadedSvg.hasAttribute("width")){
                            canvas.setAttribute("width",loadedSvg.getAttribute("width"));
                        }
                        if(loadedSvg.hasAttribute("height")){
                            canvas.setAttribute("height",loadedSvg.getAttribute("height"));
                        }
                        if(loadedSvg.hasAttribute("viewBox")){
                            canvas.setAttribute("viewBox",loadedSvg.getAttribute("viewBox"));
                        }
                        size=[parseFloat(canvas.getAttribute("width"))||480,parseFloat(canvas.getAttribute("height"))||360];
                    };
                    reader.readAsText(file);
                }
            });
            input.click();
            break;
        case "file-save":
            await save_svg(canvas);
            break;
        default:
            current_tool=tool;
            break;
    }
});