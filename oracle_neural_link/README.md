# 🔮 Oracle Neural Link — Dota 2 AI Coach

**Coach de Dota 2 en tiempo real con inteligencia artificial.**  
Analiza tu partida mientras juegas y te da consejos por voz y texto.

---

## 🗺️ ¿Cómo funciona?

```
Tu PC                                    Internet
─────────────────────────────────────────────────────────────────
  🎮 Dota 2                                   🤖 AI (OpenRouter)
     │                                              ▲
     │ Game State Integration                       │ análisis
     ▼                                              │
  📡 GSI Server ──── WebSocket ──────► 🌐 Backend (Render.com)
  (localhost:3000)    token               oracledota2.onrender.com
     │                                              │
     ▼                                              ▼
  🖥️ OracleNeuralLink.exe              🔥 Firebase (tokens/usuarios)
     │
     ▼
  🔊 Voz del Coach (pyttsx3)
  💬 Chat en pantalla
```

---

## 🚀 Pasos para usar el programa

### 1. Regístrate en la web
👉 Ve a `https://oracledota2.onrender.com` y crea tu cuenta.  
Al registrarte recibirás automáticamente un **token de acceso** válido para **2 partidas**.

> Tu token aparece en el Dashboard → sección "Live Coaching"

### 2. Descarga e instala el programa
- **[DESCARGAR ORACLE NEURAL LINK (Google Drive)](https://drive.google.com/uc?export=download&id=10ryKp5y3s0JnMAtfdZPvEo1-OY-1jrOY)** (≈ 29 MB)
- No requiere instalación — ejecuta el `.exe` directamente

### 3. Instala la configuración de Dota 2 (GSI)
1. Abre `OracleNeuralLink.exe`
2. Haz clic en **"Instalar GSI Config"**
3. Reinicia Dota 2

> Si Steam no está en `C:\Program Files (x86)\Steam\...`, instala el GSI manualmente (ver abajo)

### 4. Conecta el Oracle
1. Pega tu **token** en el campo "Access Token"
2. Haz clic en **"⚡ ACTIVAR ENLACE"**
3. Espera a ver **"Conectado a Oracle ✓"** en verde

### 5. ¡Juega!
- Entra a una partida de Dota 2
- El coach analizará tu juego automáticamente
- Verás consejos en el chat y los escucharás por los parlantes

---

## 📋 Requisitos del sistema

| Requisito | Valor |
|-----------|-------|
| Sistema Operativo | Windows 10 / 11 (64-bit) |
| Dota 2 | Instalado y actualizado |
| Internet | Requerido (para conectar al backend) |
| Cuenta en la web | Requerida (para el token) |

---

## ⚠️ Solución de problemas

| Problema | Solución |
|----------|----------|
| "Conectando..." no cambia | Verifica tu internet y que el token sea válido |
| GSI: Inactivo durante la partida | Asegúrate de haber instalado el GSI y reiniciado Dota 2 |
| Token inválido o expirado | Ve al Dashboard web y genera un nuevo token |
| Sin voz del coach | Verifica que el volumen no esté en 0 o que el idioma español esté instalado en Windows TTS |
| "No se encontró Dota 2" | Instala el GSI manualmente (ver abajo) |

### Instalación manual del GSI
Crea el archivo:
```
C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration\gamestate_integration_oracle.cfg
```
Con este contenido:
```
"Oracle Config"
{
    "uri"           "http://localhost:3000/"
    "timeout"       "5.0"
    "buffer"        "0.1"
    "throttle"      "0.1"
    "heartbeat"     "30.0"
    "data"
    {
        "provider"      "1"
        "map"           "1"
        "player"        "1"
        "hero"          "1"
        "abilities"     "1"
        "items"         "1"
        "allplayers"    "1"
    }
}
```

---

## 🔑 Sistema de tokens

- Cada usuario nuevo recibe **2 partidas gratis**
- Para más partidas, consulta el sistema de donaciones en la web
- El token se consume automáticamente al terminar una partida

---

## 🛠️ Para desarrolladores (correr desde código fuente)

```bash
cd oracle_neural_link
pip install -r requirements.txt
python oracle_bridge.py
```

---

## 📦 Build del ejecutable

```bash
cd oracle_neural_link
python -m PyInstaller OracleNeuralLink.spec --clean
# El .exe queda en dist/OracleNeuralLink.exe
```

---

*Versión 1.3.2 — Oracle Neural Link*
