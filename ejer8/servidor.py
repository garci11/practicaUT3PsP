import socket
import json
from threading import Thread, Lock
from datetime import datetime

# Estado de la subasta
ARTICULO = "Laptop Gaming RTX 4090"
PRECIO_INICIAL = 100
subasta_activa = True
puja_actual = PRECIO_INICIAL
ganador_actual = None
historial_pujas = []
lock = Lock()

def manejar_cliente(cliente, direccion):
    """Maneja las pujas de un cliente"""
    print(f"Cliente conectado: {direccion}")
    
    try:
        # Recibir nick
        data = cliente.recv(1024)
        if not data:
            cliente.close()
            return
        
        mensaje = json.loads(data.decode())
        nick = mensaje.get("nick")
        
        print(f"Pujador conectado: {nick}")
        
        # Enviar información de la subasta
        with lock:
            info_subasta = {
                "res": "ok",
                "articulo": ARTICULO,
                "precio_inicial": PRECIO_INICIAL,
                "puja_actual": puja_actual,
                "ganador_actual": ganador_actual,
                "subasta_activa": subasta_activa,
                "total_pujas": len(historial_pujas)
            }
        
        cliente.send(json.dumps(info_subasta).encode())
        
        # Bucle de pujas
        while True:
            data = cliente.recv(1024)
            if not data:
                break
            
            peticion = json.loads(data.decode())
            accion = peticion.get("accion")
            
            if accion == "pujar":
                cantidad = peticion.get("cantidad")
                
                with lock:
                    if not subasta_activa:
                        respuesta = {
                            "res": "error",
                            "mensaje": "La subasta ha terminado",
                            "ganador": ganador_actual,
                            "precio_final": puja_actual
                        }
                    elif cantidad <= puja_actual:
                        respuesta = {
                            "res": "error",
                            "mensaje": f"Debes pujar más de {puja_actual}€",
                            "puja_actual": puja_actual,
                            "ganador_actual": ganador_actual
                        }
                    else:
                        # Puja válida
                        puja_actual = cantidad
                        ganador_actual = nick
                        
                        historial_pujas.append({
                            "nick": nick,
                            "cantidad": cantidad,
                            "hora": datetime.now().strftime("%H:%M:%S")
                        })
                        
                        respuesta = {
                            "res": "ok",
                            "mensaje": f"¡Puja aceptada! Ahora vas ganando con {cantidad}€",
                            "puja_actual": puja_actual,
                            "ganador_actual": ganador_actual,
                            "total_pujas": len(historial_pujas)
                        }
                        
                        print(f"💰 Nueva puja: {nick} - {cantidad}€")
                
                cliente.send(json.dumps(respuesta).encode())
            
            elif accion == "consultar":
                # Consultar estado actual
                with lock:
                    respuesta = {
                        "res": "ok",
                        "puja_actual": puja_actual,
                        "ganador_actual": ganador_actual,
                        "subasta_activa": subasta_activa,
                        "total_pujas": len(historial_pujas)
                    }
                
                cliente.send(json.dumps(respuesta).encode())
            
            elif accion == "historial":
                # Ver historial de pujas
                with lock:
                    respuesta = {
                        "res": "ok",
                        "historial": list(historial_pujas),
                        "total": len(historial_pujas)
                    }
                
                cliente.send(json.dumps(respuesta).encode())
            
            elif accion == "cerrar":
                # Cerrar subasta (solo para demostración)
                with lock:
                    if subasta_activa:
                        subasta_activa = False
                        respuesta = {
                            "res": "ok",
                            "mensaje": "Subasta cerrada",
                            "ganador": ganador_actual,
                            "precio_final": puja_actual,
                            "historial": list(historial_pujas)
                        }
                        print(f"\n🔨 SUBASTA CERRADA")
                        print(f"Ganador: {ganador_actual}")
                        print(f"Precio final: {puja_actual}€\n")
                    else:
                        respuesta = {
                            "res": "error",
                            "mensaje": "La subasta ya estaba cerrada"
                        }
                
                cliente.send(json.dumps(respuesta).encode())
            
            elif accion == "salir":
                respuesta = {
                    "res": "ok",
                    "mensaje": "Hasta luego"
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
sock.listen(10)

print("="*60)
print("🔨 SERVIDOR DE SUBASTAS 🔨")
print("="*60)
print(f"Artículo en subasta: {ARTICULO}")
print(f"Precio inicial: {PRECIO_INICIAL}€")
print(f"Escuchando en {direccion}...")
print("="*60 + "\n")

while True:
    cliente, direccion_cliente = sock.accept()
    Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()