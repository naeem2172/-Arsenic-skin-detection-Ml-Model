/**
 * Arsenic Awareness Chatbot - Embeddable Widget
 * Usage: Include this script and add <div id="arsenic-chatbot"></div>
 */
(function() {
  const API_URL = window.ARSENIC_CHATBOT_API || '/chatbot/api/chat';
  const CONTAINER_ID = 'arsenic-chatbot';

  function createWidget() {
    const container = document.getElementById(CONTAINER_ID);
    if (!container) return;

    container.innerHTML = `
      <div class="arsenic-chatbot-widget">
        <div class="arsenic-chatbot-header">Arsenic Awareness Assistant</div>
        <div class="arsenic-chatbot-messages"></div>
        <div class="arsenic-chatbot-input">
          <input type="text" placeholder="Ask in English or Bangla..." />
          <button>Send</button>
        </div>
      </div>
    `;

    const messagesEl = container.querySelector('.arsenic-chatbot-messages');
    const inputEl = container.querySelector('input');
    const btnEl = container.querySelector('button');

    function addMessage(role, content) {
      const div = document.createElement('div');
      div.className = `arsenic-msg arsenic-msg-${role}`;
      div.textContent = content;
      messagesEl.appendChild(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    async function send() {
      const msg = inputEl.value.trim();
      if (!msg) return;
      inputEl.value = '';
      addMessage('user', msg);
      btnEl.disabled = true;

      try {
        const res = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg, session_id: 'widget' })
        });
        const data = await res.json();
        addMessage('assistant', data.response);
      } catch (e) {
        addMessage('assistant', 'Error: ' + e.message);
      }
      btnEl.disabled = false;
    }

    btnEl.onclick = send;
    inputEl.onkeypress = (e) => { if (e.key === 'Enter') send(); };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createWidget);
  } else {
    createWidget();
  }
})();
