from machine import Pin, PWM
import time

# --- 1. CONFIGURACIÓN DEL HARDWARE ---
buzzer = PWM(Pin(17)) 

led_rojo = Pin(11, Pin.OUT)
led_verde = Pin(12, Pin.OUT)

def color_apagado():
    led_rojo.value(0); led_verde.value(0)

def color_verde():
    led_rojo.value(0); led_verde.value(1)

def color_rojo():
    led_rojo.value(1); led_verde.value(0)

def color_blanco():
    led_rojo.value(1); led_verde.value(1)

colores_patrios = [color_verde, color_blanco, color_rojo]

# --- 2. TUS TUPLAS ORIGINALES ---
NUEVAS_NOTAS = [
    (0, 0.69), (8.18, 0.0), (0, 1.38), (8.18, 0.0), (0, 1.03), (8.18, 0.0), (0, 1.03), 
    (8.18, 0.0), (0, 1.03), (8.18, 0.0), (0, 1.03), (8.18, 0.0), (0, 1.03), (8.18, 0.0), 
    (0, 1.03), (8.18, 0.0), (0, 1.03), (8.18, 0.0), (0, 2.05), (8.18, 0.0), (0, 1.98), 
    (8.18, 0.0), (0, 1.96), (8.18, 0.0), (0, 1.98), (8.18, 0.0), (0, 2.0), (8.18, 0.0), 
    (0, 1.0), (293.66, 0.27), (0, 0.06), (293.66, 0.23), (0, 0.1), (246.94, 0.58), 
    (0, 0.08), (277.18, 0.27), (0, 0.06), (220.0, 0.14), (0, 0.03), (293.66, 0.22), 
    (0, 0.11), (293.66, 0.4), (0, 0.42), (246.94, 0.29), (0, 0.04), (277.18, 0.27), 
    (0, 0.06), (220.0, 0.16), (0, 0.01), (293.66, 0.41), (0, 0.08), (293.66, 0.58), 
    (0, 0.08), (246.94, 0.14), (0, 0.03), (277.18, 0.39), (0, 0.1), (220.0, 0.16), 
    (0, 0.0), (196.0, 0.41), (0, 0.08), (164.81, 0.82), (0, 2.81), (293.66, 0.25), 
    (0, 0.08), (293.66, 0.26), (0, 0.07), (277.18, 0.53), (0, 0.14), (246.94, 0.3), 
    (0, 0.03), (220.0, 0.28), (0, 0.06), (196.0, 0.28), (0, 0.06), (196.0, 0.41), 
    (0, 0.25), (164.81, 0.31), (0, 0.02), (185.0, 0.27), (0, 0.06), (196.0, 0.14), 
    (0, 0.03), (220.0, 0.42), (0, 0.08), (220.0, 0.37), (0, 0.3), (293.66, 0.27), 
    (0, 0.06), (277.18, 0.29), (0, 0.04), (246.94, 0.15), (0, 0.01), (220.0, 0.41), 
    (0, 0.1), (220.0, 0.35), (0, -0.01), (185.0, 0.97), (0, 2.4), (293.66, 0.28), 
    (0, 0.06), (293.66, 0.25), (0, 0.08), (246.94, 0.54), (0, 0.14), (277.18, 0.29), 
    (0, 0.04), (220.0, 0.13), (0, 0.03), (293.66, 0.42), (0, 0.09), (293.66, 0.31), 
    (0, 0.36), (246.94, 0.28), (0, 0.05), (277.18, 0.29), (0, 0.04), (220.0, 0.14), 
    (0, 0.03), (293.66, 0.33), (0, 0.17), (293.66, 0.36)
]

print("=========================================")
print(" ▶️ REPRODUCIENDO MELODÍA ")
print("=========================================")

indice_color = 0
musica_iniciada = False  # Nueva bandera para saltar los silencios largos del inicio

try:
    while True:
        for frecuencia_float, duracion_seg in NUEVAS_NOTAS:
            
            # 1. Filtro contra tiempos negativos o ceros
            if duracion_seg <= 0:
                continue 
            
            frecuencia = int(frecuencia_float)
            
            # 2. Lógica para silencios y frecuencias inaudibles (< 20Hz)
            if frecuencia < 20:
                # Si es un silencio, pero la música no ha empezado, lo saltamos
                if not musica_iniciada:
                    continue
                
                # Si la música ya empezó, respetamos los silencios normales de la canción
                buzzer.duty_u16(0)
                color_apagado()
                time.sleep(duracion_seg)
            
            # 3. Lógica para las notas musicales reales
            else:
                musica_iniciada = True # ¡Ya encontramos la primera nota!
                
                colores_patrios[indice_color]()
                indice_color = (indice_color + 1) % 3
                
                buzzer.freq(frecuencia)
                buzzer.duty_u16(16384) 
                time.sleep(duracion_seg)
                
                # Micro-silencio separador
                buzzer.duty_u16(0)
                time.sleep(0.015)
                
        print("\nCiclo terminado, reiniciando...")
        musica_iniciada = False # Reiniciamos la bandera para la siguiente vuelta
        time.sleep(2.0)

except KeyboardInterrupt:
    print("\n[INFO] Ejecución detenida.")
finally:
    buzzer.duty_u16(0)
    color_apagado()
    print("🔒 HW seguro.")
