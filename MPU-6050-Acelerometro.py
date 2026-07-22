from machine import Pin, I2C
import time
import ustruct

# 1. Inicializar el bus I2C en los pines GP0 y GP1
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Dirección I2C por defecto del MPU-6050
MPU_ADDR = 0x68

# 2. Despertar el sensor
#(escribir 0 en el registro de control de energía 0x6B)
try:
    i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')
    print("¡MPU-6050 detectado y despierto con éxito!")
except OSError:
    print("Error: No se encuentra el sensor. Revisa las soldaduras y cables.")

# Función para convertir datos crudos de 16 bits
#(código de complemento a dos)

def combinar_bytes(alto, bajo):
    val = (alto << 8) | bajo
    return val if val < 32768 else val - 65536

print("\nLeyendo Acelerómetro (Fuerzas G)... Mueve el sensor.")
time.sleep(1)

try:
    while True:
        # Leer 6 bytes desde el registro del acelerómetro (0x3B)
        # Contiene los ejes X, Y y Z (2 bytes por eje)
        datos = i2c.readfrom_mem(MPU_ADDR, 0x3B, 6)
        
        # Decodificar cada eje
        raw_x = combinar_bytes(datos[0], datos[1])
        raw_y = combinar_bytes(datos[2], datos[3])
        raw_z = combinar_bytes(datos[4], datos[5])
        
        # Convertir a Fuerza G
        #(Escala por defecto de +/-2g usa factor 16384)
        g_x = raw_x / 16384.0
        g_y = raw_y / 16384.0
        g_z = raw_z / 16384.0
        
        # Imprimir en consola de forma estética
#       print(f"Eje X: {g_x:+.2f}g  |  Eje Y: {g_y:+.2f}g  |  Eje Z: {g_z:+.2f}g")
        print(g_x," ",g_y," ",g_z)
        time.sleep_ms(200)

except KeyboardInterrupt:
    print("\nLectura detenida.")
