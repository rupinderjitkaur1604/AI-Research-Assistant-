console.log("SCRIPT LOADED");


let chats = [];
let currentChat = [];
let uploadedFilePath = null;


// ====================
// Load PDFs on Start
// ====================


async function loadPDFList() {
    try {
        const response = await fetch("/pdfs");
        const data = await response.json();
        renderPDFList(data.pdfs);
    } catch (e) {
        console.error("Failed to load PDFs", e);
    }
}


function renderPDFList(pdfs) {
    const pdfList = document.getElementById("pdfList");
    pdfList.innerHTML = "";


    if (pdfs.length === 0) {
        pdfList.innerHTML = `<div style="color:#888;font-size:12px;padding:4px;">No PDFs uploaded yet.</div>`;
        return;
    }


    pdfs.forEach(filename => {
        const item = document.createElement("div");
        item.className = "pdf-item";
        item.style.cssText = "display:flex;justify-content:space-between;align-items:center;padding:6px 4px;border-bottom:1px solid #333;cursor:pointer;";


        const name = document.createElement("span");
        name.textContent = filename;
        name.style.cssText = "font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;";
        name.title = filename;


        // Click to select PDF
        name.onclick = () => selectPDF(filename);


        const deleteBtn = document.createElement("span");
        deleteBtn.innerHTML = "🗑️";
        deleteBtn.style.cssText = "cursor:pointer;margin-left:8px;font-size:14px;";
        deleteBtn.title = "Delete PDF";
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deletePDF(filename);
        };


        item.appendChild(name);
        item.appendChild(deleteBtn);
        pdfList.appendChild(item);
    });
}


function selectPDF(filename) {
    uploadedFilePath = `uploads/${filename}`;
    alert(`✅ Now chatting with: ${filename}`);


    // Highlight selected
    document.querySelectorAll(".pdf-item span:first-child").forEach(el => {
        el.style.color = el.textContent === filename ? "#4f9eff" : "";
    });
}


async function deletePDF(filename) {
    if (!confirm(`Delete '${filename}'?`)) return;


    try {
        const response = await fetch(`/pdfs/${filename}`, { method: "DELETE" });
        const data = await response.json();


        if (uploadedFilePath === `uploads/${filename}`) {
            uploadedFilePath = null;
        }


        alert(data.message);
        loadPDFList();


    } catch (e) {
        alert("Delete failed");
    }
}




// ====================
// Upload PDF
// ====================


async function uploadPDF() {


    // Upload is allowed only in PDF mode
    if (MODE !== "pdf") {
        return;
    }


    const fileInput = document.getElementById("pdfFile");


    if (!fileInput) {
        return;
    }


    const file = fileInput.files[0];


    if (!file) {
        alert("Please select a PDF.");
        return;
    }


    const formData = new FormData();
    formData.append("file", file);


    try {


        const response = await fetch("/upload-pdf", {
            method: "POST",
            body: formData
        });


        const data = await response.json();


        uploadedFilePath = data.file_path;


        alert(data.message);


        loadPDFList();


    }
    catch (error) {


        console.error(error);


        alert("Upload Failed");


    }


}


// ====================
// Ask Question
// ====================


async function askQuestion() {
    const questionInput = document.getElementById("question");
    const question = questionInput.value.trim();


    if (!question) return;


    const chatBox = document.getElementById("chatBox");


    chatBox.innerHTML += `
        <div class="message user">
            <b>You:</b> ${question}
        </div>
    `;


    questionInput.value = "";


    const loadingId = "loading-" + Date.now();
    chatBox.innerHTML += `
        <div class="message bot" id="${loadingId}">
            <b>Assistant:</b> Thinking...
        </div>
    `;
    chatBox.scrollTop = chatBox.scrollHeight;


    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: question,
                file_path: uploadedFilePath || null
            })
        });


        if (!response.ok) throw new Error("Backend Error");


        const data = await response.json();


        document.getElementById(loadingId).remove();


        chatBox.innerHTML += `
            <div class="message bot">
                <b>Assistant:</b><br><br>
                ${data.final_answer}
            </div>
        `;


        chatBox.scrollTop = chatBox.scrollHeight;


        currentChat.push({ question, answer: data.final_answer });
        saveCurrentChat();


    } catch (error) {
        console.error(error);
        document.getElementById(loadingId)?.remove();
        chatBox.innerHTML += `
            <div class="message bot">
                <b>Error:</b> ${error.message}
            </div>
        `;
    }
}




// ====================
// Save Chat
// ====================


function saveCurrentChat() {
    if (currentChat.length === 0) return;


    const title = currentChat[0].question;
    const existingIndex = chats.findIndex(chat => chat.title === title);
    const chatData = { title, messages: [...currentChat] };


    if (existingIndex === -1) chats.push(chatData);
    else chats[existingIndex] = chatData;


    localStorage.setItem("chatHistory", JSON.stringify(chats));
    loadHistorySidebar();
}




// ====================
// New Chat
// ====================


function newChat() {
    currentChat = [];
    uploadedFilePath = null;
    document.getElementById("chatBox").innerHTML = "";
    document.getElementById("question").value = "";
    document.getElementById("pdfFile").value = "";
}




// ====================
// Sidebar History
// ====================


function loadHistorySidebar() {
    const historyList = document.getElementById("historyList");
    historyList.innerHTML = "";


    [...chats].reverse().forEach((chat, reverseIndex) => {
        const index = chats.length - 1 - reverseIndex;


        const item = document.createElement("div");
        item.className = "chat-history-item";
        item.onclick = () => openChat(index);


        const title = document.createElement("span");
        title.className = "chat-title";
        title.textContent = chat.title || "Untitled Chat";


        const deleteBtn = document.createElement("span");
        deleteBtn.className = "delete-chat";
        deleteBtn.innerHTML = "🗑️";
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            chats.splice(index, 1);
            localStorage.setItem("chatHistory", JSON.stringify(chats));
            loadHistorySidebar();
        };


        item.appendChild(title);
        item.appendChild(deleteBtn);
        historyList.appendChild(item);
    });
}




// ====================
// Open Chat
// ====================


function openChat(index) {
    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML = "";
    currentChat = chats[index].messages;


    currentChat.forEach(msg => {
        chatBox.innerHTML += `
            <div class="message user"><b>You:</b> ${msg.question}</div>
            <div class="message bot"><b>Assistant:</b><br><br>${msg.answer}</div>
        `;
    });


    chatBox.scrollTop = chatBox.scrollHeight;
}




// ====================
// On Page Load
// ====================


window.onload = function () {
    const savedChats = localStorage.getItem("chatHistory");
    if (savedChats) {
        chats = JSON.parse(savedChats);
        loadHistorySidebar();
    }


    loadPDFList();   // ✅ load uploaded PDFs on start
};




// ====================
// Enter Key
// ====================


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("question").addEventListener("keypress", function (event) {
        if (event.key === "Enter") askQuestion();
    });
});
