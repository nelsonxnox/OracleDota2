import asyncio
import json
import os
import sys
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from http.server import BaseHTTPRequestHandler, HTTPServer
import pyttsx3
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import winreg
import json
import os
import sys
import websockets
from concurrent.futures import ThreadPoolExecutor

# Configuration
BACKEND_HOST = os.getenv("ORACLE_BACKEND_HOST", "localhost:8000")
BACKEND_WS_URL = f"ws://{BACKEND_HOST}/ws/live"
GSI_PORT = 3000
VOSK_MODEL_PATH = "vosk-model-small-es-0.42"

# Global State
current_token = "asd"
status_message = "Desconectado"
last_advice = "Esperando partida..."
loop = None

# Offline Audio Engine Init
tts_engine = None

# Vosk Model Init
model = None
if os.path.exists(VOSK_MODEL_PATH):
    try:
        model = Model(VOSK_MODEL_PATH)
        print(f"[VOSK] Modelo cargado: {VOSK_MODEL_PATH}")
    except Exception as e:
        print(f"[VOSK] Error cargando modelo: {e}")
else:
    print(f"[VOSK] ALERTA: No se encontró la carpeta '{VOSK_MODEL_PATH}'")
    print("Por favor ejecuta 'python setup_vosk.py' o descárgalo manualmente.")

# State Cache for Throttling
last_sent_state = {}
last_sent_time = 0
HEARTBEAT_INTERVAL = 10.0 # Send full data every 10s regardless

# --- GSI SERVER (Local) ---
class GSIDataHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Silence logs

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            # Forward to Async Loop using a thread-safe call
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(bridge.handle_gsi(data), loop)
                
            self.send_response(200)
        except Exception as e:
            print(f"GSI Error: {e}")
            self.send_response(500)
            
        self.end_headers()

def run_gsi_server():
    server = HTTPServer(('localhost', GSI_PORT), GSIDataHandler)
    print(f"[BRIDGE] GSI Server listening on port {GSI_PORT}")
    server.serve_forever()

# --- AUDIO PLAYER ---
# --- AUDIO PLAYER (OFFLINE) ---
def play_audio_thread(text: str):
    try:
        # Initialize engine per thread to ensure safety
        engine = pyttsx3.init()
        
        # Configure Voice (Spanish)
        voices = engine.getProperty('voices')
        for v in voices:
            if "spanish" in v.name.lower() or "es-" in v.id.lower():
                engine.setProperty('voice', v.id)
                break
        
        engine.setProperty('rate', 160)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Error: {e}")

async def play_audio(text: str):
    print(f"[AUDIO] Saying: {text}")
    threading.Thread(target=play_audio_thread, args=(text,)).start()

