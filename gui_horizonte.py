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
from horizonte_3d_gui import HorizonteViewer3D_GUI

class HorizonteGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏔️ Visualizador 3D de Horizonte - Ecuador")
        self.root.geometry("650x750")  # MÁS GRANDE para que todo sea visible
        self.root.resizable(True, True)
        self.root.minsize(600, 700)  # Tamaño mínimo más grande
        
        # Variables de estado
        self.viewer = None
        self.vista_actual = None
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Centrar ventana
        self.centrar_ventana()
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz."""
        
        # Título principal
        titulo = tk.Label(self.root, text="🏔️ Visualizador 3D de Horizonte", 
                         font=("Arial", 16, "bold"), fg="darkblue")
        titulo.pack(pady=10)
        
        subtitulo = tk.Label(self.root, text="Ecuador Continental", 
                           font=("Arial", 12), fg="gray")
        subtitulo.pack(pady=(0, 10))
        
        # === CREAR CANVAS CON SCROLLBAR PARA CONTENIDO ===
        # Frame contenedor para canvas y scrollbar
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Canvas principal
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        
        # Scrollbar vertical
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Frame principal DENTRO del canvas
        self.main_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        # Configurar scroll con rueda del mouse
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Configurar actualización del scroll region
        def configure_scroll_region(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        self.main_frame.bind("<Configure>", configure_scroll_region)
        
        # Configurar ancho del frame interno
        def configure_canvas_width(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind("<Configure>", configure_canvas_width)
        
        # === CONTENIDO ORIGINAL (usando main_frame en lugar de main_frame) ===
        
        # === SECCIÓN 1: UBICACIONES PRECONFIGURADAS ===
        ubicaciones_frame = tk.LabelFrame(self.main_frame, text="📍 Ubicaciones Preconfiguradas", 
                                        font=("Arial", 11, "bold"), padx=10, pady=10)
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
        ubicacion_combo = ttk.Combobox(ubicaciones_frame, textvariable=self.ubicacion_var,
                                     values=list(self.ubicaciones.keys()), 
                                     state="readonly", width=40)
        ubicacion_combo.pack(pady=5)
        ubicacion_combo.bind("<<ComboboxSelected>>", self.cargar_ubicacion)
        
        # === SECCIÓN 2: COORDENADAS PERSONALIZADAS ===
        coords_frame = tk.LabelFrame(self.main_frame, text="🗺️ Coordenadas Personalizadas", 
                                   font=("Arial", 11, "bold"), padx=10, pady=10)
        coords_frame.pack(fill="x", pady=(0, 15))
        
        # Latitud
        lat_frame = tk.Frame(coords_frame)
        lat_frame.pack(fill="x", pady=5)
        tk.Label(lat_frame, text="Latitud:", width=12, anchor="w").pack(side="left")
        self.lat_var = tk.StringVar(value="-0.1807")
        lat_entry = tk.Entry(lat_frame, textvariable=self.lat_var, width=15)
        lat_entry.pack(side="left", padx=(5, 10))
        tk.Label(lat_frame, text="(Ej: -2.1709)", fg="gray").pack(side="left")
        
        # Longitud
        lon_frame = tk.Frame(coords_frame)
        lon_frame.pack(fill="x", pady=5)
        tk.Label(lon_frame, text="Longitud:", width=12, anchor="w").pack(side="left")
        self.lon_var = tk.StringVar(value="-78.4678")
        lon_entry = tk.Entry(lon_frame, textvariable=self.lon_var, width=15)
        lon_entry.pack(side="left", padx=(5, 10))
        tk.Label(lon_frame, text="(Ej: -79.9224)", fg="gray").pack(side="left")
        
        # === SECCIÓN 3: DIRECCIÓN DE VISTA ===
        direccion_frame = tk.LabelFrame(self.main_frame, text="🧭 Dirección de Vista", 
                                      font=("Arial", 11, "bold"), padx=10, pady=10)
        direccion_frame.pack(fill="x", pady=(0, 15))
        
        # Azimut con slider
        azimut_frame = tk.Frame(direccion_frame)
        azimut_frame.pack(fill="x", pady=5)
        
        tk.Label(azimut_frame, text="Azimut:", width=12, anchor="w").pack(side="left")
        self.azimut_var = tk.IntVar(value=90)
        azimut_scale = tk.Scale(azimut_frame, from_=0, to=359, orient="horizontal",
                              variable=self.azimut_var, command=self.actualizar_direccion)
        azimut_scale.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        self.direccion_label = tk.Label(azimut_frame, text="Este", fg="darkgreen", 
                                      font=("Arial", 10, "bold"), width=10)
        self.direccion_label.pack(side="right")
        
        # Botones de dirección rápida
        botones_frame = tk.Frame(direccion_frame)
        botones_frame.pack(pady=10)
        
        direcciones = [("Norte", 0), ("Este", 90), ("Sur", 180), ("Oeste", 270)]
        for texto, valor in direcciones:
            btn = tk.Button(botones_frame, text=texto, width=8,
                          command=lambda v=valor: self.set_azimut(v))
            btn.pack(side="left", padx=5)
        
        # === SECCIÓN 4: CONTROLES ===
        # Frame de controles JUSTO DESPUÉS de dirección
        controles_frame = tk.LabelFrame(self.main_frame, text="🎮 Controles", 
                                      font=("Arial", 11, "bold"), padx=10, pady=15)
        controles_frame.pack(fill="x", pady=20)
        
        # Botón generar vista - MÁS GRANDE Y VISIBLE
        self.btn_generar = tk.Button(controles_frame, text="🏔️ GENERAR VISTA 3D", 
                                   font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                                   command=self.generar_vista, height=2, relief="raised", bd=3)
        self.btn_generar.pack(fill="x", padx=10, pady=5)
        
        # Botón salir
        btn_salir = tk.Button(controles_frame, text="❌ Salir", 
                            font=("Arial", 10), bg="#f44336", fg="white",
                            command=self.root.quit, height=1)
        btn_salir.pack(fill="x", padx=10, pady=(5, 10))
        
        # === SECCIÓN 5: INFORMACIÓN ACTUAL (MOVIDA ABAJO) ===
        info_frame = tk.LabelFrame(self.main_frame, text="📊 Información", 
                                 font=("Arial", 10), padx=10, pady=5)
        info_frame.pack(fill="x", pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=3, wrap="word", state="disabled",
                               bg="#f0f0f0", font=("Courier", 8))
        self.info_text.pack(fill="x", pady=3)
        
        self.actualizar_info()
        
        # === ESPACIO FINAL ===
        espacio_final = tk.Frame(self.main_frame, height=30, bg="white")
        espacio_final.pack(fill="x", pady=10)
        
        # === STATUS BAR (FUERA DEL CANVAS) ===
        self.status_var = tk.StringVar(value="✅ Listo para generar vista 3D")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                            relief="sunken", anchor="w", bg="lightgray", height=1)
        status_bar.pack(side="bottom", fill="x")
        
        # Actualizar dirección inicial
        self.actualizar_direccion()
        
        # Actualizar scroll region después de crear todo
        self.main_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def cargar_ubicacion(self, event=None):
        """Carga una ubicación preconfigurada."""
        ubicacion = self.ubicacion_var.get()
        if ubicacion in self.ubicaciones:
            lat, lon = self.ubicaciones[ubicacion]
            self.lat_var.set(str(lat))
            self.lon_var.set(str(lon))
            self.actualizar_info()
            self.status_var.set(f"📍 Ubicación cargada: {ubicacion}")
    
    def set_azimut(self, valor):
        """Establece el azimut usando botones rápidos."""
        self.azimut_var.set(valor)
        self.actualizar_direccion()
    
    def actualizar_direccion(self, event=None):
        """Actualiza la etiqueta de dirección cardinal."""
        azimut = self.azimut_var.get()
        direccion = self.obtener_direccion_cardinal(azimut)
        self.direccion_label.config(text=direccion)
        self.actualizar_info()
    
    def obtener_direccion_cardinal(self, angulo):
        """Convierte ángulo a dirección cardinal."""
        angulo = angulo % 360
        if angulo < 22.5 or angulo >= 337.5:
            return "Norte"
        elif angulo < 67.5:
            return "Noreste"
        elif angulo < 112.5:
            return "Este"
        elif angulo < 157.5:
            return "Sureste"
        elif angulo < 202.5:
            return "Sur"
        elif angulo < 247.5:
            return "Suroeste"
        elif angulo < 292.5:
            return "Oeste"
        else:
            return "Noroeste"
    
    def actualizar_info(self):
        """Actualiza el panel de información."""
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            azimut = self.azimut_var.get()
            direccion = self.obtener_direccion_cardinal(azimut)
            
            info = f"""📍 Lat: {lat:.6f}°, Lon: {lon:.6f}°
