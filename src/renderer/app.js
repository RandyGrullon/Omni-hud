import { PAGES } from './constants.js';
import { state } from './state.js';
import { $, setupPasswordToggle } from './utils.js';
import { showError, showLoader, hideLoader, showToast, initSplashLogs } from './ui.js';
import * as chat from './chat.js';
import * as auth from './auth.js';
import * as fileExplorer from './fileExplorer.js';
import { setupToolsMenu, setupVoice } from './tools.js';

const pages = document.querySelectorAll('.page');
const contentArea = document.querySelector('.content-area');
const fileSearchEl = $('file-search');

function baseNavigate(index) {
  pages.forEach((p) => {
    const isActive = parseInt(p.dataset.page, 10) === index;
    p.classList.toggle('active', isActive);
  });
  document.body.classList.toggle('login-page', index === PAGES.LOGIN);
  if (index === PAGES.LOGIN) auth.restoreRememberedLogin();
}

function navigate(index) {
  baseNavigate(index);
  if (index === PAGES.FILE) {
    if (fileSearchEl) fileSearchEl.value = '';
    fileExplorer.fileExplorerState.searchQuery = '';
    setTimeout(fileExplorer.onNavigateToFilePage, 0);
  }
}

const chatApi = {
  renderChatList: chat.renderChatList,
  loadChatContent: chat.loadChatContent
};

initSplashLogs();
chat.init(navigate);
auth.init(chatApi);
fileExplorer.init(navigate);

setupPasswordToggle('login-password', 'btn-toggle-login-password');
setupPasswordToggle('config-api-key', 'btn-toggle-config-password');
setupPasswordToggle('profile-groq-key', 'btn-toggle-profile-groq');

async function doLogin() {
  const email = $('login-email').value.trim();
  const password = $('login-password').value.trim();
  showError('login-error', '');
  if (!email || !password) {
    showError('login-error', 'ERROR: MISSING CREDENTIALS');
    return;
  }
  const btn = $('btn-login');
  btn.textContent = 'AUTHENTICATING...';
  btn.disabled = true;
  showLoader('Iniciando sesión...');
  let result;
  try {
    result = await window.omni.login(email, password);
  } finally {
    hideLoader();
  }
  btn.textContent = 'SIGN IN';
  btn.disabled = false;
  if (!result.ok) {
    showError('login-error', result.error || 'Login failed');
    return;
  }
  const remember = $('login-remember')?.checked;
  auth.saveRememberedLogin(email, remember);
  state.profile = result.profile;
  showToast('Sesión iniciada', 'success');
  if (result.profile.plan === 'architect' || result.profile.purchase_id) {
    const key = await window.omni.getGroqKeyAsync();
    navigate(key ? PAGES.CHAT : PAGES.CONFIG);
  } else {
    navigate(PAGES.ACTIVATION);
  }
  state.chats = await window.omni.loadChats();
  if (!state.chats) state.chats = [];
  state.currentChatIndex = state.chats.length === 0 ? -1 : 0;
  chat.renderChatList();
  chat.loadChatContent(state.currentChatIndex >= 0 ? state.chats[state.currentChatIndex].messages : []);
}

$('login-form').addEventListener('submit', (e) => {
  e.preventDefault();
  doLogin();
});

$('btn-activate').addEventListener('click', async () => {
  const key = $('activation-key').value.trim();
  showError('activation-error', '');
  if (!key) {
    showError('activation-error', 'Enter key');
    return;
  }
  const btn = $('btn-activate');
  btn.textContent = 'VALIDATING KEY...';
  btn.disabled = true;
  showLoader('Validando clave...');
  let result;
  try {
    result = await window.omni.activateKey(key);
  } finally {
    hideLoader();
  }
  btn.textContent = 'ACTIVATE OMNI';
  btn.disabled = false;
  if (!result.ok) showError('activation-error', result.error || 'Activation failed');
  else {
    showToast('Clave activada', 'success');
    navigate(PAGES.CONFIG);
  }
});

