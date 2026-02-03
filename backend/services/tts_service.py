
import edge_tts
import tempfile
import os

# Voice selection
# "es-ES-XimenaNeural" -> Joven, enérgica y natural (España)
# "es-MX-DaliaNeural" -> Joven y muy natural (México)
# "es-ES-AlvaroNeural" -> Masculino, más "adulto"
VOICE = "es-ES-XimenaNeural"

async def generate_audio_stream(text: str) -> bytes:
    """
    Generates audio in memory using edge-tts and returns bytes.
    Avoids writing to disk for speed.
    """
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

async def generate_audio_file(text: str) -> str:
    """
    Generates audio to a temporary file and returns path.
    Useful if streaming fails or for debugging.
    """
    communicate = edge_tts.Communicate(text, VOICE)
    
    # Create temp file
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    
    await communicate.save(path)
    return path
