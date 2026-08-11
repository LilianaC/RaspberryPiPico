import machine
import time
import urandom
import os
import network
import socket

# ==========================================================
# 🛑 BITÁCORA ALEATORIZADA GENERADA POR PYDOE
# ==========================================================
LISTA_CORRIDAS = [
    (1, 'Rojo', 'Tono Agudo (4000 Hz)'),
    (2, 'Amarillo', 'Tono Medio (1000 Hz)'),
    (2, 'Verde', 'Tono Grave (250 Hz)'),
    (3, 'Verde', 'Tono Medio (1000 Hz)'),
    (1, 'Verde', 'Tono Grave (250 Hz)'),
    (2, 'Rojo', 'Tono Grave (250 Hz)'),
    (2, 'Amarillo', 'Tono Agudo (4000 Hz)'),
    (2, 'Rojo', 'Tono Agudo (4000 Hz)'),
    (2, 'Verde', 'Tono Medio (1000 Hz)'),
    (3, 'Verde', 'Tono Agudo (4000 Hz)'),
    (1, 'Amarillo', 'Tono Grave (250 Hz)'),
    (1, 'Amarillo', 'Tono Medio (1000 Hz)'),
    (1, 'Rojo', 'Tono Medio (1000 Hz)'),
    (1, 'Rojo', 'Tono Grave (250 Hz)'),
    (2, 'Verde', 'Tono Agudo (4000 Hz)'),
    (3, 'Amarillo', 'Tono Medio (1000 Hz)'),
    (1, 'Verde', 'Tono Medio (1000 Hz)'),
    (3, 'Amarillo', 'Tono Agudo (4000 Hz)'),
    (3, 'Rojo', 'Tono Medio (1000 Hz)'),
    (3, 'Verde', 'Tono Grave (250 Hz)'),
    (3, 'Rojo', 'Tono Agudo (4000 Hz)'),
    (3, 'Rojo', 'Tono Grave (250 Hz)'),
    (1, 'Amarillo', 'Tono Agudo (4000 Hz)'),
    (2, 'Amarillo', 'Tono Grave (250 Hz)'),
    (2, 'Rojo', 'Tono Medio (1000 Hz)'),
    (3, 'Amarillo', 'Tono Grave (250 Hz)'),
    (1, 'Verde', 'Tono Agudo (4000 Hz)'),
]

# ==========================================================
# CONFIGURACIÓN DE HARDWARE
# ==========================================================
led_verde = machine.Pin(14, machine.Pin.OUT)
led_amarillo = machine.Pin(15, machine.Pin.OUT)
led_rojo = machine.Pin(12, machine.Pin.OUT)
dict_leds = {'Verde': led_verde, 'Amarillo': led_amarillo, 'Rojo': led_rojo}

buzzer = machine.PWM(machine.Pin(17))
ARCHIVO_RESULTADOS = "reaccion_automatizada.csv"

# Estimación de retraso por procesamiento de socket/pantalla táctil (ms)
OVERHEAD_SOCKET_MS = 12

# ==========================================================
# CONFIGURACIÓN DE RED CON CONTRASEÑA (CORREGIDA)
# ==========================================================
WIFI_SSID = 'Pico_DoE_Lab'
WIFI_PASSWORD = '12345678'  # ⚠️ Mínimo 8 caracteres

ap = network.WLAN(network.AP_IF)

# 1. PASO CLAVE: Asignar SSID y PASSWORD con la red AÚN APAGADA
ap.config(essid=WIFI_SSID, password=WIFI_PASSWORD)

# 2. PASO CLAVE: Activar la red DESPUÉS de aplicar la seguridad
ap.active(True)

# Esperar medio segundo para que el hardware estabilice la señal
time.sleep(0.5)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)

# ==========================================================
# FUNCIONES DE CONTROL
# ==========================================================
def inicializar_csv():
    try:
        os.stat(ARCHIVO_RESULTADOS)
    except OSError:
        with open(ARCHIVO_RESULTADOS, mode='w') as f:
            f.write('Replica,Color_LED,Tono_Buzzer,Tiempo_Reaccion_ms\n')

def encender_alarma(color, tono):
    for led in dict_leds.values(): led.value(0)
    if color in dict_leds:
        dict_leds[color].value(1)
        
    if tono == 'Tono Grave (250 Hz)': buzzer.freq(250)
    elif tono == 'Tono Medio (1000 Hz)': buzzer.freq(1000)
    elif tono == 'Tono Agudo (4000 Hz)': buzzer.freq(4000)
    buzzer.duty_u16(32768)

def apagar_alarma():
    for led in dict_leds.values(): led.value(0)
    buzzer.duty_u16(0)

