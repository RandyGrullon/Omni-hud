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

Antes de generar el instalador, revisa **`src/main/supabase.config.json`**:

- **`SUPABASE_URL`** y **`SUPABASE_KEY`** (anon): deben ser los del mismo proyecto Supabase que usa omni-web.
- **`OMNI_WEB_API_URL`**: debe ser la URL real de producción de tu web (p. ej. `https://tu-app.vercel.app`). Así la app instalada podrá usar la clave de Groq guardada en el perfil web.

```bash
npm run build
# o solo Windows / Mac
npm run build:win
npm run build:mac
```

El instalador se genera en `dist/`. Si en Windows aparece un error de "símbolo de enlace" o privilegios al extraer winCodeSign, ejecuta el terminal como **Administrador** o define `CSC_IDENTITY_AUTO_DISCOVERY=false` antes de `npm run build`. Con `npm run build:dir` se genera solo la carpeta (sin instalador NSIS).

**macOS (.dmg):** La primera vez, macOS puede bloquear la app (Gatekeeper). El usuario puede hacer **clic derecho en la app > Abrir** para confirmar que quiere ejecutarla.

## Atajos

- **Ctrl+Space**: Mostrar/ocultar HUD
- **Ctrl+Shift+R**: Captura de audio del sistema (mic vía ventana)
- **Ctrl+Shift+M**: Micrófono → transcripción (Groq Whisper)
- **Ctrl+L**: Limpiar chat actual

## Ghost mode

En Windows 10 versión 2004 o superior, la ventana se excluye de capturas (OBS, Discord, etc.) mediante `setContentProtection(true)`.
