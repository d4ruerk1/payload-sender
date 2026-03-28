import tkinter as tk
from tkinter import filedialog
import os, threading, socket, struct, sys, webbrowser, time, re
from datetime import datetime

# --- CONFIGURAZIONE AUTOMODIFICANTE ---
CFG_DATA = {'eula': False, 'ip': '', 'port': '', 'file': '', 'lang': 'en', 'col': 0}

IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

# Gestione DPI per Windows per evitare testo sfocato
if IS_WIN:
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

FNT = "Segoe UI" if IS_WIN else "SF Pro Display" if IS_MAC else "Ubuntu"
FORB_CUR = "no" if IS_WIN else "circle"

# Dizionari Lingue
LANGS = {
    "en": {"h": "HOME", "l": "LOG", "ip": "IP", "pt": "Port", "f": "Payload", "s": "SEND", "b": "Browse", "m_mis": "Missing Data!", "m_run": "Sending...", "m_ok": "Done!", "m_err": "Error!", "m_fail": "Failed!", "eu_t": "TERMS OF USE", "eu_a": "Accept & Continue", "eu_d": "Decline & Exit", "eu_txt": "Credits: d4ruerk1.\n\nEND USER LICENSE AGREEMENT\n\n1. AUTHORIZED USE ONLY\nYou explicitly declare you OWN or have WRITTEN AUTHORIZATION to access target systems. Unauthorized access is illegal.\n\n2. NO WARRANTY\nSoftware is 'AS IS'. Author disclaims all warranties.\n\n3. LIABILITY\nAuthor is not liable for damages/misuse. Use at your own risk. You indemnify the author."},
    "it": {"h": "PRINCIPALE", "l": "REGISTRO", "ip": "IP", "pt": "Porta", "f": "Payload", "s": "INVIA", "b": "Sfoglia", "m_mis": "Dati mancanti!", "m_run": "Invio...", "m_ok": "Completato!", "m_err": "Errore!", "m_fail": "Fallito!", "eu_t": "CONDIZIONI D'USO", "eu_a": "Accetta e Continua", "eu_d": "Rifiuta ed Esci", "eu_txt": "Crediti: d4ruerk1.\n\nCONTRATTO DI LICENZA\n\n1. USO AUTORIZZATO\nDichiari di POSSEDERE o avere AUTORIZZAZIONE SCRITTA per i sistemi target. L'accesso non autorizzato è illegale.\n\n2. NESSUNA GARANZIA\nFornito 'COSÌ COM'È'. L'autore declina ogni garanzia.\n\n3. RESPONSABILITÀ\nL'autore non è responsabile per danni/abusi. Uso a tuo rischio e pericolo."},
    "zh": {"h": "主页", "l": "日志", "ip": "IP", "pt": "端口", "f": "Payload", "s": "发送", "b": "浏览", "m_mis": "数据丢失！", "m_run": "发送中...", "m_ok": "完成！", "m_err": "错误！", "m_fail": "失败！", "eu_t": "使用条款", "eu_a": "接受并继续", "eu_d": "拒绝并退出", "eu_txt": "鸣谢: d4ruerk1.\n\n使用条款\n\n1. 授权使用：您拥有书面授权。未经授权访问是非法的。\n\n2. 无担保：软件按原样提供。\n\n3. 责任：作者不承担损害责任。风险自负。"},
    "ru": {"h": "ГЛАВНАЯ", "l": "ЛОГ", "ip": "IP", "pt": "Порт", "f": "Payload", "s": "ОТПРАВИТЬ", "b": "Обзор", "m_mis": "Нет данных!", "m_run": "Отправка...", "m_ok": "Готово!", "m_err": "Ошибка!", "m_fail": "Сбой!", "eu_t": "УСЛОВИЯ ИСПОЛЬЗОВАНИЯ", "eu_a": "Принять", "eu_d": "Отклонить", "eu_txt": "Кредиты: d4ruerk1.\n\nУСЛОВИЯ ИСПОЛЬЗОВАНИЯ\n\n1. РАЗРЕШЕННОЕ ИСПОЛЬЗОВАНИЕ: Есть ПИСЬМЕННОЕ РАЗРЕШЕНИЕ. Незаконно без него.\n\n2. БЕЗ ГАРАНТИЙ: КАК ЕСТЬ.\n\n3. ОТВЕТСТВЕННОСТЬ: Автор НЕ несет ответственности. Риск ваш."}
}

