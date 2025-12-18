import socket
import json

direccion_server = ("127.0.0.1", 5000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(direccion_server)

print("Conexión establecida")
print("\n" + "="*60)
print("🔨 SISTEMA DE SUBASTAS ONLINE 🔨")
print("="*60)

# Enviar nick
nick = input("\nIntroduce tu nick: ")
paquete = json.dumps({"nick": nick})
sock.send(paquete.encode())

# Recibir información de la subasta
respuesta = sock.recv(4096)
if respuesta:
    info = json.loads(respuesta.decode())
    print(f"\n📦 Artículo: {info['articulo']}")
    print(f"💰 Precio inicial: {info['precio_inicial']}€")
    print(f"💵 Puja actual: {info['puja_actual']}€")
    if info['ganador_actual']:
        print(f"🏆 Va ganando: {info['ganador_actual']}")
    print(f"📊 Total de pujas: {info['total_pujas']}")
    print(f"🟢 Subasta activa: {'Sí' if info['subasta_activa'] else 'No'}")

print("\n" + "="*60)
print("COMANDOS:")
print("  pujar <cantidad>  - Hacer una puja")
print("  consultar         - Ver estado actual")
print("  historial         - Ver todas las pujas")
print("  cerrar            - Cerrar la subasta")
print("  salir             - Salir")
print("="*60 + "\n")

# Bucle de comandos
while True:
    entrada = input(f"[{nick}] >> ").strip()
    
    if not entrada:
        continue
    
    partes = entrada.split()
    comando = partes[0].lower()
    
    if comando == "pujar":
        if len(partes) < 2:
            print("Uso: pujar <cantidad>")
            continue
        
        try:
            cantidad = float(partes[1])
            paquete = json.dumps({
                "accion": "pujar",
                "cantidad": cantidad
            })
            sock.send(paquete.encode())
            
            respuesta = sock.recv(4096)
            if respuesta:
                resultado = json.loads(respuesta.decode())
                
                if resultado["res"] == "ok":
                    print(f"✓ {resultado['mensaje']}")
                    print(f"  Puja actual: {resultado['puja_actual']}€")
                    print(f"  Va ganando: {resultado['ganador_actual']}")
                    print(f"  Total pujas: {resultado['total_pujas']}")
                else:
                    print(f"✗ {resultado['mensaje']}")
                    if "puja_actual" in resultado:
                        print(f"  Puja mínima: {resultado['puja_actual'] + 0.01}€")
        
        except ValueError:
            print("Error: Introduce una cantidad válida")
    
    elif comando == "consultar":
        paquete = json.dumps({"accion": "consultar"})
        sock.send(paquete.encode())
        
        respuesta = sock.recv(4096)
        if respuesta:
            info = json.loads(respuesta.decode())
            print("\n--- ESTADO ACTUAL ---")
            print(f"Puja actual: {info['puja_actual']}€")
            print(f"Va ganando: {info['ganador_actual']}")
            print(f"Subasta activa: {'Sí' if info['subasta_activa'] else 'No'}")
            print(f"Total de pujas: {info['total_pujas']}")
            print()
    
    elif comando == "historial":
        paquete = json.dumps({"accion": "historial"})
        sock.send(paquete.encode())
        
        respuesta = sock.recv(8192)
        if respuesta:
            resultado = json.loads(respuesta.decode())
            print(f"\n--- HISTORIAL DE PUJAS ({resultado['total']}) ---")
            for i, puja in enumerate(resultado['historial'], 1):
                print(f"{i:2d}. [{puja['hora']}] {puja['nick']:15s} - {puja['cantidad']:6.2f}€")
            print()
    
    elif comando == "cerrar":
        confirmacion = input("¿Cerrar la subasta? (s/n): ")
        if confirmacion.lower() == 's':
            paquete = json.dumps({"accion": "cerrar"})
            sock.send(paquete.encode())
            
            respuesta = sock.recv(8192)
            if respuesta:
                resultado = json.loads(respuesta.decode())
                
                if resultado["res"] == "ok":
                    print("\n" + "="*60)
                    print("🔨 SUBASTA CERRADA 🔨")
                    print("="*60)
                    print(f"🏆 GANADOR: {resultado['ganador']}")
                    print(f"💰 PRECIO FINAL: {resultado['precio_final']}€")
                    print("\n--- HISTORIAL DE PUJAS ---")
                    for i, puja in enumerate(resultado['historial'], 1):
                        simbolo = "🏆" if puja['nick'] == resultado['ganador'] else "  "
                        print(f"{simbolo} {i:2d}. [{puja['hora']}] {puja['nick']:15s} - {puja['cantidad']:6.2f}€")
                    print("="*60 + "\n")
                else:
                    print(f"✗ {resultado['mensaje']}")
    
    elif comando == "salir":
        paquete = json.dumps({"accion": "salir"})
        sock.send(paquete.encode())
        
        respuesta = sock.recv(1024)
        if respuesta:
            resultado = json.loads(respuesta.decode())
            print(f"\n{resultado['mensaje']}")
        break
    
    else:
        print("Comando no reconocido. Usa: pujar, consultar, historial, cerrar, salir")

sock.close()

# 📚 EJERCICIO 7: SUBASTA ONLINE ENTRE MÚLTIPLES CLIENTES
# Enunciado:
# Sistema de subastas donde múltiples clientes pujan por un artículo. El servidor mantiene la puja más alta y notifica quién va ganando. Cuando el servidor termina la subasta, declara al ganador.
# Requisitos:

# Múltiples clientes pueden pujar simultáneamente
# Solo se aceptan pujas mayores a la actual
# Se guarda quién hizo cada puja
# Al cerrar subasta, se muestra historial de pujas y ganador
# Usar hilos y sincronización con Lock