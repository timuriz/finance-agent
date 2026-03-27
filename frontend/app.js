async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("file", file);

    const responce = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData
    });
    const data = await responce.json();

    document.getElementById("reportOutput").innerText = JSON.stringify(data, null, 2);
}

async function sendMessage() {
    const input = document.getElementById["chatInput"].value;

    const responce = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "aplication/json"
        },
        body: JSON.stringify({message: input})
    });
    const data = await responce.json();
    
    document.getElementById("chatOutput").innerText = data.responce;
}