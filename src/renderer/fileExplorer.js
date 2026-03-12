import { state } from './state.js';
import { $, escapeHtml } from './utils.js';
import { showToast } from './ui.js';
import { ensureCurrentChat, appendUserMessage, persistChats } from './chat.js';
import { PAGES } from './constants.js';

let navigateRef = null;

export function init(navigate) {
  navigateRef = navigate;
}

const ext = (name) => (name || '').split('.').pop().toLowerCase();
const analyzable = (e) => !e.isDirectory && ['docx', 'pdf', 'xlsx', 'xls'].includes(ext(e.name));

export const fileExplorerState = {
  currentPath: null,
  stack: [],
  currentEntries: [],
  searchQuery: '',
  selectedFilePath: null
};

export function updateFileExplorerUI() {
  const backBtn = $('file-explorer-back');
  const openBtn = $('btn-open-file');
  if (backBtn) backBtn.style.display = fileExplorerState.stack.length > 0 ? '' : 'none';
  if (openBtn) openBtn.style.display = fileExplorerState.selectedFilePath ? '' : 'none';
}

export function renderFileList(entries) {
  const treeEl = $('file-tree');
  if (!treeEl) return;
  const q = (fileExplorerState.searchQuery || '').trim().toLowerCase();
  const filtered = q ? entries.filter((e) => (e.name || '').toLowerCase().includes(q)) : entries;
  treeEl.innerHTML = '';
  filtered.forEach((e) => {
    const row = document.createElement('div');
    row.className = 'file-tree-row' + (e.isDirectory ? ' is-dir' : ' is-file');
    if (e.path === fileExplorerState.selectedFilePath) row.classList.add('selected');
    row.dataset.path = e.path;
    row.dataset.isDirectory = e.isDirectory ? '1' : '0';
    const icon = e.isDirectory ? '📁' : '📄';
    const nameSpan = document.createElement('span');
    nameSpan.className = 'file-tree-name';
    nameSpan.textContent = e.name || '(unnamed)';
    row.appendChild(nameSpan);
    if (e.isDirectory) {
      row.prepend(document.createTextNode(icon + ' '));
      row.addEventListener('click', () => {
        fileExplorerState.stack.push(fileExplorerState.currentPath);
        fileExplorerState.selectedFilePath = null;
        loadFileTree(e.path);
      });
    } else {
      row.prepend(document.createTextNode(icon + ' '));
      row.addEventListener('click', () => {
        fileExplorerState.selectedFilePath = analyzable(e) ? e.path : null;
        treeEl.querySelectorAll('.file-tree-row').forEach((r) => r.classList.remove('selected'));
        if (fileExplorerState.selectedFilePath) row.classList.add('selected');
        updateFileExplorerUI();
      });
      if (analyzable(e)) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'file-tree-analyze';
        btn.textContent = 'Analizar';
        btn.addEventListener('click', (ev) => {
          ev.stopPropagation();
          analyzeFile(e.path, navigateRef);
        });
        row.appendChild(btn);
      }
    }
    treeEl.appendChild(row);
  });
  updateFileExplorerUI();
}

export async function loadFileTree(dirPath) {
  const treeEl = $('file-tree');
  const breadcrumbEl = $('file-breadcrumb');
  if (!treeEl) return;
  treeEl.innerHTML = '<span class="file-tree-loading">Loading...</span>';
  fileExplorerState.selectedFilePath = null;
  updateFileExplorerUI();
  const result = await window.omni.listDirectory(dirPath);
  if (!result.ok) {
    treeEl.innerHTML = `<span class="file-tree-error">${escapeHtml(result.error || 'Error listing directory')}</span>`;
    if (breadcrumbEl) breadcrumbEl.textContent = '';
    return;
  }
  fileExplorerState.currentPath = dirPath || null;
  const entries = (result.entries || []).slice().sort((a, b) => {
    if (a.isDirectory !== b.isDirectory) return a.isDirectory ? -1 : 1;
    return (a.name || '').localeCompare(b.name || '', undefined, { sensitivity: 'base' });
  });
  fileExplorerState.currentEntries = entries;
  if (breadcrumbEl) {
    if (!dirPath) breadcrumbEl.innerHTML = '<span class="breadcrumb-part">Home</span>';
    else {
      const parts = dirPath.split(/[/\\]/).filter(Boolean);
      breadcrumbEl.innerHTML = '<span class="breadcrumb-part" data-path="">Home</span>' + parts.map((p, i) => {
        const pathSoFar = parts.slice(0, i + 1).join('/');
        return `<span class="breadcrumb-sep">/</span><span class="breadcrumb-part" data-path="${escapeHtml(pathSoFar)}">${escapeHtml(p)}</span>`;
      }).join('');
    }
  }
  breadcrumbEl?.querySelectorAll('.breadcrumb-part').forEach((el) => {
    el.addEventListener('click', () => {
      fileExplorerState.stack = [];
      loadFileTree(el.dataset.path || null);
    });
  });
  renderFileList(entries);
}

export async function analyzeFile(filePath, navigate) {
  const nav = navigate ?? navigateRef;
  const result = await window.omni.extractDocument(filePath);
  if (!result.ok) {
    appendUserMessage(`[DOC ERROR] ${result.error}`);
    showToast('Error al analizar el archivo', 'error');
    return;
  }
  const chat = ensureCurrentChat(result.filename ? result.filename.slice(0, 20) + (result.filename.length > 20 ? '...' : '') : 'Documento');
  appendUserMessage(`[DOC] ${result.filename}\n${result.content}`);
  chat.messages.push({ role: 'user', content: `[DOC]\n${result.content}` });
  await persistChats();
  showToast('Archivo añadido al chat', 'success');
  if (nav) nav(PAGES.CHAT);
}

export function onNavigateToFilePage() {
  loadFileTree(fileExplorerState.currentPath);
}
