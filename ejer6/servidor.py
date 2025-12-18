import socket
import json
from threading import Thread, Lock
import hashlib

# Base de datos de usuarios {nick: password_hash}
usuarios = {}
usuarios_online = []
lock = Lock()

def hash_password(password):
    """Hashea la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def manejar_cliente(cliente, direccion):
    """Maneja las peticiones del cliente"""
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
        password = mensaje.get("password")
        
        print(f"Petición: {accion} de usuario {nick}")
        
        with lock:
            if accion == "registro":
                # Registrar nuevo usuario
                if nick in usuarios:
                    respuesta = {
                        "res": "error",
                        "mensaje": f"El usuario '{nick}' ya existe"
                    }
                elif len(password) < 4:
                    respuesta = {
                        "res": "error",
                        "mensaje": "La contraseña debe tener al menos 4 caracteres"
                    }
                else:
                    # Guardar usuario
                    usuarios[nick] = hash_password(password)
                    usuarios_online.append(nick)
                    
                    respuesta = {
                        "res": "ok",
                        "mensaje": "Usuario registrado correctamente",
                        "usuarios_totales": len(usuarios),
                        "usuarios_online": len(usuarios_online)
                    }
                    print(f"Usuario '{nick}' registrado")
            
            elif accion == "login":
                # Hacer login
                if nick not in usuarios:
                    respuesta = {
                        "res": "error",
                        "mensaje": f"El usuario '{nick}' no existe"
                    }
                elif usuarios[nick] != hash_password(password):
                    respuesta = {
                        "res": "error",
                        "mensaje": "Contraseña incorrecta"
                    }
                else:
                    # Login exitoso
                    if nick not in usuarios_online:
                        usuarios_online.append(nick)
                    
                    respuesta = {
                        "res": "ok",
                        "mensaje": f"Bienvenido de nuevo, {nick}!",
                        "usuarios_totales": len(usuarios),
                        "usuarios_online": len(usuarios_online),
                        "lista_online": list(usuarios_online)
                    }
                    print(f"Usuario '{nick}' ha hecho login")
            
            elif accion == "listar":
                # Listar usuarios online
                respuesta = {
                    "res": "ok",
                    "usuarios_online": list(usuarios_online),
                    "total_online": len(usuarios_online),
                    "total_registrados": len(usuarios)
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

print(f"Servidor de Autenticación escuchando en {direccion}...")
print("Acciones: registro, login, listar\n")

while True:
    cliente, direccion_cliente = sock.accept()
    Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()