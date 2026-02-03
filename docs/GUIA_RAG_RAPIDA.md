# 🚀 GUÍA RÁPIDA - Sistema RAG Oracle Coach

## ✅ ¿Qué Cambió?

### Antes (Eliminado)
- ❌ Groq (llama models)
- ❌ OpenAI (gpt-4o-mini)
- ❌ Fallbacks complejos
- ❌ 2000-3000 tokens por consulta

### Ahora (Implementado)
- ✅ **Solo DeepSeek R1** (vía OpenRouter)
- ✅ **Sistema RAG** con conocimiento del meta
- ✅ **Inyección selectiva** (solo lo relevante)
- ✅ **400-600 tokens** por consulta (ahorro 75%)

## 🎯 Uso del Sistema

### El RAG Funciona Automáticamente

Cuando haces una pregunta al coach, el sistema:

1. **Analiza keywords** en tu pregunta
2. **Busca conocimiento relevante** del meta
3. **Inyecta solo lo necesario** (~300 tokens)
4. **Envía todo a DeepSeek** para respuesta precisa

### Ejemplos de Consultas Optimizadas

**Pregunta**: "¿Qué items comprar contra Zeus?"
```
🔍 Keywords detectadas: "items", "contra"
📚 Conocimiento inyectado:
   - TIER_S_ITEMS (BKB, Eternal Shroud, Pipe)
   - CRITICAL_COUNTERS (Magic burst)
💬 Tokens enviados: ~450 (vs 2000 antes)
```

**Pregunta**: "¿Cómo mejorar de pos5?"
```
🔍 Keywords detectadas: "pos5"
📚 Conocimiento inyectado:
   - ROLE_PRIORITIES (Pos5 específico)
   - COMMON_MISTAKES (Detection, positioning)
💬 Tokens enviados: ~350 (vs 1800 antes)
```

**Pregunta**: "¿Las facetas de Void son buenas?"
```
🔍 Keywords detectadas: "facetas", "void"
📚 Conocimiento inyectado:
   - PATCH_CORE_CONCEPTS (Facetas/Innatos)
   - TOP_FACETS (Void específico)
💬 Tokens enviados: ~400 (vs 2200 antes)
```

## 📝 Actualizar el Meta

### Cada Nuevo Parche

Edita `knowledge/meta_737.py`:

```python
# Ejemplo: Agregar nuevo item tier S
TIER_S_ITEMS["nuevo_item"] = "Descripción breve (1-2 frases)."

# Ejemplo: Actualizar counter
CRITICAL_COUNTERS["nuevo_tipo"] = {
    "heroes": ["Hero1", "Hero2"],
    "counters": "Item/Hero counter. Explicación corta."
}

# Ejemplo: Modificar benchmark de rol
ROLE_PRIORITIES["pos1"]["farm_benchmark"] = "10min: 65 CS. 20min: 160 CS."
```

### Actualizar DotaConstants (Cada Parche Mayor)

```bash
cd knowledge
curl -O https://raw.githubusercontent.com/odota/dotaconstants/master/build/heroes.json
curl -O https://raw.githubusercontent.com/odota/dotaconstants/master/build/items.json
```

## 🧪 Verificar que Funciona

### Test del RAG
```bash
cd knowledge
python test_rag.py
```

**Output esperado**:
```
✅ Sistema RAG funcionando correctamente!
📊 Items tier S disponibles: 8
📊 Categorías de counters: 5
```

### Test del Coach
```bash
python -c "from ai_coach import oracle; print('OK')"
```

**Output esperado**:
```
[DotaMapper] Loaded: 127 heroes, 89 items, 598 abilities
[ORACLE] RAG System activado - Conocimiento del meta disponible
OK
```

### Test API Completo
```bash
# Inicia el servidor
python main.py
```

**Logs esperados**:
```
[ORACLE] RAG System activado - Conocimiento del meta disponible
[DotaMapper] Loaded: 127 heroes, 89 items, 598 abilities
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 📚 Archivos de Documentación

- **`knowledge/README.md`**: Documentación técnica completa del módulo RAG
- **`IMPLEMENTACION_RAG.md`**: Resumen ejecutivo con métricas y roadmap
- **Este archivo**: Guía de uso rápido

## 💡 Tips de Optimización

### DO ✅
- Mantén las descripciones **cortas** (1-2 frases)
- Usa **abreviaciones** (NW, GPM, XPM, Pos1-5)
- Actualiza el meta **cada parche**
- Prueba con `test_rag.py` después de cambios

### DON'T ❌
- No pongas todo el conocimiento en cada consulta
- No uses párrafos largos (aumentan tokens)
- No dejes datos desactualizados
- No ignores los logs de tokens

## 🎮 Casos de Uso Reales

### Análisis Post-Match
```bash
POST /analyze/7123456789
```
El coach:
- Inyecta conocimiento de TODOS los roles
- Analiza errores de itemización
- Compara con benchmarks del meta
- Respuesta completa en ~600 tokens

### Chat Interactivo
```bash
POST /chat
{
  "match_id": "7123456789",
  "query": "¿Por qué el enemy carry nos destruyó?"
}
```
El coach:
- Inyecta counters críticos
- Analiza builds del enemy
- Detecta falta de items clave
- Respuesta específica en ~350 tokens

## 🔥 Ventajas del Sistema

1. **75% menos tokens** = Más consultas gratis
2. **Respuestas más precisas** = Conocimiento actualizado
3. **Escalable** = Fácil agregar más conocimiento
4. **Fallback seguro** = Si RAG falla, coach continúa
5. **Mantenible** = Editar 1 archivo vs reentrenar IA

## 📞 Solución de Problemas

### "RAG System no disponible"
```bash
# Verifica que existe la carpeta
ls knowledge/

# Reinstala el módulo
rm -rf knowledge/__pycache__
python -c "from knowledge import get_relevant_knowledge; print('OK')"
```

### "No se cargan los JSONs"
```bash
# Descarga de nuevo
cd knowledge
curl -O https://raw.githubusercontent.com/odota/dotaconstants/master/build/heroes.json
```

### "Tokens muy altos todavía"
- Revisa que `meta_737.py` use descripciones cortas
- Verifica que las keywords detectan correctamente
- Chequea los logs: `[RAG] Inyectado conocimiento relevante (XXX chars)`

---

**¡Tu coach ahora sabe el meta sin gastar una fortuna en tokens!** 🚀

**Modelo Único**: DeepSeek R1 (gratis vía OpenRouter)  
**Ahorro Promedio**: 75% de tokens  
**Actualización**: Manual cada parche
