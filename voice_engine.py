# voice_engine.py
import pyaudiowpatch as pyaudio
import speech_recognition as sr
import io
import wave
import time
from PyQt6.QtCore import QThread, pyqtSignal

class VoiceWorker(QThread):
    """
    Motor de Audio Dual: Puede capturar Audio del Sistema (WASAPI)
    o Micrófono estándar.
    """
    transcription_ready = pyqtSignal(str)
    listening_status = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, max_duration=15, source_type="system"):
        super().__init__()
        self.max_duration = max_duration
        self.source_type = source_type
        self._is_running = True

    def stop_recording(self):
        self._is_running = False

    def run(self):
        with pyaudio.PyAudio() as p:
            try:
                self.listening_status.emit(True)
                
                # Seleccionar dispositivo según el tipo de fuente
                if self.source_type == "system":
                    device = self._get_wasapi_loopback_device(p)
                else:
                    device = p.get_default_input_device_info()

                if not device:
                    self.error_occurred.emit("No se encontró el dispositivo de audio.")
                    return

                samplerate = int(device["defaultSampleRate"])
                channels = int(device["maxInputChannels"]) if self.source_type == "system" else 1

                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=channels,
                    rate=samplerate,
                    input=True,
                    input_device_index=device["index"],
                    frames_per_buffer=1024
                )

                frames = []
                start_time = time.time()
                while self._is_running and (time.time() - start_time) < self.max_duration:
                    data = stream.read(1024, exception_on_overflow=False)
                    frames.append(data)

                stream.stop_stream()
                stream.close()
                self.listening_status.emit(False)

                # Transcripción
                byte_io = io.BytesIO()
                with wave.open(byte_io, 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(samplerate)
                    wf.writeframes(b''.join(frames))
                
                byte_io.seek(0)
                recognizer = sr.Recognizer()
                with sr.AudioFile(byte_io) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language="es-ES")
                    if text:
                        self.transcription_ready.emit(text)
                    else:
                        self.error_occurred.emit("No se detectó voz clara.")

            except Exception as e:
                self.listening_status.emit(False)
                self.error_occurred.emit(f"Error de audio ({self.source_type}): {str(e)}")

    def _get_wasapi_loopback_device(self, p):
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            if default_speakers["isLoopbackDevice"]:
                return default_speakers
            for loopback in p.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    return loopback
        except:
            pass
        return None
