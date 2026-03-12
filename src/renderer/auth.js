import { state } from './state.js';
import { $ } from './utils.js';
import { showError, showLoader, hideLoader, showToast, hideSplash } from './ui.js';
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
  const token = await window.omni.getAuthToken();
  if (!token) return { nextPage: PAGES.LOGIN };
  const access = await window.omni.validateAccess();
  if (!access.ok) {
    if (access.needLogin) return { nextPage: PAGES.LOGIN };
    if (access.needActivation) return { nextPage: PAGES.ACTIVATION };
    return { nextPage: PAGES.LOGIN };
  }
  const key = await window.omni.getGroqKey();
  if (!key) return { nextPage: PAGES.CONFIG };
  return { nextPage: PAGES.CHAT };
}

export async function runVerificationAndNavigate(navigate) {
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
  state.profile = (await window.omni.validateAccess()).profile;
  state.chats = await window.omni.loadChats();
  if (!state.chats) state.chats = [];
  state.currentChatIndex = state.chats.length === 0 ? -1 : 0;
  renderChatList();
  navigate(PAGES.CHAT);
  loadChatContent(state.currentChatIndex >= 0 ? state.chats[state.currentChatIndex].messages : []);
}

export async function loadState(navigate) {
  const minDelayPromise = new Promise((r) => setTimeout(r, SPLASH_MIN_MS));
  const verifyPromise = runVerificationAndNavigate(navigate);
  await Promise.all([minDelayPromise, verifyPromise]);
  hideSplash();
}

export function setProfileLoading(loading) {
  if (loading) {
    $('profile-name').textContent = 'Name: Loading...';
    $('profile-email').textContent = 'Email: Loading...';
    $('profile-plan').textContent = 'Plan: Loading...';
    $('profile-expiry').textContent = 'Expires: Loading...';
    $('profile-error').textContent = '';
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
  if (profile) {
    $('profile-name').textContent = `Name: ${profile.first_name || ''} ${profile.last_name || ''}`;
    $('profile-email').textContent = `Email: ${profile.email || ''}`;
    $('profile-plan').textContent = `Plan: ${(profile.plan || '').toUpperCase()}`;
    $('profile-expiry').textContent = `Expires: ${profile.plan_expires_at ? profile.plan_expires_at.slice(0, 10) : 'N/A'}`;
    $('profile-error').textContent = '';
  } else {
    $('profile-name').textContent = 'Name: —';
    $('profile-email').textContent = 'Email: —';
    $('profile-plan').textContent = 'Plan: —';
    $('profile-expiry').textContent = 'Expires: N/A';
    $('profile-error').textContent = 'No se pudo cargar el perfil.';
  }
}
