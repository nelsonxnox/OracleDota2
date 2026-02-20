import asyncio
import json
import os
import sys
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk # Requires: pip install Pillow
from http.server import BaseHTTPRequestHandler, HTTPServer
import pyttsx3
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import winreg
import websockets
import keyboard
from concurrent.futures import ThreadPoolExecutor

# Configuration
CURRENT_VERSION = "1.3.1"  
LOCAL_MODE = True # PRODUCTION DEFAULT: Set to False for official release
BACKEND_HOST = "localhost:8000" if LOCAL_MODE else os.getenv("ORACLE_BACKEND_HOST", "oracledota2.onrender.com")
BACKEND_HTTP_PROTOCOL = "http" if LOCAL_MODE else "https"
BACKEND_WS_PROTOCOL = "ws" if LOCAL_MODE else "wss"
BACKEND_API_URL = f"{BACKEND_HTTP_PROTOCOL}://{BACKEND_HOST}"
BACKEND_WS_URL = f"{BACKEND_WS_PROTOCOL}://{BACKEND_HOST}/ws/live"
UPDATE_CHECK_URL = f"{BACKEND_API_URL}/api/version"
GSI_PORT = 3000
VOSK_MODEL_PATH = "vosk-model-small-es-0.42"
CONFIG_FILE = "oracle_config.json"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Global State
current_token = None  # Load from config file
status_message = "Desconectado"
last_advice = "Esperando partida..."
last_gsi_time = 0
loop = None
app = None # Reference to UI

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
HEARTBEAT_INTERVAL = 3.0 # Send full data every 3s to ensure backend hits timing windows

# --- GSI SERVER (Local) ---
class GSIDataHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Silence logs

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            # print(f"[GSI] Received data: {data.keys()}") # Verbose debug
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
        print(f"[AUDIO] Error playing audio: {e}")

def play_audio(text: str):
    threading.Thread(target=play_audio_thread, args=(text,), daemon=True).start()

