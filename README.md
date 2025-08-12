# 🏔️ Visualizador 3D de Horizonte - Ecuador

Proyecto académico que genera vistas 3D del horizonte desde cualquier punto del Ecuador continental usando datos SRTM (.hgt) y un render interactivo con PyVista.

![Estado](https://img.shields.io/badge/Estado-Activa-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)
![3D](https://img.shields.io/badge/3D-PyVista-red)

## 📋 Contenido

- Características
- Estructura del proyecto
- Instalación (Windows/PowerShell)
- Uso rápido
- Cómo funciona (flujo y arquitectura)
- Controles 3D y HUD
- Requisitos de datos (.hgt)
- Solución de problemas
- Estado actual y tareas pendientes

## ✨ Características

- Interfaz gráfica con mapa interactivo para elegir coordenadas (tkinter + tkintermapview)
- Motor 3D con PyVista/VTK, malla estructurada del terreno y colores por elevación
- Selección de dirección (azimut) mediante una brújula interactiva; muestra dirección cardinal
- Parámetros de cámara configurables: altura sobre el terreno y campo de visión (FOV)
- HUD en la ventana 3D con información actual (FOV, dirección, etc.)
- Radio del terreno simulado de hasta ~150 km alrededor del observador

## 🗂️ Estructura del proyecto

```text
PROYECTO_IIB_REPOSITORIO/
├── gui_horizonte.py                  # Aplicación principal (GUI, mapa, formularios, estado)
├── horizonte_3d_gui.py               # Visualizador 3D (PyVista) para la GUI
├── simulador_horizonte_corregido.py  # Capa de datos: carga y mosaico de HGT, utilidades
├── Matrices/                         # Archivos .hgt (SRTM) para Ecuador
└── README.md
```

## � Instalación (Windows / PowerShell)

1) Requisitos

- Python 3.11 o superior (se ha probado con 3.11/3.12)
- OpenGL/Drivers actualizados (necesario para VTK)

1) Instalar dependencias

```powershell
cd C:\DANIMF\WORKCENTER\CUARTO_SEMESTRE\METODOS_NUMERICOS\PROYECTO_IIB_REPOSITORIO
pip install -r requirements.txt
```

Si VTK falla al instalarse, actualiza pip y wheel, e inténtalo de nuevo:

```powershell
python -m pip install --upgrade pip wheel
pip install -r requirements.txt
```

1) Datos de terreno (.hgt)

- Copia los archivos .hgt en la carpeta `Matrices/` siguiendo el patrón SRTM (p. ej. `S01W079.hgt`).
- El proyecto ya incluye una selección de archivos para Ecuador; verifica que existan.

## 🎯 Uso rápido

Ejecuta la GUI:

```powershell
python gui_horizonte.py
```

Pasos en la aplicación:

1. Selecciona ubicación en el mapa o desde el listado preconfigurado.
2. Ajusta azimut en la brújula y, si deseas, la altura y el FOV.
3. Pulsa “🏔️ GENERAR VISTA 3D” y espera a que aparezca la ventana 3D.

## 🧠 Cómo funciona (flujo y arquitectura)

Resumen del flujo de datos y control:

1) Carga y mosaico de HGT — `SimuladorHorizonte` (simulador_horizonte_corregido.py)

- Busca en `Matrices/` los tiles SRTM disponibles dentro de un rango fijo (latitudes 3..-8, longitudes -82..-73).
- Carga cada archivo .hgt (1201×1201, enteros big-endian), recorta los bordes compartidos y construye una gran matriz continua del terreno de Ecuador.
- Expone utilidades para convertir entre coordenadas geográficas (lat/lon) e índices de la matriz global.

1) Interfaz y parámetros — `HorizonteGUI` (gui_horizonte.py)

- Tkinter arma la ventana: mapa interactivo (tkintermapview), formularios y una brújula para el azimut.
- Cuando pulsas “Generar”, recoge lat/lon (del mapa), azimut, altura y FOV y llama al visualizador 3D.
- Muestra en un panel de información los resultados devueltos por el motor 3D (coordenadas, elevaciones, puntos, etc.).

1) Render 3D — `HorizonteViewer3D_GUI` (horizonte_3d_gui.py)

- Hereda de `SimuladorHorizonte` para reutilizar la matriz de elevaciones.
- Recorta una región alrededor del observador (hasta ~150 km) y submuestrea para rendimiento (hasta ~2000 puntos).
- Construye una malla `StructuredGrid` (X/Y en km, Z en km) y asigna colores por elevación.
- Configura cámara: posición en el observador (Z = altura terreno + altura usuario), `focal_point` a la dirección del azimut, `up=[0,0,1]`, y `view_angle=FOV`.
- Ajusta el “clipping range” para evitar que el terreno cercano desaparezca al hacer zoom.
- Registra eventos de teclado para rotación/zoom y actualiza un HUD con la info actual (incluye FOV).

Retorno a la GUI:

- El método `vista_3d_realista()` devuelve un diccionario con métricas útiles: dirección actual, puntos del terreno renderizados, elevación máxima/mínima, etc., que la GUI muestra en texto.

## 🎮 Controles 3D y HUD

- Rotación: Flechas ← → ↑ ↓ o teclas A/D/W/S
- Zoom: teclas + y − (también = como alternativa al +)
- HUD: Se muestra información en pantalla (azimut/dirección y FOV). El FOV se actualiza al hacer zoom.

Nota: el ratón está deshabilitado en esta versión para evitar conflictos; todo se maneja por teclado.

## 📦 Requisitos de datos (.hgt)

- El patrón de nombres debe ser SRTM, por ejemplo: `N00W073.hgt`, `S01W079.hgt`.
- Los archivos deben corresponder al rango geográfico de Ecuador. Si se selecciona un punto sin datos (por ejemplo, mar), se informará un error.

## �️ Solución de problemas

1) “PyVista/VTK no está instalado”

- `pip install -r requirements.txt`
- Actualiza pip/wheel si persiste.

1) Ventana 3D negra o no abre

- Verifica soporte OpenGL y drivers de video.
- Prueba con un entorno virtual limpio (venv).

1) “No se encontraron archivos .hgt”

- Asegúrate de que `Matrices/` exista y tenga los tiles requeridos con el nombre correcto.

1) El terreno “desaparece” al hacer zoom

- Asegúrate de usar una versión que reajusta el `clipping_range` al cambiar el FOV.

## Autores
Este proyecto es un trabajo académico de Métodos Numéricos en la Escuela Politécnica Nacional.

- Daniel Menendez
- Jesua Villacis
- Celeste Gallardo