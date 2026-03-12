# Omni HUD (Electron)

HUD de escritorio con Electron. Modo ghost en Windows 10 2004+ (no detectable en capturas).

## Requisitos

- Node.js 18+
- Cuenta Supabase (auth + tabla `profiles`)
- API Key de Groq

## Configuración

1. Copia `.env.example` a `.env` en la raíz del proyecto.
2. Rellena `SUPABASE_URL`, `SUPABASE_KEY` y `GROQ_API_KEY`.

## Desarrollo

```bash
npm install
npm start
```

## Build

```bash
npm run build
# o solo Windows
npm run build:win
```

El instalador se genera en `dist/`. Si en Windows aparece un error de "símbolo de enlace" o privilegios al extraer winCodeSign, ejecuta el terminal como **Administrador** o define `CSC_IDENTITY_AUTO_DISCOVERY=false` antes de `npm run build`. Con `npm run build:dir` se genera solo la carpeta (sin instalador NSIS).

## Atajos

- **Ctrl+Space**: Mostrar/ocultar HUD
- **Ctrl+Shift+R**: Captura de audio del sistema (mic vía ventana)
- **Ctrl+Shift+M**: Micrófono → transcripción (Groq Whisper)
- **Ctrl+L**: Limpiar chat actual

## Ghost mode

En Windows 10 versión 2004 o superior, la ventana se excluye de capturas (OBS, Discord, etc.) mediante `setContentProtection(true)`.
