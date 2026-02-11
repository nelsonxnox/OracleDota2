# Comandos Git para Despliegue

## 1. Verificar Estado
```bash
cd "d:\Proyectos de Informatica\proyecto de dota 2"
git status
```

## 2. Agregar Todos los Cambios
```bash
git add .
```

## 3. Crear Commit Descriptivo
```bash
git commit -m "feat: Sistema de tokens de un solo uso + planes de pago

BACKEND:
- Token service con límite de partidas (matches_remaining)
- Consumo automático de token al inicio de partida
- Endpoint /api/token/status para consultar partidas restantes
- Advertencias cuando quedan ≤2 partidas
- Desactivación automática cuando token llega a 0

FRONTEND:
- Página /plans con diseño moderno
- Plan Básico: $1.99 USD (10 partidas)
- Plan Premium: $2.50 USD (50 partidas)
- Animaciones con Framer Motion
- Placeholder para integración de pago

LIVE COACH:
- Consolidación de consejos cada 5 minutos
- Análisis maestro detallado sin límite de palabras
- Mejoras en AI coach con openrouter/auto"
```

## 4. Push a GitHub
```bash
git push origin main
```

## 5. Verificar Despliegue Automático

### Render (Backend)
1. Ve a https://dashboard.render.com
2. Busca tu servicio "oracle-dota2-backend"
3. Verifica que el despliegue se active automáticamente
4. Espera a que el estado sea "Live"

### Netlify (Frontend)
1. Ve a https://app.netlify.com
2. Busca tu sitio "oracle-dota2"
3. Verifica que el despliegue se active automáticamente
4. Espera a que el estado sea "Published"

## 6. Testing Post-Despliegue

### Backend
```bash
# Health check
curl https://tu-backend.onrender.com/health

# Token status (reemplaza TOKEN con un token real)
curl https://tu-backend.onrender.com/api/token/status/TOKEN
```

### Frontend
- Visita https://tu-frontend.netlify.app/plans
- Verifica que las tarjetas de planes se muestren correctamente
- Prueba hacer clic en "Seleccionar Plan"

## Notas

- **Primera vez**: Si es tu primer push, puede tardar 5-10 minutos en desplegar
- **Errores**: Revisa los logs en Render/Netlify si algo falla
- **Variables de entorno**: Asegúrate de que `OPENROUTER_API_KEY` y `FIREBASE_CREDENTIALS` estén configuradas en Render

## Rollback (Si algo sale mal)

```bash
# Ver commits recientes
git log --oneline -5

# Revertir al commit anterior
git revert HEAD

# Push del revert
git push origin main
```