# --- BRIDGE LOGIC ---
class OracleBridge:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.mic_active = False

    async def send_question(self, text: str):
        if self.connected and self.ws:
            payload = {"type": "question", "text": text}
            await self.ws.send(json.dumps(payload))
            print(f"[BRIDGE] Question sent: {text}")

    def listen_mic(self):
        """Offline Speech Recognition using Vosk + SoundDevice"""
        if not model:
            print("[MIC] Error: Modelo Vosk no cargado")
            return "Error: Modelo no encontrado"

        print("[MIC] Listening... (Vosk Offline)")
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        try:
            # Vosk expects 16kHz mono 16-bit PCM
            with sd.RawInputStream(samplerate=16000, blocksize=4000, device=None,
                                   dtype='int16', channels=1, callback=callback):
                
                rec = KaldiRecognizer(model, 16000)
                start_time = time.time()
                text_result = None

                # Listen for up to 5 seconds
                while time.time() - start_time < 5:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        if res.get('text'):
                            text_result = res['text']
                            break
                
                if not text_result:
                    res = json.loads(rec.FinalResult())
                    text_result = res.get('text', "")

                print(f"[MIC] Recognized: {text_result}")
                return text_result

        except Exception as e:
            print(f"[MIC] Error: {e}")
            return None


    async def connect(self):
        global status_message
        if not current_token:
            status_message = "Error: Falta Token"
            return

        status_message = f"Conectando a {BACKEND_WS_URL}..."
        try:
            url = f"{BACKEND_WS_URL}/{current_token}"
            async with websockets.connect(url) as websocket:
                self.ws = websocket
                self.connected = True
                status_message = "Conectado y Escuchando"
                print("[BRIDGE] Connected to Backend")
                
                # Listen for messages
                await self.listen()
        except Exception as e:
            status_message = f"Error Conexión: {str(e)[:20]}"
            self.connected = False
            print(f"[BRIDGE] Connection Failed: {e}")

    async def listen(self):
        try:
            while True:
                msg = await self.ws.recv()
                data = json.loads(msg)
                await self.process_backend_message(data)
        except websockets.ConnectionClosed:
            print("[BRIDGE] Connection Closed")
            self.connected = False

    async def handle_gsi(self, data: dict):
        global last_sent_state, last_sent_time
        
        if self.connected and self.ws:
            try:
                # THROTTLING / DIFFING LOGIC
                current_time = time.time()
                should_send = False
                
                # 1. Critical Events Check (Death, Health Drop, High Gold Change)
                hero = data.get("hero", {})
                player = data.get("player", {})
                
                # Check Death
                was_alive = last_sent_state.get("hero", {}).get("alive", True)
                is_alive = hero.get("alive", True)
                if was_alive != is_alive: should_send = True
                
                # Check Health Change > 5%
                last_hp = last_sent_state.get("hero", {}).get("health", 0)
                curr_hp = hero.get("health", 0)
                if abs(curr_hp - last_hp) > 50: should_send = True # Arbritrary 50hp change
                
                # Check Gold Change > 200
                last_gold = last_sent_state.get("player", {}).get("gold", 0)
                curr_gold = player.get("gold", 0)
                if abs(curr_gold - last_gold) > 200: should_send = True
                
                # 2. Heartbeat (Force send every X seconds)
                if (current_time - last_sent_time) > HEARTBEAT_INTERVAL:
                    should_send = True
                
                if should_send:
                    await self.ws.send(json.dumps(data))
                    last_sent_state = data
                    last_sent_time = current_time
                    # print("Sent GSI update") # Debug
                    
            except Exception as e:
                print(f"[BRIDGE] Send Error: {e}")

    async def process_backend_message(self, data: dict):
        global last_advice
        msg_type = data.get("type", "info")
        text = data.get("text", "")
        
        if text:
            last_advice = text
            # Play Audio Priority
            await play_audio(text)

bridge = OracleBridge()

# --- STEAM / GSI CONFIG ---
def install_gsi():
    # Try to find Dota 2 path from Registry
    dota_path = None
    try:
        ts = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam")
        steam_path, _ = winreg.QueryValueEx(ts, "SteamPath")
        
        # Check libraryfolders.vdf or default paths
        possible_paths = [
            f"{steam_path}/steamapps/common/dota 2 beta",
            r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta",
            r"D:\SteamLibrary\steamapps\common\dota 2 beta"
        ]
        
        for p in possible_paths:
            if os.path.exists(p):
                dota_path = p
                break
    except:
        pass

    if not dota_path:
        dota_path = filedialog.askdirectory(title="Selecciona la carpeta 'dota 2 beta'")

    if dota_path:
        cfg_path = os.path.join(dota_path, "game", "dota", "cfg", "gamestate_integration")
        os.makedirs(cfg_path, exist_ok=True)
        
        gsi_file = os.path.join(cfg_path, "gamestate_integration_oracle.cfg")
        content = """
"Oracle Live Coach"
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
    }
}
"""
        with open(gsi_file, "w") as f:
            f.write(content)
        messagebox.showinfo("Éxito", f"Configuración GSI instalada en: {gsi_file}")
    else:
        messagebox.showerror("Error", "No se encontró la carpeta de Dota 2.")

