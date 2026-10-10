export function get_svg_point(canvas,event){
    const point=canvas.createSVGPoint();
    point.x=event.clientX;
    point.y=event.clientY;
    return point.matrixTransform(canvas.getScreenCTM().inverse());
}
export function translate_element(element,dx,dy){
    const transform=element.getAttribute("transform")||"";
    const translation=`translate(${dx},${dy})`;
    element.setAttribute("transform",transform?`${translation} ${transform}`:translation);
}
export function get_resize_handle(point,box,tolerance=6){
    const handles={
        n:[box.x+box.width/2,box.y],
        s:[box.x+box.width/2,box.y+box.height],
        w:[box.x,box.y+box.height/2],
        e:[box.x+box.width,box.y+box.height/2],
        nw:[box.x,box.y],
        ne:[box.x+box.width,box.y],
        sw:[box.x,box.y+box.height],
        se:[box.x+box.width,box.y+box.height]
    };
    return Object.entries(handles).find(([,position])=>{
        const dx=point.x-position[0];
        const dy=point.y-position[1];
        return dx*dx+dy*dy<=tolerance*tolerance;
    })?.[0]||null;
}
export function get_resize_cursor(handle){
    return {
        n:"ns-resize",
        s:"ns-resize",
        e:"ew-resize",
        w:"ew-resize",
        nw:"nwse-resize",
        se:"nwse-resize",
        ne:"nesw-resize",
        sw:"nesw-resize"
    }[handle]||"default";
}
export function set_resize_handles_visible(overlay,visible){
    overlay.querySelectorAll("[data-handle]").forEach((handle)=>{
        handle.style.display=visible?"":"none";
    });
}
export function resize_element(element,handle,box,dx,dy,originalTransform="",preserveAspect=false){
    const left=box.x+(handle.includes("w")?dx:0);
    const right=box.x+box.width+(handle.includes("e")?dx:0);
    const top=box.y+(handle.includes("n")?dy:0);
    const bottom=box.y+box.height+(handle.includes("s")?dy:0);
    let x=Math.min(left,right);
    let y=Math.min(top,bottom);
    let width=Math.max(1,Math.abs(right-left));
    let height=Math.max(1,Math.abs(bottom-top));
    if(element.localName==="circle"){preserveAspect=true;}
    if(preserveAspect){
        const aspect=box.width/box.height||1;
        if(handle==="e"||handle==="w"){
            height=Math.max(1,width/aspect);
            y=box.y+(box.height-height)/2;
        }else if(handle==="n"||handle==="s"){
            width=Math.max(1,height*aspect);
            x=box.x+(box.width-width)/2;
        }else if(width/height>aspect){
            height=Math.max(1,width/aspect);
        }else{
            width=Math.max(1,height*aspect);
        }
        if(handle.includes("w")){x=box.x+box.width-width;}
        if(handle.includes("n")){y=box.y+box.height-height;}
    }
    if(!originalTransform&&element.localName==="rect"){
        element.setAttribute("x",x);
        element.setAttribute("y",y);
        element.setAttribute("width",width);
        element.setAttribute("height",height);
        return;
    }
    if(!originalTransform&&element.localName==="circle"){
        const radius=width/2;
        element.setAttribute("cx",x+width/2);
        element.setAttribute("cy",y+height/2);
        element.setAttribute("r",radius);
        return;
    }
    if(!originalTransform&&element.localName==="ellipse"){
        element.setAttribute("cx",x+width/2);
        element.setAttribute("cy",y+height/2);
        element.setAttribute("rx",width/2);
        element.setAttribute("ry",height/2);
        return;
    }
    if(!originalTransform&&element.localName==="line"){
        const x1=box.x===parseFloat(element.getAttribute("x1"))?x:x+width;
        const y1=box.y===parseFloat(element.getAttribute("y1"))?y:y+height;
        const x2=box.x===parseFloat(element.getAttribute("x2"))?x:x+width;
        const y2=box.y===parseFloat(element.getAttribute("y2"))?y:y+height;
        element.setAttribute("x1",x1);
        element.setAttribute("y1",y1);
        element.setAttribute("x2",x2);
        element.setAttribute("y2",y2);
        return;
    }
    const scaleX=box.width?width/box.width:1;
    const scaleY=box.height?height/box.height:1;
    const translateX=x-box.x*scaleX;
    const translateY=y-box.y*scaleY;
    element.setAttribute("transform",`translate(${translateX},${translateY}) scale(${scaleX},${scaleY})${originalTransform?` ${originalTransform}`:""}`);
}
function shape_is_empty(shape){
    switch(shape.localName){
        case "rect":
            return shape.width.baseVal.value===0||shape.height.baseVal.value===0;
        case "circle":
            return shape.r.baseVal.value===0;
        case "ellipse":
            return shape.rx.baseVal.value===0||shape.ry.baseVal.value===0;
        default:
            return false;
    }
}
export function stop_drawing(canvas,current_shape,event,cancel=false){
    if(current_shape&&(cancel||shape_is_empty(current_shape))){canvas.removeChild(current_shape);}
    if(event&&typeof event.pointerId==="number"&&canvas.hasPointerCapture(event.pointerId)){
        canvas.releasePointerCapture(event.pointerId);
    }
}
export function select_element(overlay,element){
    const box=element.getBBox();
    const x=box.x;
    const y=box.y;
    const width=box.width;
    const height=box.height;
    const mid_x=x+width/2;
    const mid_y=y+height/2;
    overlay.innerHTML=`
        <rect x="${x}" y="${y}" width="${width}" height="${height}" fill="none" stroke="#5af" stroke-width="1"/>
        <circle data-handle="n" cx="${mid_x}" cy="${y}" r="1.5" fill="#5af"/>
        <circle data-handle="s" cx="${mid_x}" cy="${y+height}" r="1.5" fill="#5af"/>
        <circle data-handle="w" cx="${x}" cy="${mid_y}" r="1.5" fill="#5af"/>
        <circle data-handle="e" cx="${x+width}" cy="${mid_y}" r="1.5" fill="#5af"/>
        <circle data-handle="nw" cx="${x}" cy="${y}" r="1.5" fill="#5af"/>
        <circle data-handle="ne" cx="${x+width}" cy="${y}" r="1.5" fill="#5af"/>
        <circle data-handle="sw" cx="${x}" cy="${y+height}" r="1.5" fill="#5af"/>
        <circle data-handle="se" cx="${x+width}" cy="${y+height}" r="1.5" fill="#5af"/>
        <line x1="${mid_x-1.5}" y1="${mid_y-1.5}" x2="${mid_x+1.5}" y2="${mid_y+1.5}" stroke="#5af" stroke-width="1.5" stroke-linecap="round"/>
        <line x1="${mid_x-1.5}" y1="${mid_y+1.5}" x2="${mid_x+1.5}" y2="${mid_y-1.5}" stroke="#5af" stroke-width="1.5" stroke-linecap="round"/>
    `
    let outline=element.cloneNode(true);
    outline.setAttribute("fill","none");
    outline.setAttribute("stroke","#5af");
    outline.setAttribute("stroke-width","1.5");
    outline.setAttribute("pointer-events","none");
    overlay.appendChild(outline);
}