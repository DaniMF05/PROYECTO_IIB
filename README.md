# 🏔️ Visualizador 3D de Horizonte - Ecuador

**Proyecto de Métodos Numéricos - Cuarto Semestre**

Un visualizador 3D interactivo que permite generar vistas realistas del horizonte desde cualquier punto del Ecuador continental, utilizando datos de elevación digital del terreno (archivos .hgt).

![Vista del Horizonte](https://img.shields.io/badge/Status-Funcional-brightgreen)
![Python](https://img.shields.io/badge/Python-3.7+-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)
![3D](https://img.shields.io/badge/3D-PyVista-red)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso Rápido](#-uso-rápido)
- [Arquitectura del Código](#-arquitectura-del-código)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Troubleshooting](#-troubleshooting)
- [Contribuir](#-contribuir)

## ✨ Características

- **🗺️ Interfaz Gráfica Intuitiva**: Control completo desde una GUI con Tkinter
- **📍 Ubicaciones Preconfiguradas**: 9 ubicaciones emblemáticas del Ecuador
- **🧭 Control de Dirección**: Selector de azimut (0-359°) con direcciones cardinales
- **🏔️ Visualización 3D Realista**: Renderizado con PyVista sin exageración vertical
- **⚡ Multithreading**: Generación no bloqueante de vistas 3D
- **📏 Configuración Flexible**: Radio de visualización hasta 150km
- **🎨 Mapeo de Colores Realista**: Colores basados en elevación del terreno

## 🗂️ Estructura del Proyecto

```
PROYECTO_IIB_REPOSITORIO/
├── gui_horizonte.py              # 🎮 APLICACIÓN PRINCIPAL - Ejecutar este archivo
├── horizonte_3d_gui.py           # 🎨 Motor de visualización 3D (PyVista)
├── simulador_horizonte_corregido.py # 🧮 Clase base - Procesamiento de datos
├── horizonte_3d_final.py         # 🔧 Versión standalone (opcional)
├── Matrices/                     # 📊 Datos de elevación (.hgt)
│   ├── N00W073.hgt
│   ├── N01W074.hgt
│   └── ... (archivos de terreno)
└── README.md                     # 📖 Esta documentación
```

### 📁 Descripción de Archivos

| Archivo | Propósito | Estado |
|---------|-----------|--------|
| `gui_horizonte.py` | **APLICACIÓN PRINCIPAL** - Interfaz gráfica | ✅ Activo |
| `horizonte_3d_gui.py` | Motor de renderizado 3D para GUI | ✅ Activo |
| `simulador_horizonte_corregido.py` | Clase base para procesamiento de datos | ✅ Activo |
| `horizonte_3d_final.py` | Versión standalone independiente | 🟡 Opcional |

## 🚀 Instalación

### Prerrequisitos

- **Python 3.7 o superior**
- **Sistema Operativo**: Windows, Linux, macOS

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/proyecto-horizonte-3d.git
cd proyecto-horizonte-3d
```

### 2. Instalar Dependencias

```bash
# Instalar dependencias principales
pip install numpy matplotlib pyvista tkinter

# O usando requirements (si está disponible)
pip install -r requirements.txt
```

### 3. Verificar Instalación

```bash
python -c "import numpy, matplotlib, pyvista, tkinter; print('✅ Todas las dependencias instaladas correctamente')"
```

## 🎯 Uso Rápido

### Ejecutar la Aplicación

```bash
# Navegar al directorio del proyecto
cd PROYECTO_IIB_REPOSITORIO

# Ejecutar la aplicación principal
python gui_horizonte.py
```

### Pasos para Generar una Vista

1. **Abrir la aplicación**: Ejecutar `python gui_horizonte.py`
2. **Seleccionar ubicación**: 
   - Usar el menú desplegable para ubicaciones preconfiguradas, O
   - Ingresar coordenadas manualmente (Lat: -5° a 2°, Lon: -82° a -75°)
3. **Configurar dirección**: Ajustar el azimut (0°=Norte, 90°=Este, etc.)
4. **Generar vista**: Hacer clic en "🏔️ GENERAR VISTA 3D"
5. **Explorar**: La ventana 3D se abrirá con controles interactivos

## 🏗️ Arquitectura del Código

### Diagrama de Dependencias

```
gui_horizonte.py (INTERFAZ PRINCIPAL)
    ↓ importa
horizonte_3d_gui.py (VISUALIZADOR 3D)
    ↓ hereda de
simulador_horizonte_corregido.py (PROCESADOR DE DATOS)
```

### Clases Principales

#### 1. `HorizonteGUI` (gui_horizonte.py)
- **Responsabilidad**: Interfaz gráfica principal
- **Componentes**: Tkinter widgets, validación, threading
- **Métodos clave**: `crear_interfaz()`, `generar_vista()`, `validar_coordenadas()`

#### 2. `HorizonteViewer3D_GUI` (horizonte_3d_gui.py)
- **Responsabilidad**: Renderizado 3D con PyVista
- **Hereda de**: `SimuladorHorizonte`
- **Métodos clave**: `vista_3d_realista()`, `_vista_pyvista_gui()`

#### 3. `SimuladorHorizonte` (simulador_horizonte_corregido.py)
- **Responsabilidad**: Procesamiento de datos de terreno
- **Funciones**: Carga de archivos .hgt, conversión de coordenadas
- **Métodos clave**: `cargar_terreno_ecuador()`, `coordenadas_a_indices()`

## 📍 Ejemplos de Uso

### Ubicaciones Preconfiguradas

```python
# Ubicaciones disponibles en la GUI:
ubicaciones = {
    "Quito - Vista hacia Cotopaxi": (-0.1807, -78.4678),
    "Guayaquil - Vista hacia cordillera": (-2.1709, -79.9224),
    "Cuenca - Ciudad colonial": (-2.9001, -79.0059),
    "Ambato - Valle central": (-1.2549, -78.6291),
    # ... más ubicaciones
}
```

### Uso Programático (Opcional)

```python
from horizonte_3d_gui import HorizonteViewer3D_GUI

# Crear visualizador
viewer = HorizonteViewer3D_GUI()

# Generar vista 3D
vista = viewer.vista_3d_realista(
    lat_observador=-0.1807,    # Quito
    lon_observador=-78.4678,
    azimut=90,                 # Mirando al Este
    campo_vision=90,           # Campo de visión
    radio_km=150              # Radio de terreno
)
```

## 🔧 Troubleshooting

### Problemas Comunes

#### ❌ Error: "PyVista no está instalado"
```bash
pip install pyvista
```

#### ❌ Error: "No module named 'tkinter'"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

#### ❌ Error: "No se encontraron archivos .hgt"
- Verificar que la carpeta `Matrices/` contenga archivos .hgt
- Los archivos deben seguir el formato: `N00W073.hgt`, `S01W079.hgt`, etc.

#### ❌ La ventana 3D no se abre
- Verificar que el sistema soporte OpenGL
- Comprobar drivers de tarjeta gráfica actualizados

### Logs y Debugging

La aplicación muestra información detallada en la consola:
```
🏔️ Iniciando Interfaz Gráfica del Visualizador 3D
📍 Coordenadas corregidas para Ecuador continental
🎯 GENERANDO VISTA 3D PARA GUI
```

## 🤝 Contribuir

### Para Colaboradores del Proyecto

1. **Fork del repositorio**
2. **Crear rama para tu feature**: `git checkout -b feature/nueva-funcionalidad`
3. **Commit tus cambios**: `git commit -m 'Agregar nueva funcionalidad'`
4. **Push a la rama**: `git push origin feature/nueva-funcionalidad`
5. **Crear Pull Request**

### Convenciones de Código

- **Estilo**: Seguir PEP 8
- **Documentación**: Docstrings en español
- **Commits**: Mensajes descriptivos en español
- **Emoji**: Usar emojis en comentarios para mejor legibilidad 🎨

## 📊 Datos Técnicos

- **Resolución de datos**: 1201x1201 puntos por grado
- **Formato de elevación**: Archivos .hgt (SRTM)
- **Cobertura geográfica**: Ecuador continental
- **Precisión**: ~90 metros por píxel
- **Radio máximo de visualización**: 150 km
- **Campo de visión**: Configurable (por defecto 90°)

## 📄 Licencia

Este proyecto es parte de un trabajo académico de Métodos Numéricos. Uso educativo.

## 👥 Autores

- **Estudiante**: [Tu Nombre]
- **Curso**: Métodos Numéricos - Cuarto Semestre
- **Institución**: [Tu Universidad]

---

**¿Problemas o sugerencias?** Abre un [Issue](https://github.com/tu-usuario/proyecto-horizonte-3d/issues) en GitHub.

**⭐ Si te gusta el proyecto, ¡dale una estrella!**
# PROYECTO_IIB