# --- AUTO-UPDATE FUNCTIONS ---
def check_for_updates():
    """Verifica si hay una nueva versión disponible"""
    try:
        import requests
        response = requests.get(UPDATE_CHECK_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("version", "0.0.0")
            
            # Compare versions (simple string comparison works for semantic versioning)
            if latest_version > CURRENT_VERSION:
                return {
                    "update_available": True,
                    "version": latest_version,
                    "download_url": data.get("download_url"),
                    "changelog": data.get("changelog", "")
                }
        return {"update_available": False}
    except Exception as e:
        print(f"[UPDATE] Error checking for updates: {e}")
        return {"update_available": False, "error": str(e)}

def download_and_install_update(download_url):
    """Descarga e instala la actualización"""
    try:
        import requests
        import subprocess
        
        # 1. Descargar nuevo ejecutable
        print(f"[UPDATE] Downloading from {download_url}")
        response = requests.get(download_url, stream=True)
        temp_file = "OracleNeuralLink_new.exe"
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                    print(f"[UPDATE] Progress: {progress:.1f}%")
        
        print(f"[UPDATE] Download complete: {temp_file}")
        
        # 2. Crear script de actualización
        update_script = '''@echo off
timeout /t 2 /nobreak > nul
del "OracleNeuralLink.exe"
ren "OracleNeuralLink_new.exe" "OracleNeuralLink.exe"
start "" "OracleNeuralLink.exe"
del "%~f0"
'''
        with open("update.bat", "w") as f:
            f.write(update_script)
        
        print("[UPDATE] Executing update script...")
        
        # 3. Ejecutar script y cerrar aplicación
        subprocess.Popen(["update.bat"], shell=True)
        sys.exit(0)
        
    except Exception as e:
        messagebox.showerror("Error de Actualización", f"Error al actualizar: {e}")
        print(f"[UPDATE] Error: {e}")

# --- BRIDGE LOGIC ---
class OracleBridge:
    def __init__(self):
        self.ws = None
        self.listening = False
        self.mic_queue = queue.Queue()
        self.recognizer = KaldiRecognizer(model, 16000) if model else None

    async def connect(self):
        global status_message
        status_message = "Conectando al servidor..."
        update_ui_status(status_message, "yellow")
        
        while True:
            try:
                # WebSocket URL must include token in path: /ws/live/{token}
                # And remove duplicate slash if BACKEND_WS_URL ends with one
                base_url = BACKEND_WS_URL.rstrip('/')
                ws_url_with_token = f"{base_url}/{current_token}"
                print(f"[WS] Connecting to: {ws_url_with_token}")
                
                async with websockets.connect(ws_url_with_token) as ws:
                    self.ws = ws
                    status_message = "Conectado a Oracle"
                    update_ui_status(status_message, "#00ffcc")
                    print("[WS] Connected!")
                    
                    # Handle Incoming Messages
                    async for msg in ws:
                        data = json.loads(msg)
                        self.handle_message(data)
                        
            except Exception as e:
                status_message = f"Desconectado: {e}"
                update_ui_status(status_message, "red")
                print(f"[WS] Connection Error: {e}")
                await asyncio.sleep(5) # Retry in 5s

    async def handle_gsi(self, data: dict):
        global last_gsi_time, last_sent_time
        last_gsi_time = time.time()
        
        # Update UI: GSI is active
        update_ui_gsi("GSI: Activo", "#00ffcc")
        
        # Throttle logic: Only send if changed or HEARBEAT_INTERVAL passed
        # Simplification: Just send every HEARTBEAT_INTERVAL for now to avoid complexity
        if time.time() - last_sent_time < HEARTBEAT_INTERVAL:
             return

        if self.ws:
            try:
                payload = {
                    "type": "gsi_event",
                    "data": data
                }
                await self.ws.send(json.dumps(payload))
                last_sent_time = time.time()
            except Exception as e:
                print(f"[WS] Send Error: {e}")

    def handle_message(self, message: dict):
        global last_advice
        msg_type = message.get("type")
        
        if msg_type == "advice":
            text = message.get("text", "")
            print(f"[WS] Advice received: {text}")
            last_advice = text
            update_ui_chat("Oracle", text, "oracle") # Show in chat
            play_audio(text)
            
        elif msg_type == "warning":
            text = message.get("text", "")
            print(f"[WS] WARNING: {text}")
            update_ui_chat("Oracle", f"⚠️ {text}", "oracle")
            play_audio(text)
            
        elif msg_type == "answer":
            text = message.get("text", "")
            update_ui_chat("Oracle", text, "oracle")
            play_audio(text)
            
        elif msg_type == "pong":
            print("[WS] Pong received")

    async def send_question(self, text: str):
        if self.ws:
            try:
                payload = {"type": "question", "text": text}
                await self.ws.send(json.dumps(payload))
            except Exception as e:
                print(f"[WS] Send Error: {e}")

    def start_listening(self):
        self.listening = True
        
    def stop_listening(self):
        self.listening = False

    def listen_mic(self):
        """Records from mic until silence or manually stopped."""
        if not model or not self.recognizer: 
            print("[MIC] Error: Modelo Vosk no cargado.")
            return None
        
        print("[MIC] Listening...")
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=self._audio_callback):
            while self.listening:
                try:
                    data = self.mic_queue.get(timeout=1.0)
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "")
                        if text:
                            print(f"[MIC] Heard: {text}")
                            self.listening = False # Auto-stop after one sentence
                            return text
                except queue.Empty:
                    continue
        return None

    def _audio_callback(self, indata, frames, time, status):
        if status: print(status, file=sys.stderr)
        self.mic_queue.put(bytes(indata))

    def setup_hotkey(self, callback):
        keyboard.add_hotkey('ctrl', callback)

bridge = OracleBridge()

def run_async_loop():
    asyncio.run(bridge.connect())

# --- INSTALLATION HELPERS ---
def install_gsi():
    dota_path = r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration"
    if not os.path.exists(dota_path):
        try:
            os.makedirs(dota_path)
        except OSError:
            # Try to find user path?
            pass

    if os.path.exists(dota_path):
        gsi_file = os.path.join(dota_path, "gamestate_integration_oracle.cfg")
        content = """
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
"""
        with open(gsi_file, "w") as f:
            f.write(content)
        messagebox.showinfo("Éxito", f"Configuración GSI instalada en: {gsi_file}")
    else:
        messagebox.showerror("Error", "No se encontró la carpeta de Dota 2.")

