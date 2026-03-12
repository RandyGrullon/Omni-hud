const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('omni', {
  // Window
  close: () => ipcRenderer.invoke('window:close'),
  isVisible: () => ipcRenderer.invoke('window:isVisible'),

  // Storage
  loadChats: () => ipcRenderer.invoke('storage:loadChats'),
  saveChats: (chats) => ipcRenderer.invoke('storage:saveChats', chats),
  getAuthToken: () => ipcRenderer.invoke('storage:getAuthToken'),
  setAuthToken: (token) => ipcRenderer.invoke('storage:setAuthToken', token),
  removeAuthToken: () => ipcRenderer.invoke('storage:removeAuthToken'),
  getGroqKey: () => ipcRenderer.invoke('storage:getGroqKey'),
  getGroqKeyAsync: () => ipcRenderer.invoke('storage:getGroqKeyAsync'),
  setGroqKey: (key) => ipcRenderer.invoke('storage:setGroqKey', key),
  syncGroqKeyToWeb: (key) => ipcRenderer.invoke('storage:syncGroqKeyToWeb', key),

  // Auth
  login: (email, password) => ipcRenderer.invoke('auth:login', email, password),
  logout: () => ipcRenderer.invoke('auth:logout'),
  getProfile: () => ipcRenderer.invoke('auth:getProfile'),
  validateAccess: () => ipcRenderer.invoke('auth:validateAccess'),
  activateKey: (key) => ipcRenderer.invoke('auth:activate', key),
  updateProfile: (payload) => ipcRenderer.invoke('profile:update', payload),

  // AI
  streamChat: (payload) => ipcRenderer.invoke('ai:stream', payload),
  cancelAi: () => ipcRenderer.send('ai-cancel'),
  onAiChunk: (cb) => { ipcRenderer.on('ai-chunk', (_, chunk) => cb(chunk)); },
  onAiDone: (cb) => { ipcRenderer.on('ai-done', (_, full) => cb(full)); },
  onAiError: (cb) => { ipcRenderer.on('ai-error', (_, err) => cb(err)); },

  // Voice (renderer records, main transcribes)
  voiceTranscribe: (audioBase64) => ipcRenderer.invoke('voice:transcribe', audioBase64),
  onVoiceTrigger: (cb) => { ipcRenderer.on('voice-trigger', (_, source) => cb(source)); },
  onTranscription: (cb) => { ipcRenderer.on('transcription', (_, text) => cb(text)); },

  // Screen
  getScreenSources: () => ipcRenderer.invoke('screen:getSources'),
  captureRegion: (bounds) => ipcRenderer.invoke('screen:captureRegion', bounds),
  startScreenRegionSelect: () => ipcRenderer.invoke('screen:startRegionSelect'),

  // Documents
  extractDocument: (filePath) => ipcRenderer.invoke('documents:extract', filePath),
  openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
  listDirectory: (dirPath) => ipcRenderer.invoke('files:listDirectory', dirPath),
  openDirectoryDialog: () => ipcRenderer.invoke('dialog:openDirectory'),

  // Updates
  checkUpdates: () => ipcRenderer.invoke('updates:check'),

  // Clear chat hotkey
  onClearChatRequest: (cb) => { ipcRenderer.on('clear-chat-request', () => cb()); }
});
