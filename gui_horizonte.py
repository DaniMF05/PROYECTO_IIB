"""
INTERFAZ GRÁFICA PARA VISUALIZADOR 3D DE HORIZONTE - ECUADOR
Interfaz simple para configurar coordenadas y dirección de vista.

🎯 CARACTERÍSTICAS:
- Entrada de coordenadas personalizadas
- Selector de dirección (azimut)
- Ubicaciones preconfiguradas
- Información en tiempo real
- Integración con visualizador 3D
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import math
import tkintermapview 
from horizonte_3d_gui import HorizonteViewer3D_GUI

class Compass(tk.Canvas):
    """Widget de brújula interactiva para seleccionar el azimut."""
    def __init__(self, parent, width=150, height=150, variable=None, command=None):
        super().__init__(parent, width=width, height=height, bg=parent.cget('bg'), highlightthickness=0)
        self.variable = variable if variable else tk.DoubleVar(value=90.0)
        self.command = command
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.radius = min(self.center_x, self.center_y) * 0.8

        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Button-1>", self._on_click)
        self._draw_compass()

    def _draw_compass(self):
        self.delete("all")
        # Dibuja el cuerpo de la brújula
        self.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                         self.center_x + self.radius, self.center_y + self.radius,
                         outline="gray", width=2)
        
        # Dibuja las etiquetas cardinales
        for angle, label in [(0, "N"), (90, "E"), (180, "S"), (270, "O")]:
            rad = math.radians(angle - 90)
            x = self.center_x + self.radius * 1.15 * math.cos(rad)
            y = self.center_y + self.radius * 1.15 * math.sin(rad)
            self.create_text(x, y, text=label, font=("Arial", 10, "bold"))
        
        # Dibuja la aguja
        azimut = self.variable.get()
        rad = math.radians(azimut - 90)
        x_end = self.center_x + self.radius * 0.9 * math.cos(rad)
        y_end = self.center_y + self.radius * 0.9 * math.sin(rad)
        
        # Aguja principal (Roja)
        self.create_line(self.center_x, self.center_y, x_end, y_end,
                         fill="red", width=3, arrow=tk.LAST)
        # Contrapeso de la aguja (Gris)
        x_start = self.center_x - self.radius * 0.3 * math.cos(rad)
        y_start = self.center_y - self.radius * 0.3 * math.sin(rad)
        self.create_line(x_start, y_start, self.center_x, self.center_y, fill="gray", width=3)
        self.create_oval(self.center_x - 5, self.center_y - 5, self.center_x + 5, self.center_y + 5, fill="black")

    def _update_azimut(self, event):
        dx = event.x - self.center_x
        dy = event.y - self.center_y
        # Atan2 devuelve el ángulo en radianes. +90 para ajustar el 0 al Norte.
        angle = math.degrees(math.atan2(dy, dx)) + 90
        if angle < 0:
            angle += 360
        self.variable.set(round(angle, 1))
        self._draw_compass()
        if self.command:
            self.command(self.variable.get())

    def _on_click(self, event):
        self._update_azimut(event)

    def _on_drag(self, event):
        self._update_azimut(event)
        
    def set(self, angle):
        self.variable.set(angle)
        self._draw_compass()
        if self.command:
            self.command(self.variable.get())
            
            
class HorizonteGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏔️ Visualizador 3D de Horizonte - Ecuador")
        # Geometría más ancha para el mapa
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
        
        self.viewer = None
        self.crear_interfaz()
        self.centrar_ventana()
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def crear_interfaz(self):
        # Frame principal para dividir en dos columnas: controles (izquierda) y mapa (derecha)
        # Status Bar
        self.status_var = tk.StringVar(value="✅ Listo")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", bg="lightgray")
        status_bar.pack(side="top", fill="x")
        
        
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)     
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === COLUMNA IZQUIERDA: CONTROLES CON SCROLLBAR VERTICAL ===
        controls_container = tk.Frame(main_pane, width=400)
        main_pane.add(controls_container, stretch="never")

        canvas = tk.Canvas(controls_container, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(controls_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === CONTENIDO DE LA COLUMNA IZQUIERDA (antes en controls_frame) ===

        # Título
        titulo = tk.Label(scrollable_frame, text="Configuración de Vista", font=("Arial", 16, "bold"), fg="darkblue")
        titulo.pack(pady=(5, 15), anchor="w")

        # --- UBICACIONES PRECONFIGURADAS ---
        ubicaciones_frame = tk.LabelFrame(scrollable_frame, text="📍 Ubicaciones Preconfiguradas", font=("Arial", 11, "bold"), padx=10, pady=10)
        ubicaciones_frame.pack(fill="x", pady=(0, 15))

        self.ubicaciones = {
            "Quito - Vista hacia Cotopaxi": (-0.1807, -78.4678),
            "Guayaquil - Vista hacia cordillera": (-2.1709, -79.9224),
            "Guayaquil → Chimborazo": (-2.1709, -79.9224),
            "Cuenca - Ciudad colonial": (-2.9001, -79.0059),
            "Ambato - Valle central": (-1.2549, -78.6291),
            "Esmeraldas - Costa norte": (0.9538, -79.6528),
            "Cerro Montecristi": (-1.0339, -80.6701),
            "Volcán Cotopaxi": (-0.6137, -78.4729),
            "Norte de Quito": (-0.2292, -78.5182)
        }
        self.ubicacion_var = tk.StringVar(value="Seleccionar ubicación...")
        ubicacion_combo = ttk.Combobox(ubicaciones_frame, textvariable=self.ubicacion_var, values=list(self.ubicaciones.keys()), state="readonly")
        ubicacion_combo.pack(fill="x", pady=5)
        ubicacion_combo.bind("<<ComboboxSelected>>", self.cargar_ubicacion)

        # --- COORDENADAS (AHORA SOLO LECTURA, ACTUALIZADO POR EL MAPA) ---
        coords_frame = tk.LabelFrame(scrollable_frame, text="🗺️ Coordenadas (Seleccionadas en el mapa)", font=("Arial", 11, "bold"), padx=10, pady=10)
        coords_frame.pack(fill="x", pady=(0, 15))
        self.lat_var = tk.StringVar(value="-0.1807")
        self.lon_var = tk.StringVar(value="-78.4678")

        tk.Label(coords_frame, text="Latitud:").grid(row=0, column=0, sticky="w", pady=2)
        tk.Entry(coords_frame, textvariable=self.lat_var, state="readonly").grid(row=0, column=1, sticky="ew")
        tk.Label(coords_frame, text="Longitud:").grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(coords_frame, textvariable=self.lon_var, state="readonly").grid(row=1, column=1, sticky="ew")
        coords_frame.grid_columnconfigure(1, weight=1)

        # --- NUEVA SECCIÓN: PARÁMETROS DE CÁMARA ---
        cam_params_frame = tk.LabelFrame(scrollable_frame, text="📷 Parámetros de Cámara", font=("Arial", 11, "bold"), padx=10, pady=10)
        cam_params_frame.pack(fill="x", pady=(0, 15))

        # ALTURA SOBRE EL TERRENO
        self.altura_var = tk.DoubleVar(value=1.7)  # Altura de una persona por defecto
        tk.Label(cam_params_frame, text="Altura sobre el terreno (m):").grid(row=0, column=0, sticky="w", pady=4)
        altura_spinbox = tk.Spinbox(cam_params_frame, from_=0, to=500, increment=1, textvariable=self.altura_var, width=10)
        altura_spinbox.grid(row=0, column=1, sticky="e")

        # CAMPO DE VISIÓN (ZOOM)
        self.fov_var = tk.IntVar(value=60)  # Zoom realista por defecto
        tk.Label(cam_params_frame, text="Campo de Visión / Zoom (°):").grid(row=1, column=0, sticky="w", pady=4)
        fov_scale = tk.Scale(cam_params_frame, from_=20, to=120, orient="horizontal", variable=self.fov_var)
        fov_scale.grid(row=1, column=1, sticky="ew")
        cam_params_frame.grid_columnconfigure(1, weight=1)

        # --- DIRECCIÓN DE VISTA (BRÚJULA INTERACTIVA) ---
        direccion_frame = tk.LabelFrame(scrollable_frame, text="🧭 Dirección de Vista", font=("Arial", 11, "bold"), padx=10, pady=10)
        direccion_frame.pack(fill="x", pady=(0, 15))

        self.azimut_var = tk.DoubleVar(value=0.0)  # Apuntando al Norte por defecto
        self.azimut_label = tk.Label(direccion_frame, text="", font=("Arial", 10, "bold"))
        self.azimut_label.pack()

        self.compass_widget = Compass(direccion_frame, variable=self.azimut_var, command=self.actualizar_direccion_label)
        self.compass_widget.pack(pady=5)
        self.actualizar_direccion_label()

        # --- CONTROLES ---
        controles_frame = tk.LabelFrame(scrollable_frame, text="🎮 Acciones", font=("Arial", 11, "bold"), padx=10, pady=15)
        controles_frame.pack(fill="x", pady=10)

        self.btn_generar = tk.Button(controles_frame, text="🏔️ GENERAR VISTA 3D", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=self.generar_vista, height=2)
        self.btn_generar.pack(fill="x", padx=10, pady=5)

        # === COLUMNA DERECHA: MAPA INTERACTIVO y cuadro de información ===
        right_frame = tk.Frame(main_pane)
        main_pane.add(right_frame, stretch="always")

        right_frame.grid_rowconfigure(0, weight=6)  # 60%
        right_frame.grid_rowconfigure(1, weight=4)  # 40%
        right_frame.grid_columnconfigure(0, weight=1)

        # Mapa
        map_frame = tk.LabelFrame(right_frame, text="Haga clic en el mapa para seleccionar la ubicación", font=("Arial", 11, "bold"), padx=5, pady=5)
        map_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.map_widget = tkintermapview.TkinterMapView(map_frame, width=550, height=450, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_position(-0.1807, -78.4678)  # Quito inicial
        self.map_widget.set_zoom(10)

        self.map_marker = self.map_widget.set_marker(-0.1807, -78.4678, text="Observador")
        self.map_widget.add_left_click_map_command(self.map_click_callback)

        # Cuadro de información con scrollbar
        info_frame = tk.LabelFrame(right_frame, text="📋 Información", font=("Arial", 11, "bold"), padx=5, pady=5)
        info_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        info_canvas = tk.Canvas(info_frame, borderwidth=0, highlightthickness=0)
        info_canvas.pack(side="left", fill="both", expand=True)

        scrollbar_info = tk.Scrollbar(info_frame, orient="vertical", command=info_canvas.yview)
        scrollbar_info.pack(side="right", fill="y")

        info_canvas.configure(yscrollcommand=scrollbar_info.set)

        self.info_content = tk.Frame(info_canvas)
        info_canvas.create_window((0, 0), window=self.info_content, anchor="nw")

        def on_info_frame_configure(event):
            info_canvas.configure(scrollregion=info_canvas.bbox("all"))

        self.info_content.bind("<Configure>", on_info_frame_configure)

        # Ejemplo texto inicial largo para info
        self.info_label = tk.Label(self.info_content, text="Aquí se mostrará la información detallada.\n", justify="left", anchor="nw")
        self.info_label.pack(fill="both", expand=True)

    def map_click_callback(self, coords):
        lat, lon = coords
        self.lat_var.set(f"{lat:.6f}")
        self.lon_var.set(f"{lon:.6f}")
        self.map_marker.set_position(lat, lon)
        self.status_var.set(f"Nuevas coordenadas seleccionadas: Lat {lat:.4f}, Lon {lon:.4f}")
        self.ubicacion_var.set("Ubicación personalizada")

    def cargar_ubicacion(self, event=None):
        ubicacion_nombre = self.ubicacion_var.get()
        if ubicacion_nombre in self.ubicaciones:
            lat, lon = self.ubicaciones[ubicacion_nombre]
            self.lat_var.set(str(lat))
            self.lon_var.set(str(lon))
            self.map_widget.set_position(lat, lon)
            self.map_marker.set_position(lat, lon)
            self.status_var.set(f"📍 Ubicación cargada: {ubicacion_nombre}")

    def actualizar_direccion_label(self, event=None):
        azimut = self.azimut_var.get()
        direccion = self.obtener_direccion_cardinal(azimut)
        self.azimut_label.config(text=f"Azimut: {azimut:.1f}° ({direccion})")

    def obtener_direccion_cardinal(self, angulo):
        direcciones = ["Norte", "Noreste", "Este", "Sureste", "Sur", "Suroeste", "Oeste", "Noroeste"]
        indice = round(angulo / 45) % 8
        return direcciones[indice]

    def validar_coordenadas(self):
        # La validación ahora es menos crítica ya que se eligen del mapa
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            if not (-8 <= lat < 4):
                messagebox.showerror("Error", "Latitud fuera del rango de datos de Ecuador.")
                return False
            if not (-82 <= lon < -72):
                messagebox.showerror("Error", "Longitud fuera del rango de datos de Ecuador.")
                return False
            return True
        except ValueError:
            messagebox.showerror("Error", "Coordenadas inválidas.")
            return False

    def validar_altura(self):
        try:
            altura = float(self.altura_var.get())
            if altura < 0 or altura > 500:   
                messagebox.showerror("Error", "Altura debe estar entre 0 m y 500 m.")
                return False    
            return True
        except ValueError:
            messagebox.showerror("Error", "Altura inválida.")
            return False
        
    def actualizar_info(self, texto):
        """Actualiza el cuadro de información con texto formateado."""
        self.info_label.config(text=texto)
        # Forzar refresco del scroll region
        self.info_content.update_idletasks()
    
    def generar_vista_thread(self, lat, lon, azimut, altura, fov):
        try:
            self.status_var.set("🔄 Generando vista 3D... Esto puede tardar unos segundos.")
            self.btn_generar.config(state="disabled", text="⏳ Generando...")
            
            if self.viewer is None:
                self.viewer = HorizonteViewer3D_GUI()
            
            # Pasar los nuevos parámetros al visualizador
            info_gui = self.viewer.vista_3d_realista(
                lat_observador=lat, 
                lon_observador=lon, 
                azimut=azimut, 
                campo_vision=fov, 
                altura_sobre_terreno=altura,
                radio_km=150
            )
            info_text = (
                f"📍 Coordenadas: Lat {info_gui['coordenadas'][0]:.6f}°, Lon {info_gui['coordenadas'][1]:.6f}°\n"
                f"🧭 Dirección: {info_gui['azimut_actual'][0]:.1f}° ({info_gui['direccion_cardinal']})\n"
                f"↕️ Altura observador: {info_gui['altura_observador']:.2f} m\n"
                f"📏 Radio terreno simulado: {info_gui['radio_km']} km\n"
                f"📊 Puntos renderizados: {info_gui['puntos_terreno']:,}\n"
                f"⛰️ Elevación máxima: {info_gui['elevacion_max']:.0f} m\n"
                f"🌄 Elevación mínima: {info_gui['elevacion_min']:.0f} m\n"
                f"⌨️ Controles: ← → (rotar), + - (zoom)\n"
            )

            # Actualizar info en GUI (en hilo principal)
            self.root.after(0, self.actualizar_info, info_text)
            
            self.status_var.set("✅ Vista 3D generada exitosamente. Puede cerrar la ventana 3D.")
        except Exception as e:
            self.status_var.set(f"❌ Error: {e}")
            messagebox.showerror("Error al Generar Vista", f"No se pudo generar la vista 3D:\n\n{e}")
        finally:
            self.btn_generar.config(state="normal", text="🏔️ GENERAR VISTA 3D")

    def generar_vista(self):
        if not self.validar_coordenadas():
            return
        
        lat = float(self.lat_var.get())
        lon = float(self.lon_var.get())
        azimut = self.azimut_var.get()
        altura = self.altura_var.get()
        fov = self.fov_var.get()
        
        if not self.validar_altura():
            return
        
        msg = (f"¿Generar vista con los siguientes parámetros?\n\n"
               f"📍 Lat: {lat:.4f}°, Lon: {lon:.4f}°\n"
               f"🧭 Dirección: {azimut:.1f}° ({self.obtener_direccion_cardinal(azimut)})\n"
               f"↕️ Altura sobre terreno: {altura:.1f} m\n"
               f"👁️ Campo de Visión: {fov}°\n\n"
               f"La simulación se abrirá en una nueva ventana.")

        if messagebox.askyesno("Confirmar Simulación", msg):
            thread = threading.Thread(
                target=self.generar_vista_thread,
                args=(lat, lon, azimut, altura, fov),
                daemon=True
            )
            thread.start()
    
    def ejecutar(self):
        self.root.mainloop()

def main():
    """Función principal para ejecutar la GUI."""
    print("🏔️ Iniciando Interfaz Gráfica del Visualizador 3D")
    print("=" * 50)
    
    try:
        app = HorizonteGUI()
        app.ejecutar()
    except Exception as e:
        print(f"❌ Error en la interfaz: {e}")
        messagebox.showerror("Error Crítico", f"No se pudo iniciar la interfaz:\n{str(e)}")


if __name__ == "__main__":
    main()
