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
            </main>
            <aside id="properties"></aside>
        </div>
    </div>
`;
const canvas=document.getElementById("canvas");
const toolbar=document.getElementById("toolbar");
let drawing=false;
let start_point=null;
let current_shape=null;
function get_svg_point(event){
    const point=canvas.createSVGPoint();
    point.x=event.clientX;
    point.y=event.clientY;
    return point.matrixTransform(canvas.getScreenCTM().inverse());
}
canvas.addEventListener("pointerdown",(event)=>{
    if(current_tool=="shape-rectangle"){
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
    if(!drawing||!current_shape){
        return;
    }
    const point=get_svg_point(event);
    const x=Math.min(start_point.x,point.x);
    const y=Math.min(start_point.y,point.y);
    const width=Math.abs(point.x-start_point.x);
    const height=Math.abs(point.y-start_point.y);
    current_shape.setAttribute("x",x);
    current_shape.setAttribute("y",y);
    current_shape.setAttribute("width",width);
    current_shape.setAttribute("height",height);
});
canvas.addEventListener("pointerup",(event)=>{
    if(!drawing){
        return;
    }
    drawing=false;
    start_point=null;
    current_shape=null;
    canvas.releasePointerCapture(event.pointerId);
});
async function save_svg(svg){
    const svgData=new XMLSerializer().serializeToString(svg);
    if("showSaveFilePicker" in window){
        try{
            const handle=await window.showSaveFilePicker({
                suggestedName:"my_drawing.svg",
                types:[{
                    description:"SVG Image",
                    accept:{
                        "image/svg+xml":[".svg"]
                    }
                }]
            });
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
            if(!confirm("This will clear the entire canvas. Okay to proceed?")){
                break;
            }
            canvas.innerHTML="";
            break;
        case "file-resize":
            const newWidth=parseInt(prompt("Enter new width:",size[0]));
            const newHeight=parseInt(prompt("Enter new height:",size[1]));
            if(Number.isFinite(newWidth)&&Number.isFinite(newHeight)&&newWidth>0&&newHeight>0){
                size=[newWidth,newHeight];
                canvas.setAttribute("width",size[0]);
                canvas.setAttribute("height",size[1]);
                canvas.setAttribute("viewBox",`0 0 ${size[0]} ${size[1]}`);
            }
            break;
        case "file-open":
            if(!confirm("This will clear the entire canvas. Okay to proceed?")){
                break;
            }
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