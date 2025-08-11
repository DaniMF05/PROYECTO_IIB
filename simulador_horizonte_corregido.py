import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

class SimuladorHorizonte:
    def __init__(self, carpeta_matrices='Matrices'):
        """
        Simulador de horizonte para Ecuador continental.
        
        Args:
            carpeta_matrices: Ruta a la carpeta con archivos .hgt
        """
        self.carpeta_matrices = carpeta_matrices
        self.matriz_terreno = None
        self.resolucion = 1201     # Puntos por grado
        
        # Límites reales se determinan dinámicamente
        self.lat_min_matriz = None  
        self.lat_max_matriz = None  
        self.lon_min_matriz = None
        self.lon_max_matriz = None
        
        # Para almacenar la configuración real después de cargar
        self.latitudes_disponibles = []
        self.longitudes_disponibles = []
        
    def generar_nombre_hgt(self, lat, lon):
        # Se usa math.floor() para encontrar la esquina inferior izquierda
        lat_base = math.floor(lat)
        lon_base = math.floor(lon)
        
        lat_label = 'N' if lat_base >= 0 else 'S'
        lon_label = 'E' if lon_base >= 0 else 'W'
        
        return f"{lat_label}{abs(int(lat_base)):02d}{lon_label}{abs(int(lon_base)):03d}.hgt"
    
    def cargar_hgt(self, path_archivo):
        """Carga un archivo .hgt individual."""
        if not os.path.exists(path_archivo):
            return None
        
        tamanio = os.path.getsize(path_archivo)
        puntos = tamanio // 2
        resolucion = int(np.sqrt(puntos))
        
        if resolucion ** 2 != puntos:
            print(f"[ERROR] Archivo corrupto: {path_archivo}")
            return None
        
        with open(path_archivo, 'rb') as f:
            datos = f.read()
        
        matriz = np.frombuffer(datos, dtype='>i2').reshape((resolucion, resolucion))
        return matriz
    
    def cargar_terreno_ecuador(self):
        """Carga y une todos los archivos .hgt para formar el mapa de Ecuador."""
        print("Cargando datos de elevación de Ecuador...")
        
        # Definir explícitamente el rango de archivos disponibles
        latitudes = [3, 2, 1, 0, -1, -2, -3, -4, -5, -6, -7, -8]
        longitudes = [-82, -81, -80, -79, -78, -77, -76, -75, -74, -73]
        
        # Verificar qué archivos existen realmente
        archivos_disponibles = {}
        for lat in latitudes:
            for lon in longitudes:
                nombre = self.generar_nombre_hgt(lat, lon)
                ruta = os.path.join(self.carpeta_matrices, nombre)
                if os.path.exists(ruta):
                    archivos_disponibles[(lat, lon)] = ruta
        
        print(f"Archivos .hgt encontrados: {len(archivos_disponibles)}")
        
        # Determinar límites reales basados en archivos disponibles
        lats_disponibles = [lat for lat, lon in archivos_disponibles.keys()]
        lons_disponibles = [lon for lat, lon in archivos_disponibles.keys()]
        
        # Construir listas ordenadas de coordenadas disponibles
        self.latitudes_disponibles = sorted(list(set(lats_disponibles)), reverse=True)
        self.longitudes_disponibles = sorted(list(set(lons_disponibles)))
        
        # Establecer límites reales
        self.lat_min_matriz = max(self.latitudes_disponibles)   # Norte
        self.lat_max_matriz = min(self.latitudes_disponibles)   # Sur
        self.lon_min_matriz = min(self.longitudes_disponibles)  # Oeste
        self.lon_max_matriz = max(self.longitudes_disponibles)  # Este
        
        print(f"Rango real de datos: Lat {self.lat_max_matriz}° a {self.lat_min_matriz}°, Lon {self.lon_min_matriz}° a {self.lon_max_matriz}°")
        
        # Construir matriz con archivos disponibles
        bloques = []
        
        for i, lat in enumerate(self.latitudes_disponibles):
            fila = []
            for j, lon in enumerate(self.longitudes_disponibles):
                if (lat, lon) in archivos_disponibles:
                    ruta = archivos_disponibles[(lat, lon)]
                    bloque = self.cargar_hgt(ruta)
                    if bloque is None:
                        bloque = np.full((self.resolucion, self.resolucion), -32768)
                else:
                    # Crear bloque vacío si no existe el archivo
                    bloque = np.full((self.resolucion, self.resolucion), -32768)
                
                # Recortar bordes compartidos para evitar duplicados
                if j < len(self.longitudes_disponibles) - 1:
                    bloque = bloque[:, :-1]
                if i < len(self.latitudes_disponibles) - 1:
                    bloque = bloque[:-1, :]
                
                fila.append(bloque)
            
            if fila:  # Solo agregar si hay bloques en la fila
                fila_unida = np.hstack(fila)
                bloques.append(fila_unida)
        
        if bloques:
            self.matriz_terreno = np.vstack(bloques)
            print(f"Matriz de terreno cargada: {self.matriz_terreno.shape}")
        else:
            raise ValueError("No se pudo cargar ningún archivo .hgt válido")
        
    def coordenadas_a_indices(self, lat, lon):
        """Convierte coordenadas geográficas a índices de matriz."""
        if self.matriz_terreno is None:
            self.cargar_terreno_ecuador()
        
        lat_archivo = None
        lon_archivo = None
        
        # Encontrar la latitud del archivo correspondiente
        for lat_disp in self.latitudes_disponibles:
            # El rango de un archivo hgt es [lat_disp, lat_disp+1)
            if lat_disp <= lat < lat_disp + 1:
                lat_archivo = lat_disp
                break
        
        # Encontrar la longitud del archivo correspondiente
        for lon_disp in self.longitudes_disponibles:
            # El rango de un archivo hgt es [lon_disp, lon_disp+1)
            if lon_disp <= lon < lon_disp + 1:
                lon_archivo = lon_disp
                break
        
        if lat_archivo is None or lon_archivo is None:
            raise ValueError(f"Coordenada ({lat}, {lon}) fuera del rango de datos disponibles")

        # Calcular índices dentro del archivo específico
        lat_rel = lat - lat_archivo
        lon_rel = lon - lon_archivo

        # Convertir a índices dentro del archivo (1201x1201)
        # La orientación de los archivos .hgt ya está de Norte a Sur,
        # no se necesita inversión.
        fila_archivo = int((self.resolucion - 1) - lat_rel * (self.resolucion - 1))
        col_archivo = int(lon_rel * (self.resolucion - 1))

        # Encontrar la posición del archivo en la matriz global
        indice_lat_archivo = self.latitudes_disponibles.index(lat_archivo)
        indice_lon_archivo = self.longitudes_disponibles.index(lon_archivo)

        # Calcular índices globales
        fila_global = indice_lat_archivo * (self.resolucion - 1) + fila_archivo
        col_global = indice_lon_archivo * (self.resolucion - 1) + col_archivo
        
        return fila_global, col_global

    
    def indices_a_coordenadas(self, i, j):
        """Convierte índices de matriz a coordenadas geográficas."""
        if self.matriz_terreno is None:
            self.cargar_terreno_ecuador()
        
        # Determinar en qué archivo estamos
        indice_archivo_lat = i // (self.resolucion - 1)
        indice_archivo_lon = j // (self.resolucion - 1)
        
        # Obtener coordenadas del archivo
        if (indice_archivo_lat < len(self.latitudes_disponibles) and
            indice_archivo_lon < len(self.longitudes_disponibles)):
            
            lat_archivo = self.latitudes_disponibles[indice_archivo_lat]
            lon_archivo = self.longitudes_disponibles[indice_archivo_lon]
            
            # Calcular posición dentro del archivo
            fila_archivo = i % (self.resolucion - 1)
            col_archivo = j % (self.resolucion - 1)
            
            # Convertir a coordenadas. La inversión ya no es necesaria
            lat_rel = (self.resolucion - 1 - fila_archivo) / (self.resolucion - 1)
            lon_rel = col_archivo / (self.resolucion - 1)
            
            lat = lat_archivo + lat_rel
            lon = lon_archivo + lon_rel
            
            return lat, lon
        else:
            raise ValueError(f"Índices ({i}, {j}) fuera del rango de la matriz")
    
    def calcular_horizonte(self, lat_observador, lon_observador, azimut, campo_vision=60, 
                          altura_observador=1.7, max_distancia_km=50, num_rayos=360):
        """
        Calcula el perfil del horizonte visible desde una posición.
        
        Args:
            lat_observador, lon_observador: Posición del observador
            azimut: Dirección central de la vista (0=Norte, 90=Este, etc.)
            campo_vision: Ángulo de campo de visión en grados
            altura_observador: Altura del observador sobre el terreno en metros
            max_distancia_km: Distancia máxima a considerar en km
            num_rayos: Número de rayos para calcular el horizonte
            
        Returns:
            angulos: Array de ángulos de cada rayo
            elevaciones: Array de ángulos de elevación del horizonte para cada rayo
            distancias: Array de distancias al horizonte para cada rayo
        """
        if self.matriz_terreno is None:
            self.cargar_terreno_ecuador()
        
        # Convertir posición del observador a índices
        i_obs, j_obs = self.coordenadas_a_indices(lat_observador, lon_observador)
        
        # Verificar que el observador esté dentro de la matriz
        if (i_obs < 0 or i_obs >= self.matriz_terreno.shape[0] or 
            j_obs < 0 or j_obs >= self.matriz_terreno.shape[1]):
            raise ValueError("La posición del observador está fuera del área de datos")
        
        altura_terreno = self.matriz_terreno[i_obs, j_obs]
        if altura_terreno == -32768:
            raise ValueError("No hay datos de elevación en la posición del observador")
        
        altura_total = altura_terreno + altura_observador
        
        # Generar ángulos de los rayos
        angulos = np.linspace(azimut - campo_vision/2, azimut + campo_vision/2, num_rayos)
        elevaciones = []
        distancias = []
        
        # Conversión aproximada: 1 grado ≈ 111 km
        paso_indices = 1  # Paso en índices de matriz
        paso_metros = (1 / (self.resolucion - 1)) * 111000  # metros por paso
        max_pasos = int(max_distancia_km * 1000 / paso_metros)
        
        for angulo in angulos:
            # Convertir ángulo a componentes de dirección
            rad = math.radians(angulo)
            di = -math.cos(rad)  # Negativo porque i crece hacia el sur
            dj = math.sin(rad)   # Positivo porque j crece hacia el este
            
            max_elevacion = -90  # Ángulo de elevación máximo encontrado
            distancia_horizonte = 0
            
            # Lanzar rayo desde el observador
            for paso in range(1, max_pasos + 1):
                # Calcular posición del punto actual
                i_actual = int(i_obs + di * paso)
                j_actual = int(j_obs + dj * paso)
                
                # Verificar límites
                if (i_actual < 0 or i_actual >= self.matriz_terreno.shape[0] or
                    j_actual < 0 or j_actual >= self.matriz_terreno.shape[1]):
                    break
                
                altura_punto = self.matriz_terreno[i_actual, j_actual]
                if altura_punto == -32768:
                    continue
                
                # Calcular distancia y ángulo de elevación
                distancia_metros = paso * paso_metros
                diferencia_altura = altura_punto - altura_total
                angulo_elevacion = math.degrees(math.atan2(diferencia_altura, distancia_metros))
                
                # Actualizar máximo si es necesario
                if angulo_elevacion > max_elevacion:
                    max_elevacion = angulo_elevacion
                    distancia_horizonte = distancia_metros
            
            elevaciones.append(max_elevacion)
            distancias.append(distancia_horizonte)
        
        return np.array(angulos), np.array(elevaciones), np.array(distancias)
