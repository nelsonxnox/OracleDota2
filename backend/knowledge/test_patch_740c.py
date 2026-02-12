"""
Test script para verificar que el sistema RAG carga correctamente
el conocimiento del patch 7.40c
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge import get_relevant_knowledge, PATCH_740C_NERFS, PATCH_740C_BUFFS

def test_patch_740c_knowledge():
    """Prueba que el conocimiento del patch 7.40c se inyecta correctamente"""
    
    print("=" * 60)
    print("TEST: Verificando conocimiento del Patch 7.40c")
    print("=" * 60)
    
    # Test 1: Pregunta sobre Clinkz (nerfeado)
    print("\n[TEST 1] Pregunta sobre Clinkz...")
    query1 = "¿Qué pasó con Clinkz en el último patch?"
    knowledge1 = get_relevant_knowledge(query1, debug=True)
    
    assert "clinkz" in knowledge1.lower(), "❌ No se encontró información de Clinkz"
    assert "skeleton walk" in knowledge1.lower(), "❌ No se encontró información de Skeleton Walk"
    print("✅ Test 1 PASADO: Información de Clinkz detectada correctamente")
    
    # Test 2: Pregunta sobre Terrorblade (buffed)
    print("\n[TEST 2] Pregunta sobre Terrorblade...")
    query2 = "¿Es viable Terrorblade ahora?"
    knowledge2 = get_relevant_knowledge(query2, debug=True)
    
    assert "terrorblade" in knowledge2.lower(), "❌ No se encontró información de Terrorblade"
    assert "buff" in knowledge2.lower() or "sunder" in knowledge2.lower(), "❌ No se encontró información de buffs"
    print("✅ Test 2 PASADO: Información de Terrorblade detectada correctamente")
    
    # Test 3: Pregunta sobre items
    print("\n[TEST 3] Pregunta sobre items del patch...")
    query3 = "¿Qué items fueron nerfeados en 7.40c?"
    knowledge3 = get_relevant_knowledge(query3, debug=True)
    
    assert "phylactery" in knowledge3.lower(), "❌ No se encontró información de Phylactery"
    assert "7.40" in knowledge3 or "740" in knowledge3, "❌ No se detectó el patch 7.40c"
    print("✅ Test 3 PASADO: Información de items del patch detectada correctamente")
    
    # Test 4: Pregunta sobre Largo (nuevo en Captain's Mode)
    print("\n[TEST 4] Pregunta sobre Largo...")
    query4 = "¿Largo está en Captain's Mode?"
    knowledge4 = get_relevant_knowledge(query4, debug=True)
    
    assert "largo" in knowledge4.lower(), "❌ No se encontró información de Largo"
    assert "captain" in knowledge4.lower() or "ranked" in knowledge4.lower(), "❌ No se encontró información de Captain's Mode"
    print("✅ Test 4 PASADO: Información de Largo detectada correctamente")
    
    # Test 5: Verificar que los diccionarios están cargados
    print("\n[TEST 5] Verificando diccionarios de patch...")
    assert len(PATCH_740C_NERFS) > 0, "❌ PATCH_740C_NERFS está vacío"
    assert len(PATCH_740C_BUFFS) > 0, "❌ PATCH_740C_BUFFS está vacío"
    assert "clinkz" in PATCH_740C_NERFS, "❌ Clinkz no está en PATCH_740C_NERFS"
    assert "terrorblade" in PATCH_740C_BUFFS, "❌ Terrorblade no está en PATCH_740C_BUFFS"
    print("✅ Test 5 PASADO: Diccionarios de patch cargados correctamente")
    
    print("\n" + "=" * 60)
    print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("=" * 60)
    print("\nEl sistema RAG está correctamente configurado para el patch 7.40c")
    print("El coach ahora tiene conocimiento actualizado del meta actual.")

if __name__ == "__main__":
    try:
        test_patch_740c_knowledge()
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
