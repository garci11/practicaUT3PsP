import socket
import json
from threading import Thread, Lock

# Sistema de turnos
ultimo_numero = 0
turno_actual = 1
turnos_asignados = {}  # {nick: numero_turno}
lock = Lock()

def manejar_cliente(cliente, direccion):
    """Maneja las peticiones del cliente"""
    global ultimo_numero, turno_actual
    
    print(f"Cliente conectado: {direccion}")
    
    try:
        # Recibir petición
        data = cliente.recv(1024)
        if not data:
            cliente.close()
            return
        
        mensaje = json.loads(data.decode())
        accion = mensaje.get("accion")
        nick = mensaje.get("nick")
        
        print(f"Petición de {nick}: {accion}")
        
        with lock:
            if accion == "pedir_turno":
                # Dar nuevo turno
                if nick in turnos_asignados:
                    respuesta = {
                        "res": "error",
                        "mensaje": f"Ya tienes el turno número {turnos_asignados[nick]}"
                    }
                else:
                    ultimo_numero += 1
                    turnos_asignados[nick] = ultimo_numero
                    
                    # Calcular cuántos hay delante
                    delante = ultimo_numero - turno_actual
                    
                    respuesta = {
                        "res": "ok",
                        "turno": ultimo_numero,
                        "delante": delante,
                        "mensaje": f"Tu turno es el número {ultimo_numero}"
                    }
            
            elif accion == "consultar":
                # Consultar estado del turno
                if nick not in turnos_asignados:
                    respuesta = {
                        "res": "error",
                        "mensaje": "No tienes ningún turno asignado"
                    }
                else:
                    turno_usuario = turnos_asignados[nick]
                    
                    if turno_usuario < turno_actual:
                        respuesta = {
                            "res": "error",
                            "mensaje": "Tu turno ya pasó"
                        }
                    elif turno_usuario == turno_actual:
                        respuesta = {
                            "res": "ok",
                            "mensaje": "¡ES TU TURNO!",
                            "turno": turno_usuario,
                            "delante": 0
                        }
                    else:
                        delante = turno_usuario - turno_actual
                        respuesta = {
                            "res": "ok",
                            "turno": turno_usuario,
                            "delante": delante,
                            "turno_actual": turno_actual,
                            "mensaje": f"Hay {delante} personas delante de ti"
                        }
            
            elif accion == "atender":
                # Consumir turno (solo si es tu turno)
                if nick not in turnos_asignados:
                    respuesta = {
                        "res": "error",
                        "mensaje": "No tienes ningún turno asignado"
                    }
                elif turnos_asignados[nick] != turno_actual:
                    delante = turnos_asignados[nick] - turno_actual
                    respuesta = {
                        "res": "error",
                        "mensaje": f"No es tu turno. Hay {delante} personas delante"
                    }
                else:
                    # Atender al usuario
                    del turnos_asignados[nick]
                    turno_actual += 1
                    
                    respuesta = {
                        "res": "ok",
                        "mensaje": "Has sido atendido. ¡Gracias!",
                        "siguiente_turno": turno_actual
                    }
            
            else:
                respuesta = {
                    "res": "error",
                    "mensaje": f"Acción '{accion}' no válida"
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

print(f"Servidor de Turnos escuchando en {direccion}...")
print("Acciones: pedir_turno, consultar, atender\n")

while True:
    cliente, direccion_cliente = sock.accept()
    Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()