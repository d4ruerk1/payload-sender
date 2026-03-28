import tkinter as tk
from tkinter import filedialog
import os
import threading
from datetime import datetime
import platform
import webbrowser
import math
import json
import socket
import struct
import sys

# Rilevamento OS
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"

# DPI Awareness per Windows
if IS_WINDOWS:
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# Determina la cartella corrente in modo sicuro
try:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CURRENT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

SETTINGS_FILE = os.path.join(CURRENT_DIR, "payload_config.json")

# Definizione Cursore Divieto Cross-Platform
if IS_WINDOWS:
    CURSOR_FORBIDDEN = "no"
elif IS_MAC:
    CURSOR_FORBIDDEN = "notallowed"
else:
    CURSOR_FORBIDDEN = "circle"

# Font di sistema
FONT_FAMILY = "Segoe UI" if IS_WINDOWS else ("SF Pro Display" if IS_MAC else "Ubuntu")

LANGUAGES = {
    "en": {"nav_home": "HOME", "nav_log": "LOG", "ip_label": "IP", "port_label": "Port", "file_label": "Payload", "btn_send": "SEND", "btn_browse": "Browse", "msg_missing": "Missing Data!", "msg_executing": "Sending...", "msg_sent": "Done!", "msg_error": "Error!", "msg_failed": "Failed!", "ver_text": "Version"},
    "it": {"nav_home": "PRINCIPALE", "nav_log": "REGISTRO", "ip_label": "IP", "port_label": "Porta", "file_label": "Payload", "btn_send": "INVIA", "btn_browse": "Sfoglia", "msg_missing": "Dati mancanti!", "msg_executing": "Invio in corso...", "msg_sent": "Completato!", "msg_error": "Errore!", "msg_failed": "Fallito!", "ver_text": "Versione"},
    "de": {"nav_home": "START", "nav_log": "PROTOKOLL", "ip_label": "IP", "port_label": "Port", "file_label": "Payload", "btn_send": "SENDEN", "btn_browse": "Durchsuchen", "msg_missing": "Fehlende Daten!", "msg_executing": "Senden...", "msg_sent": "Erledigt!", "msg_error": "Fehler!", "msg_failed": "Fehlgeschlagen!", "ver_text": "Version"},
    "fr": {"nav_home": "ACCUEIL", "nav_log": "JOURNAL", "ip_label": "IP", "port_label": "Port", "file_label": "Payload", "btn_send": "ENVOYER", "btn_browse": "Parcourir", "msg_missing": "Données manquantes !", "msg_executing": "Envoi...", "msg_sent": "Terminé !", "msg_error": "Erreur !", "msg_failed": "Échec !", "ver_text": "Version"},
    "zh": {"nav_home": "主页", "nav_log": "日志", "ip_label": "IP", "port_label": "端口", "file_label": "Payload", "btn_send": "发送", "btn_browse": "浏览", "msg_missing": "数据丢失！", "msg_executing": "发送中...", "msg_sent": "完成！", "msg_error": "错误！", "msg_failed": "失败！", "ver_text": "版本"},
    "ja": {"nav_home": "ホーム", "nav_log": "ログ", "ip_label": "IP", "port_label": "ポート", "file_label": "Payload", "btn_send": "送信", "btn_browse": "参照", "msg_missing": "データなし！", "msg_executing": "送信中...", "msg_sent": "完了！", "msg_error": "エラー！", "msg_failed": "失敗！", "ver_text": "バージョン"},
    "ru": {"nav_home": "ГЛАВНАЯ", "nav_log": "ЛОГ", "ip_label": "IP", "port_label": "Порт", "file_label": "Payload", "btn_send": "ОТПРАВИТЬ", "btn_browse": "Обзор", "msg_missing": "Нет данных!", "msg_executing": "Отправка...", "msg_sent": "Готово!", "msg_error": "Ошибка!", "msg_failed": "Сбой!", "ver_text": "Версия"},
    "ar": {"nav_home": "الرئيسية", "nav_log": "السجل", "ip_label": "IP", "port_label": "المنفذ", "file_label": "Payload", "btn_send": "إرسال", "btn_browse": "تصفح", "msg_missing": "بيانات مفقودة!", "msg_executing": "جاري الإرسال...", "msg_sent": "تم!", "msg_error": "خطأ!", "msg_failed": "فشل!", "ver_text": "الإصدار"}
}

