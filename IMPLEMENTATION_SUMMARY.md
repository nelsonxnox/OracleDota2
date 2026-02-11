# Resumen de Implementación - Términos de Uso y Auto-Actualización

**Fecha:** 11 de febrero de 2026  
**Desarrollador:** Nelson Planes Arencibia  
**Contacto:** nelsonplanes@gmail.com

---

## 📋 TÉRMINOS DE USO Y CONDICIONES

### ✅ Archivos Creados

1. **`TERMS_OF_SERVICE.md`** (Raíz del proyecto)
   - Documento legal completo con 15 secciones
   - ~400 líneas de términos detallados
   - Incluye toda la información legal necesaria

2. **`frontend/components/TermsModal.tsx`**
   - Modal interactivo de React/Next.js
   - Scroll-to-accept functionality
   - Diseño moderno con Framer Motion
   - Resumen visual de los términos

### 📝 Contenido de los Términos

#### Secciones Principales:

1. **Información del Servicio**
   - Desarrollador: Nelson Planes Arencibia
   - Contacto: nelsonplanes@gmail.com
   - Naturaleza: Proyecto de código abierto para Dota 2

2. **Tecnologías Utilizadas** (Completo)
   - **Backend:** FastAPI, Uvicorn, Python 3.10+, Firebase Admin SDK, Websockets
   - **IA:** OpenRouter API, OpenAI SDK, modelos (DeepSeek, Gemini, LLaMA)
   - **Datos:** OpenDota API, Stratz API, Valve GSI
   - **Frontend:** Next.js, React, TailwindCSS, Framer Motion, Recharts
   - **Desktop:** Tkinter, PyInstaller, Vosk, pyttsx3
   - **Cloud:** Render.com, Netlify, Firebase (Google Cloud)

3. **Propiedad Intelectual**
   - Licencia MIT (código abierto)
   - Atribuciones a Valve Corporation
   - No afiliación con Valve
   - Derechos de contribuidores

4. **Privacidad y Datos (GDPR Compliant)**
   - Datos recopilados: email, historial de partidas, consultas al AI
   - Almacenamiento en Firebase (Google Cloud)
   - NO vendemos datos a terceros
   - Derechos del usuario: acceso, corrección, eliminación, exportación

5. **Sistema de Tokens**
   - Cuenta Gratuita: 1 token (1 partida)
   - Plan Básico: $1.99 USD - 10 partidas
   - Plan Premium: $2.50 USD - 50 partidas
   - Tokens no reembolsables una vez consumidos
   - Procesamiento de pagos seguro (Stripe/PayPal)

6. **Uso Aceptable**
   - ✅ Permitido: Análisis personal, compartir insights, contribuir al proyecto
   - ❌ Prohibido: Trampa, fraude, DDoS, bots maliciosos

7. **Limitaciones de Responsabilidad**
   - Servicio "TAL CUAL"
   - IA puede cometer errores
   - No garantizamos victoria ni mejora de rendimiento
   - No responsables por suspensiones de Steam

8. **Contribuciones Comunitarias** ⭐
   - Proyecto de código abierto
   - Llamado a la comunidad para ayudar
   - Áreas: Backend, Frontend, ML/AI, UI/UX, Testing, Documentación
   - Contacto: nelsonplanes@gmail.com

9. **Información Legal**
   - Legislación aplicable
   - Resolución de disputas
   - Contacto y soporte

### 🎨 Modal de Términos (TermsModal.tsx)

**Características:**
- ✅ Diseño moderno con gradientes purple/blue
- ✅ Scroll-to-accept: botón "Acepto" se habilita al llegar al final
- ✅ Resumen visual organizado por secciones
- ✅ Iconos y colores para mejor legibilidad
- ✅ Información destacada:
  - 📋 Información del servicio
  - 🎮 Qué es Oracle Dota 2
  - 🔧 Tecnologías utilizadas
  - 💰 Sistema de tokens
  - 🔒 Privacidad y datos
  - ✅ Uso permitido
  - ❌ Uso prohibido
  - ⚖️ Limitaciones de responsabilidad
  - 🤝 Proyecto comunitario (con llamado a contribuir)
  - 📄 Información legal
- ✅ Link a términos completos
- ✅ Animaciones con Framer Motion

### 🔄 Integración en Registro

**Archivo modificado:** `frontend/app/register/page.tsx`

**Cambios:**
1. Importación de `TermsModal`
2. Estados agregados:
   - `showTerms`: controla visibilidad del modal
   - `termsAccepted`: indica si el usuario aceptó

3. Lógica de registro actualizada:
   - Verifica `termsAccepted` antes de permitir registro
   - Si no aceptó, muestra modal
   - Guarda en Firestore:
     ```javascript
     termsAccepted: true,
     termsAcceptedAt: new Date().toISOString()
     ```

4. UI actualizada:
   - Checkbox "Acepto los Términos de Uso y Condiciones"
   - Botón clickeable para abrir modal
   - Botón de registro deshabilitado si no aceptó términos
   - Texto dinámico: "Acepta los términos primero" / "Registrarse"

5. Handlers:
   - `handleAcceptTerms()`: marca checkbox y cierra modal
   - `handleDeclineTerms()`: cierra modal y muestra error

---

## 🔄 SISTEMA DE AUTO-ACTUALIZACIÓN

### ✅ Archivos Modificados/Creados

1. **`backend/main.py`**
   - Nuevo endpoint: `GET /api/version`
   - Retorna: versión, download_url, changelog

