import { state } from './state.js';
import { $ } from './utils.js';
import { showToast } from './ui.js';
import { ensureCurrentChat, appendUserMessage, sendMessage } from './chat.js';
import { MAX_RECORDING_MS } from './constants.js';

export function setupToolsMenu(contentArea) {
  const toolsMenu = $('tools-menu');
  if (!toolsMenu) return;

  $('btn-tools')?.addEventListener('click', () => toolsMenu.classList.toggle('show'));
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#btn-tools') && !e.target.closest('.tools-menu')) toolsMenu.classList.remove('show');
  });

  toolsMenu.querySelectorAll('[data-tool]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      toolsMenu.classList.remove('show');
      const tool = btn.dataset.tool;
      if (tool === 'clipboard') {
        const text = await navigator.clipboard.readText().catch(() => '');
        if (text) {
          const chat = ensureCurrentChat('Portapapeles');
          appendUserMessage(`[CLIPBOARD]\n${text}`);
          chat.messages.push({ role: 'user', content: `[CLIPBOARD]\n${text}` });
          await window.omni.saveChats(state.chats);
          const input = $('chat-input');
          if (input) { input.value = 'Analiza: '; input.focus(); }
          showToast('Portapapeles añadido al chat', 'success');
        } else {
          showToast('Portapapeles vacío', 'info');
        }
      } else if (tool === 'screen_read') {
        const bounds = await window.omni.startScreenRegionSelect();
        if (bounds) {
          const result = await window.omni.captureRegion(bounds);
          if (result.ok && result.imageBase64) {
            sendMessage('Analiza detalladamente esta captura.', result.imageBase64);
            showToast('Captura enviada al chat', 'success');
          }
        }
      }
    });
  });
}

export function setupVoice(contentArea) {
  window.omni.onVoiceTrigger(async (source) => {
    if (state.mediaRecorder?.state === 'recording') {
      state.mediaRecorder.stop();
      return;
    }
    try {
      const stream = source === 'system_audio'
        ? await navigator.mediaDevices.getDisplayMedia({
            video: false,
            audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false, suppressLocalAudioPlayback: false }
          })
        : await navigator.mediaDevices.getUserMedia({ audio: true });
      state.mediaRecorder = new MediaRecorder(stream);
      state.recordingChunks = [];
      state.mediaRecorder.ondataavailable = (e) => { if (e.data.size) state.recordingChunks.push(e.data); };
      state.mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(state.recordingChunks, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.onloadend = async () => {
          const base64 = reader.result.split(',')[1];
          const result = await window.omni.voiceTranscribe(base64);
          if (result.ok && result.text) {
            const input = $('chat-input');
            if (input) { input.value = result.text; input.focus(); }
          }
          contentArea?.classList.remove('listening-border', 'mic', 'system_audio');
        };
        reader.readAsDataURL(blob);
      };
      contentArea?.classList.add('listening-border', source === 'mic' ? 'mic' : source === 'system_audio' ? 'system_audio' : '');
      state.mediaRecorder.start();
      setTimeout(() => {
        if (state.mediaRecorder?.state === 'recording') state.mediaRecorder.stop();
      }, MAX_RECORDING_MS);
    } catch (_) {
      contentArea?.classList.remove('listening-border', 'mic', 'system_audio');
    }
  });
}
