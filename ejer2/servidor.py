import socket
import json
from threading import Thread, Lock

# Historial de las últimas 5 operaciones
historial = []
lock = Lock()

def calcular(operacion, a, b):
    """Realiza la operación matemática"""
    if operacion == "suma":
        return a + b
    elif operacion == "resta":
        return a - b
    elif operacion == "multiplicacion":
        return a * b
    elif operacion == "division":
        if b == 0:
            return None
        return a / b
    else:
        return None

def manejar_cliente(cliente, direccion):
    """Maneja las peticiones del cliente"""
    print(f"Cliente conectado: {direccion}")
    
    try:
        # Recibir operación
        data = cliente.recv(1024)
        if not data:
            cliente.close()
            return
        
        mensaje = json.loads(data.decode())
        operacion = mensaje.get("op")
        a = mensaje.get("a")
        b = mensaje.get("b")
        
        print(f"Operación recibida: {operacion}({a}, {b})")
        
        # Calcular resultado
        resultado = calcular(operacion, a, b)
        
        if resultado is None:
            # Error en la operación
            if operacion == "division" and b == 0:
                respuesta = {
                    "res": "error",
                    "mensaje": "No se puede dividir por cero"
                }
            else:
                respuesta = {
                    "res": "error",
                    "mensaje": f"Operación '{operacion}' no válida"
                }
        else:
            # Operación exitosa
            with lock:
                historial.append({
                    "operacion": operacion,
                    "a": a,
                    "b": b,
                    "resultado": resultado
                })
                # Mantener solo las últimas 5
                if len(historial) > 5:
                    historial.pop(0)
                
                ultimas = list(historial)
            
            respuesta = {
                "res": "ok",
                "resultado": resultado,
                "ultimas": ultimas
            }
        
        # Enviar respuesta
        cliente.send(json.dumps(respuesta).encode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cliente.close()
        print(f"Conexión cerrada: {direccion}")

# Configuración del servidor
direccion = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(direccion)
sock.listen(5)

print(f"Servidor Calculadora escuchando en {direccion}...")

while True:
    cliente, direccion_cliente = sock.accept()
    Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()