🧭 Azimut: {azimut}° ({direccion})
⚙️ Radio: 150km | Campo: 90° | Altura: Terreno+1.7m"""
            
            self.info_text.config(state="normal")
            self.info_text.delete(1.0, "end")
            self.info_text.insert(1.0, info)
            self.info_text.config(state="disabled")
            
        except ValueError:
            self.info_text.config(state="normal")
            self.info_text.delete(1.0, "end")
            self.info_text.insert(1.0, "❌ Coordenadas inválidas")
            self.info_text.config(state="disabled")
    
    def validar_coordenadas(self):
        """Valida que las coordenadas sean correctas."""
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            
            # Validar rangos para Ecuador
            if not (-5 <= lat <= 2):
                messagebox.showerror("Error", "Latitud debe estar entre -5° y 2° (Ecuador)")
                return False
            
            if not (-82 <= lon <= -75):
                messagebox.showerror("Error", "Longitud debe estar entre -82° y -75° (Ecuador)")
                return False
            
            return True
            
        except ValueError:
            messagebox.showerror("Error", "Coordenadas deben ser números válidos")
            return False
    
    def generar_vista_thread(self, lat, lon, azimut):
        """Genera la vista 3D en un hilo separado."""
        try:
            self.status_var.set("🔄 Generando vista 3D...")
            self.btn_generar.config(state="disabled", text="⏳ Generando...")
            
            # Crear viewer si no existe
            if self.viewer is None:
                self.viewer = HorizonteViewer3D_GUI()
            
            # Generar vista
            self.vista_actual = self.viewer.vista_3d_realista(
                lat, lon, azimut, campo_vision=90, radio_km=150
            )
            
            self.status_var.set("✅ Vista 3D generada exitosamente")
            self.btn_generar.config(state="normal", text="🏔️ Generar Vista 3D")
            
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")
            self.btn_generar.config(state="normal", text="🏔️ Generar Vista 3D")
            messagebox.showerror("Error", f"No se pudo generar la vista 3D:\n{str(e)}")
    
    def generar_vista(self):
        """Inicia la generación de la vista 3D."""
        if not self.validar_coordenadas():
            return
        
        lat = float(self.lat_var.get())
        lon = float(self.lon_var.get())
        azimut = self.azimut_var.get()
        
        # Confirmar acción
        respuesta = messagebox.askyesno(
            "Generar Vista 3D",
            f"¿Generar vista 3D para:\n\n"
            f"📍 Latitud: {lat:.6f}°\n"
            f"📍 Longitud: {lon:.6f}°\n"
            f"🧭 Dirección: {azimut}° ({self.obtener_direccion_cardinal(azimut)})\n\n"
            f"Esto abrirá una ventana 3D separada."
        )
        
        if respuesta:
            # Ejecutar en hilo separado para no bloquear la GUI
            thread = threading.Thread(
                target=self.generar_vista_thread,
                args=(lat, lon, azimut),
                daemon=True
            )
            thread.start()
    
    def ejecutar(self):
        """Ejecuta la interfaz gráfica."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Interfaz cerrada por el usuario")


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