LANG_NAMES = {
    "Arabic": "ar", "Chinese": "zh", "English": "en", "French": "fr",
    "German": "de", "Italian": "it", "Japanese": "ja", "Russian": "ru"
}

BG_COLOR, FG_COLOR = "#1E1E1E", "#FFFFFF"
BTN_BG, ERROR_COLOR = "#333333", "#D13438"
SUCCESS_COLOR = "#107C10"
INPUT_BG = "#2D2D2D"

GITHUB_URL = "https://github.com/d4ruerk1/payload-sender"

COLOR_CYCLE = [
    "#0078D7", "#D32F2F", "#9C27B0", "#D4AF37", "#43A047", "#E91E63"
]

class PayloadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Payload Sender")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        self.root.configure(bg=BG_COLOR)

        # Variabili di stato
        self.current_lang = "en"
        self.color_index = 0
        self.accent_color = COLOR_CYCLE[self.color_index]
        self.hold_job = None
        self.path_file = tk.StringVar()
        self.ui_elements = {}
        self.tip_window = None
        
        # Variabili per l'ottimizzazione grafica
        self.last_width = 0
        self.scaling_locked = False
        self._resize_job = None

        self.setup_nav()
        
        self.frame_home = tk.Frame(self.root, bg=BG_COLOR)
        self.frame_log = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=20)
        
        self.setup_home()
        self.setup_log()
        self.cambia_scheda("home")
        
        self.load_credentials()
        self.root.bind("<Configure>", self.debounce_scaler)
        self.update_ui_text()

    def load_credentials(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.entry_ip.insert(0, data.get("ip", ""))
                    self.entry_porta.insert(0, data.get("port", ""))
                    self.path_file.set(data.get("file", ""))
                    self.current_lang = data.get("lang", "en")
                    
                    saved_idx = data.get("color_idx", 0)
                    if isinstance(saved_idx, int) and 0 <= saved_idx < len(COLOR_CYCLE):
                        self.color_index = saved_idx
            except Exception:
                pass
        
        self.accent_color = COLOR_CYCLE[self.color_index]
        self.update_theme_colors()

    def save_credentials(self):
        data = {
            "ip": self.entry_ip.get(),
            "port": self.entry_porta.get(),
            "file": self.path_file.get(),
            "lang": self.current_lang,
            "color_idx": self.color_index
        }
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    # --- FUNZIONI DI SUPPORTO CROSS-PLATFORM ---
    def _apply_cursor(self, widget, target_cursor, fallback="X_cursor"):
        """Tenta di applicare un cursore, con fallback in caso di OS incompatibile"""
        try:
            widget.config(cursor=target_cursor)
        except tk.TclError:
            try:
                widget.config(cursor=fallback)
            except tk.TclError:
                pass # Fallback estremo: ignora se l'OS non lo supporta affatto

    def lock_ui(self):
        self._apply_cursor(self.root, "watch", "clock")
        self._apply_cursor(self.btn_invia, "watch", "clock")
        
        widgets = [self.entry_ip, self.entry_porta, self.f_btn, 
                   self.f_ent, self.btn_tab_home, self.btn_tab_log, self.btn_lang]
        
        for w in widgets:
            w.config(state="disabled")
            self._apply_cursor(w, CURSOR_FORBIDDEN, "X_cursor")

    def unlock_ui(self):
        self._apply_cursor(self.root, "")
        self._apply_cursor(self.btn_invia, "hand2", "pointinghand")
        
        for w in [self.f_btn, self.btn_tab_home, self.btn_tab_log, self.btn_lang]:
            w.config(state="normal")
            self._apply_cursor(w, "hand2", "pointinghand")
            
        for w in [self.entry_ip, self.entry_porta]:
            w.config(state="normal")
            self._apply_cursor(w, "xterm")
            
        self.f_ent.config(state="readonly")
        self._apply_cursor(self.f_ent, "xterm")

    # --- GESTIONE PRESSIONE PROLUNGATA ---
    def start_action_hold(self, event):
        self.hold_job = self.root.after(1500, self.trigger_color_cycle)

    def trigger_color_cycle(self):
        self.hold_job = None
        self.color_index = (self.color_index + 1) % len(COLOR_CYCLE)
        self.accent_color = COLOR_CYCLE[self.color_index]
        self.update_theme_colors()
        self.save_credentials()

    def stop_action_hold_and_click(self, event):
        if self.hold_job:
            self.root.after_cancel(self.hold_job)
            self.hold_job = None
            webbrowser.open(GITHUB_URL)

    # --- UI UPDATE & RESIZE ---
    def update_theme_colors(self):
        self.btn_info.config(fg=self.accent_color)
        self.btn_lang.config(bg=self.accent_color)
        
        self.txt_log.config(fg=self.accent_color)
        self.entry_ip.config(fg=self.accent_color)
        self.entry_porta.config(fg=self.accent_color)
        self.f_ent.config(fg=self.accent_color)
        self.f_btn.config(fg=self.accent_color)

        if self.frame_home.winfo_viewable():
            self.btn_tab_home.config(bg=self.accent_color)
            self.btn_tab_log.config(bg=BTN_BG)
        elif self.frame_log.winfo_viewable():
            self.btn_tab_log.config(bg=self.accent_color)
            self.btn_tab_home.config(bg=BTN_BG)
        
        self.btn_invia.config(bg=self.accent_color)

    def validate_ip(self, p):
        return not p or (all(c.isdigit() or c == '.' for c in p) and len(p) <= 15)

    def setup_nav(self):
        self.nav_bg = tk.Frame(self.root, bg="#111111")
        self.nav_bg.pack(fill="x", side="top")

        self.btn_info = tk.Label(self.nav_bg, text="ⓘ", bg="#111111", fg=self.accent_color, cursor="hand2")
        self.btn_info.place(relx=0.0, rely=0.5, anchor="w", x=30)
        
        self.btn_info.bind("<ButtonPress-1>", self.start_action_hold)
        self.btn_info.bind("<ButtonRelease-1>", self.stop_action_hold_and_click)
        self.btn_info.bind("<Enter>", self.show_tooltip)
        self.btn_info.bind("<Leave>", self.hide_tooltip)

        self.nav_center = tk.Frame(self.nav_bg, bg="#111111")
        self.nav_center.pack(side="top", anchor="center", fill="y")

        self.btn_tab_home = tk.Button(self.nav_center, bg=self.accent_color, fg=FG_COLOR, relief="flat", cursor="hand2", command=lambda: self.cambia_scheda("home"), highlightthickness=0)
        self.btn_tab_home.pack(side="left", fill="y")

        self.btn_tab_log = tk.Button(self.nav_center, bg=BTN_BG, fg=FG_COLOR, relief="flat", cursor="hand2", command=lambda: self.cambia_scheda("log"), highlightthickness=0)
        self.btn_tab_log.pack(side="left", fill="y")

        self.btn_lang = tk.Button(self.nav_bg, bg=self.accent_color, fg=FG_COLOR, relief="flat", cursor="hand2", command=self.show_language_menu, highlightthickness=0)
        self.btn_lang.place(relx=1.0, rely=0.5, anchor="e", x=-30)

    def debounce_scaler(self, event):
        """Previene il blocco della UI richiamando la funzione di scaler in modo ritardato"""
        if event.widget != self.root or self.scaling_locked: return
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(50, lambda: self.dynamic_scaler(event.width))

    def dynamic_scaler(self, w):
        if abs(w - self.last_width) < 5: return
        self.last_width = w
        scale_factor = min(1 + (math.log(w / 1000) if w > 1000 else 0) * 0.8, 1.4)
        
        nav_h = int(60 * scale_factor)
        self.nav_bg.configure(height=nav_h)
        base_size = int(10 * scale_factor)
        
        self.btn_info.configure(font=(FONT_FAMILY, int(20 * scale_factor)))
        self.btn_lang.configure(font=(FONT_FAMILY, int(11 * scale_factor), "bold"), padx=15*scale_factor)
        self.btn_tab_home.configure(font=(FONT_FAMILY, int(10 * scale_factor), "bold"), padx=25*scale_factor)
        self.btn_tab_log.configure(font=(FONT_FAMILY, int(10 * scale_factor), "bold"), padx=25*scale_factor)
        
        self.update_content_fonts(FONT_FAMILY, base_size, scale_factor)
        self.main_container.place_configure(relwidth=(0.85 if w < 1300 else 0.70))

    def update_content_fonts(self, family, size, scale):
        title_f = (family, size + 1, "bold")
        widget_f = (family, size)
        btn_f = (family, size + 2, "bold")
        
        self.btn_invia.configure(font=btn_f)
        self.entry_ip.configure(font=widget_f)
        self.entry_porta.configure(font=widget_f)
        self.f_ent.configure(font=widget_f)
        
        for k in ["ip_lbl", "port_lbl", "f_lbl"]:
            if k in self.ui_elements: self.ui_elements[k].configure(font=title_f)
        
        if hasattr(self, 'f_btn'):
            self.f_btn.configure(font=(family, size-1, "bold"))

    def setup_home(self):
        self.main_container = tk.Frame(self.frame_home, bg=BG_COLOR)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85)

        f_rete = tk.Frame(self.main_container, bg=BG_COLOR)
        f_rete.pack(fill="x", pady=(0, 20))

        f_ip = tk.Frame(f_rete, bg=BG_COLOR)
        f_ip.pack(side="left", expand=True, fill="x", padx=(0, 20))
        self.ui_elements["ip_lbl"] = tk.Label(f_ip, fg="#FFFFFF", bg=BG_COLOR)
        self.ui_elements["ip_lbl"].pack(anchor="w")
        vcmd_ip = (self.root.register(self.validate_ip), '%P')
        self.entry_ip = tk.Entry(f_ip, bg=INPUT_BG, fg=self.accent_color, insertbackground=FG_COLOR, relief="flat", bd=1, validate="key", validatecommand=vcmd_ip, highlightthickness=0)
        self.entry_ip.pack(fill="x", ipady=8, pady=(5, 0))

        f_p = tk.Frame(f_rete, bg=BG_COLOR)
        f_p.pack(side="right")
        self.ui_elements["port_lbl"] = tk.Label(f_p, fg="#FFFFFF", bg=BG_COLOR)
        self.ui_elements["port_lbl"].pack(anchor="w")
        vcmd_p = (self.root.register(lambda p: not p or (p.isdigit() and len(p) <= 5)), '%P')
        self.entry_porta = tk.Entry(f_p, bg=INPUT_BG, fg=self.accent_color, width=12, relief="flat", bd=1, validate="key", validatecommand=vcmd_p, highlightthickness=0)
        self.entry_porta.pack(fill="x", ipady=8, pady=(5, 0))

        self.ui_elements["f_lbl"], self.f_btn, self.f_ent = self.crea_selettore(self.path_file)

        f_btn = tk.Frame(self.main_container, bg=BG_COLOR)
        f_btn.pack(fill="x", pady=(30, 0))
        self.btn_invia = tk.Button(f_btn, bg=self.accent_color, fg=FG_COLOR, relief="flat", cursor="hand2", command=self.esegui_script, highlightthickness=0)
        self.btn_invia.pack(ipady=10, ipadx=60)

    def crea_selettore(self, var_path):
        frame = tk.Frame(self.main_container, bg=BG_COLOR)
        frame.pack(fill="x", pady=10)
        lbl = tk.Label(frame, fg="#FFFFFF", bg=BG_COLOR)
        lbl.pack(anchor="w")
        f_line = tk.Frame(frame, bg=BG_COLOR)
        f_line.pack(fill="x", pady=(5, 0))
        
        ent = tk.Entry(f_line, textvariable=var_path, fg=self.accent_color, bg=INPUT_BG, readonlybackground=INPUT_BG, relief="flat", state="readonly", highlightthickness=0)
        ent.pack(side="left", expand=True, fill="both", ipady=8) 
        
        btn = tk.Button(f_line, bg=BTN_BG, fg=self.accent_color, relief="flat", cursor="hand2", command=lambda: self.seleziona(var_path), highlightthickness=0)
        btn.pack(side="right", padx=(15, 0), ipadx=15, fill="y") 
        
        return lbl, btn, ent

    def setup_log(self):
        self.txt_log = tk.Text(self.frame_log, font=("Consolas", 10), bg="#111111", fg=self.accent_color, relief="flat", state="disabled", wrap="word", highlightthickness=0)
        self.txt_log.pack(fill="both", expand=True)
        
        # Scorciatoie Standard (Win/Linux)
        self.txt_log.bind("<Control-a>", self.select_all_log)
        self.txt_log.bind("<Control-c>", self.copy_log)
        
        # Scorciatoie macOS (Garantisce compatibilità indipendentemente dalla versione Tkinter)
        self.txt_log.bind("<Command-a>", self.select_all_log)
        self.txt_log.bind("<Command-c>", self.copy_log)
        self.txt_log.bind("<Meta-a>", self.select_all_log)
        self.txt_log.bind("<Meta-c>", self.copy_log)

    def select_all_log(self, event):
        self.txt_log.tag_add("sel", "1.0", "end")
        return "break"

    def copy_log(self, event):
        try:
            text = self.txt_log.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.txt_log.tag_remove("sel", "1.0", "end")
        except tk.TclError:
            pass 
        return "break"

    def show_tooltip(self, event):
        if self.tip_window:
            return  # Previene la creazione di tooltip multipli
            
        x = self.btn_info.winfo_rootx() + 45
        y = self.btn_info.winfo_rooty() + 45
        self.tip_window = tw = tk.Toplevel(self.btn_info)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=f"{LANGUAGES[self.current_lang]['ver_text']}: 1.0.0", bg="#333333", fg="white", relief='flat', border=4, font=(FONT_FAMILY, 9, "bold")).pack()

    def hide_tooltip(self, event):
        if self.tip_window: 
            self.tip_window.destroy()
            self.tip_window = None

    def show_language_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg=BTN_BG, fg=FG_COLOR, activebackground=self.accent_color, activeforeground=FG_COLOR, relief="flat")
        
        for lang_name in sorted(LANG_NAMES.keys()):
            lang_code = LANG_NAMES[lang_name]
            menu.add_command(label=lang_name, command=lambda c=lang_code: self.change_language(c))
            
        x = self.btn_lang.winfo_rootx()
        y = self.btn_lang.winfo_rooty() + self.btn_lang.winfo_height()
        menu.tk_popup(x, y)

    def change_language(self, lang_code):
        self.current_lang = lang_code
        self.update_ui_text()
        self.save_credentials()

    def update_ui_text(self):
        l = LANGUAGES[self.current_lang]
        self.btn_tab_home.config(text=l["nav_home"])
        self.btn_tab_log.config(text=l["nav_log"])
        self.btn_lang.config(text=self.current_lang.upper()) 
        self.ui_elements["ip_lbl"].config(text=l["ip_label"])
        self.ui_elements["port_lbl"].config(text=l["port_label"])
        self.ui_elements["f_lbl"].config(text=l["file_label"])
        self.f_btn.config(text=l["btn_browse"])
        
        # Non sovrascriviamo il testo se c'è un'azione in corso
        if self.btn_invia.cget("state") == "normal":
            self.btn_invia.config(text=l["btn_send"])

    def seleziona(self, var):
        self.scaling_locked = True 
        p = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if p: var.set(p)
        self.root.after(200, self.unlock_scaling)

    def unlock_scaling(self):
        self.scaling_locked = False

    def cambia_scheda(self, scheda):
        if scheda == "home":
            self.frame_log.pack_forget()
            self.frame_home.pack(fill="both", expand=True)
            self.btn_tab_home.config(bg=self.accent_color)
            self.btn_tab_log.config(bg=BTN_BG)
        else:
            self.frame_home.pack_forget()
            self.frame_log.pack(fill="both", expand=True)
            self.btn_tab_log.config(bg=self.accent_color)
            self.btn_tab_home.config(bg=BTN_BG)

    def log_sistema(self, msg):
        if hasattr(self, 'txt_log'):
            orario = datetime.now().strftime("%H:%M:%S")
            self.txt_log.config(state="normal")
            self.txt_log.insert("end", f"[{orario}] {msg}\n\n")
            self.txt_log.see("end")
            self.txt_log.config(state="disabled")

    def esegui_script(self):
        self.save_credentials()
        l = LANGUAGES[self.current_lang]
        ip, porta = self.entry_ip.get().strip(), self.entry_porta.get().strip()
        filepath = self.path_file.get()
        
        if not all([ip, porta, filepath]):
            self.log_sistema(l["msg_missing"])
            self.btn_invia.config(text=l["msg_missing"], bg=ERROR_COLOR)
            self.root.after(2000, lambda: self.btn_invia.config(text=l["btn_send"], bg=self.accent_color))
            return
            
        self.btn_invia.config(text=l["msg_executing"], state="disabled", bg="#555555")
        self.lock_ui() 
        
        threading.Thread(target=self.run_process, args=(filepath, ip, porta), daemon=True).start()

    def run_process(self, filepath, ip, porta):
        l = LANGUAGES[self.current_lang]
        try:
            port_num = int(porta)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)
                self.root.after(0, lambda: self.log_sistema(f"Tentativo di connessione a {ip}:{port_num}..."))
                s.connect((ip, port_num))
                self.root.after(0, lambda: self.log_sistema(f"Connesso!\nPreparazione file: {os.path.basename(filepath)}"))
                
                # OTTIMIZZAZIONE MEMORIA: Lettura e invio in blocchi (Chunking)
                file_size = os.path.getsize(filepath)
                s.sendall(struct.pack('<Q', file_size))
                
                bytes_sent = 0
                with open(filepath, 'rb') as f:
                    while chunk := f.read(65536): # 64 KB a blocco
                        s.sendall(chunk)
                        bytes_sent += len(chunk)
                
                self.root.after(0, lambda: self.log_sistema(f"Inviati {bytes_sent} byte. In attesa di segnale dall'host..."))
                
                s.shutdown(socket.SHUT_WR)
                s.settimeout(5.0)
                try:
                    response = s.recv(4096)
                    if response:
                        testo_risposta = response.decode('utf-8', errors='replace').strip()
                        msg = f"SUCCESS: Segnale ricevuto -> {testo_risposta}"
                    else:
                        msg = "SUCCESS: Payload inviato (Nessun segnale, host ha chiuso la connessione)."
                    self.root.after(0, lambda: self.finish(l["msg_sent"], SUCCESS_COLOR, msg))
                except socket.timeout:
                    msg = "ATTENZIONE: Payload inviato, ma timeout (5s) durante l'attesa del segnale dall'host."
                    self.root.after(0, lambda: self.finish("Timeout Segnale", "#D98300", msg))

        except ConnectionRefusedError:
            msg = "ERROR: Connessione rifiutata.\nL'host è in ascolto sulla porta corretta?"
            self.root.after(0, lambda: self.finish(l["msg_error"], ERROR_COLOR, msg))
        except socket.timeout:
            msg = "ERROR: Timeout della connessione iniziale (5s superati)."
            self.root.after(0, lambda: self.finish(l["msg_error"], ERROR_COLOR, msg))
        except Exception as e:
            self.root.after(0, lambda: self.finish(l["msg_failed"], ERROR_COLOR, f"CRITICAL ERR: {str(e)}"))

    def finish(self, txt, col, log):
        self.btn_invia.config(text=txt, bg=col, state="normal")
        self.log_sistema(log)
        self.unlock_ui()
        
        self.root.after(1000, lambda: self.btn_invia.config(text=LANGUAGES[self.current_lang]["btn_send"], bg=self.accent_color))

if __name__ == "__main__":
    try:
        app_root = tk.Tk()
        app = PayloadApp(app_root)
        app_root.mainloop()
    except Exception:
        pass