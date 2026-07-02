from machine import Pin, PWM
import time

# Usamos el canal Rojo en el GP10
led_pwm = PWM(Pin(10))
# Fijamos la frecuencia a 1000 Hz 
led_pwm.freq(1000)

print("=== Demostración de PWM en Vivo ===")
print("Observa cómo varía el 'Duty Cycle' de 0 a 100%...")

try:
    while True:
        # 1. Incrementando el brillo (Aumentando el Duty Cycle)
        print("-> Subiendo brillo (Más tiempo encendido)")
        for ciclo in range(0, 65536, 1000):
            led_pwm.duty_u16(ciclo)
            time.sleep_ms(20)
            
        # 2. Mantener al brillo máximo un momento
        time.sleep_ms(500)
        
        # 3. Disminuyendo el brillo (Reduciendo el Duty Cycle)
        print("<- Bajando brillo (Más tiempo apagado)")
        for ciclo in range(65535, -1, -1000):
            led_pwm.duty_u16(ciclo)
            time.sleep_ms(20)
            
        # 4. Pausa completamente apagado
        time.sleep_ms(500)

except KeyboardInterrupt:
    # Asegurar que el LED quede completamente apagado al detener el video
    led_pwm.duty_u16(0)
    print("\nDemostración finalizada.")
