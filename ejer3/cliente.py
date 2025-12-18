import socket
import json

direccion_server = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(direccion_server)

print("Conexión establecida con el sistema de votaciones")
print("\n=== SISTEMA DE VOTACIONES ===")
print("Opciones disponibles: A, B, C\n")

# Pedir datos
nick = input("Introduce tu nick: ")
voto = input("Tu voto (A/B/C): ").upper()

# Enviar voto
paquete = json.dumps({
    "nick": nick,
    "voto": voto
})
sock.send(paquete.encode())

print("Paquete enviado")

# Recibir respuesta
respuesta = sock.recv(4096)

if respuesta:
    respuesta_dict = json.loads(respuesta.decode())
    
    if respuesta_dict["res"] == "ok":
        print(f"\n✓ {respuesta_dict['mensaje']}")
        print("\n--- RESULTADOS ACTUALES ---")
        resultados = respuesta_dict['resultados']
        print(f"Total de votos: {resultados['total']}")
        print("\nDistribución:")
        for opcion in ['A', 'B', 'C']:
            votos = resultados['votos'][opcion]
            porcentaje = resultados['porcentajes'][opcion]
            barra = "█" * int(porcentaje / 5)
            print(f"Opción {opcion}: {votos:3d} votos ({porcentaje:5.2f}%) {barra}")
    else:
        print(f"\n✗ Error: {respuesta_dict['mensaje']}")

sock.close()