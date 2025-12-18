import socket
import json
from threading import Thread, Lock
from datetime import datetime

# Historial de mensajes
mensajes = []
lock = Lock()

def manejar_cliente(cliente, direccion):
    """Maneja las peticiones del cliente"""
    print(f"Cliente conectado: {direccion}")
    
    try:
        # Recibir petición inicial (nick)
        data = cliente.recv(1024)
        if not data:
            cliente.close()
            return
        
        mensaje = json.loads(data.decode())
        nick = mensaje.get("nick")
        
        print(f"Usuario conectado: {nick}")
        
        # Enviar últimos 10 mensajes
        with lock:
            ultimos = mensajes[-10:] if len(mensajes) > 10 else mensajes
        
        respuesta = {
            "res": "ok",
            "mensaje": "Bienvenido al chat",
            "ultimos_mensajes": ultimos
        }
        cliente.send(json.dumps(respuesta).encode())
        
        # Bucle de mensajes
        while True:
            data = cliente.recv(1024)
            if not data:
                break
            
            peticion = json.loads(data.decode())
            accion = peticion.get("accion")
            
            if accion == "enviar":
                # Guardar mensaje
                texto = peticion.get("texto")
                
                with lock:
                    mensajes.append({
                        "nick": nick,
                        "texto": texto,
                        "hora": datetime.now().strftime("%H:%M:%S")
                    })
                
                print(f"[{nick}]: {texto}")
                
                respuesta = {
                    "res": "ok",
                    "mensaje": "Mensaje enviado"
                }
                cliente.send(json.dumps(respuesta).encode())
            
            elif accion == "historial":
                # Enviar historial completo
                with lock:
                    historial_completo = list(mensajes)
                
                respuesta = {
                    "res": "ok",
                    "mensajes": historial_completo,
                    "total": len(historial_completo)
                }
                cliente.send(json.dumps(respuesta).encode())
            
            elif accion == "salir":
                respuesta = {
                    "res": "ok",
                    "mensaje": "Hasta luego!"
                }
                cliente.send(json.dumps(respuesta).encode())
                break
            
            else:
                respuesta = {
                    "res": "error",
                    "mensaje": f"Acción '{accion}' no válida"
                }
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

print(f"Servidor de Chat escuchando en {direccion}...")

while True:
    cliente, direccion_cliente = sock.accept()
    Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()