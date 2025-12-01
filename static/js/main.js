const messages = document.getElementById('messages');
const input = document.getElementById('user-input');

// Welcome message
addMessage("Hello! I'm Adib.AI — your personal assistant. Ask me anything");

function addMessage(text, role = 'assistant') {
  const div = document.createElement('div');
  div.className = `message ${role === 'user' ? 'user' : ''}`;
  div.innerHTML = `<div class="avatar">${role==='user'?'You':'AI'}</div><div class="content">${text.replace(/\n/g,'<br>')}</div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, 'user');
  input.value = '';

  const typing = document.createElement('div');
  typing.className = 'message';
  typing.innerHTML = `<div class="avatar">AI</div><div class="content">thinking...</div>`;
  messages.appendChild(typing);
  messages.scrollTop = messages.scrollHeight;

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    typing.remove();
    addMessage(data.reply || "No response");
  } catch {
    typing.remove();
    addMessage("Check internet");
  }
}

function clearChat() {
  messages.innerHTML = '';
  addMessage("New chat started — how can I help you?");
}

// Enter key to send
input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Feedback form
document.getElementById('feedback-form').onsubmit = async e => {
  e.preventDefault();
  const status = document.getElementById('fb-status');
  status.textContent = 'Sending...';

  const name = document.getElementById('fb-name').value || 'Anonymous';
  const email = document.getElementById('fb-email').value;
  const message = document.getElementById('fb-message').value;

  try {
    const res = await fetch('/feedback', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name, email, message})
    });
    const data = await res.json();
    status.textContent = data.success ? 'Thank you!' : 'Failed to send';
    if (data.success) e.target.reset();
  } catch {
    status.textContent = 'Error sending feedback';
  }
};
