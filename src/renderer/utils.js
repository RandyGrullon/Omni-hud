export const $ = (id) => document.getElementById(id);

export function escapeHtml(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

export function simpleMarkdown(text) {
  const s = String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  return s
    .replace(/```([\s\S]*?)```/g, (_, c) => '<pre><code>' + c + '</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

export function setupPasswordToggle(inputId, buttonId) {
  const input = $(inputId);
  const btn = $(buttonId);
  if (!input || !btn) return;
  const icon = btn.querySelector('.icon use');
  if (!icon) return;
  btn.addEventListener('click', () => {
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
    icon.setAttribute('href', isPassword ? '#icon-eye-off' : '#icon-eye');
    btn.title = isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña';
    btn.setAttribute('aria-label', btn.title);
  });
}
