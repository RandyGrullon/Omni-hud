const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('api', {
  sendRegion: (bounds) => ipcRenderer.send('region-selected', bounds)
});
