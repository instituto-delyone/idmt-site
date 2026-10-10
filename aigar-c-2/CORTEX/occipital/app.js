const $ = s=>document.querySelector(s);
const messages = $("#messages");
const input = $("#promptInput");
const sendBtn = $("#sendBtn");
const moduleSelect = $("#moduleSelect");
const statusEl = $("#status");
const cardsList = $("#cardsList");

function addMsg(text, role="assistant"){
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

async function loadModules(){
  const r = await fetch("/api/modules");
  const data = await r.json();
  moduleSelect.innerHTML = "";
  (data.modules || []).forEach(name=>{
    const opt = document.createElement("option");
    opt.value = name; opt.textContent = name;
    moduleSelect.appendChild(opt);
  });
}

async function loadCards(){
  const r = await fetch("/api/memory-cards");
  const data = await r.json();
  cardsList.innerHTML = "";
  (data.files || []).forEach(f=>{
    const li = document.createElement("li");
    li.textContent = f;
    cardsList.appendChild(li);
  });
}

async function init(){
  try{
    const r = await fetch("/health");
    statusEl.textContent = r.ok ? "Pronto" : "Offline";
  }catch(e){ statusEl.textContent = "Offline"; }
  await loadModules();
  await loadCards();
  addMsg("AIGAR UI — Chat pronta. Selecione o módulo e envie sua mensagem.", "system");
}

async function send(){
  const text = input.value.trim();
  if(!text) return;
  addMsg(text, "user");
  input.value = ""; sendBtn.disabled = true;
  try{
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({message:text, module: moduleSelect.value})
    });
    const data = await r.json();
    addMsg(data.reply || "(sem resposta)", "assistant");
  }catch(e){
    addMsg("Erro: "+e.message, "assistant");
  }finally{
    sendBtn.disabled = false; input.focus();
  }
}

sendBtn.addEventListener("click", send);
input.addEventListener("keydown", e=>{ if(e.key==="Enter") send(); });
init();
