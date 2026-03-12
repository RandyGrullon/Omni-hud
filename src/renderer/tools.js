import { state } from './state.js';
import { $ } from './utils.js';
import { showToast } from './ui.js';
import { ensureCurrentChat, appendUserMessage, sendMessage, persistChats } from './chat.js';
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
          await persistChats();
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

async function getScreenAudioStream() {
  const audioOpts = { echoCancellation: false, noiseSuppression: false, autoGainControl: false, suppressLocalAudioPlayback: false };
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: false,
      audio: audioOpts
    });
    if (stream.getAudioTracks().length > 0) return stream;
    stream.getTracks().forEach((t) => t.stop());
  } catch (_) {}
  const fallback = await navigator.mediaDevices.getDisplayMedia({
    video: true,
    audio: true
  });
  const audioTracks = fallback.getAudioTracks();
  if (audioTracks.length === 0) {
    fallback.getTracks().forEach((t) => t.stop());
    return null;
  }
  fallback.getVideoTracks().forEach((t) => t.stop());
  return new MediaStream(audioTracks);
}

export function setupVoice(contentArea) {
  const removeListeningClasses = () => contentArea?.classList.remove('listening-border', 'mic', 'system', 'system_audio');

  window.omni.onVoiceTrigger(async (source) => {
    if (state.mediaRecorder?.state === 'recording') {
      state.mediaRecorder.stop();
      return;
    }
    try {
      const isScreen = source === 'system' || source === 'system_audio';
      const stream = isScreen
        ? await getScreenAudioStream()
        : await navigator.mediaDevices.getUserMedia({ audio: true });

      if (!stream || stream.getAudioTracks().length === 0) {
        if (stream) stream.getTracks().forEach((t) => t.stop());
        showToast(isScreen ? 'Selecciona una pantalla con audio para grabar.' : 'No se pudo acceder al micrófono.', 'error');
        return;
      }

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
          removeListeningClasses();
        };
        reader.readAsDataURL(blob);
      };

      contentArea?.classList.add('listening-border', source === 'mic' ? 'mic' : 'system');
      state.mediaRecorder.start();
      setTimeout(() => {
        if (state.mediaRecorder?.state === 'recording') state.mediaRecorder.stop();
      }, MAX_RECORDING_MS);
    } catch (e) {
      removeListeningClasses();
      const msg = e?.message || String(e);
      const isScreen = source === 'system' || source === 'system_audio';
      showToast(isScreen ? 'Debes compartir una pantalla para grabar su audio.' : 'No se pudo acceder al micrófono.', 'error');
    }
  });
}
