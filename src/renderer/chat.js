import { state } from './state.js';
import { $, escapeHtml, simpleMarkdown } from './utils.js';
import { showToast } from './ui.js';
import { PAGES } from './constants.js';

let navigateRef = null;
let streamingBuffer = '';
let streamingRenderScheduled = null;
let expectingCompleteCodeResponse = false;

const COMPLETAR_INSTRUCTION = [
  'Completa el siguiente código. Devuelve el código completo.',
  'Envuelve cada parte que AÑADAS (que no esté en el código del usuario) exactamente así: {{ADDED}}...{{/ADDED}}.',
  'Empieza tu respuesta con: **Código completado mejorado**\n\n'
].join(' ');

function applyCompletedCodeHighlight(html) {
  return html.replace(/\{\{ADDED\}\}([\s\S]*?)\{\{\/ADDED\}\}/g, '<span class="code-completed-highlight">$1</span>');
}

export function init(navigate) {
  navigateRef = navigate;
}

function navigate(index) {
  if (navigateRef) navigateRef(index);
}

export function injectCopyButtons(container) {
  if (!container) return;
  const pres = container.querySelectorAll('pre');
  Array.from(pres).forEach((pre) => {
    if (pre.closest('.code-block-wrapper')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'code-block-wrapper';
    pre.parentNode.insertBefore(wrapper, pre);
    const header = document.createElement('div');
    header.className = 'code-block-header';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'copy-code-btn';
    btn.title = 'Copiar código';
    btn.setAttribute('aria-label', 'Copiar código');
    btn.innerHTML = '<svg class="icon" aria-hidden="true"><use href="#icon-clipboard"/></svg><span>Copiar</span>';
    header.appendChild(btn);
    wrapper.appendChild(header);
    wrapper.appendChild(pre);
    btn.addEventListener('click', () => {
      const codeEl = pre.querySelector('code');
      const text = (codeEl || pre).textContent;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Código copiado', 'success');
        btn.classList.add('copied');
        const span = btn.querySelector('span');
        if (span) span.textContent = 'Copiado';
        setTimeout(() => {
          btn.classList.remove('copied');
          if (span) span.textContent = 'Copiar';
        }, 2000);
      }).catch(() => showToast('Error al copiar', 'error'));
    });
  });
}

export function renderChatList() {
  const list = $('chat-list');
  if (!list) return;
  list.innerHTML = state.chats.map((c, i) => `
    <li class="${i === state.currentChatIndex && state.currentChatIndex >= 0 ? 'selected' : ''}" data-index="${i}">
      <span class="title">${escapeHtml(c.title)}</span>
      <span class="actions">
        <button type="button" class="edit" data-index="${i}" title="Editar nombre"><svg class="icon" aria-hidden="true"><use href="#icon-pencil"/></svg></button>
        <button type="button" class="del" data-index="${i}" title="Eliminar"><svg class="icon" aria-hidden="true"><use href="#icon-trash"/></svg></button>
      </span>
    </li>
  `).join('');
  list.querySelectorAll('li').forEach((li) => {
    li.addEventListener('click', (e) => {
      if (e.target.closest('.actions')) return;
      switchChat(parseInt(li.dataset.index, 10));
    });
  });
  list.querySelectorAll('.edit').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const idx = parseInt(btn.dataset.index, 10);
      const newTitle = prompt('Rename session', state.chats[idx].title);
      if (newTitle?.trim()) {
        state.chats[idx].title = newTitle.trim();
        window.omni.saveChats(state.chats);
        renderChatList();
        showToast('Nombre actualizado', 'success');
      }
    });
  });
  list.querySelectorAll('.del').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      showDeleteConfirm(parseInt(btn.dataset.index, 10));
    });
  });
}

export function showDeleteConfirm(chatIndex) {
  const overlay = $('modal-delete-overlay');
  if (!overlay) return;
  overlay.dataset.pendingIndex = String(chatIndex);
  overlay.classList.add('show');
}

export function hideDeleteConfirm() {
  const overlay = $('modal-delete-overlay');
  if (overlay) {
    overlay.classList.remove('show');
    delete overlay.dataset.pendingIndex;
  }
}