$('btn-save-config').addEventListener('click', async () => {
  const apiKey = $('config-api-key').value.trim();
  if (!apiKey) return;
  await window.omni.setGroqKey(apiKey);
  const syncResult = await window.omni.syncGroqKeyToWeb(apiKey);
  if (syncResult && syncResult.ok) {
    showToast('Configuración guardada y sincronizada con la web', 'success');
  } else {
    showToast('Configuración guardada localmente; no se pudo sincronizar con la web', 'success');
  }
  navigate(PAGES.CHAT);
  chat.loadChatContent(state.currentChatIndex >= 0 && state.chats[state.currentChatIndex] ? state.chats[state.currentChatIndex].messages : []);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    $('modal-overlay')?.classList.remove('show');
    $('tools-menu')?.classList.remove('show');
  }
});

$('btn-hamburger').addEventListener('click', () => {
  $('sidebar').classList.toggle('expanded');
});

$('btn-info').addEventListener('click', () => $('modal-overlay').classList.add('show'));
$('btn-modal-close').addEventListener('click', () => $('modal-overlay').classList.remove('show'));
$('modal-overlay').addEventListener('click', (e) => {
  if (e.target === $('modal-overlay')) $('modal-overlay').classList.remove('show');
});

$('btn-delete-cancel').addEventListener('click', chat.hideDeleteConfirm);
$('btn-delete-confirm').addEventListener('click', chat.confirmDeleteChat);
$('modal-delete-overlay').addEventListener('click', (e) => {
  if (e.target === $('modal-delete-overlay')) chat.hideDeleteConfirm();
});

$('btn-close').addEventListener('click', () => window.omni.close());

$('btn-profile').addEventListener('click', async () => {
  auth.setProfileLoading(true);
  navigate(PAGES.PROFILE);
  try {
    let profile = state.profile;
    if (!profile) {
      const res = await window.omni.getProfile();
      if (res.ok) profile = res.profile;
    }
    auth.fillProfileEls(profile);
    const groqKey = await window.omni.getGroqKeyAsync();
    auth.setProfileGroqKeyStatus(!!groqKey);
    auth.setProfileGroqKeyPlaceholder(!!groqKey);
    if (!profile) $('profile-error').textContent = 'No se pudo cargar el perfil.';
  } catch (_) {
    auth.fillProfileEls(null);
    $('profile-error').textContent = 'No se pudo cargar el perfil.';
    showToast('No se pudo cargar el perfil', 'error');
  } finally {
    auth.setProfileLoading(false);
  }
});

$('profile-back').addEventListener('click', (e) => {
  e.preventDefault();
  e.stopPropagation();
  navigate(PAGES.CHAT);
});

$('btn-profile-save').addEventListener('click', () => {
  const data = auth.getProfileFormData();
  if (!data.first_name || !data.last_name) {
    showToast('Nombre y apellido son obligatorios', 'error');
    return;
  }
  $('modal-profile-save-overlay').classList.add('show');
});

$('btn-profile-save-cancel').addEventListener('click', () => {
  $('modal-profile-save-overlay').classList.remove('show');
});

$('modal-profile-save-overlay').addEventListener('click', (e) => {
  if (e.target === $('modal-profile-save-overlay')) e.target.classList.remove('show');
});

$('btn-profile-save-confirm').addEventListener('click', async () => {
  $('modal-profile-save-overlay').classList.remove('show');
  const data = auth.getProfileFormData();
  try {
    const result = await window.omni.updateProfile(data);
    if (result.ok) {
      state.profile = state.profile ? { ...state.profile, ...data } : data;
      if (result.profile) state.profile = result.profile;
      auth.fillProfileEls(state.profile);
      showToast('Perfil guardado', 'success');
    } else {
      showToast(result.error || 'Error al guardar', 'error');
    }
  } catch (_) {
    showToast('Error al guardar perfil', 'error');
  }
});

