import asyncio
import json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
from http.server import BaseHTTPRequestHandler, HTTPServer
import pyttsx3
import websockets
import queue

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
CURRENT_VERSION = "1.3.2"
LOCAL_MODE = False  # PRODUCCIÓN: conecta al backend de Render
BACKEND_HOST         = "localhost:8000" if LOCAL_MODE else os.getenv("ORACLE_BACKEND_HOST", "oracledota2.onrender.com")
BACKEND_HTTP_PROTOCOL = "http"  if LOCAL_MODE else "https"
BACKEND_WS_PROTOCOL   = "ws"   if LOCAL_MODE else "wss"
BACKEND_API_URL  = f"{BACKEND_HTTP_PROTOCOL}://{BACKEND_HOST}"
BACKEND_WS_URL   = f"{BACKEND_WS_PROTOCOL}://{BACKEND_HOST}/ws/live"
UPDATE_CHECK_URL = f"{BACKEND_API_URL}/api/version"
GSI_PORT         = 3000

# ── RUTAS CORRECTAS PARA EL EJECUTABLE ──────────────────────────────────────
def resource_path(relative_path: str) -> str:
    """Ruta absoluta al recurso — funciona en .py y en .exe compilado."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_config_path() -> str:
    """Ruta al config en AppData del usuario (siempre escribible)."""
    app_data  = os.getenv("APPDATA", os.path.expanduser("~"))
    config_dir = os.path.join(app_data, "OracleNeuralLink")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "oracle_config.json")

CONFIG_FILE = get_config_path()

# ─── GLOBAL STATE ─────────────────────────────────────────────────────────────
current_token  = None
status_message = "Desconectado"
last_gsi_time  = 0
loop           = None
app            = None

# ─── THROTTLE STATE ───────────────────────────────────────────────────────────
last_sent_time     = 0
HEARTBEAT_INTERVAL = 3.0

# ─── GSI SERVER (recibe datos de Dota 2) ─────────────────────────────────────
class GSIDataHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar logs HTTP

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(bridge.handle_gsi(data), loop)
            self.send_response(200)
        except Exception as e:
            print(f"[GSI] Error: {e}")
            self.send_response(500)
        self.end_headers()

def run_gsi_server():
    server = HTTPServer(("localhost", GSI_PORT), GSIDataHandler)
    print(f"[BRIDGE] GSI Server escuchando en puerto {GSI_PORT}")
    server.serve_forever()

# ─── AUDIO (TTS solo texto → voz para consejos) ─────────────────────────────
def play_audio_thread(text: str):
    try:
        engine = pyttsx3.init()
        for v in engine.getProperty("voices"):
            if "spanish" in v.name.lower() or "es-" in v.id.lower():
                engine.setProperty("voice", v.id)
                break
        engine.setProperty("rate", 160)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[AUDIO] Error TTS: {e}")

def play_audio(text: str):
    threading.Thread(target=play_audio_thread, args=(text,), daemon=True).start()

# ─── AUTO-UPDATE ──────────────────────────────────────────────────────────────
def check_for_updates() -> dict:
    try:
        import requests
        r = requests.get(UPDATE_CHECK_URL, timeout=5)
        if r.status_code == 200:
            data    = r.json()
            latest  = data.get("version", "0.0.0")
            if latest > CURRENT_VERSION:
                return {
                    "update_available": True,
                    "version":      latest,
                    "download_url": data.get("download_url"),
                    "changelog":    data.get("changelog", ""),
                }
        return {"update_available": False}
    except Exception as e:
        return {"update_available": False, "error": str(e)}

def download_and_install_update(download_url: str):
    try:
        import requests, subprocess
        print(f"[UPDATE] Descargando desde {download_url}")
        r          = requests.get(download_url, stream=True)
        total_size = int(r.headers.get("content-length", 0))
        downloaded = 0
        tmp        = "OracleNeuralLink_new.exe"
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    pct = (downloaded / total_size * 100) if total_size else 0
                    print(f"[UPDATE] {pct:.1f}%")
        script = (
            "@echo off\n"
            "timeout /t 2 /nobreak >nul\n"
            'del "OracleNeuralLink.exe"\n'
            'ren "OracleNeuralLink_new.exe" "OracleNeuralLink.exe"\n'
            'start "" "OracleNeuralLink.exe"\n'
            'del "%~f0"\n'
        )
        with open("update.bat", "w") as f:
            f.write(script)
        subprocess.Popen(["update.bat"], shell=True)
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Error de Actualización", f"Error al actualizar: {e}")

# ─── BRIDGE LOGIC ─────────────────────────────────────────────────────────────
class OracleBridge:
    def __init__(self):
        self.ws = None

    async def connect(self):
        global status_message
        while True:
            try:
                base_url         = BACKEND_WS_URL.rstrip("/")
                ws_url = f"{base_url}/{current_token}"
                print(f"[WS] Conectando a: {ws_url}")
                status_message = "Conectando al servidor..."
                update_ui_status(status_message, "yellow")

                async with websockets.connect(ws_url) as ws:
                    self.ws        = ws
                    status_message = "Conectado a Oracle ✓"
                    update_ui_status(status_message, "#00ffcc")
                    print("[WS] ¡Conectado!")

                    async for msg in ws:
                        data = json.loads(msg)
                        self.handle_message(data)

            except Exception as e:
                status_message = f"Desconectado: {e}"
                update_ui_status(status_message, "red")
                print(f"[WS] Error de conexión: {e}")
                await asyncio.sleep(5)

    async def handle_gsi(self, data: dict):
        global last_gsi_time, last_sent_time
        last_gsi_time = time.time()
        update_ui_gsi("GSI: Activo ✓", "#00ffcc")

        if time.time() - last_sent_time < HEARTBEAT_INTERVAL:
            return

        if self.ws:
            try:
                payload = {"type": "gsi_event", "data": data}
                await self.ws.send(json.dumps(payload))
                last_sent_time = time.time()
            except Exception as e:
                print(f"[WS] Error enviando GSI: {e}")

    def handle_message(self, message: dict):
        msg_type = message.get("type")
        if msg_type == "advice":
            text = message.get("text", "")
            update_ui_chat("Oracle", text, "oracle")
            play_audio(text)
        elif msg_type == "warning":
            text = message.get("text", "")
            update_ui_chat("Oracle", f"⚠️ {text}", "oracle")
            play_audio(text)
        elif msg_type == "answer":
            text = message.get("text", "")
            update_ui_chat("Oracle", text, "oracle")
            play_audio(text)
        elif msg_type == "pong":
            print("[WS] Pong")

    async def send_question(self, text: str):
        if self.ws:
            try:
                await self.ws.send(json.dumps({"type": "question", "text": text}))
            except Exception as e:
                print(f"[WS] Error enviando pregunta: {e}")

bridge = OracleBridge()

def run_async_loop():
    asyncio.run(bridge.connect())

# ─── GSI INSTALLATION HELPER ─────────────────────────────────────────────────
def install_gsi():
    dota_path = r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration"
    if not os.path.exists(dota_path):
        try:
            os.makedirs(dota_path)
        except OSError:
            pass

    if os.path.exists(dota_path):
        gsi_file = os.path.join(dota_path, "gamestate_integration_oracle.cfg")
        content = (
            '"Oracle Config"\n{\n'
            '    "uri"           "http://localhost:3000/"\n'
            '    "timeout"       "5.0"\n'
            '    "buffer"        "0.1"\n'
            '    "throttle"      "0.1"\n'
            '    "heartbeat"     "30.0"\n'
            '    "data"\n    {\n'
            '        "provider"      "1"\n'
            '        "map"           "1"\n'
            '        "player"        "1"\n'
            '        "hero"          "1"\n'
            '        "abilities"     "1"\n'
            '        "items"         "1"\n'
            '        "allplayers"    "1"\n'
            '    }\n}\n'
        )
        with open(gsi_file, "w") as f:
            f.write(content)
        messagebox.showinfo("Éxito", f"GSI instalado en:\n{gsi_file}")
    else:
        messagebox.showerror(
            "Error",
            "No se encontró la carpeta de Dota 2.\nVerifica que Steam esté instalado."
        )

# ─── UI ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Oracle Neural Link - Dota 2 Coach")
        self.geometry("900x650")
        self.config(bg="#121212")
        self.ui_queue = queue.Queue()
        self.running  = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.assets = {}
        self.load_assets()

        if self.assets.get("icon"):
            try:
                self.iconphoto(False, self.assets["icon"])
            except Exception:
                pass

        # ── CANVAS (background) ──
        self.canvas = tk.Canvas(self, width=900, height=650,
                                highlightthickness=0, bg="#121212")
        self.canvas.pack(fill="both", expand=True)

        if self.assets.get("bg"):
            self.bg_image_ref = self.assets["bg"]
            self.canvas.create_image(0, 0, image=self.bg_image_ref, anchor="nw")

        # ── HEADER ──
        header_frame = tk.Frame(self.canvas, bg="#000000")
        self.canvas.create_window(450, 40, window=header_frame,
                                  anchor="center", width=880)
        tk.Label(header_frame, text="ORACLE NEURAL LINK",
                 font=("Arial", 22, "bold"), bg="#000000", fg="#ff4b4b").pack(pady=5)

        # ── CONTENT FRAME ──
        content_frame = tk.Frame(self.canvas, bg="#121212")
        self.canvas.create_window(450, 350, window=content_frame,
                                  anchor="center", width=880, height=550)

        # ── LEFT PANEL (Controles) ──
        left_panel = tk.Frame(content_frame, bg="#1e1e1e", bd=2, relief="ridge")
        left_panel.place(x=0, y=0, width=300, height=550)

        tk.Label(left_panel, text="CONTROL DE ENLACE",
                 font=("Arial", 12, "bold"), bg="#1e1e1e", fg="#aaaaaa").pack(pady=10)

        self.lbl_status = tk.Label(left_panel, text=status_message,
                                   bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 10))
        self.lbl_status.pack(pady=5)

        # Token
        tk.Label(left_panel, text="Access Token:", bg="#1e1e1e", fg="gray").pack(pady=(10, 0))
        self.entry_token = tk.Entry(left_panel, width=35, bg="#333",
                                    fg="white", insertbackground="white")
        self.entry_token.pack(pady=5)

        tk.Button(left_panel, text="⚡ ACTIVAR ENLACE",
                  command=self.start_connection,
                  bg="#ff4b4b", fg="white", font=("Arial", 11, "bold"),
                  activebackground="#ff6b6b", relief="flat"
                  ).pack(pady=10, fill="x", padx=20)

        # GSI
        tk.Label(left_panel, text="GAME STATE INTEGRATION",
                 font=("Arial", 10, "bold"), bg="#1e1e1e", fg="#aaaaaa").pack(pady=(20, 10))

        self.lbl_gsi = tk.Label(left_panel, text="GSI: Inactivo",
                                 bg="#1e1e1e", fg="#555", font=("Arial", 8))
        self.lbl_gsi.pack(pady=2)

        tk.Button(left_panel, text="Instalar GSI Config", command=install_gsi,
                  bg="#2d5986", fg="white", font=("Arial", 9),
                  activebackground="#3d6996", relief="flat"
                  ).pack(pady=5, fill="x", padx=20)

        tk.Button(left_panel, text="Desinstalar GSI", command=self.uninstall_gsi,
                  bg="#444", fg="#ffaaaa", font=("Arial", 9),
                  activebackground="#555", relief="flat"
                  ).pack(pady=5, fill="x", padx=20)

        # Actualización
        tk.Label(left_panel, text="ACTUALIZACIÓN",
                 font=("Arial", 10, "bold"), bg="#1e1e1e", fg="#aaaaaa").pack(pady=(20, 5))

        tk.Button(left_panel, text="🔄 Buscar Actualizaciones",
                  command=self.handle_update_click,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
                  activebackground="#66BB6A", relief="flat"
                  ).pack(pady=5, fill="x", padx=20)

        tk.Label(left_panel, text=f"Versión: {CURRENT_VERSION}",
                 bg="#1e1e1e", fg="#666", font=("Arial", 8)).pack(pady=5)

        # ── RIGHT PANEL (Chat) ──
        right_panel = tk.Frame(content_frame, bg="#121212", bd=2, relief="ridge")
        right_panel.place(x=320, y=0, width=560, height=550)

        tk.Label(right_panel, text="CONSEJOS DEL ORÁCULO",
                 font=("Arial", 11, "bold"), bg="#121212", fg="#00ffcc").pack(pady=5)

        self.chat_history = scrolledtext.ScrolledText(
            right_panel, bg="#0d0d0d", fg="#cccccc",
            font=("Segoe UI", 10), state="disabled", wrap="word")
        self.chat_history.pack(fill="both", expand=True, padx=5, pady=(5, 0))
        self.chat_history.tag_config("user",   foreground="#00ffcc")
        self.chat_history.tag_config("oracle", foreground="#ff9900",
                                     font=("Segoe UI", 10, "bold"))
        self.chat_history.tag_config("system", foreground="gray",
                                     font=("Consolas", 9, "italic"))

        self.load_token()
        self.check_queue()

    # ── ASSETS ──
    def load_assets(self):
        try:
            for path in [resource_path("assets/dota2_oracle_bg.png"),
                         resource_path("dota2_oracle_bg.png")]:
                if os.path.exists(path):
                    img = Image.open(path).convert("RGBA").resize(
                        (900, 650), Image.Resampling.LANCZOS)
                    self.assets["bg"] = ImageTk.PhotoImage(img)
                    break
            for path in [resource_path("assets/logo.png"),
                         resource_path("logo.png")]:
                if os.path.exists(path):
                    self.assets["icon"] = ImageTk.PhotoImage(Image.open(path))
                    break
        except Exception as e:
            print(f"[UI] Error cargando assets: {e}")

    # ── CHAT ──
    def append_chat(self, sender: str, text: str, tag: str):
        self.chat_history.config(state="normal")
        self.chat_history.insert("end", f"{sender}: ", tag)
        self.chat_history.insert("end", f"{text}\n\n")
        self.chat_history.see("end")
        self.chat_history.config(state="disabled")

    # ── GSI ──
    def uninstall_gsi(self):
        path = (
            r"C:\Program Files (x86)\Steam\steamapps\common"
            r"\dota 2 beta\game\dota\cfg\gamestate_integration"
            r"\gamestate_integration_oracle.cfg"
        )
        if os.path.exists(path):
            try:
                os.remove(path)
                messagebox.showinfo("Desinstalado", "Configuración GSI eliminada.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        else:
            messagebox.showinfo("Info", "No hay configuración GSI instalada.")

    # ── TOKEN ──
    def load_token(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    saved = json.load(f).get("token", "")
                    if saved:
                        self.entry_token.insert(0, saved)
                        print(f"[CONFIG] Token cargado desde {CONFIG_FILE}")
        except Exception as e:
            print(f"[CONFIG] Error cargando token: {e}")

    # ── CONEXIÓN ──
    def start_connection(self):
        global current_token
        token = self.entry_token.get().strip()
        if not token:
            messagebox.showwarning(
                "Falta Token",
                "Ingresa tu token de acceso.\n"
                "Puedes encontrarlo en el Dashboard de la web."
            )
            return
        current_token = token
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"token": token}, f)
        except Exception:
            pass
        self.lbl_status.config(text="Conectando...", fg="yellow")
        threading.Thread(target=run_async_loop, daemon=True).start()

    # ── ACTUALIZAR ──
    def handle_update_click(self):
        info = check_for_updates()
        if info.get("error"):
            messagebox.showerror("Error", f"No se pudo verificar:\n{info['error']}")
            return
        if info.get("update_available"):
            msg = (
                f"🎉 Nueva versión: {info['version']}\n"
                f"Versión actual: {CURRENT_VERSION}\n\n"
                f"Cambios:\n{info['changelog']}\n\n"
                "¿Actualizar ahora?"
            )
            if messagebox.askyesno("Actualización", msg):
                self.lbl_status.config(text="Descargando...", fg="yellow")
                self.update_idletasks()
                download_and_install_update(info["download_url"])
        else:
            messagebox.showinfo("Al día", f"Ya tienes la versión {CURRENT_VERSION} (última).")

    # ── QUEUE PROCESSOR ──
    def check_queue(self):
        try:
            while True:
                task = self.ui_queue.get_nowait()
                if callable(task):
                    task()
                elif isinstance(task, tuple):
                    kind = task[0]
                    if kind == "update_status":
                        self.lbl_status.config(text=task[1], fg=task[2])
                    elif kind == "update_gsi":
                        self.lbl_gsi.config(text=task[1], fg=task[2])
                    elif kind == "chat_msg":
                        self.append_chat(task[1], task[2], task[3])
        except queue.Empty:
            pass
        except (tk.TclError, RuntimeError):
            pass
        except Exception as e:
            print(f"[UI] Queue Error: {e}")

        if self.running:
            try:
                self.after(100, self.check_queue)
            except Exception:
                pass

    def on_closing(self):
        self.running = False
        self.destroy()
        sys.exit(0)

# ─── UI UPDATE HELPERS ────────────────────────────────────────────────────────
def update_ui_status(msg: str, color: str = "white"):
    if app:
        app.ui_queue.put(("update_status", msg, color))

def update_ui_chat(sender: str, text: str, tag: str):
    if app:
        app.ui_queue.put(("chat_msg", sender, text, tag))

def update_ui_gsi(msg: str, color: str = "white"):
    if app:
        app.ui_queue.put(("update_gsi", msg, color))

# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def main():
    global loop, app
    loop = asyncio.get_running_loop()

    threading.Thread(target=run_gsi_server, daemon=True).start()
    app = App()

    while app and app.running:
        try:
            app.update()
            await asyncio.sleep(0.01)
        except (tk.TclError, RuntimeError):
            if app:
                app.running = False
            break
        except Exception as e:
            print(f"[MAIN] Error: {e}")
            break

    print("[BRIDGE] Cerrado.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
