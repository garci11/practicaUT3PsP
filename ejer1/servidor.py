import socket
import json
import random
from threading import Thread, Lock

# Lista para los últimos 10 jugadores (FIFO)
ultimos_jugadores = []
lock = Lock()

def manejar_cliente(cliente, direccion):
    """Maneja la petición de un cliente"""
    print(f"Cliente conectado: {direccion}")
    
    try:
        # Recibir el nick del jugador
        data = cliente.recv(1024)
        if not data:
            cliente.close()
            return
            
        mensaje_json = json.loads(data.decode())
        nick = mensaje_json.get("nick", "Anonimo")
        
        print(f"Jugador: {nick}")
        
        # Generar número aleatorio entre 0 y 100
        numero_secreto = random.randint(0, 100)
        intentos = 0
        max_intentos = 10
        
        print(f"Número secreto para {nick}: {numero_secreto}")
        
        # Enviar confirmación inicial
        respuesta = {"num": 1}
        cliente.send(json.dumps(respuesta).encode())
        
        # Bucle del juego
        while intentos < max_intentos:
            # Recibir intento del cliente
            data = cliente.recv(1024)
            if not data:
                break
                
            mensaje_json = json.loads(data.decode())
            numero_cliente = mensaje_json.get("num")
            
            intentos += 1
            print(f"{nick} intenta: {numero_cliente} (intento {intentos})")
            
            # Verificar si adivinó
            if numero_cliente == numero_secreto:
                # ¡Adivinó!
                with lock:
                    ultimos_jugadores.append({
                        "nick": nick,
                        "intentos": intentos
                    })
                    # Mantener solo los últimos 10
                    if len(ultimos_jugadores) > 10:
                        ultimos_jugadores.pop(0)
                    lista_jugadores = list(ultimos_jugadores)
                
                respuesta = {
                    "res": "ok",
                    "datos": {
                        "intentos": intentos,
                        "ultimos": lista_jugadores
                    }
                }
                cliente.send(json.dumps(respuesta).encode())
                print(f"¡{nick} adivinó el número en {intentos} intentos!")
                break
            else:
                # No adivinó, dar pista
                if numero_cliente > numero_secreto:
                    pista = "menor"
                else:
                    pista = "mayor"
                
                respuesta = {
                    "res": "error",
                    "datos": {
                        "intentos": intentos,
                        "pista": pista
                    }
                }
                cliente.send(json.dumps(respuesta).encode())
        
        # Si se acabaron los intentos
        if intentos >= max_intentos and numero_cliente != numero_secreto:
            with lock:
                ultimos_jugadores.append({
                    "nick": nick,
                    "intentos": max_intentos
                })
                # Mantener solo los últimos 10
                if len(ultimos_jugadores) > 10:
                    ultimos_jugadores.pop(0)
                lista_jugadores = list(ultimos_jugadores)
            
            respuesta = {
                "res": "perdido",
                "datos": {
                    "intentos": max_intentos,
                    "numero_secreto": numero_secreto,
                    "ultimos": lista_jugadores
                }
            }
            cliente.send(json.dumps(respuesta).encode())
            print(f"{nick} no adivinó el número. Era {numero_secreto}")
    
    except Exception as e:
        print(f"Error con cliente {direccion}: {e}")
    finally:
        cliente.close()
        print(f"Conexión cerrada: {direccion}")

# Configuración del servidor
direccion = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(direccion)

sock.listen(5)

print(f"Servidor escuchando en {direccion}...")

while True:
    cliente, direccion_cliente = sock.accept()
    Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()