# --- UI (Modern Dota 2 Theme) ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Oracle Neural Link - Dota 2 Coach")
        self.geometry("900x650") # Larger window for chat
        self.config(bg="#121212")
        self.ui_queue = queue.Queue()
        self.running = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load Assets
        self.assets = {}
        self.load_assets()
        
        # Set Icon
        if self.assets.get("icon"):
            try:
                self.iconphoto(False, self.assets["icon"])
            except: pass
            
        # Background Image (Canvas)
        self.canvas = tk.Canvas(self, width=900, height=650, highlightthickness=0, bg="#121212")
        self.canvas.pack(fill="both", expand=True)
        
        if self.assets.get("bg"):
            self.bg_image_ref = self.assets["bg"] # Keep reference
            self.canvas.create_image(0, 0, image=self.bg_image_ref, anchor="nw")
            
        # --- UI LAYOUT (Placed on Canvas) ---
        
        # 1. Header Area
        header_frame = tk.Frame(self.canvas, bg="#000000", bd=0)
        # Using canvas.create_window to place widgets on top of image
        self.canvas.create_window(450, 40, window=header_frame, anchor="center", width=880)
        
        lbl_title = tk.Label(header_frame, text="ORACLE NEURAL LINK", font=("Trajan Pro", 24, "bold"), bg="#000000", fg="#ff4b4b")
        lbl_title.pack(pady=5)
        
        # 2. Main Content Area (Left: Controls, Right: Chat)
        content_frame = tk.Frame(self.canvas, bg="#121212") # Fallback bg
        # Make transparent if possible (Tkinter doesn't support true transparency easily, so we use a dark frame)
        self.canvas.create_window(450, 350, window=content_frame, anchor="center", width=880, height=550)
        
        # Left Panel (Controls)
        left_panel = tk.Frame(content_frame, bg="#1e1e1e", bd=2, relief="ridge")
        left_panel.place(x=0, y=0, width=300, height=550)
        
        # Controls Content
        tk.Label(left_panel, text="CONTROL DE ENLACE", font=("Arial", 12, "bold"), bg="#1e1e1e", fg="#aaaaaa").pack(pady=10)
        
        self.lbl_status = tk.Label(left_panel, text=status_message, bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 10))
        self.lbl_status.pack(pady=5)
        
        # Token Input
        tk.Label(left_panel, text="Access Token:", bg="#1e1e1e", fg="gray").pack(pady=(10,0))
        self.entry_token = tk.Entry(left_panel, width=35, bg="#333", fg="white", insertbackground="white")
        self.entry_token.pack(pady=5)
        
        btn_connect = tk.Button(left_panel, text="ACTIVAR ENLACE", command=self.start_connection, 
                                bg="#ff4b4b", fg="white", font=("Arial", 11, "bold"), activebackground="#ff6b6b", activeforeground="white", relief="flat")
        btn_connect.pack(pady=10, fill="x", padx=20)
        
        # GSI Controls
        tk.Label(left_panel, text="GAME STATE INTEGRATION", font=("Arial", 10, "bold"), bg="#1e1e1e", fg="#aaaaaa").pack(pady=(20, 10))
        
        # GSI Status
        self.lbl_gsi = tk.Label(left_panel, text="GSI: Inactivo", bg="#1e1e1e", fg="#555", font=("Arial", 8))
        self.lbl_gsi.pack(pady=2)

        btn_install = tk.Button(left_panel, text="Instalar GSI Config", command=install_gsi, 
                                bg="#2d5986", fg="white", font=("Arial", 9), activebackground="#3d6996", relief="flat")
        btn_install.pack(pady=5, fill="x", padx=20)
        
        btn_uninstall = tk.Button(left_panel, text="Desinstalar GSI", command=self.uninstall_gsi, 
                                  bg="#444", fg="#ffaaaa", font=("Arial", 9), activebackground="#555", relief="flat")
        btn_uninstall.pack(pady=5, fill="x", padx=20)
        
        # Update Button
        tk.Label(left_panel, text="ACTUALIZACIÓN", font=("Arial", 10, "bold"), bg="#1e1e1e", fg="#aaaaaa").pack(pady=(20, 10))
        
        btn_update = tk.Button(left_panel, text="🔄 Buscar Actualizaciones", command=self.handle_update_click, 
                              bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), activebackground="#66BB6A", relief="flat")
        btn_update.pack(pady=5, fill="x", padx=20)
        
        # Version Label
        version_label = tk.Label(left_panel, text=f"Versión: {CURRENT_VERSION}", bg="#1e1e1e", fg="#666", font=("Arial", 8))
        version_label.pack(pady=5)
        
        # Status Label
        self.lbl_status = tk.Label(left_panel, text="Sistema en espera", bg="#1e1e1e", fg="gray", font=("Consolas", 10))
        self.lbl_status.place(relx=0.5, rely=0.9, anchor="center")

        # Right Panel (Coach Message Display)
        right_panel = tk.Frame(content_frame, bg="#121212", bd=2, relief="ridge")
        right_panel.place(x=320, y=0, width=560, height=550)
        
        # Chat Header
        chat_header = tk.Label(right_panel, text="CONSEJOS DEL ORÁCULO", font=("Arial", 11, "bold"), bg="#121212", fg="#00ffcc")
        chat_header.pack(pady=5)
        
        # Chat History - Expanded to fill frame
        self.chat_history = scrolledtext.ScrolledText(right_panel, bg="#0d0d0d", fg="#cccccc", font=("Segoe UI", 10), state="disabled", wrap="word")
        self.chat_history.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_history.tag_config("user", foreground="#00ffcc")
        self.chat_history.tag_config("oracle", foreground="#ff9900", font=("Segoe UI", 10, "bold"))
        self.chat_history.tag_config("system", foreground="gray", font=("Consolas", 9, "italic"))

        # Load saved token
        self.load_token()
        
        # Update Loop
        self.check_queue()

    def load_assets(self):
        """Loads images using Pillow."""
        try:
            # 1. Background (Try multiple locations)
            # When compiled as EXE, we bundle assets in 'assets/'
            bg_locations = [
                resource_path("dota2_oracle_bg.png"),
                resource_path("assets/dota2_oracle_bg.png"),
                os.path.join("..", "frontend", "public", "dota2_oracle_bg.png")
            ]
            
            for path in bg_locations:
                if os.path.exists(path):
                    pil_img = Image.open(path).convert("RGBA")
                    pil_img = pil_img.resize((900, 650), Image.Resampling.LANCZOS)
                    self.assets["bg"] = ImageTk.PhotoImage(pil_img)
                    print(f"[UI] BG loaded from {path}")
                    break

            # 2. Icon
            icon_locations = [
                resource_path("logo.png"),
                resource_path("assets/logo.png"),
                os.path.join("..", "frontend", "public", "logo.png")
            ]
            for path in icon_locations:
                if os.path.exists(path):
                    icon_img = Image.open(path)
                    self.assets["icon"] = ImageTk.PhotoImage(icon_img)
                    break
        except Exception as e:
            print(f"[UI] Asset Load Error: {e}")

    def append_chat(self, sender: str, text: str, tag: str):
        self.chat_history.config(state="normal")
        self.chat_history.insert("end", f"{sender}: ", tag)
        self.chat_history.insert("end", f"{text}\n\n")
        self.chat_history.see("end")
        self.chat_history.config(state="disabled")

    def uninstall_gsi(self):
        dota_path = r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration"
        gsi_file = os.path.join(dota_path, "gamestate_integration_oracle.cfg")
        if os.path.exists(gsi_file):
            try:
                os.remove(gsi_file)
                messagebox.showinfo("Desinstalado", "Configuración GSI eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        else:
            messagebox.showinfo("Info", "No se encontró configuración GSI instalada.")

    def handle_hotkey(self):
        """Callback for the 'keyboard' library hotkey"""
        self.ui_queue.put(self.toggle_mic)

    def load_token(self):
        """Load saved token from config file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    saved_token = data.get("token", "")
                    if saved_token:
                        self.entry_token.insert(0, saved_token)
                        print(f"[CONFIG] Token loaded from {CONFIG_FILE}")
        except Exception as e:
            print(f"[CONFIG] Error loading token: {e}")
    
    def handle_update_click(self):
        """Maneja el clic en el botón de actualización"""
        print("[UPDATE] Checking for updates...")
        update_info = check_for_updates()
        
        if update_info.get("error"):
            messagebox.showerror("Error", f"No se pudo verificar actualizaciones:\n{update_info['error']}")
            return
        
        if update_info.get("update_available"):
            message = f"🎉 Nueva versión disponible: {update_info['version']}\n\n"
            message += f"Versión actual: {CURRENT_VERSION}\n\n"
            message += f"Cambios:\n{update_info['changelog']}\n\n"
            message += "¿Deseas actualizar ahora? La aplicación se reiniciará."
            
            if messagebox.askyesno("Actualización Disponible", message):
                self.lbl_status.config(text="Descargando actualización...", fg="yellow")
                self.update()  # Force UI update
                download_and_install_update(update_info['download_url'])
        else:
            messagebox.showinfo("Sin Actualizaciones", f"Ya tienes la última versión instalada.\n\nVersión actual: {CURRENT_VERSION}")

    def start_connection(self):
        global current_token
        token = self.entry_token.get().strip()
        if not token:
            messagebox.showwarning("Falta Token", "Por favor ingresa tu token de acceso.")
            return
            
        current_token = token
        
        # Save token
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"token": token}, f)
        except: pass
        
        self.lbl_status.config(text="Conectando...", fg="yellow")
        
        # Start Bridge logic in thread
        threading.Thread(target=run_async_loop, daemon=True).start()

    def check_queue(self):
        """Process requests from other threads"""
        try:
            while True:
                task = self.ui_queue.get_nowait()
                if callable(task):
                    task()
                elif isinstance(task, tuple) and task[0] == "update_status":
                     # ("update_status", message, color)
                     self.lbl_status.config(text=task[1], fg=task[2])
                elif isinstance(task, tuple) and task[0] == "update_gsi":
                     # ("update_gsi", message, color)
                     self.lbl_gsi.config(text=task[1], fg=task[2])
                elif isinstance(task, tuple) and task[0] == "chat_msg":
                     # ("chat_msg", sender, text, tag)
                     self.append_chat(task[1], task[2], task[3])
                     
        except (tk.TclError, RuntimeError):
            # Safe ignore if UI is closing or already destroyed
            pass
        except Exception as e:
            print(f"[UI] Queue Error: {e}")
        
        if self.running:
            try:
                self.after(100, self.check_queue)
            except:
                pass

    def on_closing(self):
        self.running = False
        self.destroy()
        sys.exit(0)

    def update_gui(self):
        # Deprecated: Now using check_queue
        pass

# Override Bridge methods to update UI
def update_ui_status(msg, color="white"):
    if app:
        app.ui_queue.put(("update_status", msg, color))

def update_ui_chat(sender, text, tag):
    if app:
        app.ui_queue.put(("chat_msg", sender, text, tag))

def update_ui_gsi(msg, color="white"):
    if app:
        app.ui_queue.put(("update_gsi", msg, color))

async def main():
    global loop, app
    loop = asyncio.get_running_loop()
    
    # Start GSI Server in Thread
    gsi_thread = threading.Thread(target=run_gsi_server, daemon=True)
    gsi_thread.start()
    
    # Init UI
    app = App()
    
    # Main Loop (Tkinter mainloop must run on main thread)
    # But asyncio.run blocks.
    # We need to run Tkinter loop here, and run asyncio in a separate thread?
    # NO. Tkinter MUST run on the main thread.
    # The current architecture:
    # asyncio.run(main()) -> await asyncio.sleep() loop
    # inside loop: app.update()
    
    # Let's keep the existing loop logic but use the Queue properly
    while app and app.running:
        try:
            app.update() # Process Tkinter events
            await asyncio.sleep(0.01)
        except (tk.TclError, RuntimeError):
            # Window was likely closed
            if app: app.running = False
            break
        except Exception as e:
            print(f"[UI] Loop Error: {e}")
            break
    
    print("[BRIDGE] Bridge Closed.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
