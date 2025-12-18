import socket
import json
from threading import Thread, Lock

# Preguntas del juego
PREGUNTAS = [
    {
        "pregunta": "¿Cuál es la capital de Francia?",
        "opciones": ["A) Londres", "B) París", "C) Berlín"],
        "correcta": "B"
    },
    {
        "pregunta": "¿Cuántos continentes hay?",
        "opciones": ["A) 5", "B) 6", "C) 7"],
        "correcta": "C"
    },
    {
        "pregunta": "¿Qué lenguaje usa Python?",
        "opciones": ["A) Compilado", "B) Interpretado", "C) Ensamblador"],
        "correcta": "B"
    },
    {
        "pregunta": "¿Cuál es el océano más grande?",
        "opciones": ["A) Atlántico", "B) Índico", "C) Pacífico"],
        "correcta": "C"
    },
    {
        "pregunta": "¿En qué año llegó el hombre a la Luna?",
        "opciones": ["A) 1969", "B) 1971", "C) 1965"],
        "correcta": "A"
    }
]

# Ranking global de jugadores {nick: puntos}
ranking = {}
lock = Lock()

def calcular_ranking():
    """Ordena el ranking por puntos"""
    return sorted(ranking.items(), key=lambda x: x[1], reverse=True)

def manejar_cliente(cliente, direccion):
    """Maneja la partida de un jugador"""
    print(f"Cliente conectado: {direccion}")
    
    try:
        # Recibir nick
        data = cliente.recv(1024)
        if not data:
            cliente.close()
            return
        
        mensaje = json.loads(data.decode())
        nick = mensaje.get("nick")
        
        print(f"Jugador: {nick}")
        
        # Inicializar puntos
        puntos = 0
        
        # Enviar confirmación y número de preguntas
        respuesta = {
            "res": "ok",
            "mensaje": "Bienvenido al juego de trivia",
            "total_preguntas": len(PREGUNTAS)
        }
        cliente.send(json.dumps(respuesta).encode())
        
        # Bucle de preguntas
        for i, pregunta in enumerate(PREGUNTAS, 1):
            # Enviar pregunta
            data_pregunta = {
                "numero": i,
                "pregunta": pregunta["pregunta"],
                "opciones": pregunta["opciones"]
            }
            cliente.send(json.dumps(data_pregunta).encode())
            
            # Recibir respuesta
            data = cliente.recv(1024)
            if not data:
                break
            
            respuesta_usuario = json.loads(data.decode())
            respuesta_letra = respuesta_usuario.get("respuesta").upper()
            
            # Verificar respuesta
            if respuesta_letra == pregunta["correcta"]:
                puntos += 10
                resultado = {
                    "correcto": True,
                    "mensaje": "¡Correcto! +10 puntos",
                    "puntos_actuales": puntos
                }
            else:
                resultado = {
                    "correcto": False,
                    "mensaje": f"Incorrecto. La respuesta era {pregunta['correcta']}",
                    "puntos_actuales": puntos
                }
            
            cliente.send(json.dumps(resultado).encode())
            
            print(f"{nick} - Pregunta {i}: {respuesta_letra} - Puntos: {puntos}")
        
        # Guardar en ranking
        with lock:
            # Si el jugador ya existe, mantener su mejor puntuación
            if nick in ranking:
                ranking[nick] = max(ranking[nick], puntos)
            else:
                ranking[nick] = puntos
            
            # Calcular ranking ordenado
            ranking_ordenado = calcular_ranking()
        
        # Enviar resultado final
        resultado_final = {
            "res": "fin",
            "puntos_finales": puntos,
            "ranking": [
                {"posicion": i, "nick": jugador, "puntos": pts}
                for i, (jugador, pts) in enumerate(ranking_ordenado, 1)
            ]
        }
        cliente.send(json.dumps(resultado_final).encode())
        
        print(f"{nick} terminó con {puntos} puntos")
        
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

print(f"Servidor de Trivia escuchando en {direccion}...")
print(f"Total de preguntas: {len(PREGUNTAS)}\n")

while True:
    cliente, direccion_cliente = sock.accept()
    Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()