export function showLogoutConfirm() {
  const overlay = $('modal-logout-overlay');
  if (overlay) overlay.classList.add('show');
}

export function hideLogoutConfirm() {
  const overlay = $('modal-logout-overlay');
  if (overlay) overlay.classList.remove('show');
}

export function confirmDeleteChat() {
  const overlay = $('modal-delete-overlay');
  const idx = overlay ? parseInt(overlay.dataset.pendingIndex, 10) : -1;
  hideDeleteConfirm();
  if (idx < 0 || idx >= state.chats.length) return;
  if (state.chats.length <= 1) {
    state.chats = [];
    state.currentChatIndex = -1;
    loadChatContent([]);
  } else {
    state.chats.splice(idx, 1);
    state.currentChatIndex = Math.min(state.currentChatIndex, state.chats.length - 1);
    switchChat(state.currentChatIndex);
  }
  window.omni.saveChats(state.chats);
  renderChatList();
  showToast(state.chats.length <= 1 ? 'Chat borrado' : 'Conversación eliminada', 'info');
}

export function switchChat(index) {
  if (index < 0 || index >= state.chats.length) return;
  state.currentChatIndex = index;
  loadChatContent(state.chats[index].messages);
  renderChatList();
}

export function loadChatContent(messages) {
  const display = $('chat-display');
  if (!display) return;
  display.innerHTML = (messages || []).map((msg) => {
    if (msg.role === 'user') {
      return `<div class="user-msg"><div class="bubble">${escapeHtml(msg.content)}</div></div>`;
    }
    const html = typeof marked !== 'undefined' && marked.parse ? marked.parse(msg.content) : simpleMarkdown(msg.content);
    return `<div class="ai-msg"><div class="label"><span>●</span><span>OMNI_CORE</span></div><div class="bubble">${html}</div></div>`;
  }).join('');
  injectCopyButtons(display);
  display.scrollTop = display.scrollHeight;
}

export function appendUserMessage(text) {
  const display = $('chat-display');
  if (!display) return;
  const div = document.createElement('div');
  div.className = 'user-msg';
  div.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
  display.appendChild(div);
  /* Enfocar el mensaje que acabas de enviar: que quede visible al final del viewport */
  div.scrollIntoView({ block: 'end', behavior: 'smooth' });
}

function renderStreamingContent() {
  const display = $('chat-display');
  if (!display) return;
  const last = display.querySelector('.ai-msg.streaming');
  const bubble = last?.querySelector('.bubble');
  if (!bubble || streamingBuffer === '') return;
  let html = typeof marked !== 'undefined' && marked.parse ? marked.parse(streamingBuffer) : simpleMarkdown(streamingBuffer);
  if (expectingCompleteCodeResponse) html = applyCompletedCodeHighlight(html);
  bubble.innerHTML = html;
  injectCopyButtons(bubble);
  streamingRenderScheduled = null;
}

export function appendAiChunk(chunk) {
  const display = $('chat-display');
  if (!display) return;
  let last = display.querySelector('.ai-msg.streaming');
  if (!last) {
    streamingBuffer = '';
    const wrap = document.createElement('div');
    wrap.className = 'ai-msg streaming';
    wrap.innerHTML = '<div class="label"><span>●</span><span>OMNI_CORE</span></div><div class="bubble"></div>';
    display.appendChild(wrap);
    last = wrap;
    /* Ajustar vista: tu mensaje y solo el inicio de la respuesta de la IA */
    const lastUserMsg = display.querySelector('.user-msg:last-of-type');
    if (lastUserMsg) {
      lastUserMsg.scrollIntoView({ block: 'end', behavior: 'smooth' });
    }
  }
  streamingBuffer += chunk;
  const bubble = last.querySelector('.bubble');
  if (!bubble) return;
  /* Throttle: re-render con decoración como máximo cada ~60ms */
  if (!streamingRenderScheduled) {
    streamingRenderScheduled = requestAnimationFrame(() => {
      renderStreamingContent();
    });
  }
}

function flushStreamingRender() {
  if (streamingRenderScheduled) {
    cancelAnimationFrame(streamingRenderScheduled);
    streamingRenderScheduled = null;
  }
  renderStreamingContent();
}

