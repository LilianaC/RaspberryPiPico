import machine
import time
import urandom
import os

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
boton_joystick = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)

ARCHIVO_RESULTADOS = "reaccion_automatizada.csv"

# ==========================================================
# FUNCIONES DE CONTROL
# ==========================================================
def inicializar_csv():
    try:
        os.stat(ARCHIVO_RESULTADOS)
    except OSError:
        # Escribimos el encabezado directamente como una cadena de texto
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

# ==========================================================
# BUCLE EJECUTOR AUTOMÁTICO
# ==========================================================
def iniciar_laboratorio():
    inicializar_csv()
    total_pruebas = len(LISTA_CORRIDAS)
    
    print("==========================================================")
    print("   SISTEMA DE ADQUISICIÓN DE DATOS DoE INICIADO")
    print(f"   Se ejecutarán de forma secuencial {total_pruebas} pruebas.")
    print("==========================================================")
    
    for indice, prueba in enumerate(LISTA_CORRIDAS):
        replica, color, tono = prueba
        
        print(f"\n▶️ [CORRIDA {indice + 1}/{total_pruebas}] Réplica: {replica} | LED: {color} | Buzzer: {tono}")
        print("Esperando retraso aleatorio anti-anticipación...")
        
        time.sleep(urandom.uniform(2.0, 4.5))
        
        # 💥 ¡DISPARO DE ALARMA Y CRONÓMETRO!
        marca_inicial = time.ticks_ms()
        encender_alarma(color, tono)
        
        # Espera activa mientras el joystick esté en reposo (1)
        while boton_joystick.value() == 1:
            pass
            
        # ⏱️ ¡PALANCA PRESIONADA! El pin bajó a 0
        tiempo_reaccion = time.ticks_diff(time.ticks_ms(), marca_inicial)
        apagar_alarma()
        
        # Filtro hardware/software contra rebotes mecánicos
        time.sleep_ms(150)
        
        print(f"🎯 ¡Click! Joystick presionado. Tiempo: {tiempo_reaccion} ms")
        
        # 💾 ESCRITURA MANUAL EN CSV (Sin librerías externas)
        # Construimos la cadena de texto separada por comas y terminada en salto de línea (\n)
        fila_datos = f"{replica},{color},{tono},{tiempo_reaccion}\n"
        with open(ARCHIVO_RESULTADOS, mode='a') as f:
            f.write(fila_datos)
            
        print(f"💾 Fila guardada en el dispositivo.")
        
        if indice < total_pruebas - 1:
            print("Descansa 2 segundos... Preparando siguiente configuración aleatoria...")
            time.sleep(2.0)
            
    print("\n==========================================================")
    print(" 🎉 ¡EXPERIMENTO COMPLETADO CON ÉXITO! 🎉")
    print(f" Descarga el archivo '{ARCHIVO_RESULTADOS}' desde Thonny.")
    print("==========================================================")

# ==========================================================
# 🚀 ARRANQUE AUTOMÁTICO
# ==========================================================
iniciar_laboratorio()
