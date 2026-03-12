import { state } from './state.js';
import { $ } from './utils.js';
import { showError, showLoader, hideLoader, showToast, hideSplash, addSplashLog } from './ui.js';
import { PAGES, SPLASH_MIN_MS, REMEMBER_EMAIL_KEY, REMEMBER_ME_KEY } from './constants.js';

let chatRef = null;

export function init(chat) {
  chatRef = chat;
}

function renderChatList() { if (chatRef?.renderChatList) chatRef.renderChatList(); }
function loadChatContent(msgs) { if (chatRef?.loadChatContent) chatRef.loadChatContent(msgs); }

export function restoreRememberedLogin() {
  try {
    const remember = localStorage.getItem(REMEMBER_ME_KEY) === 'true';
    const email = localStorage.getItem(REMEMBER_EMAIL_KEY) || '';
    const emailEl = $('login-email');
    const rememberEl = $('login-remember');
    if (emailEl) emailEl.value = email;
    if (rememberEl) rememberEl.checked = remember;
  } catch (_) {}
}

export function saveRememberedLogin(email, remember) {
  try {
    if (remember && email) {
      localStorage.setItem(REMEMBER_ME_KEY, 'true');
      localStorage.setItem(REMEMBER_EMAIL_KEY, email);
    } else {
      localStorage.removeItem(REMEMBER_ME_KEY);
      localStorage.removeItem(REMEMBER_EMAIL_KEY);
    }
  } catch (_) {}
}

export async function runStartupGuard() {
  try {
    addSplashLog('Checking session...', 'log');
    const token = await window.omni.getAuthToken();
    if (!token) {
      addSplashLog('No session, redirecting to login', 'log');
      return { nextPage: PAGES.LOGIN };
    }
    addSplashLog('Validating access...', 'log');
    const access = await window.omni.validateAccess();
    if (!access.ok) {
      addSplashLog(access.error || 'Access denied', access.needLogin || access.needActivation ? 'log' : 'error');
      if (access.needLogin) return { nextPage: PAGES.LOGIN };
      if (access.needActivation) return { nextPage: PAGES.ACTIVATION };
      return { nextPage: PAGES.LOGIN };
    }
    addSplashLog('Checking Groq key (local or web)...', 'log');
    const key = await window.omni.getGroqKeyAsync();
    if (!key) {
      addSplashLog('No Groq key, redirecting to Config', 'log');
      return { nextPage: PAGES.CONFIG };
    }
    addSplashLog('Ready, opening chat', 'log');
    return { nextPage: PAGES.CHAT };
  } catch (e) {
    addSplashLog(e?.message || String(e), 'error');
    return { nextPage: PAGES.LOGIN };
  }
}

export async function runVerificationAndNavigate(navigate) {
  try {
    const { nextPage } = await runStartupGuard();
    if (nextPage === PAGES.LOGIN) {
      navigate(PAGES.LOGIN);
      return;
    }
    if (nextPage === PAGES.ACTIVATION) {
      navigate(PAGES.ACTIVATION);
      return;
    }
    if (nextPage === PAGES.CONFIG) {
      addSplashLog('Loading profile and chats for Config...', 'log');
      state.profile = (await window.omni.validateAccess()).profile;
      state.chats = await window.omni.loadChats();
      if (!state.chats) state.chats = [];
      state.currentChatIndex = state.chats.length === 0 ? -1 : 0;
      renderChatList();
      navigate(PAGES.CONFIG);
      const existing = await window.omni.getGroqKey();
      if ($('config-api-key')) $('config-api-key').value = existing || '';
      return;
    }
    addSplashLog('Loading profile and chats...', 'log');
    state.profile = (await window.omni.validateAccess()).profile;
    state.chats = await window.omni.loadChats();
    if (!state.chats) state.chats = [];
    state.currentChatIndex = state.chats.length === 0 ? -1 : 0;
    renderChatList();
    navigate(PAGES.CHAT);
    loadChatContent(state.currentChatIndex >= 0 ? state.chats[state.currentChatIndex].messages : []);
  } catch (e) {
    addSplashLog(e?.message || String(e), 'error');
    navigate(PAGES.LOGIN);
  }
}

