import socket
import json

direccion_server = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(direccion_server)

print("Conexión establecida")

# Pedir el nick al usuario
nick = input("Introduce tu nick: ")

# Enviar el nick al servidor
paquete = json.dumps({"nick": nick})
sock.send(paquete.encode())

print("Paquete enviado")

# Recibir confirmación
respuesta = sock.recv(1024)

if respuesta:
    respuesta_dict = json.loads(respuesta.decode())
    print(f"Servidor responde: {respuesta_dict}")

print("\n" + "="*50)
print("¡JUEGO DE ADIVINANZA!")
print("Adivina el número entre 0 y 100")
print("Tienes 10 intentos máximo")
print("="*50 + "\n")

# Bucle del juego
while True:
    # Pedir número al usuario
    try:
        numero = int(input("Introduce un número (0-100): "))
        if numero < 0 or numero > 100:
            print("El número debe estar entre 0 y 100")
            continue
    except ValueError:
        print("Por favor introduce un número válido")
        continue
    
    # Enviar número al servidor
    paquete = json.dumps({"num": numero})
    sock.send(paquete.encode())
    
    # Recibir respuesta
    respuesta = sock.recv(4096)
    
    if respuesta:
        respuesta_dict = json.loads(respuesta.decode())
        
        # Procesar respuesta
        if respuesta_dict["res"] == "ok":
            # ¡Ganó!
            print("\n" + "="*50)
            print(f"¡FELICIDADES! ¡Adivinaste el número!")
            print(f"Lo lograste en {respuesta_dict['datos']['intentos']} intentos")
            print("="*50)
            print("\nÚLTIMOS 10 JUGADORES:")
            print("-" * 50)
            for i, jugador in enumerate(respuesta_dict['datos']['ultimos'], 1):
                print(f"{i:2d}. {jugador['nick']:20s} - {jugador['intentos']:2d} intentos")
            print("-" * 50)
            break
        
        elif respuesta_dict["res"] == "perdido":
            # Perdió
            print("\n" + "="*50)
            print(f"¡Se acabaron los intentos!")
            print(f"El número era: {respuesta_dict['datos']['numero_secreto']}")
            print("="*50)
            print("\nÚLTIMOS 10 JUGADORES:")
            print("-" * 50)
            for i, jugador in enumerate(respuesta_dict['datos']['ultimos'], 1):
                print(f"{i:2d}. {jugador['nick']:20s} - {jugador['intentos']:2d} intentos")
            print("-" * 50)
            break
        
        else:
            # Continuar jugando
            intentos = respuesta_dict['datos']['intentos']
            pista = respuesta_dict['datos']['pista']
            intentos_restantes = 10 - intentos
            
            print(f"\nIncorrecto. El número es {pista.upper()}")
            print(f"Intentos usados: {intentos}/10 (quedan {intentos_restantes})\n")

sock.close()












# FASE 1: ANÁLISIS DEL PROBLEMA 📋
# 1. Lee el enunciado y extrae:

# ¿Qué envía el cliente? → Formato de datos (JSON, texto plano, etc.)
# ¿Qué responde el servidor? → Estructura de la respuesta
# ¿Necesita hilos? → Si múltiples clientes a la vez = SÍ
# ¿Necesita compartir datos entre hilos? → Si sí = necesitas Lock

# 2. Identifica el flujo de mensajes:
# Cliente → Servidor: {mensaje 1}
# Servidor → Cliente: {respuesta 1}
# Cliente → Servidor: {mensaje 2}
# ...
# 3. Detecta estructuras de datos necesarias:

# ¿Guardar historial? → Lista
# ¿Rankings? → Lista ordenada
# ¿Últimos N elementos? → Lista con control de tamaño


# FASE 2: ESTRUCTURA DEL SERVIDOR 🖥️
# Esqueleto básico (SIEMPRE igual):
# pythonimport socket
# from threading import Thread, Lock
# import json  # Si usa JSON

# # 1. VARIABLES GLOBALES (datos compartidos)
# datos_compartidos = []
# lock = Lock()

# # 2. FUNCIÓN MANEJADORA (un hilo por cliente)
# def manejar_cliente(cliente, direccion):
#     try:
#         # A. Recibir datos del cliente
#         data = cliente.recv(1024)
#         mensaje = json.loads(data.decode())
        