export function finalizeAiMessage(fullText) {
  const display = $('chat-display');
  if (!display) return;
  streamingBuffer = fullText;
  flushStreamingRender();
  expectingCompleteCodeResponse = false;
  const last = display.querySelector('.ai-msg.streaming');
  if (last) {
    last.classList.remove('streaming');
  }
  streamingBuffer = '';
  streamingRenderScheduled = null;
  /* No scroll al terminar: que se quede mirando el mensaje donde está */
}

export function ensureCurrentChat(title) {
  if (state.currentChatIndex === -1 || state.currentChatIndex >= state.chats.length) {
    const newId = state.chats.length ? Math.max(...state.chats.map((c) => c.id)) + 1 : 0;
    state.chats.push({ id: newId, title: title || 'New Session', messages: [] });
    state.currentChatIndex = state.chats.length - 1;
    renderChatList();
  }
  return state.chats[state.currentChatIndex];
}

export async function sendMessage(prompt, imageB64) {
  if (state.currentChatIndex === -1 || state.currentChatIndex >= state.chats.length) {
    const newId = state.chats.length ? Math.max(...state.chats.map((c) => c.id)) + 1 : 0;
    const title = prompt.slice(0, 20) + (prompt.length > 20 ? '...' : '');
    state.chats.push({ id: newId, title, messages: [] });
    state.currentChatIndex = state.chats.length - 1;
    renderChatList();
  }
  const chat = state.chats[state.currentChatIndex];
  if (!chat.messages) chat.messages = [];
  if (chat.messages.length === 0) {
    chat.title = prompt.slice(0, 20) + (prompt.length > 20 ? '...' : '');
    renderChatList();
  }
  let promptToSend = prompt;
  if (prompt.trim().toLowerCase().startsWith('/completar')) {
    const code = prompt.replace(/^\/completar\s*/i, '').trim();
    if (code) {
      promptToSend = COMPLETAR_INSTRUCTION + '\n\n' + code;
      expectingCompleteCodeResponse = true;
    }
  }

  chat.messages.push({ role: 'user', content: prompt });
  appendUserMessage(prompt);
  await window.omni.saveChats(state.chats);

  state.streaming = true;
  const history = chat.messages.slice(0, -1).map((m) => ({ role: m.role, content: m.content }));
  const result = await window.omni.streamChat({ prompt: promptToSend, history, imageB64: imageB64 || null });
  state.streaming = false;

  if (!result.ok) {
    expectingCompleteCodeResponse = false;
    appendAiChunk('');
    const errEl = document.querySelector('.ai-msg.streaming .bubble');
    if (errEl) errEl.innerHTML = `<span style="color:#ef4444">${escapeHtml(result.error)}</span>`;
    const last = document.querySelector('.ai-msg.streaming');
    if (last) last.classList.remove('streaming');
  }
}

export function setupClearChatListener() {
  window.omni.onClearChatRequest(() => {
    if (state.currentChatIndex >= 0 && state.chats[state.currentChatIndex]) {
      state.chats[state.currentChatIndex].messages = [];
      state.chats[state.currentChatIndex].title = 'New Session';
      loadChatContent([]);
      window.omni.saveChats(state.chats);
      renderChatList();
      showToast('Chat borrado', 'info');
    }
  });
}

export function setupAiListeners() {
  window.omni.onAiChunk((chunk) => appendAiChunk(chunk));
  window.omni.onAiDone((full) => {
    const chat = state.chats[state.currentChatIndex];
    if (chat?.messages?.length) {
      const last = chat.messages[chat.messages.length - 1];
      if (last?.role === 'model') last.content = full;
      else chat.messages.push({ role: 'model', content: full });
    }
    finalizeAiMessage(full);
    window.omni.saveChats(state.chats);
  });
  window.omni.onAiError((err) => {
    finalizeAiMessage('');
    const display = $('chat-display');
    if (display) {
      const last = display.querySelector('.ai-msg.streaming');
      if (last) {
        last.classList.remove('streaming');
        const bubble = last.querySelector('.bubble');
        if (bubble) bubble.innerHTML = `<span style="color:#ef4444">${escapeHtml(err)}</span>`;
      }
    }
    state.streaming = false;
    showToast('Error en la respuesta', 'error');
  });
}