2. **`oracle_neural_link/oracle_bridge.py`**
   - Constante: `CURRENT_VERSION = "1.3.0"`
   - Función: `check_for_updates()`
   - Función: `download_and_install_update(download_url)`
   - Botón UI: "🔄 Buscar Actualizaciones"
   - Label: "Versión: 1.3.0"
   - Handler: `handle_update_click()`

3. **`oracle_neural_link/build_exe.py`**
   - Script de build con PyInstaller
   - Limpia builds anteriores
   - Genera ejecutable
   - Copia a `backend/dist/`
   - Muestra tamaño del archivo

### 🔧 Funcionalidad

**Flujo de Actualización:**
1. Usuario hace clic en "🔄 Buscar Actualizaciones"
2. App consulta `/api/version` del backend
3. Compara versiones (latest > current)
4. Si hay actualización, muestra diálogo con changelog
5. Usuario acepta → Descarga nuevo `.exe`
6. Crea `update.bat`:
   - Espera 2 segundos
   - Elimina `.exe` antiguo
   - Renombra `.exe` nuevo
   - Reinicia aplicación
   - Se auto-elimina
7. Aplicación se cierra y ejecuta `update.bat`
8. Aplicación se reinicia con nueva versión

**Endpoint `/api/version`:**
```python
{
    "version": "1.3.0",
    "download_url": "https://backend.onrender.com/download/OracleNeuralLink.exe",
    "changelog": "- Sistema de tokens\n- Auto-actualización\n- Mejoras en AI coach"
}
```

---

## 📦 ARCHIVOS CREADOS/MODIFICADOS

### Nuevos Archivos:
1. `TERMS_OF_SERVICE.md` - Términos completos
2. `frontend/components/TermsModal.tsx` - Modal de términos
3. `oracle_neural_link/build_exe.py` - Script de build

### Archivos Modificados:
1. `backend/main.py` - Endpoint `/api/version`
2. `oracle_neural_link/oracle_bridge.py` - Auto-update + UI
3. `frontend/app/register/page.tsx` - Integración de términos

---

### ✅ 4. Optimizaciones del Dashboard (v1.4.0)

**Backend:**
- Endpoint `/api/player/{account_id}/stats`: Winrate, Versatilidad y Total Games desde OpenDota.
- Endpoint `/api/user/{user_id}/question-limit`: Verifica cuota de preguntas.
- Servicio `question_limit_service.py`: Control de límites según plan (Gratis: 3/mes).

**Frontend:**
- `PlayerStatsCard.tsx`: Visualización de estadísticas reales.
- `PlansPanel.tsx`: Comparativa de planes (Gratis, Básico $1.99, Premium $2.50).
- Banner "Oracle Protocol" en Dashboard.
- Planes integrados en Homepage y Dashboard.

---

## 🚀 PRÓXIMOS PASOS


### Para Desarrolladores:

1. **Generar Ejecutable:**
   ```bash
   cd oracle_neural_link
   python build_exe.py
   ```

2. **Verificar:**
   - Ejecutable en `backend/dist/OracleNeuralLink.exe`
   - Tamaño: ~20-30 MB

3. **Actualizar Versiones:**
   - `oracle_bridge.py`: `CURRENT_VERSION = "1.4.0"`
   - `backend/main.py`: endpoint `/api/version`

4. **Desplegar:**
   ```bash
   git add .
   git commit -m "feat: Términos de uso y auto-actualización v1.3.0"
   git push origin main
   ```

### Para Usuarios:

1. **Registrarse:**
   - Llenar formulario
   - Hacer clic en checkbox de términos
   - Leer términos (scroll hasta el final)
   - Aceptar términos
   - Completar registro

2. **Actualizar Oracle Bridge:**
   - Abrir aplicación
   - Hacer clic en "🔄 Buscar Actualizaciones"
   - Si hay actualización, hacer clic en "Sí"
   - Esperar descarga e instalación
   - Aplicación se reiniciará automáticamente

---

## 📧 CONTACTO Y SOPORTE

**Desarrollador:** Nelson Planes Arencibia  
**Email:** nelsonplanes@gmail.com  
**Proyecto:** Oracle Dota 2 - AI Coaching Platform  
**Licencia:** MIT (Código Abierto)

---

## 🤝 LLAMADO A LA COMUNIDAD

**¡Necesitamos tu ayuda!**

Oracle Dota 2 es un proyecto comunitario de código abierto. Si tienes habilidades en:

- 🐍 Desarrollo Backend (Python/FastAPI)
- ⚛️ Desarrollo Frontend (React/Next.js)
- 🤖 Machine Learning / AI
- 🎨 Diseño UI/UX
- 🧪 Testing y QA
- 📝 Documentación

**¡Únete a nosotros!**  
Contacta a: **nelsonplanes@gmail.com**

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Crear documento de términos completo
- [x] Crear modal interactivo de términos
- [x] Integrar modal en flujo de registro
- [x] Agregar checkbox de aceptación
- [x] Guardar aceptación en Firestore
- [x] Crear endpoint `/api/version`
- [x] Implementar funciones de auto-actualización
- [x] Agregar botón de actualización a UI
- [x] Crear script de build
- [ ] Generar ejecutable (en proceso)
- [ ] Probar flujo de registro con términos
- [ ] Probar auto-actualización
- [ ] Desplegar a producción

---

**Versión del Sistema:** 1.3.0  
**Fecha de Implementación:** 11 de febrero de 2026  
**Estado:** ✅ Implementado - Pendiente de Testing