#         # B. Procesar (la lógica del ejercicio)
#         # ... tu código aquí ...
        
#         # C. Enviar respuesta
#         respuesta = {"res": "ok"}
#         cliente.send(json.dumps(respuesta).encode())
        
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         cliente.close()

# # 3. CONFIGURACIÓN DEL SERVIDOR
# direccion = ("127.0.0.1", 5000)
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind(direccion)
# sock.listen(5)

# print(f"Servidor escuchando en {direccion}...")

# # 4. BUCLE PRINCIPAL
# while True:
#     cliente, direccion_cliente = sock.accept()
#     Thread(target=manejar_cliente, args=(cliente, direccion_cliente)).start()

# FASE 3: ESTRUCTURA DEL CLIENTE 💻
# Esqueleto básico:
# pythonimport socket
# import json

# # 1. CONEXIÓN
# direccion_server = ("127.0.0.1", 5000)
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect(direccion_server)

# print("Conexión establecida")

# # 2. ENVIAR DATOS INICIALES
# paquete = json.dumps({"dato": "valor"})
# sock.send(paquete.encode())

# # 3. BUCLE DE COMUNICACIÓN (si es interactivo)
# while True:
#     # A. Entrada del usuario
#     entrada = input("Tu entrada: ")
    
#     # B. Enviar al servidor
#     paquete = json.dumps({"dato": entrada})
#     sock.send(paquete.encode())
    
#     # C. Recibir respuesta
#     respuesta = sock.recv(1024)
#     respuesta_dict = json.loads(respuesta.decode())
    
#     # D. Procesar respuesta
#     print(respuesta_dict)
    
#     # E. Condición de salida
#     if respuesta_dict["res"] == "fin":
#         break

# # 4. CERRAR
# sock.close()

# FASE 4: PATRONES COMUNES 🔧
# Pattern 1: Datos compartidos entre hilos
# python# SIEMPRE con Lock
# with lock:
#     datos_compartidos.append(nuevo_dato)
#     # Mantener máximo N elementos
#     if len(datos_compartidos) > 10:
#         datos_compartidos.pop(0)  # Elimina el primero (FIFO)
# Pattern 2: Bucle de juego/interacción
# pythonwhile condicion:
#     # Recibir
#     data = cliente.recv(1024)
#     mensaje = json.loads(data.decode())
    
#     # Procesar
#     resultado = procesar(mensaje)
    
#     # Responder
#     respuesta = {"res": resultado}
#     cliente.send(json.dumps(respuesta).encode())
    
#     # Actualizar condición
#     if resultado == "fin":
#         break
# Pattern 3: JSON request-response
# python# CLIENTE envía:
# {"accion": "login", "usuario": "pepe"}

# # SERVIDOR responde:
# {"res": "ok", "datos": {...}}
# # o
# {"res": "error", "mensaje": "Usuario no existe"}

# FASE 5: CHECKLIST FINAL ✅
# Antes de entregar, verifica:
# Servidor:

#  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) ✓
#  sock.listen() antes del while ✓
#  Thread(target=...).start() para cada cliente ✓
#  cliente.close() en el finally ✓
#  Lock() si hay datos compartidos ✓
#  Prints informativos (conexiones, acciones) ✓

# Cliente:

#  sock.connect() al principio ✓
#  sock.close() al final ✓
#  Manejo de excepciones (try-except) ✓
#  Validación de entrada del usuario ✓

# JSON:

#  json.dumps() antes de enviar ✓
#  .encode() después de dumps ✓
#  .decode() después de recv ✓
#  json.loads() para parsear ✓


# FASE 6: DEBUGGING TIPS 🐛
# Problemas comunes:

# "Address already in use"
# → Solución: sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# El servidor no responde
# → Asegúrate de que cliente.send() está DENTRO del try, no después del finally
# JSON decode error
# → Imprime data.decode() antes de hacer json.loads() para ver qué llega
# Race conditions con listas
# → SIEMPRE usa with lock: cuando modifiques datos compartidos
# El cliente se queda colgado
# → Verifica que el servidor envíe SIEMPRE una respuesta