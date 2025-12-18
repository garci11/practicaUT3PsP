import socket
import json

direccion_server = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(direccion_server)

print("Conexión establecida")
print("\n" + "="*50)
print("🎮 JUEGO DE TRIVIA 🎮")
print("="*50)

# Enviar nick
nick = input("\nIntroduce tu nick: ")
paquete = json.dumps({"nick": nick})
sock.send(paquete.encode())

# Recibir confirmación
respuesta = sock.recv(1024)
if respuesta:
    respuesta_dict = json.loads(respuesta.decode())
    print(f"\n{respuesta_dict['mensaje']}")
    print(f"Total de preguntas: {respuesta_dict['total_preguntas']}")
    print("\nCada respuesta correcta vale 10 puntos")
    print("="*50 + "\n")

# Bucle de preguntas
puntos = 0
while True:
    # Recibir pregunta
    data = sock.recv(4096)
    if not data:
        break
    
    pregunta = json.loads(data.decode())
    
    # Verificar si es el resultado final
    if pregunta.get("res") == "fin":
        # Mostrar resultado final
        print("\n" + "="*50)
        print("🏁 JUEGO TERMINADO 🏁")
        print("="*50)
        print(f"\nTu puntuación final: {pregunta['puntos_finales']} puntos\n")
        
        print("🏆 RANKING GLOBAL 🏆")
        print("-"*50)
        for jugador in pregunta['ranking']:
            if jugador['nick'] == nick:
                print(f">>> {jugador['posicion']:2d}. {jugador['nick']:20s} - {jugador['puntos']:3d} puntos <<<")
            else:
                print(f"    {jugador['posicion']:2d}. {jugador['nick']:20s} - {jugador['puntos']:3d} puntos")
        print("-"*50)
        break
    
    # Mostrar pregunta
    print(f"\n📝 PREGUNTA {pregunta['numero']}")
    print("-"*50)
    print(pregunta['pregunta'])
    for opcion in pregunta['opciones']:
        print(f"  {opcion}")
    
    # Pedir respuesta
    respuesta_usuario = input("\nTu respuesta (A/B/C): ").upper()
    
    # Enviar respuesta
    paquete = json.dumps({"respuesta": respuesta_usuario})
    sock.send(paquete.encode())
    
    # Recibir resultado
    resultado = sock.recv(1024)
    if resultado:
        resultado_dict = json.loads(resultado.decode())
        
        if resultado_dict['correcto']:
            print(f"✓ {resultado_dict['mensaje']}")
        else:
            print(f"✗ {resultado_dict['mensaje']}")
        
        print(f"Puntos actuales: {resultado_dict['puntos_actuales']}")

sock.close()

# 📚 EJERCICIO 6: JUEGO DE PREGUNTAS CON RANKING
# Enunciado:
# Sistema de trivia donde múltiples jugadores responden preguntas. Cada respuesta correcta suma puntos. Al final se muestra un ranking ordenado de todos los jugadores.
# Requisitos:

# 5 preguntas con 3 opciones cada una
# Respuesta correcta = +10 puntos
# Respuesta incorrecta = 0 puntos
# Ranking ordenado por puntos (mayor a menor)
# Mostrar ranking al final de cada partida