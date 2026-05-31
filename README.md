# 🌍 GlobePlanner

GlobePlanner es una aplicación web desarrollada con Flask que funciona como un asistente de viajes inteligente. Permite consultar información relevante para planificar un viaje, incluyendo clima, conversión de moneda, vuelos y hoteles desde una única interfaz.

## 👨‍💻 Desarrollado por

- Juan David Vega Alfonso
- Iván Andrés Vanegas Cabrera

## 🚀 Funcionalidades

- 🌦️ Consulta del clima actual de una ciudad.
- 💱 Conversión de monedas en tiempo real.
- ✈️ Consulta de vuelos mediante códigos IATA.
- 🏨 Búsqueda de hoteles en la ciudad destino.
- 🗺️ Visualización de la ubicación en mapa interactivo.
- 🖼️ Imagen representativa de la ciudad consultada.
- 📊 Resumen rápido con la información más importante del destino.

---

## 🛠️ Tecnologías utilizadas

### Backend
- Python 3
- Flask
- Requests
- Gunicorn

### Frontend
- HTML5
- CSS3
- JavaScript
- Leaflet.js

---

## 🌐 APIs y servicios utilizados

### 1. OpenWeatherMap API
Obtención de información meteorológica en tiempo real.

- Datos consultados:
  - Temperatura
  - Sensación térmica
  - Humedad
  - Presión atmosférica
  - Velocidad del viento
  - Visibilidad

Documentación:
https://openweathermap.org/api

---

### 2. ExchangeRate API
Conversión de monedas y consulta de tasas de cambio actualizadas.

Documentación:
https://www.exchangerate-api.com/

---

### 3. AviationStack API
Consulta de vuelos utilizando códigos IATA de origen y destino.

Datos obtenidos:
- Aerolínea
- Número de vuelo
- Estado del vuelo
- Aeropuertos de salida y llegada

Documentación:
https://aviationstack.com/

---

### 4. Nominatim (OpenStreetMap)
Utilizado para:
- Geolocalización de ciudades.
- Obtención de coordenadas.
- Búsqueda de hoteles cercanos.

Documentación:
https://nominatim.org/

---

### 5. Wikipedia REST API
Utilizada para obtener imágenes representativas de las ciudades consultadas.

Documentación:
https://en.wikipedia.org/api/rest_v1/

---

### 6. Leaflet.js
Biblioteca utilizada para mostrar mapas interactivos basados en OpenStreetMap.

Documentación:
https://leafletjs.com/

---

## 📂 Estructura del proyecto

```text
GlobePlanner/
│
├── app.py
├── requirements.txt
│
└── templates/
    └── index.html
```

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd GlobePlanner
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

Activar entorno virtual:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear las siguientes variables:

```bash
OPENWEATHER_KEY=tu_api_key
AVIATIONSTACK_KEY=tu_api_key
```

### 5. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en:

```text
http://localhost:5000
```

---

## 📸 Ejemplo de uso

1. Ingresar una ciudad destino.
2. Seleccionar moneda de origen y destino.
3. Los codigos IATA se dan automaticamente con el ingreso de la ciudad destino
4. Presionar **Buscar**.
5. Consultar:
   - Clima.
   - Conversión monetaria.
   - Vuelos.
   - Hoteles.
   - Ubicación en mapa.

---

## 🎯 Objetivo del proyecto

Facilitar la planificación de viajes integrando diferentes servicios web en una sola plataforma intuitiva, permitiendo al usuario obtener información relevante del destino antes de viajar.

---

## 📄 Licencia

Proyecto desarrollado con fines académicos.
