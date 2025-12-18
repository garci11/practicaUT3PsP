import socket

HOST = 'localhost'
PORT = 6000

tablero = [" "] * 9
turno = 0  # 0 = X, 1 = O

def mostrar_tablero():
    return f"""
 {tablero[0]} | {tablero[1]} | {tablero[2]}
-----------
 {tablero[3]} | {tablero[4]} | {tablero[5]}
-----------
 {tablero[6]} | {tablero[7]} | {tablero[8]}
"""

def ganador():
    combinaciones = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in combinaciones:
        if tablero[a] == tablero[b] == tablero[c] != " ":
            return tablero[a]
    if " " not in tablero:
        return "Empate"
    return None

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(2)
    print("Servidor listo")

    jugadores = [s.accept()[0] for _ in range(2)]
    jugadores[0].sendall(b"Eres X")
    jugadores[1].sendall(b"Eres O")

    while True:
        jugador = jugadores[turno]
        jugador.sendall(mostrar_tablero().encode())
        jugador.sendall(b"Tu turno (0-8): ")

        pos = int(jugador.recv(1024).decode())
        if tablero[pos] == " ":
            tablero[pos] = "X" if turno == 0 else "O"
            g = ganador()
            if g:
                for j in jugadores:
                    j.sendall(mostrar_tablero().encode())
                    j.sendall(f"Resultado: {g}".encode())
                break
            turno = 1 - turno