L_MAP = {"Chinese": "zh", "English": "en", "Italian": "it", "Russian": "ru"}
R_MAP = {v: k for k, v in L_MAP.items()}
COLS = ["#0078D7", "#D32F2F", "#9C27B0", "#D4AF37", "#43A047", "#E91E63"]

class App:
    def __init__(self, r):
        self.r = r
        self.r.withdraw()
        self.r.title("Payload Sender")
        self.r.minsize(800, 600)
        self.r.configure(bg="#1E1E1E")
        
        self.c = CFG_DATA.copy()
        self.l = self.c.get("lang", "en")
        self.col_i = self.c.get("col", 0)
        self.last_click = 0.0
        
        self.file = tk.StringVar(value=self.c.get("file", ""))
        self.w = {} 
        self.eu_ok = False
        self.locked = False
        self.cur_tab = "h"
        
        self._ui()
        self._upd_lng()
        
        if not self.c.get("eula"): 
            self.r.after(500, self._chk_eu)
        else: 
            self.eu_ok = True
            self.w["eu_t"].place_forget()
            self.nav_c.place(relx=0.5, rely=0.5, anchor="center")
            self.f_eu.pack_forget()
            self._tab("h") 
            
        self._upd_col()

        # Inserisci IP e porta (usa i default se vuoti)
        self.w["ip"].insert(0, self.c.get("ip") or "192.168.1.100")
        self.w["pt"].insert(0, self.c.get("port") or "9020")
        
        # Centra la finestra
        self.r.update_idletasks()
        w_width, w_height = 900, 650
        s_width = self.r.winfo_screenwidth()
        s_height = self.r.winfo_screenheight()
        x = (s_width // 2) - (w_width // 2)
        y = (s_height // 2) - (w_height // 2)
        self.r.geometry(f"{w_width}x{w_height}+{x}+{y}")
        self.r.deiconify()

    def _sv(self):
        # Aggiorna il dizionario con i dati attuali
        self.c.update({
            "ip": self.w["ip"].get(), 
            "port": self.w["pt"].get(), 
            "file": self.file.get(), 
            "lang": self.l, 
            "col": self.col_i,
            "eula": getattr(self, 'eu_ok', self.c.get("eula", False))
        })
        
        # Logica di automodifica del file cross-platform
        try:
            pth = os.path.abspath(__file__)
            with open(pth, "r", encoding="utf-8") as f: 
                txt = f.read()
                
            # Trova la riga CFG_DATA e la sostituisce con la nuova configurazione
            txt = re.sub(
                r"^CFG_DATA\s*=\s*\{.*\}$", 
                f"CFG_DATA = {repr(self.c)}", 
                txt, 
                count=1, 
                flags=re.MULTILINE
            )
            
            with open(pth, "w", encoding="utf-8") as f: 
                f.write(txt)
        except Exception: 
            pass # Ignora gli errori di scrittura (es. permessi mancanti o file compilato)

    def _ui(self):
        # Navbar
        n = tk.Frame(self.r, bg="#111", height=60)
        n.pack(fill="x")
        self.w["info"] = tk.Label(n, text="ⓘ", bg="#111", cursor="hand2", font=(FNT, 16))
        self.w["info"].place(relx=0.0, rely=0.5, anchor="w", x=20)
        self.w["info"].bind("<ButtonPress-1>", lambda e: setattr(self, 'h_job', self.r.after(1500, self._cyc)))
        self.w["info"].bind("<ButtonRelease-1>", self._inf_clk)
        self.w["info"].bind("<Enter>", self._ent_inf)
        self.w["info"].bind("<Leave>", self._lve_inf)
        
        self.w["eu_t"] = tk.Label(n, bg="#111", font=(FNT, 14, "bold"))
        self.w["eu_t"].place(relx=0.5, rely=0.5, anchor="center")

        self.nav_c = tk.Frame(n, bg="#111")
        self.w["b_h"] = tk.Button(self.nav_c, fg="#FFF", relief="flat", bd=0, highlightthickness=0, font=(FNT, 11, "bold"), padx=20, command=lambda: self._tab("h"))
        self.w["b_h"].pack(side="left", fill="y")
        self.w["b_l"] = tk.Button(self.nav_c, fg="#FFF", bg="#333", relief="flat", bd=0, highlightthickness=0, font=(FNT, 11, "bold"), padx=20, command=lambda: self._tab("l"))
        self.w["b_l"].pack(side="left", fill="y")
        
        self.w["lng"] = tk.Button(n, fg="#FFF", relief="flat", bd=0, highlightthickness=0, font=(FNT, 10, "bold"), cursor="hand2", command=self._lng_m)
        self.w["lng"].place(relx=1.0, rely=0.5, anchor="e", x=-20)
        self.w["lng"].bind("<Enter>", lambda e: self.w["lng"].config(bg="#444"))
        self.w["lng"].bind("<Leave>", lambda e: self.w["lng"].config(bg=COLS[self.col_i]))
        
        # Schermata EULA
        self.f_eu = tk.Frame(self.r, bg="#1E1E1E")
        self.f_eu.pack(fill="both", expand=True)
        tk.Frame(self.f_eu, bg="#333", height=1).pack(fill="x", padx=30, pady=(15, 0))
        
        bf = tk.Frame(self.f_eu, bg="#1E1E1E")
        bf.pack(side="bottom", fill="x", padx=30, pady=30)
        
        # Chiusura sicura
        self.w["eu_d"] = tk.Button(bf, bg="#2D2D2D", fg="#888", font=(FNT, 11, "bold"), padx=20, pady=10, relief="flat", bd=0, highlightthickness=0, cursor="hand2", command=lambda: sys.exit(0))
        self.w["eu_d"].pack(side="left")
        self.w["eu_d"].bind("<Enter>", lambda e: self.w["eu_d"].config(bg="#3A3A3A", fg="#FFF"))
        self.w["eu_d"].bind("<Leave>", lambda e: self.w["eu_d"].config(bg="#2D2D2D", fg="#888"))

        self.w["eu_a"] = tk.Button(bf, bg="#222", fg="#777", font=(FNT, 11, "bold"), padx=20, pady=10, relief="flat", bd=0, highlightthickness=0, cursor=FORB_CUR)
        self.w["eu_a"].pack(side="right")
        self.w["eu_a"].bind("<Button-1>", lambda e: self._acc() if self.eu_ok else None)
        
        tf = tk.Frame(self.f_eu, bg="#1E1E1E")
        tf.pack(fill="both", expand=True, padx=30, pady=20)
        sc = tk.Scrollbar(tf)
        sc.pack(side="right", fill="y")
        self.w["eu_txt"] = tk.Text(tf, bg="#111", fg="#CCC", font=(FNT, 11), wrap="word", bd=0, highlightthickness=0, yscrollcommand=sc.set, padx=15, pady=15)
        self.w["eu_txt"].pack(side="left", fill="both", expand=True)
        sc.config(command=self.w["eu_txt"].yview)
        
        # Schermata Home
        self.f_h = tk.Frame(self.r, bg="#1E1E1E")
        mc = tk.Frame(self.f_h, bg="#1E1E1E")
        mc.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)
        
        fr = tk.Frame(mc, bg="#1E1E1E")
        fr.pack(fill="x", pady=(0, 20))
        
        f_ip = tk.Frame(fr, bg="#1E1E1E")
        f_ip.pack(side="left", expand=True, fill="x", padx=(0, 20))
        self.w["l_ip"] = tk.Label(f_ip, fg="#FFF", bg="#1E1E1E", font=(FNT, 11, "bold"))
        self.w["l_ip"].pack(anchor="w")
        
        v_i = (self.r.register(lambda p: not getattr(self, 'locked', False) and (not p or (all(c.isdigit() or c=='.' for c in p) and len(p)<=15))), '%P')
        self.w["ip"] = tk.Entry(f_ip, bg="#2D2D2D", fg="#FFF", disabledbackground="#2D2D2D", font=(FNT, 11), relief="flat", bd=0, highlightthickness=0, validate="key", validatecommand=v_i)
        self.w["ip"].pack(fill="x", ipady=8, pady=(5,0))
        
        f_pt = tk.Frame(fr, bg="#1E1E1E")
        f_pt.pack(side="right")
        self.w["l_pt"] = tk.Label(f_pt, fg="#FFF", bg="#1E1E1E", font=(FNT, 11, "bold"))
        self.w["l_pt"].pack(anchor="w")
        
        v_p = (self.r.register(lambda p: not getattr(self, 'locked', False) and (not p or (p.isdigit() and len(p)<=5))), '%P')
        self.w["pt"] = tk.Entry(f_pt, bg="#2D2D2D", fg="#FFF", disabledbackground="#2D2D2D", font=(FNT, 11), width=12, relief="flat", bd=0, highlightthickness=0, validate="key", validatecommand=v_p)
        self.w["pt"].pack(fill="x", ipady=8, pady=(5,0))
        
        self.w["l_f"] = tk.Label(mc, fg="#FFF", bg="#1E1E1E", font=(FNT, 11, "bold"))
        self.w["l_f"].pack(anchor="w")
        
        fl = tk.Frame(mc, bg="#1E1E1E")
        fl.pack(fill="x", pady=(5, 30))
        
        self.w["ent_f"] = tk.Entry(fl, textvariable=self.file, bg="#2D2D2D", readonlybackground="#2D2D2D", fg="#FFF", font=(FNT, 11), state="readonly", relief="flat", bd=0, highlightthickness=0)
        self.w["ent_f"].pack(side="left", expand=True, fill="both", ipady=8)
        
        self.w["b_f"] = tk.Button(fl, bg="#333", fg="#FFF", font=(FNT, 10, "bold"), relief="flat", bd=0, highlightthickness=0, cursor="hand2", command=lambda: not self.locked and self.file.set(filedialog.askopenfilename() or self.file.get()))
        self.w["b_f"].pack(side="right", padx=(15,0), ipadx=15, fill="y")
        
        self.w["snd"] = tk.Button(mc, fg="#FFF", font=(FNT, 12, "bold"), relief="flat", bd=0, highlightthickness=0, cursor="hand2", command=self._run)
        self.w["snd"].pack(ipady=10, ipadx=60)
        self.w["snd"].bind("<Enter>", lambda e: not self.locked and self.w["snd"].config(bg="#FFF", fg="#111"))
        self.w["snd"].bind("<Leave>", lambda e: not self.locked and self.w["snd"].config(bg=COLS[self.col_i], fg="#FFF"))
        
        # Schermata Log
        self.f_l = tk.Frame(self.r, bg="#1E1E1E", padx=20, pady=20)
        self.w["log"] = tk.Text(self.f_l, font=("Consolas", 10), bg="#111", fg="#FFF", relief="flat", bd=0, highlightthickness=0, state="disabled")
        self.w["log"].pack(fill="both", expand=True)
        
        # Gestione Scorciatoie Cross-Platform
        for seq in ["<Control-a>", "<Command-a>"]: 
            self.w["log"].bind(seq, self._select_all)
        for seq in ["<Control-c>", "<Command-c>"]: 
            self.w["log"].bind(seq, self._cpy)

    def _select_all(self, e):
        self.w["log"].tag_add("sel", "1.0", "end")
        return "break"

    def _cpy(self, e):
        try:
            if self.w["log"].tag_ranges("sel"):
                self.r.clipboard_clear()
                self.r.clipboard_append(self.w["log"].get("sel.first", "sel.last"))
        except Exception: 
            pass
        return "break"

    def _ent_inf(self, e):
        self.w["info"].config(fg="#FFF")
        self.tt = tk.Toplevel(self.r)
        self.tt.wm_overrideredirect(True)
        self.tt.geometry(f"+{e.x_root+15}+{e.y_root+15}")
        tk.Label(self.tt, text="Version: 1.0.1", bg="#333", fg="#FFF", font=(FNT, 9), borderwidth=1, relief="solid").pack(ipadx=4, ipady=2)

    def _lve_inf(self, e):
        self.w["info"].config(fg=COLS[self.col_i])
        if hasattr(self, 'tt') and self.tt: 
            self.tt.destroy()

    def _cyc(self):
        self.h_job = None
        self.col_i = (self.col_i + 1) % len(COLS)
        self._upd_col()
        self._sv()
        
    def _inf_clk(self, e):
        if hasattr(self, 'h_job') and self.h_job:
            self.r.after_cancel(self.h_job)
            webbrowser.open("https://github.com/d4ruerk1/payload-sender")
            
    def _tab(self, t):
        self.cur_tab = t
        if t == "h":
            if hasattr(self, 'f_l'): self.f_l.pack_forget()
            self.f_h.pack(fill="both", expand=True)
            self.w["b_h"].config(bg=COLS[self.col_i])
            self.w["b_l"].config(bg="#333")
        else:
            self.f_h.pack_forget()
            self.f_l.pack(fill="both", expand=True)
            self.w["b_l"].config(bg=COLS[self.col_i])
            self.w["b_h"].config(bg="#333")

    def _lng_m(self):
        m = tk.Menu(self.r, tearoff=0, bg="#333", fg="#FFF", activebackground=COLS[self.col_i], bd=0, relief="flat")
        for n, c in L_MAP.items(): 
            m.add_command(label=n, command=lambda x=c: self._set_l(x))
        m.tk_popup(self.w["lng"].winfo_rootx(), self.w["lng"].winfo_rooty() + self.w["lng"].winfo_height())

    def _set_l(self, c): 
        self.l = c
        self._upd_lng()
        self._sv()

    def _upd_col(self):
        ac = COLS[self.col_i]
        for k in ["info", "ip", "pt", "ent_f", "b_f", "log", "eu_t"]: 
            self.w[k].config(fg=ac)
            if k in ["ip", "pt"]: 
                self.w[k].config(disabledforeground=ac)
            
        self.w["lng"].config(bg=ac)
        if not self.locked: 
            self.w["snd"].config(bg=ac, fg="#FFF")
        
        if self.eu_ok:
            self.w["eu_a"].config(bg=ac)
            self._tab(self.cur_tab)

    def _upd_lng(self):
        d = LANGS[self.l]
        self.w["lng"].config(text=R_MAP[self.l][:3].upper()) 
        self.w["b_h"].config(text=d["h"])
        self.w["b_l"].config(text=d["l"])
        self.w["l_ip"].config(text=d["ip"])
        self.w["l_pt"].config(text=d["pt"])
        self.w["l_f"].config(text=d["f"])
        self.w["b_f"].config(text=d["b"])
        self.w["eu_t"].config(text=d["eu_t"])
        self.w["eu_a"].config(text=d["eu_a"])
        self.w["eu_d"].config(text=d["eu_d"])
        
        if not self.locked: 
            self.w["snd"].config(text=d["s"])
        
        self.w["eu_txt"].config(state="normal")
        self.w["eu_txt"].delete("1.0", "end")
        self.w["eu_txt"].insert("1.0", d["eu_txt"])
        self.w["eu_txt"].config(state="disabled")

    def _chk_eu(self):
        if not self.f_eu.winfo_viewable(): return
        if self.w["eu_txt"].yview()[1] >= 0.99:
            self.eu_ok = True
            self.w["eu_a"].config(bg=COLS[self.col_i], fg="#FFF", cursor="hand2")
            self.w["eu_a"].bind("<Enter>", lambda e: self.w["eu_a"].config(bg="#FFF", fg=COLS[self.col_i]) if self.eu_ok else None)
            self.w["eu_a"].bind("<Leave>", lambda e: self.w["eu_a"].config(bg=COLS[self.col_i], fg="#FFF") if self.eu_ok else None)
            return
        self.r.after(200, self._chk_eu)

    def _acc(self):
        self.eu_ok = True
        self._sv()
        self.f_eu.pack_forget()
        self.w["eu_t"].place_forget()
        self.nav_c.place(relx=0.5, rely=0.5, anchor="center")
        self._tab("h")

    def _lg(self, m):
        self.w["log"].config(state="normal")
        self.w["log"].insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {m}\n\n")
        self.w["log"].see("end")
        self.w["log"].config(state="disabled")

    def _loc_ui(self, lock):
        self.locked = lock
        cur = FORB_CUR if lock else "hand2"
        ecur = FORB_CUR if lock else "xterm"
        
        for k in ["b_f", "snd"]: 
            self.w[k].config(cursor=cur)
        self.w["ent_f"].config(cursor=ecur)
        
        for k in ["ip", "pt"]:
            self.w[k].config(cursor=ecur, state="disabled" if lock else "normal")

    def _run(self):
        if self.locked or time.time() - self.last_click < 0.5: return
        self.last_click = time.time()
        self._sv()
        
        d = LANGS[self.l]
        i, p, f = self.w["ip"].get().strip(), self.w["pt"].get().strip(), self.file.get()
        
        if not all([i, p, f]):
            self._loc_ui(True)
            self.w["snd"].config(text=d["m_mis"], bg="#D13438")
            self.r.after(2000, lambda: (self._loc_ui(False), self.w["snd"].config(text=d["s"], bg=COLS[self.col_i])))
            return
            
        self._loc_ui(True)
        self.w["snd"].config(text=d["m_run"], bg="#555", fg="#FFF")
        threading.Thread(target=self._thr, args=(f, i, p, d), daemon=True).start()

    def _fin(self, txt, col, msg, d):
        self.w["snd"].config(text=txt, bg=col)
        self._lg(msg)
        self.r.after(1500, lambda: (self._loc_ui(False), self.w["snd"].config(text=d["s"], bg=COLS[self.col_i])))

    def _thr(self, fp, ip, p, d):
        def cb(t, c, m): 
            self.r.after(0, lambda: self._fin(t, c, m, d))
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)
                self.r.after(0, lambda: self._lg(f"Connessione a {ip}:{p}..."))
                s.connect((ip, int(p)))
                self.r.after(0, lambda: self._lg(f"Connesso!\nPreparazione: {os.path.basename(fp)}"))
                
                s.sendall(struct.pack('<Q', os.path.getsize(fp)))
                bs = 0
                with open(fp, 'rb') as f:
                    while c := f.read(65536): 
                        s.sendall(c)
                        bs += len(c)
                        
                self.r.after(0, lambda: self._lg(f"Inviati {bs} byte. In attesa..."))
                s.shutdown(socket.SHUT_WR)
                s.settimeout(5.0)
                
                try:
                    res = s.recv(4096)
                    cb(d["m_ok"], "#107C10", f"SUCCESS: {res.decode(errors='replace').strip()}" if res else "SUCCESS: Inviato.")
                except socket.timeout: 
                    cb("Timeout", "#D98300", "WARNING: Timeout segnale (5s).")
                    
        except ConnectionRefusedError:
            cb(d["m_err"], "#D13438", f"ERR: Connessione Rifiutata. Nessun server in ascolto su {ip}:{p}")
        except Exception as e: 
            cb(d["m_fail"], "#D13438", f"ERR: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()