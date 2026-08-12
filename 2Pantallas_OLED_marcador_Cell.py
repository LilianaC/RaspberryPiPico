import network
import socket
import machine
import time
import ssd1306

# ==========================================================
# 1. CONFIGURACIÓN DE LAS DOS PANTALLAS OLED (I2C)
# ==========================================================
# Pantalla 1: Bus I2C 0 -> GP0 (SDA) y GP1 (SCL)
i2c_0 = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

# Pantalla 2: Bus I2C 1 -> GP2 (SDA) y GP3 (SCL)
i2c_1 = machine.I2C(1, sda=machine.Pin(2), scl=machine.Pin(3), freq=400000)

# Intentar inicializar Pantalla 1 (probar dirección 0x3C o 0x3D)
try:
    oled1 = ssd1306.SSD1306_I2C(128, 64, i2c_0, addr=0x3C)
except OSError:
    oled1 = ssd1306.SSD1306_I2C(128, 64, i2c_0, addr=0x3D)

# Intentar inicializar Pantalla 2 (probar dirección 0x3C o 0x3D)
try:
    oled2 = ssd1306.SSD1306_I2C(128, 64, i2c_1, addr=0x3C)
except OSError:
    oled2 = ssd1306.SSD1306_I2C(128, 64, i2c_1, addr=0x3D)

# Agrupamos las dos pantallas en una lista para poder actualizarlas juntas
pantallas = [oled1, oled2]

# Variables globales del marcador
goles_local = 0
goles_visita = 0

def actualizar_pantallas():
    """Dibuja el marcador actualizado en AMBAS pantallas al mismo tiempo"""
    str_local = str(goles_local)
    str_visita = str(goles_visita)
    
    for oled in pantallas:
        oled.fill(0) # Limpiar pantalla actual
        
        # Encabezado
        oled.text("MARCADOR PICO W", 4, 2)
        oled.line(0, 13, 128, 13, 1) # Línea divisoria
        
        # Nombres de los equipos
        oled.text("LOCAL", 12, 22)
        oled.text("VISITA", 76, 22)
        
        # Marcador de Goles
        oled.text(str_local, 28, 40)
        oled.text(" - ", 56, 40)
        oled.text(str_visita, 96, 40)
        
        # Borde exterior
        oled.rect(0, 0, 128, 64, 1)
        
        oled.show() # Renderizar en la pantalla física

# Dibujar en ambas pantallas por primera vez
actualizar_pantallas()

# ==========================================================
# 2. CONFIGURACIÓN DE RED WI-FI (Access Point)
# ==========================================================
WIFI_SSID = 'Pico_Marcador'
WIFI_PASSWORD = '12345678'  # Mínimo 8 caracteres

ap = network.WLAN(network.AP_IF)

# Asignar credenciales antes de activar
ap.config(essid=WIFI_SSID, password=WIFI_PASSWORD)
ap.active(True)

time.sleep(0.5) # Pausa de estabilización

# Configurar Socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)

print("==========================================================")
print(f" Servidor de Doble Marcador Listo")
print(f" 1. Conéctate a la red Wi-Fi: {WIFI_SSID}")
print(f" 2. Contraseña: {WIFI_PASSWORD}")
print(f" 3. Entra desde el navegador a: 192.168.4.1")
print("==========================================================")

# ==========================================================
# 3. BUCLE PRINCIPAL (Servidor Web)
# ==========================================================
while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode('utf-8')
        
        # Procesar los botones presionados en el celular
        if "GET /local_mas" in request:
            goles_local += 1
            actualizar_pantallas()
        elif "GET /local_menos" in request and goles_local > 0:
            goles_local -= 1
            actualizar_pantallas()
        elif "GET /visita_mas" in request:
            goles_visita += 1
            actualizar_pantallas()
        elif "GET /visita_menos" in request and goles_visita > 0:
            goles_visita -= 1
            actualizar_pantallas()
        elif "GET /reset" in request:
            goles_local = 0
            goles_visita = 0
            actualizar_pantallas()

        # Interfaz web responsiva para el celular
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Control de Marcador</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #121212; color: white; text-align: center; padding: 15px; margin: 0; }}
                .card {{ max-width: 400px; margin: auto; padding: 20px; background: #1e1e1e; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
                h2 {{ color: #00e676; margin-top: 0; }}
                .scoreboard {{ display: flex; justify-content: space-around; margin-bottom: 20px; }}
                .team {{ background: #2a2a2a; padding: 15px; border-radius: 10px; width: 42%; }}
                .score {{ font-size: 3.5rem; font-weight: bold; color: #ffeb3b; margin: 10px 0; }}
                .btn {{ display: inline-block; padding: 14px 20px; font-size: 1.3rem; font-weight: bold; color: white; border: none; border-radius: 8px; text-decoration: none; margin: 4px; }}
                .btn-add {{ background-color: #2e7d32; }}
                .btn-add:active {{ background-color: #1b5e20; }}
                .btn-sub {{ background-color: #c62828; }}
                .btn-sub:active {{ background-color: #b71c1c; }}
                .btn-reset {{ background-color: #f57c00; width: 90%; margin-top: 15px; display: block; margin-left: auto; margin-right: auto; }}
                .btn-reset:active {{ background-color: #e65100; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Marcador de Fútbol</h2>
                <div class="scoreboard">
                    <div class="team">
                        <h3>LOCAL</h3>
                        <div class="score">{goles_local}</div>
                        <a href="/local_mas" class="btn btn-add">+1</a>
                        <a href="/local_menos" class="btn btn-sub">-1</a>
                    </div>
                    <div class="team">
                        <h3>VISITA</h3>
                        <div class="score">{goles_visita}</div>
                        <a href="/visita_mas" class="btn btn-add">+1</a>
                        <a href="/visita_menos" class="btn btn-sub">-1</a>
                    </div>
                </div>
                <a href="/reset" class="btn btn-reset">Reiniciar Marcador</a>
            </div>
        </body>
        </html>"""
        
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n')
        conn.sendall(html)
        conn.close()
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
