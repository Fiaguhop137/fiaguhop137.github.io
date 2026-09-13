async function createTabbyCat() {
    const firstName = document.getElementById("firstName").value;
    const lastName = document.getElementById("lastName").value;

    const special = document.getElementById("special").value || null;

    const color = document.getElementById("color").value;

    const body = Number(
        document.getElementById("body").value
    );

    const head = Number(
        document.getElementById("head").value
    );

    const likesPets =
        document.getElementById("likesPets").value;

    const bgColor =
        document.getElementById("bgColor").value;


    const payload = {
        petType: {
            sku: "cat_tabbycat",
            type: "cat",
            name: "Cat"
        },

        name: {
            first: firstName,
            last: lastName,
            full: `${firstName} ${lastName}`,
            special: special
        },

        color: color,
        likesPets: likesPets,
        body: body,
        head: head,
        bgColor: bgColor,

        kitten: null,
        hat: null,
        glasses: null,
        toy: null
    };


    const response = await fetch(
        "https://tabbycats.club/save",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(payload)
        }
    );


    if (!response.ok) {
        throw new Error(
            `Tabby Cats server returned HTTP ${response.status}`
        );
    }


    const snapshotId =
        (await response.text()).trim();

    return `https://tabbycats.club/cat/${snapshotId}`;
}


document
    .getElementById("createCat")
    .addEventListener("click", async () => {

        const button =
            document.getElementById("createCat");

        const result =
            document.getElementById("result");

        button.disabled = true;
        result.textContent = "Creating cat...";

        try {
            const permalink =
                await createTabbyCat();

            result.innerHTML =
                `<a href="${permalink}" target="_blank">
                    ${permalink}
                </a>`;

        } catch (error) {
            console.error(error);

            result.textContent =
                `Failed to create cat: ${error.message}`;

        } finally {
            button.disabled = false;
        }
    });