$('btn-profile-neural-key').addEventListener('click', () => {
  navigate(PAGES.ACTIVATION);
});

$('btn-profile-save-groq').addEventListener('click', async () => {
  const input = $('profile-groq-key');
  const key = input && input.value ? input.value.trim() : '';
  if (!key) {
    showToast('Introduce una clave de Groq', 'error');
    return;
  }
  try {
    await window.omni.setGroqKey(key);
    const sync = await window.omni.syncGroqKeyToWeb(key);
    if (sync.ok) {
      if (input) input.value = '';
      auth.setProfileGroqKeyStatus(true);
      auth.setProfileGroqKeyPlaceholder(true);
      showToast('Clave Groq guardada', 'success');
    } else {
      const err = sync.error || 'Error al sincronizar';
      const msg = err.toLowerCase().includes('session') || err.toLowerCase().includes('sesión') || err.toLowerCase().includes('session or key')
        ? 'Sesión incompleta. Cierra sesión e inicia de nuevo para guardar la clave en la nube.'
        : err;
      showToast(msg, 'error');
    }
  } catch (_) {
    showToast('Error al guardar clave Groq', 'error');
  }
});

$('btn-profile-logout').addEventListener('click', () => chat.showLogoutConfirm());
$('btn-logout').addEventListener('click', () => chat.showLogoutConfirm());

$('btn-logout-cancel').addEventListener('click', chat.hideLogoutConfirm);
$('btn-logout-confirm').addEventListener('click', () => {
  chat.hideLogoutConfirm();
  auth.doLogout(navigate);
});
$('modal-logout-overlay').addEventListener('click', (e) => {
  if (e.target === $('modal-logout-overlay')) chat.hideLogoutConfirm();
});

const chatInput = $('chat-input');
function resizeChatInput() {
  if (!chatInput) return;
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 240) + 'px';
}
chatInput?.addEventListener('input', resizeChatInput);
chatInput?.addEventListener('paste', () => setTimeout(resizeChatInput, 0));

chatInput?.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter') return;
  if (e.shiftKey) return; /* Shift+Enter: nueva línea, el textarea crece */
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text || state.streaming) return;
  chatInput.value = '';
  resizeChatInput();
  chat.sendMessage(text);
});

$('btn-new-session').addEventListener('click', () => {
  state.currentChatIndex = -1;
  chat.loadChatContent([]);
  chat.renderChatList();
  navigate(PAGES.CHAT);
  const sidebar = $('sidebar');
  if (sidebar?.classList.contains('expanded')) sidebar.classList.remove('expanded');
});

$('file-back').addEventListener('click', () => navigate(PAGES.CHAT));
$('btn-attach').addEventListener('click', () => navigate(PAGES.FILE));

if (fileSearchEl) {
  fileSearchEl.addEventListener('input', () => {
    fileExplorer.fileExplorerState.searchQuery = fileSearchEl.value;
    fileExplorer.renderFileList(fileExplorer.fileExplorerState.currentEntries);
  });
}

$('file-explorer-back').addEventListener('click', () => {
  if (fileExplorer.fileExplorerState.stack.length === 0) return;
  const parentPath = fileExplorer.fileExplorerState.stack.pop();
  fileExplorer.loadFileTree(parentPath);
});

$('btn-open-file').addEventListener('click', () => {
  const filePath = fileExplorer.fileExplorerState.selectedFilePath;
  if (!filePath) return;
  fileExplorer.analyzeFile(filePath);
});

setupToolsMenu(contentArea);
setupVoice(contentArea);
chat.setupClearChatListener();

$('btn-check-updates').addEventListener('click', async () => {
  const result = await window.omni.checkUpdates();
  if (!result.ok) {
    showToast('Error de conexión al buscar actualizaciones', 'error');
    return;
  }
  showToast(result.update ? `v${result.version} disponible` : 'Versión actual al día', result.update ? 'success' : 'info');
});

chat.setupAiListeners();
auth.loadState(navigate);
