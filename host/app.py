import cv2
import tkinter as tk
from tkinter import ttk, messagebox
import serial, serial.tools.list_ports
import numpy as np
from PIL import Image, ImageTk

BAUD = 115200
TOLERANCIA = 50         # píxeles de radio alrededor del centro
THRESH_VAL = 200        # umbral binario (0-255)
RES_W, RES_H = 800, 400
CMD_IDLE = "SOL CENTRO"

class App:
    def __init__(self, root):
        self.root = root
        root.title("Seguidor de luz (OpenCV + ESP32)")
        root.geometry("1100x620")

        self.cap = None
        self.camara_encendida = False
        self.last_cmd = None
        self.ser = None

        # Lado Izquierdo: video
        left = tk.Frame(root); left.pack(side=tk.LEFT, padx=10, pady=10)
        self.lbl_video = tk.Label(left); self.lbl_video.pack()

        # Lado Derecho: controles
        right = tk.Frame(root); right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Puertos serie
        tk.Label(right, text="Puerto serie:").pack(anchor="w")
        self.cb_ports = ttk.Combobox(right, values=self._listar_puertos(), state="readonly", width=25)
        if self.cb_ports["values"]:
            self.cb_ports.current(0)
        self.cb_ports.pack(anchor="w", pady=4)

        tk.Label(right, text="Índice de cámara:").pack(anchor="w")
        self.cb_cam = ttk.Combobox(right, values=["0","1","2"], state="readonly", width=8)
        self.cb_cam.current(0); self.cb_cam.pack(anchor="w", pady=4)

        # Botones
        tk.Button(right, text="Conectar ESP32", command=self.conectar_serial, bg="#DDD").pack(fill="x", pady=6)
        tk.Button(right, text="Encender Cámara + Detección", command=self.iniciar, bg="#7ad27a").pack(fill="x", pady=6)
        tk.Button(right, text="Apagar Cámara", command=self.apagar, bg="#f07070").pack(fill="x", pady=6)
        tk.Button(right, text="Salir", command=root.destroy).pack(fill="x", pady=6)

        # Estado
        self.lbl_estado = tk.Label(right, text="Estado: sin cámara", justify=tk.LEFT)
        self.lbl_estado.pack(anchor="w", pady=8)

    def _listar_puertos(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def conectar_serial(self):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            port = self.cb_ports.get()
            if not port:
                messagebox.showwarning("Serie", "Selecciona un puerto serie primero.")
                return
            self.ser = serial.Serial(port, BAUD, timeout=0.1)
            messagebox.showinfo("Serie", f"Conectado a {port} @ {BAUD} bps")
        except Exception as e:
            messagebox.showerror("Serie", f"No se pudo abrir el puerto: {e}")

    def enviar_cmd(self, cmd):
        if not self.ser or not self.ser.is_open:
            return
        if cmd == self.last_cmd:
            return
        try:
            self.ser.write((cmd + "\n").encode())
            self.last_cmd = cmd
        except Exception:
            pass

    def iniciar(self):
        if self.camara_encendida:
            return
        idx = int(self.cb_cam.get() or 0)
        self.cap = cv2.VideoCapture(idx)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, RES_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RES_H)
        if not self.cap.isOpened():
            messagebox.showerror("Cámara", "No se pudo abrir la cámara.")
            return
        self.camara_encendida = True
        self.lbl_estado.config(text="Estado: cámara encendida")
        self._loop_video()

    def _loop_video(self):
        if not self.camara_encendida or not self.cap:
            return
        ok, frame = self.cap.read()
        if not ok:
            self.lbl_estado.config(text="Estado: sin cuadro de cámara")
            self.root.after(30, self._loop_video)
            return

        # Procesamiento: gris -> umbral -> contorno mayor -> centro
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binarizada = cv2.threshold(gray, THRESH_VAL, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binarizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h, w = gray.shape[:2]
        cx_obj, cy_obj = w//2, h//2
        cmd = CMD_IDLE

        if contours:
            cmax = max(contours, key=cv2.contourArea)
            x, y, ww, hh = cv2.boundingRect(cmax)
            cx_obj = x + ww//2
            cy_obj = y + hh//2

            # Decidir comando según tolerancia
            cx_mid, cy_mid = w//2, h//2
            dx, dy = cx_obj - cx_mid, cy_obj - cy_mid
            if abs(dx) <= TOLERANCIA and abs(dy) <= TOLERANCIA:
                cmd = "SOL CENTRO"
            else:
                if dx < -TOLERANCIA: cmd = "MOTOR IZQUIERDA"
                elif dx > TOLERANCIA: cmd = "MOTOR DERECHA"
                elif dy < -TOLERANCIA: cmd = "SERVO ARRIBA"
                elif dy > TOLERANCIA: cmd = "SERVO ABAJO"

            # Visual
            cv2.rectangle(frame, (x,y), (x+ww,y+hh), (0,255,0), 2)

        # Dibujar centro
        cv2.circle(frame, (w//2, h//2), TOLERANCIA, (255,0,0), 2)
        cv2.circle(frame, (cx_obj, cy_obj), 6, (0,0,255), -1)
        cv2.putText(frame, cmd, (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        self.enviar_cmd(cmd)

        # Mostrar en Tkinter
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(rgb))
        self.lbl_video.imgtk = imgtk
        self.lbl_video.configure(image=imgtk)

        self.root.after(10, self._loop_video)

    def apagar(self):
        self.camara_encendida = False
        self.last_cmd = None
        if self.cap:
            self.cap.release()
            self.cap = None
        self.lbl_video.config(image="")
        self.lbl_estado.config(text="Estado: cámara apagada")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
