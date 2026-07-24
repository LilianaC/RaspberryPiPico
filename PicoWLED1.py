import network
import socket
import machine

# 1. Configurar el LED y la red Wi-Fi
led = machine.Pin("LED", machine.Pin.OUT)
ap = network.WLAN(network.AP_IF)
ap.config(essid='Pico_Led_Web', password='miPassword123')
ap.active(True)


# 2. Abrir el puerto de comunicación (Servidor Web)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)

print("Conéctate a 'Pico_Led_Web' y entra a 192.168.4.1")

# 3. Bucle principal
while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode('utf-8')
    
    # Revisar qué botón presionó el usuario en el celular
    if "GET /on" in request:
        led.on()
    elif "GET /off" in request:
        led.off()
        
    # HTML minimalista: Solo dos botones grandes
    html = """<!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { text-align: center; font-family: sans-serif; padding-top: 50px; background: #f0f0f0; }
        .btn { display: block; width: 200px; margin: 20px auto; padding: 20px; font-size: 1.5rem; color: white; border-radius: 10px; text-decoration: none; font-weight: bold; }
        .on { background: #2ecc71; } .off { background: #e74c3c; }
    </style></head>
    <body>
        <h1>Control de LED</h1>
        <a href="/on" class="btn on">ENCENDER</a>
        <a href="/off" class="btn off">APAGAR</a>
    </body>
    </html>"""
    
    # Enviar la página y cerrar conexión
    conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n')
    conn.sendall(html)
    conn.close()