# --- UI (Tkinter embedded in async loop) ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Oracle Neural Link")
        self.geometry("400x300")
        self.config(bg="#1a1a1a")
        self.running = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        lbl_title = tk.Label(self, text="ORACLE NEURAL LINK", font=("Arial", 16, "bold"), bg="#1a1a1a", fg="#00ffcc")
        lbl_title.pack(pady=10)
        
        # Token Input
        lbl_token = tk.Label(self, text="Access Key (Token):", bg="#1a1a1a", fg="white")
        lbl_token.pack()
        
        self.entry_token = tk.Entry(self, width=40)
        self.entry_token.pack(pady=5)
        
        btn_connect = tk.Button(self, text="ACTIVAR ENLACE", command=self.start_connection, bg="#00ffcc", fg="black", font=("Arial", 10, "bold"))
        btn_connect.pack(pady=10)
        
        # Status
        self.lbl_status = tk.Label(self, text=status_message, bg="#1a1a1a", fg="gray", font=("Consolas", 10))
        self.lbl_status.pack(pady=5)
        
        # Last Advice
        frame_advice = tk.Frame(self, bg="#2a2a2a", bd=1, relief="sunken")
        frame_advice.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.lbl_advice = tk.Label(frame_advice, text=last_advice, bg="#2a2a2a", fg="#00ffcc", wraplength=350, justify="center")
        self.lbl_advice.pack(pady=20)

        # Footer
        btn_gsi = tk.Button(self, text="Instalar GSI Config", command=install_gsi, bg="#333", fg="white", font=("Arial", 8))
        btn_gsi.pack(side="bottom", pady=5)
        
        # Mic Button
        self.btn_mic = tk.Button(self, text="🎙️ PREGUNTAR AL COACH", command=self.toggle_mic, bg="#ff9900", fg="black", font=("Arial", 12, "bold"))
        self.btn_mic.pack(pady=10)

    def toggle_mic(self):
        # Disable button while listening
        self.btn_mic.config(state="disabled", text="👂 Escuchando...", bg="#ffcc00")
        
        # Run listening in thread
        threading.Thread(target=self._mic_thread_handler).start()

    def _mic_thread_handler(self):
        text = bridge.listen_mic()
        
        # Update UI back in main thread
        self.after(0, lambda: self.finish_mic(text))

    def finish_mic(self, text):
        self.btn_mic.config(state="normal", text="🎙️ PREGUNTAR AL COACH", bg="#ff9900")
        if text:
            # Send to backend
            asyncio.run_coroutine_threadsafe(bridge.send_question(text), loop)
            # Update UI
            self.lbl_advice.config(text=f"Tú: {text}") 

    def start_connection(self):
        global current_token
        current_token = self.entry_token.get().strip()
        if not current_token:
            messagebox.showwarning("Alerta", "Ingresa tu Access Key")
            return
        
        # Start async connection task
        asyncio.create_task(bridge.connect())

    def on_closing(self):
        self.running = False
        self.destroy()

    def update_gui(self):
        if not self.running: return
        try:
            self.lbl_status.config(text=status_message)
            self.lbl_status.config(fg="#00ffcc" if "Conectado" in status_message else "red")
            self.lbl_advice.config(text=last_advice)
            self.update()
        except tk.TclError:
            self.running = False

async def main():
    global loop
    loop = asyncio.get_running_loop()
    
    # Start GSI Server in Thread
    gsi_thread = threading.Thread(target=run_gsi_server, daemon=True)
    gsi_thread.start()
    
    # Init UI
    app = App()
    
    # Main Loop
    while app.running:
        try:
            app.update_gui()
            await asyncio.sleep(0.05)
        except:
            break
    
    print("[BRIDGE] Bridge Closed.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
