import socket
import json

direccion_server = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(direccion_server)

print("Conexión establecida")
print("\n=== CHAT MULTIUSUARIO ===\n")

# Enviar nick
nick = input("Introduce tu nick: ")
paquete = json.dumps({"nick": nick})
sock.send(paquete.encode())

# Recibir bienvenida y últimos mensajes
respuesta = sock.recv(4096)
if respuesta:
    respuesta_dict = json.loads(respuesta.decode())
    print(f"\n{respuesta_dict['mensaje']}\n")
    
    if respuesta_dict['ultimos_mensajes']:
        print("--- ÚLTIMOS MENSAJES ---")
        for msg in respuesta_dict['ultimos_mensajes']:
            print(f"[{msg['hora']}] {msg['nick']}: {msg['texto']}")
        print()

print("Comandos:")
print("  - Escribe tu mensaje y presiona Enter")
print("  - 'historial' para ver todos los mensajes")
print("  - 'salir' para desconectar\n")

# Bucle de mensajes
while True:
    entrada = input(f"[{nick}] >> ")
    
    if entrada.lower() == "historial":
        # Pedir historial
        paquete = json.dumps({"accion": "historial"})
        sock.send(paquete.encode())
        
        respuesta = sock.recv(8192)
        if respuesta:
            respuesta_dict = json.loads(respuesta.decode())
            print(f"\n--- HISTORIAL COMPLETO ({respuesta_dict['total']} mensajes) ---")
            for msg in respuesta_dict['mensajes']:
                print(f"[{msg['hora']}] {msg['nick']}: {msg['texto']}")
            print()
    
    elif entrada.lower() == "salir":
        # Salir
        paquete = json.dumps({"accion": "salir"})
        sock.send(paquete.encode())
        
        respuesta = sock.recv(1024)
        if respuesta:
            respuesta_dict = json.loads(respuesta.decode())
            print(f"\n{respuesta_dict['mensaje']}")
        break
    
    else:
        # Enviar mensaje
        paquete = json.dumps({
            "accion": "enviar",
            "texto": entrada
        })
        sock.send(paquete.encode())
        
        respuesta = sock.recv(1024)
        if respuesta:
            respuesta_dict = json.loads(respuesta.decode())
            if respuesta_dict["res"] != "ok":
                print(f"Error: {respuesta_dict['mensaje']}")

sock.close()

# 📚 EJERCICIO 4: CHAT MULTIUSUARIO CON HISTORIAL
# Enunciado:
# Sistema de chat donde los usuarios envían mensajes que se guardan. Al conectarse, reciben los últimos 10 mensajes. Pueden enviar mensajes o ver el historial completo.