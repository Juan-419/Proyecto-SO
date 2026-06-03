import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import threading
from datetime import datetime
import webbrowser

class GlobePlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 GlobePlanner — Tu asistente de viajes")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f4f8')
        style.configure('TLabel', background='#f0f4f8', font=('Arial', 10))
        style.configure('Title.TLabel', background='#f0f4f8', font=('Arial', 14, 'bold'), foreground='#0f3460')
        style.configure('TButton', font=('Arial', 10))
        
        # Diccionario IATA
        self.iata_map = {
            'bogota': 'BOG', 'medellin': 'MDE', 'cali': 'CLO', 'cartagena': 'CTG',
            'barranquilla': 'BAQ', 'brasilia': 'BSB', 'sao paulo': 'GRU', 'rio de janeiro': 'GIG',
            'buenos aires': 'EZE', 'santiago': 'SCL', 'lima': 'LIM', 'quito': 'UIO',
            'paris': 'CDG', 'london': 'LHR', 'londres': 'LHR', 'madrid': 'MAD',
            'barcelona': 'BCN', 'roma': 'FCO', 'rome': 'FCO', 'berlin': 'BER',
            'amsterdam': 'AMS', 'frankfurt': 'FRA', 'tokyo': 'NRT', 'tokio': 'NRT',
            'dubai': 'DXB', 'singapur': 'SIN', 'singapore': 'SIN', 'bangkok': 'BKK',
            'hong kong': 'HKG', 'seoul': 'ICN', 'miami': 'MIA', 'nueva york': 'JFK',
            'new york': 'JFK', 'los angeles': 'LAX', 'chicago': 'ORD', 'toronto': 'YYZ'
        }
        
        # Datos actuales
        self.clima_data = None
        self.moneda_data = None
        self.vuelos_data = None
        self.hoteles_data = None
        self.ciudad_actual = None
        self.lat = None
        self.lon = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg='#0f3460', height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        tk.Label(header, text='🌍 GlobePlanner', font=('Arial', 16, 'bold'), bg='#0f3460', fg='white').pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(header, text='Tu asistente de viajes inteligente', font=('Arial', 10), bg='#0f3460', fg='#ccc').pack(side=tk.LEFT, padx=5)
        
        # SEARCH FRAME
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Label(search_frame, text='🔍 ¿A dónde viajas?', style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        # Row 1: Ciudad, desde, hasta
        row1 = ttk.Frame(search_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text='🏙️ Ciudad:').pack(side=tk.LEFT, padx=5)
        self.ciudad_entry = ttk.Entry(row1, width=15)
        self.ciudad_entry.pack(side=tk.LEFT, padx=5)
        self.ciudad_entry.insert(0, 'Paris')
        self.ciudad_entry.bind('<KeyRelease>', self.autodetect_iata)
        
        ttk.Label(row1, text='💱 Desde:').pack(side=tk.LEFT, padx=5)
        self.desde_var = tk.StringVar(value='COP')
        desde_combo = ttk.Combobox(row1, textvariable=self.desde_var, 
                                    values=['COP', 'USD', 'EUR', 'GBP', 'JPY', 'MXN', 'BRL', 'ARS', 'CLP', 'PEN'], width=8, state='readonly')
        desde_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text='Hasta:').pack(side=tk.LEFT, padx=5)
        self.hasta_var = tk.StringVar(value='EUR')
        hasta_combo = ttk.Combobox(row1, textvariable=self.hasta_var,
                                   values=['EUR', 'USD', 'COP', 'GBP', 'JPY', 'MXN', 'BRL', 'ARS', 'CLP', 'PEN'], width=8, state='readonly')
        hasta_combo.pack(side=tk.LEFT, padx=5)
        
        # Row 2: IATA
        row2 = ttk.Frame(search_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text='✈️ Origen IATA:').pack(side=tk.LEFT, padx=5)
        self.origen_entry = ttk.Entry(row2, width=6)
        self.origen_entry.pack(side=tk.LEFT, padx=5)
        self.origen_entry.insert(0, 'BOG')
        
        ttk.Label(row2, text='🛬 Destino IATA:').pack(side=tk.LEFT, padx=5)
        self.destino_entry = ttk.Entry(row2, width=6)
        self.destino_entry.pack(side=tk.LEFT, padx=5)
        self.destino_entry.insert(0, 'CDG')
        
        ttk.Label(row2, text='', foreground='#3B6D11').pack(side=tk.LEFT, padx=5)
        self.iata_ok_label = ttk.Label(row2, text='', foreground='#3B6D11', font=('Arial', 9, 'bold'))
        self.iata_ok_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text='🔍 Buscar', command=self.buscar_todo).pack(anchor=tk.E, pady=10)
        
        # NOTEBOOK (Pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Clima
        self.tab_clima = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_clima, text='🌦️ Clima')
        self.clima_text = scrolledtext.ScrolledText(self.tab_clima, height=20, width=80, state=tk.DISABLED)
        self.clima_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 2: Moneda
        self.tab_moneda = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_moneda, text='💱 Moneda')
        self.moneda_text = scrolledtext.ScrolledText(self.tab_moneda, height=20, width=80, state=tk.DISABLED)
        self.moneda_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 3: Vuelos
        self.tab_vuelos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_vuelos, text='✈️ Vuelos')
        self.vuelos_text = scrolledtext.ScrolledText(self.tab_vuelos, height=20, width=80, state=tk.DISABLED)
        self.vuelos_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 4: Hoteles
        self.tab_hoteles = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_hoteles, text='🏨 Hoteles')
        self.hoteles_text = scrolledtext.ScrolledText(self.tab_hoteles, height=20, width=80, state=tk.DISABLED)
        self.hoteles_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 5: Ubicación
        self.tab_ubicacion = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ubicacion, text='📍 Ubicación')
        self.ubicacion_text = scrolledtext.ScrolledText(self.tab_ubicacion, height=20, width=80, state=tk.DISABLED)
        self.ubicacion_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # STATUS BAR
        self.status_var = tk.StringVar(value='Listo para buscar')
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def autodetect_iata(self, event=None):
        ciudad = self.ciudad_entry.get().lower().strip()
        if ciudad in self.iata_map:
            self.destino_entry.delete(0, tk.END)
            self.destino_entry.insert(0, self.iata_map[ciudad])
            self.iata_ok_label.config(text='✅ Auto-detectado')
        else:
            self.iata_ok_label.config(text='')
    
    def update_text_widget(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)
    
    def buscar_todo(self):
        ciudad = self.ciudad_entry.get().strip() or 'Paris'
        origen = self.origen_entry.get().upper().strip() or 'BOG'
        destino = self.destino_entry.get().upper().strip() or 'CDG'
        desde = self.desde_var.get()
        hasta = self.hasta_var.get()
        
        if len(origen) != 3 or len(destino) != 3:
            messagebox.showerror('Error', 'Los códigos IATA deben tener exactamente 3 letras')
            return
        
        self.status_var.set('🔄 Buscando información...')
        self.root.update()
        
        # Ejecutar en thread para no bloquear la UI
        thread = threading.Thread(target=self._buscar_thread, args=(ciudad, origen, destino, desde, hasta))
        thread.daemon = True
        thread.start()
    
    def _buscar_thread(self, ciudad, origen, destino, desde, hasta):
        try:
            # Clima
            self.clima_data = self._get_clima(ciudad)
            self._render_clima()
            
            # Moneda
            self.moneda_data = self._get_moneda(desde, hasta)
            self._render_moneda(desde, hasta)
            
            # Vuelos
            self.vuelos_data = self._get_vuelos(origen, destino)
            self._render_vuelos(origen, destino)
            
            # Hoteles
            self.hoteles_data = self._get_hoteles(ciudad)
            self._render_hoteles()
            
            # Ubicación
            if self.clima_data and 'coord' in self.clima_data:
                self.lat = self.clima_data['coord']['lat']
                self.lon = self.clima_data['coord']['lon']
                self.ciudad_actual = self.clima_data['name']
            self._render_ubicacion()
            
            self.status_var.set(f'✅ Búsqueda completada para {ciudad}')
        except Exception as e:
            messagebox.showerror('Error', str(e))
            self.status_var.set('❌ Error en la búsqueda')
    
    def _get_clima(self, ciudad):
        r = requests.get('https://api.openweathermap.org/data/2.5/weather',
                        params={'q': ciudad, 'appid': '91ddd4f2219672b7aebd8fb4fce6d478', 'lang': 'es', 'units': 'metric'},
                        timeout=10)
        return r.json()
    
    def _get_moneda(self, desde, hasta):
        r = requests.get(f'https://open.er-api.com/v6/latest/{desde}', timeout=10)
        return r.json()
    
    def _get_vuelos(self, origen, destino):
        r = requests.get(f'https://api.aviationstack.com/v1/flights?dep_iata={origen}&arr_iata={destino}&access_key=5d2b7b825bafc0b44aaa3aec85783fd6',
                        timeout=10)
        return r.json()
    
    def _get_hoteles(self, ciudad):
        geo = requests.get('https://nominatim.openstreetmap.org/search',
                          params={'q': ciudad, 'format': 'json', 'limit': 1},
                          headers={'User-Agent': 'GlobePlanner/1.0'},
                          timeout=10).json()
        if not geo:
            return []
        bbox = geo[0]['boundingbox']
        r = requests.get('https://nominatim.openstreetmap.org/search',
                        params={'q': 'hotel', 'format': 'json', 'limit': 10, 'addressdetails': 1,
                                'viewbox': f'{bbox[2]},{bbox[1]},{bbox[3]},{bbox[0]}', 'bounded': 1},
                        headers={'User-Agent': 'GlobePlanner/1.0'},
                        timeout=10).json()
        return r
    
    def _render_clima(self):
        if not self.clima_data or 'error' in self.clima_data:
            text = '❌ Error al obtener clima'
        else:
            temp = int(self.clima_data['main']['temp'])
            desc = self.clima_data['weather'][0]['description']
            ciudad = self.clima_data['name']
            pais = self.clima_data['sys']['country']
            sensacion = int(self.clima_data['main']['feels_like'])
            temp_min = int(self.clima_data['main']['temp_min'])
            temp_max = int(self.clima_data['main']['temp_max'])
            humedad = self.clima_data['main']['humidity']
            viento = self.clima_data['wind']['speed']
            presion = self.clima_data['main']['pressure']
            
            text = f"""
🌦️  CLIMA ACTUAL
{'='*50}
📍 {ciudad}, {pais}
🌡️  Temperatura: {temp}°C
📝 Descripción: {desc.capitalize()}
🤔 Sensación térmica: {sensacion}°C
📊 Mín / Máx: {temp_min}° / {temp_max}°
💧 Humedad: {humedad}%
💨 Viento: {viento} km/h
🔽 Presión: {presion} hPa
"""
        self.update_text_widget(self.clima_text, text)
    
    def _render_moneda(self, desde, hasta):
        if not self.moneda_data or 'error' in self.moneda_data:
            text = '❌ Error al obtener tasas de cambio'
        else:
            try:
                tasa = self.moneda_data['rates'][hasta]
                tasa_fmt = f'{tasa:.6f}' if tasa < 0.01 else f'{tasa:.4f}'
                
                text = f"""
💱 CONVERSIÓN DE MONEDA
{'='*50}
Tasa: 1 {desde} = {tasa_fmt} {hasta}
Actualizado: {self.moneda_data.get('time_last_update_utc', 'N/A')[:16]}

EJEMPLOS DE CONVERSIÓN:
{'-'*50}
100,000 {desde} = {(100000 * tasa):,.2f} {hasta}
500,000 {desde} = {(500000 * tasa):,.2f} {hasta}
1,000,000 {desde} = {(1000000 * tasa):,.2f} {hasta}
5,000,000 {desde} = {(5000000 * tasa):,.2f} {hasta}
"""
            except:
                text = '❌ Moneda no encontrada o error en la API'
        
        self.update_text_widget(self.moneda_text, text)
    
    def _render_vuelos(self, origen, destino):
        if not self.vuelos_data or 'error' in self.vuelos_data:
            text = f'❌ No se encontraron vuelos de {origen} → {destino}'
        elif not self.vuelos_data.get('data') or len(self.vuelos_data['data']) == 0:
            text = f'❌ No se encontraron vuelos de {origen} → {destino}'
        else:
            vuelos = self.vuelos_data['data'][:6]
            header = f"""
✈️  VUELOS DISPONIBLES
{'='*50}
Ruta: {origen} → {destino}
Total encontrado: {len(self.vuelos_data['data'])} vuelo(s)

VUELOS:
{'-'*50}
"""
            items = []
            for v in vuelos:
                airline = v.get('airline', {}).get('name', 'N/A')
                flight = v.get('flight', {}).get('iata', 'N/A')
                status = v.get('flight_status', 'N/A')
                dep_iata = v.get('departure', {}).get('iata', origen)
                dep_time = v.get('departure', {}).get('scheduled', '')[:16] if v.get('departure', {}).get('scheduled') else ''
                arr_iata = v.get('arrival', {}).get('iata', destino)
                arr_time = v.get('arrival', {}).get('scheduled', '')[:16] if v.get('arrival', {}).get('scheduled') else ''
                
                item = f"""
{airline} {flight}
  {dep_iata} {dep_time} → {arr_iata} {arr_time}
  Estado: {status}
"""
                items.append(item)
            
            text = header + '\n'.join(items)
        
        self.update_text_widget(self.vuelos_text, text)
    
    def _render_hoteles(self):
        if not self.hoteles_data or isinstance(self.hoteles_data, dict):
            text = '❌ No se encontraron hoteles'
        elif len(self.hoteles_data) == 0:
            text = '❌ No se encontraron hoteles'
        else:
            header = f"""
🏨 HOTELES DISPONIBLES
{'='*50}
Total encontrado: {len(self.hoteles_data)} hotel(es)

HOTELES:
{'-'*50}
"""
            items = []
            for h in self.hoteles_data[:6]:
                nombre = h.get('display_name', 'N/A').split(',')[0]
                direccion = ', '.join(h.get('display_name', 'N/A').split(',')[1:3]).strip()
                
                item = f"""
{nombre}
  📍 {direccion}
"""
                items.append(item)
            
            text = header + '\n'.join(items)
        
        self.update_text_widget(self.hoteles_text, text)
    
    def _render_ubicacion(self):
        if self.lat and self.lon:
            text = f"""
📍 UBICACIÓN DE LA CIUDAD
{'='*50}
Ciudad: {self.ciudad_actual}
Latitud: {self.lat:.4f}
Longitud: {self.lon:.4f}

[Presiona el botón abajo para abrir el mapa]
"""
            self.update_text_widget(self.ubicacion_text, text)
            
            # Agregar botón para abrir mapa
            self.ubicacion_text.config(state=tk.NORMAL)
            self.ubicacion_text.window_create(tk.END, window=ttk.Button(
                self.ubicacion_text,
                text='🗺️ Ver en Google Maps',
                command=lambda: webbrowser.open(f'https://www.google.com/maps/search/{self.lat},{self.lon}')
            ))
            self.ubicacion_text.config(state=tk.DISABLED)
        else:
            self.update_text_widget(self.ubicacion_text, '❌ Sin ubicación disponible')

if __name__ == '__main__':
    root = tk.Tk()
    app = GlobePlannerApp(root)
    root.mainloop()