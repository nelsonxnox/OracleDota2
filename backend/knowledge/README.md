# 📚 Knowledge Module - Sistema RAG para Oracle Coach

Este módulo implementa un sistema de **RAG (Retrieval-Augmented Generation)** optimizado para el coach de Dota 2.

## 🎯 Objetivo

Darle al coach IA conocimiento actualizado del **meta actual** sin gastar miles de tokens en cada consulta.

## 📁 Estructura

```
knowledge/
├── __init__.py           # Exporta funciones principales
├── meta_740c.py         # Base de conocimiento curada (Parche 7.40c)
├── meta_737.py          # Base de conocimiento legacy (Parche 7.37)
├── dota_mapper.py       # Mapea IDs a nombres legibles
├── heroes.json          # Datos de héroes (dotaconstants)
├── items.json           # Datos de items (dotaconstants)
└── abilities.json       # Datos de habilidades (dotaconstants)
```

## 🧠 Cómo Funciona (RAG Selectivo)

### ❌ Método Tradicional (Costoso)
```python
# Manda TODO el conocimiento en cada pregunta
prompt = f"{TODA_LA_WIKI} + {CONTEXTO_PARTIDA} + {PREGUNTA}"
# Resultado: 3000+ tokens por consulta 💸
```

### ✅ Método RAG (Eficiente)
```python
# Solo manda lo RELEVANTE a la pregunta
knowledge = get_relevant_knowledge(query="¿Qué compro contra Medusa?")
# Resultado: ~300 tokens por consulta (ahorro del 90%) 🚀
```

## 📊 Comparación de Tokens

| Escenario | Sin RAG | Con RAG Selectivo | Ahorro |
|-----------|---------|-------------------|--------|
| Pregunta simple | 500 tokens | 200 tokens | 60% ⬇️ |
| Pregunta compleja | 2000 tokens | 400 tokens | 80% ⬇️ |
| Análisis completo | 3000 tokens | 600 tokens | 80% ⬇️ |

## 🔧 Uso

### Desde `ai_coach.py`
El sistema se activa automáticamente cuando detecta la carpeta `knowledge/`:

```python
from knowledge import get_relevant_knowledge

# Inyección selectiva basada en la pregunta
relevant_info = get_relevant_knowledge("¿Por qué perdí con Void?")
# Solo devuelve: Facetas de Void + Timings de Carry + Errores comunes
```

### Actualizar Datos de DotaConstants
```bash
# Desde el directorio del proyecto
curl -o knowledge/heroes.json https://raw.githubusercontent.com/odota/dotaconstants/master/build/heroes.json
curl -o knowledge/items.json https://raw.githubusercontent.com/odota/dotaconstants/master/build/items.json
curl -o knowledge/abilities.json https://raw.githubusercontent.com/odota/dotaconstants/master/build/abilities.json
```

## 🎓 Fuentes de Conocimiento

1. **DotaConstants** (odota/dotaconstants)
   - IDs de héroes, items, habilidades
   - Datos estructurados y actualizados

2. **Meta Curado** (`meta_737.py`)
   - Items tier S del parche actual
   - Counters críticos
   - Prioridades por rol
   - Facetas recomendadas
   - Errores comunes

3. **Liquidpedia** (futuro)
   - Notas de parches
   - Cambios de mecánicas

4. **Dota2ProTracker** (futuro)
   - Winrates de facetas
   - Builds profesionales

## 🔄 Actualizar el Meta

Para actualizar el conocimiento del meta, edita `meta_737.py`:

```python
# Ejemplo: Agregar nuevo counter
CRITICAL_COUNTERS["new_hero_type"] = {
    "heroes": ["Hero1", "Hero2"],
    "counters": "Item X, Hero Y. Descripción breve."
}
```

## 🚀 Optimizaciones Implementadas

1. **Inyección Selectiva**: Solo envía lo relevante a cada pregunta
2. **Abreviaciones**: NW en vez de Net Worth ahorra ~40% tokens
3. **Cache de Historial**: Solo últimos 4 mensajes (evita acumulación)
4. **Lazy Loading**: Solo carga JSONs cuando es necesario

## 📈 Roadmap

- [ ] Scraping automático de Liquidpedia para patch notes
- [ ] Integración con Dota2ProTracker API
- [ ] Embeddings con ChromaDB/FAISS para búsqueda semántica
- [ ] Auto-actualización semanal de meta knowledge
- [ ] Análisis de replays (.dem files)

## 🎯 Best Practices

✅ **DO:**
- Actualiza `meta_737.py` cada nuevo parche
- Usa abreviaciones en tus datos curados
- Mantén las descripciones cortas (1-2 frases max)
- Test con `SafeToAutoRun=true` para iteraciones rápidas

❌ **DON'T:**
- No metas toda la wiki en el prompt
- No pongas conocimiento en el historial de chat
- No uses tokens en datos repetitivos

## 📞 Debug

Si el RAG no funciona:
```bash
# Ver logs en consola del servidor
[ORACLE] RAG System activado - Conocimiento del meta disponible
[RAG] Inyectado conocimiento relevante (456 chars)
```

Si ves:
```
[ORACLE] Warning: RAG System no disponible
```
Verifica que la carpeta `knowledge/` exista y tenga `__init__.py`.

---

**Creado por**: Oracle Coach Development Team  
**Última actualización**: Feb 2026 (Parche 7.40c)
