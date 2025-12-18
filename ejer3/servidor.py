import socket
import json
from threading import Thread, Lock

# Votos y usuarios que ya votaron
votos = {"A": 0, "B": 0, "C": 0}
usuarios_votaron = []
lock = Lock()

def manejar_cliente(cliente, direccion):
    """Maneja la votación de un cliente"""
    print(f"Cliente conectado: {direccion}")
    
    try:
        # Recibir nick y voto
        data = cliente.recv(1024)
        if not data:
            cliente.close()
            return
        
        mensaje = json.loads(data.decode())
        nick = mensaje.get("nick")
        voto = mensaje.get("voto")
        
        print(f"{nick} quiere votar por {voto}")
        
        with lock:
            # Verificar si ya votó
            if nick in usuarios_votaron:
                respuesta = {
                    "res": "error",
                    "mensaje": "Ya has votado anteriormente"
                }
            # Verificar que el voto sea válido
            elif voto not in votos:
                respuesta = {
                    "res": "error",
                    "mensaje": f"Opción '{voto}' no válida. Opciones: A, B, C"
                }
            else:
                # Registrar voto
                votos[voto] += 1
                usuarios_votaron.append(nick)
                
                # Calcular total
                total = sum(votos.values())
                
                respuesta = {
                    "res": "ok",
                    "mensaje": "Voto registrado correctamente",
                    "resultados": {
                        "votos": dict(votos),
                        "total": total,
                        "porcentajes": {
                            "A": round(votos["A"] / total * 100, 2) if total > 0 else 0,
                            "B": round(votos["B"] / total * 100, 2) if total > 0 else 0,
                            "C": round(votos["C"] / total * 100, 2) if total > 0 else 0
                        }
                    }
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

print(f"Servidor de Votaciones escuchando en {direccion}...")
print("Opciones: A, B, C\n")

while True:
    cliente, direccion_cliente = sock.accept()
    Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()