def generar_html(corrida_actual, total_corridas, estado, tiempo_ms=0, latencia_ms=0):
    if estado == "ESPERANDO":
        contenido = f"""
            <h3>Corrida {corrida_actual + 1} de {total_corridas}</h3>
            <p>Atento a los estímulos visuales y auditivos...</p>
            <button onclick="enviarRespuesta()" class="btn btn-pulsar">¡RESPONDER!</button>
            
            <script>
            function enviarRespuesta() {{
                var tTouch = performance.now();
                window.location.href = "/pulsar?t=" + tTouch;
            }}
            </script>
        """
    elif estado == "RESULTADO":
        contenido = f"""
            <h3 style="color: #27ae60;">¡Tiempo Registrado!</h3>
            <div class="tiempo">{tiempo_ms} ms</div>
            <p style="color: #7f8c8d; font-size: 0.85rem;">Latencia descontada: ~{latencia_ms} ms</p>
            <a href="/siguiente" class="btn btn-siguiente">Siguiente Prueba ➔</a>
        """
    elif estado == "FIN":
        contenido = f"""
            <h2 style="color: #2980b9;">🎉 ¡Experimento Finalizado! 🎉</h2>
            <p>Todos los datos se han guardado exitosamente en <b>{ARCHIVO_RESULTADOS}</b>.</p>
        """

    return f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Laboratorio DoE</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f3f6; text-align: center; padding: 20px; margin: 0; }}
            .card {{ background: white; padding: 30px 20px; border-radius: 15px; max-width: 400px; margin: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            h2 {{ color: #2c3e50; margin-top: 0; }}
            .tiempo {{ font-size: 3rem; font-weight: bold; color: #e74c3c; margin: 15px 0; }}
            .btn {{ display: block; width: 100%; border: none; padding: 22px; font-size: 1.8rem; font-weight: bold; color: white; border-radius: 12px; margin: 15px 0; cursor: pointer; box-sizing: border-box; text-decoration: none; }}
            .btn-pulsar {{ background: #e74c3c; box-shadow: 0 6px #c0392b; }}
            .btn-pulsar:active {{ background: #c0392b; transform: translateY(4px); box-shadow: 0 2px #c0392b; }}
            .btn-siguiente {{ background: #3498db; font-size: 1.2rem; padding: 15px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Experimento DoE</h2>
            {contenido}
        </div>
    </body>
    </html>"""

# ==========================================================
# BUCLE PRINCIPAL DE EJECUCIÓN
# ==========================================================
def iniciar_laboratorio():
    inicializar_csv()
    total_pruebas = len(LISTA_CORRIDAS)
    
    print("==========================================================")
    print("    SISTEMA DE ADQUISICIÓN DE DATOS DoE INICIADO")
    print(f"    1. Conéctate a la red Wi-Fi: {WIFI_SSID}")
    print(f"    2. Contraseña: {WIFI_PASSWORD}")
    print("    3. Abre el navegador e ingresa a: 192.168.4.1")
    print("==========================================================")
    
    indice = 0
    estado = "ESPERANDO" # Estados: ESPERANDO, RESULTADO, FIN
    marca_inicial = 0
    tiempo_reaccion = 0
    latencia_aplicada = 0
    alarma_activa = False

    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024).decode('utf-8')
            
            # --- DISPARAR ALARMA ALEATORIA ---
            if estado == "ESPERANDO" and not alarma_activa:
                replica, color, tono = LISTA_CORRIDAS[indice]
                print(f"\n▶️ [CORRIDA {indice + 1}/{total_pruebas}] Réplica: {replica} | LED: {color} | Buzzer: {tono}")
                print("Esperando retraso aleatorio anti-anticipación...")
                
                time.sleep(urandom.uniform(2.0, 4.5))
                
                # 💥 ¡Encender Alarma y marcar inicio del cronómetro de hardware!
                marca_inicial = time.ticks_ms()
                encender_alarma(color, tono)
                alarma_activa = True

            # --- RESPUESTA DESDE EL CELULAR ---
            if "GET /pulsar" in request and estado == "ESPERANDO":
                t_llegada_pico = time.ticks_ms()
                tiempo_bruto = time.ticks_diff(t_llegada_pico, marca_inicial)
                
                # Apagar estímulos inmediatamente
                apagar_alarma()
                alarma_activa = False
                
                # Cálculo con descuento de overhead de red
                tiempo_corregido = max(0, tiempo_bruto - OVERHEAD_SOCKET_MS)
                latencia_aplicada = OVERHEAD_SOCKET_MS
                
                replica, color, tono = LISTA_CORRIDAS[indice]
                
                # 💾 Guardar en el CSV
                fila_datos = f"{replica},{color},{tono},{tiempo_corregido}\n"
                with open(ARCHIVO_RESULTADOS, mode='a') as f:
                    f.write(fila_datos)
                
                print(f"🎯 Tiempo Bruto: {tiempo_bruto} ms | Tiempo Corregido: {tiempo_corregido} ms (Latencia descontada: -{latencia_aplicada} ms)")
                print("💾 Fila registrada en CSV.")
                
                tiempo_reaccion = tiempo_corregido
                estado = "RESULTADO"

            elif "GET /siguiente" in request and estado == "RESULTADO":
                indice += 1
                if indice < total_pruebas:
                    estado = "ESPERANDO"
                else:
                    estado = "FIN"
                    print("\n==========================================================")
                    print(" 🎉 ¡EXPERIMENTO COMPLETADO CON ÉXITO! 🎉")
                    print(f" Descarga el archivo '{ARCHIVO_RESULTADOS}' desde Thonny.")
                    print("==========================================================")

            # --- MANDAR PÁGINA WEB AL CELULAR ---
            html = generar_html(indice, total_pruebas, estado, tiempo_reaccion, latencia_aplicada)
            conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n')
            conn.sendall(html)
            conn.close()

        except Exception as e:
            if 'conn' in locals():
                conn.close()

# ==========================================================
# 🚀 ARRANQUE AUTOMÁTICO
# ==========================================================
iniciar_laboratorio()
