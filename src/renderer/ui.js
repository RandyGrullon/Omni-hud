import { $ } from './utils.js';

export function showError(elId, msg) {
  const el = $(elId);
  if (el) {
    el.textContent = msg || '';
    el.style.display = msg ? 'block' : 'none';
  }
}

export function showLoader(text) {
  const overlay = $('global-loader');
  const textEl = $('loader-text');
  if (overlay) {
    if (textEl) textEl.textContent = text || 'Calculando...';
    overlay.classList.add('show');
  }
}

export function hideLoader() {
  const overlay = $('global-loader');
  if (overlay) overlay.classList.remove('show');
}

export function showToast(message, type = 'info') {
  const container = $('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'status');
  toast.textContent = message;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  const duration = 3200;
  const remove = () => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 280);
  };
  const t = setTimeout(remove, duration);
  toast.addEventListener('click', () => {
    clearTimeout(t);
    remove();
  });
}

export function hideSplash() {
  const splash = $('splash');
  const appEl = $('app');
  if (splash) splash.classList.add('splash-hidden');
  if (appEl) {
    appEl.classList.add('app-ready');
    appEl.classList.remove('app-hidden');
  }
}
