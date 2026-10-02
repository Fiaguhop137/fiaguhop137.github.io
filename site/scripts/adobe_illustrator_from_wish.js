const default_toolbar=`
<div id="toolbar">
    <button data-tool="tools">Tools</button>
    <button data-tool="shape">Shape</button>
    <button data-tool="ellipse">Ellipse</button>
</div>
`;
const tools=`
<button data-tool="select">Select</button>
<button data-tool="reshape">Reshape</button>
<button data-tool="line">Line</button>
<button data-tool="text">Text</button>
<button data-tool="zoom">Zoom</button>
<button data-tool="hand">Hand</button>
<button data-tool="color">Color</button>
<button data-tool="gradient">Gradient</button>
<button data-tool="stroke">Stroke</button>
<button data-tool="fill">Fill</button>
`;
const da_box=document.getElementById("da_box");
da_box.innerHTML=`
    <div id="editor">
        <div id="sidebar_left">
            ${default_toolbar}
        </div>
        <div id="workspace">
            <aside id="layers"></aside>
            <main id="canvas_container">
                <svg id="canvas" viewBox="0 0 480 360" xmlns="http://www.w3.org/2000/svg">
                </svg>
            </main>
            <aside id="properties"></aside>
        </div>
    </div>
`;
const toolbar=document.getElementById("toolbar");
toolbar.addEventListener("click",(event)=>{
    const tool=event.target.dataset.tool;
    if(tool==="tools"){
        toolbar.innerHTML=`
            ${tools}
            <button data-tool="return">Back</button>
        `;
    }
    if(tool==="return"){
        toolbar.innerHTML=default_toolbar;
    }
});