import socket
import json

direccion_server = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(direccion_server)

print("Conexión establecida con el servidor de calculadora")
print("\nOperaciones disponibles: suma, resta, multiplicacion, division\n")

# Pedir operación
operacion = input("Operación: ")
a = float(input("Primer número: "))
b = float(input("Segundo número: "))

# Enviar operación
paquete = json.dumps({
    "op": operacion,
    "a": a,
    "b": b
})
sock.send(paquete.encode())

print("Paquete enviado")

# Recibir respuesta
respuesta = sock.recv(4096)

if respuesta:
    respuesta_dict = json.loads(respuesta.decode())
    
    if respuesta_dict["res"] == "ok":
        print(f"\n✓ Resultado: {respuesta_dict['resultado']}")
        print("\n--- ÚLTIMAS 5 OPERACIONES ---")
        for i, op in enumerate(respuesta_dict['ultimas'], 1):
            print(f"{i}. {op['operacion']}({op['a']}, {op['b']}) = {op['resultado']}")
    else:
        print(f"\n✗ Error: {respuesta_dict['mensaje']}")

sock.close()