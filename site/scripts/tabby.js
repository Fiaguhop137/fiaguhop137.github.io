const petTypes={
    cat_tabbycat:{
        type:"cat",
        name:"Cat"
    },
    dog_lildoggo:{
        type:"dog",
        name:"LilDoggo"
    },
    penguin_tuxedobird:{
        type:"penguin",
        name:"TuxedoBird"
    },
    wildcat_leopard:{
        type:"wildcat",
        name:"Leopard"
    },
    bear_bear:{
        type:"bear",
        name:"Bear"
    },
    turtle_tortoise:{
        type:"turtle",
        name:"Tortoise"
    },
    dog_classicdoggo:{
        type:"classicdoggo",
        name:"ClassicDoggo"
    },
    chicken_chicken:{
        type:"chicken",
        name:"Chicken"
    },
    seal_seal:{
        type:"seal",
        name:"Seal"
    },
    bunny_bunny:{
        type:"bunny",
        name:"Bunny"
    },
    pig_pig:{
        type:"pig",
        name:"Pig"
    }
};
function getValue(id){
    return document.getElementById(id).value;
}
function createCat(){
    const petSku=getValue("petType");
    const selectedPet=petTypes[petSku];
    if(!selectedPet){
        document.getElementById("result").textContent="Invalid pet type.";
        return;
    }
    const firstName=getValue("firstName");
    const lastName=getValue("lastName");
    const special=getValue("special");
    const payload={
        petType:{
            sku:petSku,
            type:selectedPet.type,
            name:selectedPet.name
        },
        name:{
            first:firstName,
            last:lastName,
            full:`${firstName} ${lastName}`
        },
        color:getValue("color"),
        body:Number(getValue("body")),
        head:Number(getValue("head")),
        likesPets:getValue("likesPets"),
        bgColor:getValue("bgColor"),
        kitten:getValue("kitten")||null,
        hat:getValue("hat")||null,
        glasses:getValue("glasses")||null,
        toy:getValue("toy")||null
    };
    if(special){
        payload.name.special=special;
    }
    const result=document.getElementById("result");
    result.textContent="Creating cat...";
    fetch("https://tabbycats.club/save",{
        method:"POST",
        mode:"cors",
        cache:"default",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
    })
        .then(response=>{
            if(!response.ok){
                throw new Error(`HTTP ${response.status}`);
            }
            return response.text();
        })
        .then(snapshotId=>{
            const url=`https://tabbycats.club/cat/${snapshotId}`;
            result.innerHTML="";
            const link=document.createElement("a");
            link.href=url;
            link.textContent=url;
            link.target="_blank";
            link.rel="noopener noreferrer";
            result.appendChild(link);
        })
        .catch(error=>{
            console.error(error);
            result.textContent=`Failed to create cat:${error.message}`;
        });
}
document
    .getElementById("createCat")
    .addEventListener("click", createCat);