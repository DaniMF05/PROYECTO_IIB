"""
VISUALIZADOR 3D DE HORIZONTE - ECUADOR (VERSIÓN PARA GUI)
Genera vistas 3D realistas del horizonte para integración con interfaz gráfica.

🔧 CONFIGURACIÓN:
- Radio fijo: 150km para todas las vistas
- Resolución: 2000 puntos máximo para rendimiento óptimo
- Sin contornos para evitar artefactos visuales
- Altura altura variable, por defecto 1.7m

💡 CARACTERÍSTICAS:
- Solo usa PyVista para renderizado 3D de alta calidad
- Mapeo de color corregido para correspondencia exacta
- Marcadores de verificación para elevaciones máximas y mínimas
- Visualización interactiva con teclado (solo rotación y zoom)
- Orientación geográfica corregida (Norte/Sur/Este/Oeste)
- Preparado para integración con GUI externa
- Manejo de errores para altura y coordenadas inválidas
- Brujula interactiva para indicar dirección actual
"""

import numpy as np
import math
import pyvista as pv
from pyvista import Actor
import vtk
from vtk.util import numpy_support  # type: ignore
from PIL import Image
from simulador_horizonte_corregido import SimuladorHorizonte

class HorizonteViewer3D_GUI(SimuladorHorizonte):
    """
    Visualizador 3D del horizonte adaptado para interfaz gráfica,
    basado en datos de elevación del SimuladorHorizonte.
    """
    
    def __init__(self, carpeta_matrices='Matrices'):
        super().__init__(carpeta_matrices)
        print("🏔️  VISUALIZADOR 3D DE HORIZONTE INICIALIZADO (GUI)")
        print("📍 Coordenadas corregidas para Ecuador continental")
    
    def vista_3d_realista(self, lat_observador, lon_observador, azimut=90, 
                         campo_vision=90, radio_km=150, altura_sobre_terreno=1.7):
        """
        Genera una vista 3D realista del horizonte usando PyVista para GUI.
        
        Args:
            lat_observador, lon_observador: Coordenadas del observador.
            azimut: Dirección de vista (0=Norte, 90=Este, 180=Sur, 270=Oeste).
            campo_vision: Ángulo de campo de visión en grados.
            radio_km: Radio de terreno a mostrar (kilómetros).
            altura_sobre_terreno: Altura del observador sobre el terreno en metros.
        
        Returns:
            dict: Información del renderizado para la GUI, o un error.
        """
        print(f"🎯 GENERANDO VISTA 3D PARA GUI")
        print(f"📍 Posición: ({lat_observador:.6f}°, {lon_observador:.6f}°)")
        print(f"🧭 Azimut: {azimut}° | Campo visión: {campo_vision}°")
        print(f"📏 Radio: {radio_km}km")
        print(f"⛰️  Vista natural sin exageración")
        
        return self._vista_pyvista_gui(lat_observador, lon_observador, azimut, 
                                     campo_vision, radio_km, altura_sobre_terreno)
        
    def _crear_brujula_imagen(self, plotter, compass_image_path, azimut_inicial=0):
        """
        Crea un actor de imagen de brújula 2D y lo añade al plotter.
        El actor se coloca en la esquina inferior izquierda por defecto.
        
        Args:
            plotter: El objeto pyvista.Plotter.
            compass_image_path: La ruta al archivo de imagen de la brújula.
            
        Returns:
            El actor de la imagen creado.
        """
        try:
           # 1. Cargar imagen PIL (200x200 px)
            img = Image.open(compass_image_path).convert("RGBA")
            img = img.resize((150, 150), Image.Resampling.BILINEAR) #Redimensionamos
            
            # 2. Corregir orientación de la imagen (flip vertical para que no salga invertida)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            # 3. Crear vtkImageData con rotación inicial
            compass_data = self._crear_compass_vtk_data(img, azimut_inicial)
            
            # 4. Crear mapper 2D
            mapper = vtk.vtkImageMapper()
            mapper.SetInputData(compass_data)
            mapper.SetColorWindow(255)
            mapper.SetColorLevel(127.5)

            # 5. Crear actor 2D
            actor2d = vtk.vtkActor2D()
            actor2d.SetMapper(mapper)

            # 6. Posicionar en esquina superior derecha, un poco más abajo (50 px extra)
            margin = 20
            win_width, win_height = plotter.window_size
            width, height = img.size
            actor2d.GetPositionCoordinate().SetCoordinateSystemToDisplay()
            actor2d.SetPosition(win_width - width - margin -150 , win_height -height - margin -250)  # margen abajo

            # 7. Añadir actor al renderer
            plotter.renderer.AddActor2D(actor2d)

            # 8. Función para actualizar la rotación
            def actualizar_rotacion(angulo_degrees):
                try:
                    # Crear nueva imagen rotada (giramos positivo para que coincida con cámara)
                    compass_data_rotated = self._crear_compass_vtk_data(img, -angulo_degrees)
                    mapper.SetInputData(compass_data_rotated)
                    mapper.Modified()
                    actor2d.Modified()
                except Exception as e:
                    print(f"Error al rotar brújula: {e}")

            return {
                'actor': actor2d,
                'actualizar_rotacion': actualizar_rotacion
            }
        
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo de imagen de la brújula en '{compass_image_path}'.")
            return None
        except Exception as e:
            print(f"❌ Error al crear el actor de la brújula: {e}")
            return None
        
    def _crear_compass_vtk_data(self, img_pil, angulo_degrees):
        """
        Crea vtkImageData desde una imagen PIL rotada.
        
        Args:
            img_pil: Imagen PIL de la brújula.
            angulo_degrees: Ángulo de rotación en grados.
            
        Returns:
            vtkImageData con la imagen rotada.
        """
        # Rotar la imagen PIL (positivo para coincidir con cámara)
        img_rotated = img_pil.rotate(angulo_degrees, expand=False, fillcolor=(0, 0, 0, 0))
        img_data = np.array(img_rotated)

        # Crear vtkImageData
        height, width, _ = img_data.shape
        vtk_img = vtk.vtkImageData()
        vtk_img.SetDimensions(width, height, 1)
        vtk_img.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 4)

        # Copiar los datos de la imagen a vtkImageData
        flat_img = img_data.reshape(-1, 4)
        vtk_array = numpy_support.numpy_to_vtk(flat_img, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        vtk_img.GetPointData().SetScalars(vtk_array)

        return vtk_img
    
    def _vista_pyvista_gui(self, lat, lon, azimut, campo_vision, radio_km, altura_sobre_terreno):
        """
        Método interno para generar la vista de PyVista.
        Corrige la lógica de cámara, controles y el error original.
        """
        try:
            import pyvista as pv
        except ImportError:
            raise ImportError("PyVista no está instalado. Ejecute: pip install pyvista")
        
        if self.matriz_terreno is None:
            self.cargar_terreno_ecuador()
        
        # Obtener datos del observador
        try:
            i_obs, j_obs = self.coordenadas_a_indices(lat, lon)
            altura_terreno = self.matriz_terreno[i_obs, j_obs]
        except ValueError as e:
            raise ValueError(f"Error en coordenadas del observador: {e}")
        
        if altura_terreno < -1000:
            raise ValueError(f"Posición inválida o en el mar. Altura del terreno: {altura_terreno}m. Elija otro punto.")

        # Altura corregida del observador
        altura_observador_real = altura_terreno + altura_sobre_terreno
        
        # --- Extraer y Submuestrear Terreno ---
        paso_metros = (1 / (self.resolucion - 1)) * 111000
        radio_indices = int((radio_km * 1000) / paso_metros)
        
        i_min = max(0, i_obs - radio_indices)
        i_max = min(self.matriz_terreno.shape[0], i_obs + radio_indices)
        j_min = max(0, j_obs - radio_indices)
        j_max = min(self.matriz_terreno.shape[1], j_obs + radio_indices)
        
        step = max(1, radio_indices // 2000)
        terreno_region = self.matriz_terreno[i_min:i_max:step, j_min:j_max:step]
        
        # --- Crear la malla del terreno ---
        filas, columnas = terreno_region.shape
        Z = terreno_region.astype(float)
        Z[Z == -32768] = 0
        Z_km = Z / 1000
        
        x_coords = np.arange(columnas) * paso_metros * step / 1000
        y_coords = np.arange(filas) * paso_metros * step / 1000
        
        obs_x = (j_obs - j_min) * paso_metros / 1000
        obs_y = (i_obs - i_min) * paso_metros / 1000
        x_coords = x_coords - obs_x
        y_coords = y_coords - obs_y
        y_coords = -y_coords # Corrección de orientación para PyVista
        
        X, Y = np.meshgrid(x_coords, y_coords)
        superficie = pv.StructuredGrid(X, Y, Z_km)
        
        # --- Mapeo de colores (lógica original) ---
        puntos_terreno = superficie.points
        elevaciones_terreno = puntos_terreno[:, 2] * 1000
        
        print(f"   🎨 PROCESANDO COLORES DEL TERRENO:")
        print(f"      Puntos del terreno: {superficie.n_points}")
        print(f"      Rango elevaciones: {np.min(elevaciones_terreno):.0f}m - {np.max(elevaciones_terreno):.0f}m")
        
        min_total = np.min(elevaciones_terreno)
        max_total = np.max(elevaciones_terreno)
        elevaciones_norm_terreno = np.zeros_like(elevaciones_terreno, dtype=float)
        
        for i, elev in enumerate(elevaciones_terreno):
            if elev <= 10:
                if elev <= 0:
                    elevaciones_norm_terreno[i] = 0.0
                else:
                    elevaciones_norm_terreno[i] = 0.0 + (elev / 10) * 0.15
            elif elev <= 20:
                elevaciones_norm_terreno[i] = 0.15 + ((elev - 10) / 10) * 0.15
            else:
                if max_total > 20:
                    elevaciones_norm_terreno[i] = 0.3 + ((elev - 20) / (max_total - 20)) * 0.7
                else:
                    elevaciones_norm_terreno[i] = 0.3
        
        superficie["elevacion"] = elevaciones_norm_terreno
        
        # --- Encontrar puntos min/max para info de GUI ---
        max_idx = np.unravel_index(np.argmax(Z), Z.shape)
        min_valid_z = Z[Z > 0]
        if len(min_valid_z) > 0:
            min_val = np.min(min_valid_z)
            min_idx = np.unravel_index(np.argmin(np.where(Z > 0, Z, np.inf)), Z.shape)
        else:
            min_idx = max_idx
            min_val = Z[max_idx]
        
        max_x = x_coords[max_idx[1]]
        max_y = y_coords[max_idx[0]]
        max_z = Z_km[max_idx]

        print(f"   Punto máximo: ({max_x:.2f}, {max_y:.2f}, {max_z:.3f}) = {Z[max_idx]:.0f}m")
        print(f"   ✅ Terreno procesado para GUI")

        # --- Configuración del Plotter y Cámara ---
        plotter = pv.Plotter(window_size=[1400, 900])
        plotter.set_background('lightblue')
        
        # Configurar renderizado de profundidad
        plotter.renderer.SetUseDepthPeeling(True)
        plotter.renderer.SetMaximumNumberOfPeels(4)
        plotter.renderer.SetOcclusionRatio(0.1)
        
        # Agregar el terreno con el esquema de color personalizado
        plotter.add_mesh(
            superficie, 
            scalars="elevacion", 
            cmap="gist_earth",
            smooth_shading=False,
            show_edges=False,
            metallic=0.4,
            roughness=0.6,
            ambient=0.3,
            diffuse=0.7,
            specular=0.1,
            clim=[0.0, 1.0],
            show_scalar_bar=False
        )
        
        # Efectos visuales
        plotter.enable_terrain_style()
        plotter.enable_eye_dome_lighting()
        
        # Sin contornos
        contornos_mesh = None
        
        # --- Configuración de cámara ---
        azimut_rad = math.radians(azimut)
        altura_camara_real = altura_observador_real / 1000 # En km
        
        print(f"   🎥 CONFIGURACIÓN DE CÁMARA:")
        print(f"      Altura terreno: {altura_terreno:.0f}m")
        print(f"      Altura observador total: {altura_observador_real:.1f}m")
        print(f"      Altura cámara: {altura_camara_real:.6f}km")
        
        # La cámara se ubica en el origen (0,0,0) de nuestra malla, que es el observador
        plotter.camera.position = [0, 0, altura_camara_real]
        
        # El punto focal es la dirección hacia la que mira la cámara
        focal_distance = radio_km * 0.3
        focal_x = focal_distance * math.sin(azimut_rad)
        focal_y = focal_distance * math.cos(azimut_rad)
        focal_z = altura_camara_real +0.001 # El punto focal está a la misma altura que el observador
        
        plotter.camera.focal_point = [focal_x, focal_y, focal_z]
        plotter.camera.up = [0, 0, 1] # Z es el eje 'arriba'
        plotter.camera.view_angle = campo_vision
        
        #Clipping range
        radio_km_efectivo = min(radio_km, 200)
        near_clip = 0.001
        far_clip = radio_km_efectivo * 2
        plotter.camera.clipping_range = (near_clip, far_clip)

        plotter.enable_depth_peeling()
        
        # --- Implementación de Controles (original) ---
        angulo_actual = [azimut]
        zoom_actual = [campo_vision]
        
        def obtener_direccion_cardinal(angulo):
            """Convierte ángulo a dirección cardinal."""
            angulo = angulo % 360
            if angulo < 22.5 or angulo >= 337.5: return "Norte"
            elif angulo < 67.5: return "Noreste"
            elif angulo < 112.5: return "Este"
            elif angulo < 157.5: return "Sureste"
            elif angulo < 202.5: return "Sur"
            elif angulo < 247.5: return "Suroeste"
            elif angulo < 292.5: return "Oeste"
            else: return "Noroeste"
        
        #Crear la brujula
        compass_info = self._crear_brujula_imagen(plotter, 'compass.png', azimut)
        
         #Informacion estatica
        
        info_actor = None
        
        # Controles simplificados
        controles_text = ('CONTROLES:(A/D/W/S) | + - (Zoom)')
        plotter.add_text(controles_text, position='lower_left', font_size=9,
                        color='lightgreen', shadow=True)

        def actualizar_vista_direccion(angulo_degrees):
            """
            Actualiza la dirección de la vista, el texto y la rotación de la brújula.
            """
            nonlocal info_actor
            angulo_rad = math.radians(angulo_degrees)
            plotter.camera.position = [0, 0, altura_camara_real]
            plotter.camera.clipping_range = (near_clip, far_clip)
            
            nuevo_focal_x = focal_distance * math.sin(angulo_rad)
            nuevo_focal_y = focal_distance * math.cos(angulo_rad)
            nuevo_focal_z = altura_camara_real + 0.001
            plotter.camera.focal_point = [nuevo_focal_x, nuevo_focal_y, nuevo_focal_z]
            
            angulo_actual[0] = angulo_degrees
            
            
            texto_dinamico = (
                f'Vista 3D - Lat: {lat:.5f}°, Lon: {lon:.5f}°\n'
                f'Ángulo: {angulo_degrees:.1f}° ({obtener_direccion_cardinal(angulo_degrees)})\n'
                f'Altura: {altura_observador_real:.1f}m\n'
                f'FOV: {plotter.camera.view_angle:.1f}°'
            )
            
            # CORRECCIÓN: Remover el actor anterior si existe y crear uno nuevo
            if info_actor is not None:
                plotter.renderer.RemoveActor2D(info_actor)
            
            info_actor = plotter.add_text(texto_dinamico, 
                                        position='upper_left', 
                                        font_size=10,
                                        color='white', 
                                        shadow=False)
                
            # --- NUEVO: Actualiza la rotación de la brújula ---
            if compass_info and 'actualizar_rotacion' in compass_info:
                compass_info['actualizar_rotacion'](angulo_degrees)
            
            
            plotter.render()
        
        def actualizar_zoom(nuevo_campo_vision):
            """Actualiza el zoom."""
            nuevo_campo_vision = max(10, min(120, nuevo_campo_vision))
            zoom_actual[0] = nuevo_campo_vision
            plotter.camera.view_angle = nuevo_campo_vision
            
            actualizar_vista_direccion(angulo_actual[0])
            plotter.render()

        #Iniciar texto
        actualizar_vista_direccion(azimut)

        def keypress_callback_pyvista(key):
            """Callback para teclado - Solo rotación y zoom."""
            if key in ['Left', 'a']:
                angulo_actual[0] = (angulo_actual[0] - 5) % 360
                actualizar_vista_direccion(angulo_actual[0])
            elif key in ['Right', 'd']:
                angulo_actual[0] = (angulo_actual[0] + 5) % 360
                actualizar_vista_direccion(angulo_actual[0])
            elif key in ['Up', 'w']:
                angulo_actual[0] = (angulo_actual[0] - 1) % 360
                actualizar_vista_direccion(angulo_actual[0])
            elif key in ['Down', 's']:
                angulo_actual[0] = (angulo_actual[0] + 1) % 360
                actualizar_vista_direccion(angulo_actual[0])
            elif key in ['plus', 'equal']:
                nuevo_zoom = zoom_actual[0] - 5
                actualizar_zoom(nuevo_zoom)
            elif key in ['minus']:
                nuevo_zoom = zoom_actual[0] + 5
                actualizar_zoom(nuevo_zoom)
        
        # Registrar eventos de teclado (conservando la estructura original)
        plotter.add_key_event('Left', lambda: keypress_callback_pyvista('Left'))
        plotter.add_key_event('Right', lambda: keypress_callback_pyvista('Right'))
        plotter.add_key_event('Up', lambda: keypress_callback_pyvista('Up'))
        plotter.add_key_event('Down', lambda: keypress_callback_pyvista('Down'))
        plotter.add_key_event('a', lambda: keypress_callback_pyvista('a'))
        plotter.add_key_event('d', lambda: keypress_callback_pyvista('d'))
        plotter.add_key_event('w', lambda: keypress_callback_pyvista('w'))
        plotter.add_key_event('s', lambda: keypress_callback_pyvista('s'))
        plotter.add_key_event('plus', lambda: keypress_callback_pyvista('plus'))
        plotter.add_key_event('equal', lambda: keypress_callback_pyvista('plus'))
        plotter.add_key_event('minus', lambda: keypress_callback_pyvista('minus'))
        
        # Deshabilitar interacción del mouse (como en tu código original)
        plotter.disable()
        
        # Información para retornar a la GUI
        info_gui = {
            'plotter': plotter,
            'azimut_actual': angulo_actual,
            'zoom_actual': zoom_actual,
            'altura_observador': altura_observador_real,
            'altura_terreno': altura_terreno,
            'direccion_cardinal': obtener_direccion_cardinal(azimut),
            'coordenadas': (lat, lon),
            'radio_km': radio_km,
            'elevacion_max': Z[max_idx] * 1000,
            'elevacion_min': min_val,
            'puntos_terreno': superficie.n_points
        }
        
        plotter.show(title=f"Vista 3D: {lat:.4f}, {lon:.4f}")
        
        return info_gui

# Función de demostración para GUI
def demo_horizonte_3d_gui():
    """Demostración del visualizador 3D para GUI."""
    print("🏔️  VISUALIZADOR 3D DE HORIZONTE - ECUADOR (GUI)")
    print("=" * 60)
    
    viewer = HorizonteViewer3D_GUI()
    
    ubicaciones = {
        '1': (-0.1807, -78.4678, "Quito - Vista hacia Cotopaxi"),
        '2': (-2.1709, -79.9224, "Guayaquil - Vista hacia cordillera"),
        '3': (-2.1709, -79.9224, "Guayaquil → Chimborazo"),
        '4': (-2.9001, -79.0059, "Cuenca - Ciudad colonial"), 
        '5': (-1.2549, -78.6291, "Ambato - Valle central"),
        '6': (0.9538, -79.6528, "Esmeraldas - Costa norte"),
        '7': (-1.0339447033405236, -80.67010340636165, "Cerro montecristi"),
        '8': (-0.613702, -78.472912, "Volcán Cotopaxi"),
        '9': (-0.229227, -78.518218, "Norte de Quito")
    }
    
    print("📍 SELECCIONAR UBICACIÓN:")
    for key, (lat, lon, desc) in ubicaciones.items():
        print(f"  {key}. {desc} ({lat:.4f}°, {lon:.4f}°)")
    print("  10. Coordenadas personalizadas")
    
    opcion = input("Elegir ubicación (1-10): ").strip()
    
    if opcion in ubicaciones:
        lat, lon, descripcion = ubicaciones[opcion]
        print(f"✅ Seleccionado: {descripcion}")
    elif opcion == '10':
        try:
            lat = float(input("Latitud: "))
            lon = float(input("Longitud: "))
            descripcion = "Ubicación personalizada"
        except ValueError:
            print("❌ Coordenadas inválidas")
            return
    else:
        print("❌ Opción inválida")
        return
    
    # Configurar vista
    print("🧭 DIRECCIÓN DE VISTA:")
    print("  0. Norte    90. Este    180. Sur    270. Oeste")
    try:
        azimut = int(input("Azimut (0-359°): "))
    except ValueError:
        azimut = 90
        print("Usando azimut por defecto: 90° (Este)")
    
    try:
        info_resultado = viewer.vista_3d_realista(lat, lon, azimut)
        
        print(f"✅ Vista 3D generada para GUI")
        print("⛰️  Vista natural del terreno - Radio 150km")
        print(f"📊 Información disponible para GUI:")
        print(f"   Altura observador: {info_resultado['altura_observador']:.1f}m")
        print(f"   Dirección: {info_resultado['direccion_cardinal']}")
        print(f"   Puntos renderizados: {info_resultado['puntos_terreno']:,}")
        print("⌨️  Controles: ← → (rotación) | + - (zoom)")
        print("💡 ¡Vista 3D lista para integración con GUI!")
        
    except Exception as e:
        print(f"❌ Error generando vista: {e}")
        print("💡 Verifique que PyVista esté instalado y actualizado: pip install --upgrade pyvista pyvistaqt")

if __name__ == "__main__":
    demo_horizonte_3d_gui()