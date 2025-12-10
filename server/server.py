import socket
import threading
import time

DIRECCION_HOST = '0.0.0.0'
PUERTO = 65432
BLOQUEO = threading.Lock()

OPCIONES_PERMITIDAS = {
    "FranCISCO": 0,
    "Camilo LOVER": 0,
    "Juan.py": 0,
    "NULO": 0
}
CONTEO_VOTOS = OPCIONES_PERMITIDAS.copy()
MAPEO_VOTOS = {clave.upper(): clave for clave in OPCIONES_PERMITIDAS.keys()}

VOTANTES_REGISTRADOS = set()

def mostrar_resumen():
    ROJO = '\033[91m'
    RESET = '\033[0m'
    
    with BLOQUEO:
        print(f"{ROJO}\n{'='*40}")
        print("      RESUMEN DEL CONTEO DE VOTOS")
        print(f"{'='*40}{RESET}") 
        votos_ordenados = sorted(CONTEO_VOTOS.items(), key=lambda item: item[1], reverse=True)
        for opcion, cuenta in votos_ordenados:
            print(f"{ROJO}  {opcion}: {cuenta} voto(s){RESET}") 
        print(f"{ROJO}{'='*40}{RESET}")

def manejar_cliente(conexion, direccion):
    ip_real = direccion[0] 
    
    try:
        uuid_cliente = conexion.recv(1024).decode('utf-8').strip()
        
        if not uuid_cliente:
            return 
            
        print(f"Cliente conectado. IP Red: {ip_real} | UUID: {uuid_cliente}")
        ya_voto = uuid_cliente in VOTANTES_REGISTRADOS

        lista_opciones = ", ".join(OPCIONES_PERMITIDAS.keys())
        
        if ya_voto:
             conexion.sendall(f"Ya has votado (ID: {uuid_cliente}). Tu voto ya fue registrado.".encode('utf-8'))
             print(f"Cliente {uuid_cliente} (IP: {ip_real}) intentó votar de nuevo.")
             return 
        else:
             conexion.sendall(f"Bienvenido ID: {uuid_cliente}. Opciones: {lista_opciones}\nPor favor, vote usando 'VOTE [OPCIÓN]'".encode('utf-8'))
        
        while True:
            datos = conexion.recv(1024)
            if not datos:
                break
            
            mensaje = datos.decode('utf-8').strip().upper()

            if mensaje.startswith("VOTE "):
                
                if ya_voto:
                    conexion.sendall("Ya has emitido tu voto y solo se permite uno.".encode('utf-8'))
                    continue
                    
                opcion_voto_mayus = mensaje[5:].strip() 
                
                if opcion_voto_mayus not in MAPEO_VOTOS: 
                    conexion.sendall(f"Opción no válida. Opciones: {lista_opciones}".encode('utf-8'))
                    continue

                clave_voto_original = MAPEO_VOTOS[opcion_voto_mayus]

                with BLOQUEO:
                    CONTEO_VOTOS[clave_voto_original] += 1
                    VOTANTES_REGISTRADOS.add(uuid_cliente) 
                    ya_voto = True 
                
                AZUL = '\033[94m'
                RESET = '\033[0m'
                print(f"\n{AZUL}---- NUEVO VOTO EMITIDO ---- {RESET}")
                print(f"{AZUL}    ID Votante: {uuid_cliente}{RESET}")
                print(f"{AZUL}    Desde IP (Tunnel): {ip_real}{RESET}")
                print(f"{AZUL}    Opción elegida: {clave_voto_original}{RESET}")
                
                mostrar_resumen()
                
                conexion.sendall("Voto registrado exitosamente. Gracias por participar.".encode('utf-8'))
                break 
            
            elif mensaje == "EXIT":
                print(f"Cliente {uuid_cliente} solicitó cerrar.")
                break
            
            else:
                conexion.sendall("Comando no reconocido. Use 'VOTE [OPCIÓN]' o 'EXIT'.".encode('utf-8'))

    except Exception as e:
        print(f"Error en la conexión: {e}")
    
    finally:
        conexion.close()
        print(f"Conexión cerrada.")

def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((DIRECCION_HOST, PUERTO))
        s.listen(5)
        
        try:
            ip_local = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            ip_local = "Desconocida"
            
        VERDE = '\033[92m'
        RESET = '\033[0m' 
        print(f"{VERDE}{'='*60}{RESET}")
        print(f"{VERDE}SERVIDOR DE VOTACIÓN CORRIENDO (MODO UUID){RESET}")
        print(f"{VERDE}  IP Local Container: {ip_local}{RESET}")
        print(f"{VERDE}  Puerto: {PUERTO}{RESET}")
        print(f"{VERDE}{'='*60}{RESET}")
        
        mostrar_resumen()

        while True:
            try:
                conexion, direccion = s.accept()
                hilo_cliente = threading.Thread(target=manejar_cliente, args=(conexion, direccion))
                hilo_cliente.daemon = True
                hilo_cliente.start()

            except KeyboardInterrupt:
                print("\n[SERVIDOR APAGADO]")
                break
            except Exception as e:
                print(f"Fallo al aceptar conexión: {e}")
                break

if __name__ == "__main__":
    iniciar_servidor()