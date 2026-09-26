function loadExample(examplePath,reveal=false){
    if(!examplePath)return;
    fetch(examplePath).then(response=>response.text()).then(text=>{document.getElementById("example-code").textContent=text;});
    if(reveal){
        document.getElementById("example-select2").hidden=false;
    }
    document.getElementById("example-select").value="";
    document.getElementById("example-select2").value="";
}