export async function loadState(navigate) {
  addSplashLog('Starting...', 'log');
  const minDelayPromise = new Promise((r) => setTimeout(r, SPLASH_MIN_MS));
  const verifyPromise = runVerificationAndNavigate(navigate);
  await Promise.all([minDelayPromise, verifyPromise]);
  hideSplash();
}

export function setProfileLoading(loading) {
  if (loading) {
    const fn = $('profile-first-name');
    const ln = $('profile-last-name');
    const un = $('profile-username');
    const em = $('profile-email');
    const plan = $('profile-plan');
    const exp = $('profile-expiry');
    if (fn) fn.value = '';
    if (ln) ln.value = '';
    if (un) un.value = '';
    if (em) em.value = '';
    if (plan) plan.value = 'Loading...';
    if (exp) exp.value = '';
    if ($('profile-error')) $('profile-error').textContent = '';
    if ($('profile-neural-key-status')) $('profile-neural-key-status').textContent = '—';
    if ($('profile-groq-key-status')) $('profile-groq-key-status').textContent = '—';
  }
}

export async function doLogout(navigate) {
  await window.omni.logout();
  state.profile = null;
  state.chats = [];
  if ($('login-email')) $('login-email').value = '';
  if ($('login-password')) $('login-password').value = '';
  showToast('Sesión cerrada', 'info');
  navigate(PAGES.LOGIN);
  const sidebar = $('sidebar');
  if (sidebar?.classList.contains('expanded')) sidebar.classList.remove('expanded');
}

export function fillProfileEls(profile) {
  const fn = $('profile-first-name');
  const ln = $('profile-last-name');
  const un = $('profile-username');
  const em = $('profile-email');
  const plan = $('profile-plan');
  const exp = $('profile-expiry');
  const errEl = $('profile-error');
  const neuralStatus = $('profile-neural-key-status');
  if (profile) {
    if (fn) fn.value = profile.first_name || '';
    if (ln) ln.value = profile.last_name || '';
    if (un) un.value = profile.username || '';
    if (em) em.value = profile.email || '';
    if (plan) plan.value = (profile.plan || '').toUpperCase();
    if (exp) exp.value = profile.plan_expires_at ? profile.plan_expires_at.slice(0, 10) : 'N/A';
    if (errEl) errEl.textContent = '';
    if (neuralStatus) neuralStatus.textContent = profile.purchase_id ? '••••••••' : 'No configurada';
  } else {
    if (fn) fn.value = '';
    if (ln) ln.value = '';
    if (un) un.value = '';
    if (em) em.value = '';
    if (plan) plan.value = '';
    if (exp) exp.value = 'N/A';
    if (errEl) errEl.textContent = 'No se pudo cargar el perfil.';
    if (neuralStatus) neuralStatus.textContent = '—';
  }
}

export function setProfileGroqKeyStatus(hasKey) {
  const el = $('profile-groq-key-status');
  if (el) el.textContent = hasKey ? 'Configurada (local o en la nube)' : 'No configurada';
}

export function setProfileGroqKeyPlaceholder(hasKey) {
  const input = $('profile-groq-key');
  if (input) input.placeholder = hasKey ? '•••••••• (escribe nueva clave para cambiar)' : 'Nueva clave (dejar vacío para no cambiar)';
}

export function getProfileFormData() {
  return {
    first_name: ($('profile-first-name') && $('profile-first-name').value) ? $('profile-first-name').value.trim() : '',
    last_name: ($('profile-last-name') && $('profile-last-name').value) ? $('profile-last-name').value.trim() : '',
    username: ($('profile-username') && $('profile-username').value) ? $('profile-username').value.trim() : '',
  };
}
