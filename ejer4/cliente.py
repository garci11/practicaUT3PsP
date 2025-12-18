import socket
import json

direccion_server = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(direccion_server)

print("Conexión establecida con el sistema de turnos")
print("\n=== SISTEMA DE TURNOS ===")
print("Acciones disponibles:")
print("  - pedir_turno: Solicitar un nuevo turno")
print("  - consultar: Ver el estado de tu turno")
print("  - atender: Marcar que has sido atendido\n")

# Pedir datos
nick = input("Introduce tu nick: ")
accion = input("Acción: ")

# Enviar petición
paquete = json.dumps({
    "nick": nick,
    "accion": accion
})
sock.send(paquete.encode())

print("Paquete enviado")

# Recibir respuesta
respuesta = sock.recv(4096)

if respuesta:
    respuesta_dict = json.loads(respuesta.decode())
    
    if respuesta_dict["res"] == "ok":
        print(f"\n✓ {respuesta_dict['mensaje']}")
        
        if "turno" in respuesta_dict:
            print(f"Tu turno: #{respuesta_dict['turno']}")
        
        if "delante" in respuesta_dict:
            print(f"Personas delante: {respuesta_dict['delante']}")
        
        if "turno_actual" in respuesta_dict:
            print(f"Turno actual: #{respuesta_dict['turno_actual']}")
        
        if "siguiente_turno" in respuesta_dict:
            print(f"Siguiente turno: #{respuesta_dict['siguiente_turno']}")
    else:
        print(f"\n✗ Error: {respuesta_dict['mensaje']}")

sock.close()