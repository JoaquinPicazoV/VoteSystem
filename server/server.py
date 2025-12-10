import socket
import threading
import time

# aqui configuramos el hosting del servidor
DIRECCION_HOST = '0.0.0.0' 
PUERTO = 65432 
BLOQUEO = threading.Lock() 

# ponemos opciones que son permitidas dentro de las votaciones
OPCIONES_PERMITIDAS = {
    "FranCISCO": 0,
    "Camilo LOVER": 0,
    "Juan.py": 0,
    "NULO": 0
}
CONTEO_VOTOS = OPCIONES_PERMITIDAS.copy()

# Mapeamos para insensibilidad a mayusculas y minusculas
MAPEO_VOTOS = {clave.upper(): clave for clave in OPCIONES_PERMITIDAS.keys()}

# guardamos las IP para que no voten 2 veces (1 voto por IP dentro de la LAN)
VOTANTES_REGISTRADOS = set()

# funcion para mostrar el conteo de los votos cada vez que se hace uno nuevo
def mostrar_resumen():
    ROJO = '\033[91m'
    RESET = '\033[0m'
    
    with BLOQUEO:
        print(f"{ROJO}\n{'='*40}")
        print("     RESUMEN DEL CONTEO DE VOTOS")
        print(f"{'='*40}{RESET}") 
        votos_ordenados = sorted(CONTEO_VOTOS.items(), key=lambda item: item[1], reverse=True)
        for opcion, cuenta in votos_ordenados:
            print(f"{ROJO}  {opcion}: {cuenta} voto(s){RESET}") 
        print(f"{ROJO}{'='*40}{RESET}")

# manejamos TODA la interaccion con el cliente, tanto recibir datos como enviarle
def manejar_cliente(conexion, direccion):
    ip_cliente = direccion[0] 
    identificador_cliente = ip_cliente 
    print(f"Cliente conectado desde {identificador_cliente} (Puerto: {direccion[1]})")
    
    ya_voto = identificador_cliente in VOTANTES_REGISTRADOS

    try:
        lista_opciones = ", ".join(OPCIONES_PERMITIDAS.keys())
        
        if ya_voto:
             conexion.sendall(f"Ya has votado (IP: {identificador_cliente}). Tu voto ya fue registrado. Solo se permite un voto por IP.".encode('utf-8'))
             print(f"Cliente {identificador_cliente} intentó votar de nuevo.")
             return 
        else:
             conexion.sendall(f"Bienvenido IP: {identificador_cliente}. Opciones: {lista_opciones}\nPor favor, vote usando 'VOTE [OPCIÓN]'".encode('utf-8'))
        
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
                    VOTANTES_REGISTRADOS.add(identificador_cliente) 
                    ya_voto = True 
                
                AZUL = '\033[94m'
                RESET = '\033[0m'
                print(f"\n{AZUL}---- NUEVO VOTO EMITIDO ---- {RESET}")
                print(f"{AZUL}    IP del Votante: {identificador_cliente}{RESET}")
                print(f"{AZUL}    Opción elegida: {clave_voto_original}{RESET}")
                
                mostrar_resumen()
                
                conexion.sendall("Voto registrado exitosamente. Gracias por participar.".encode('utf-8'))
                break 
            
            elif mensaje == "EXIT":
                print(f"Cliente {identificador_cliente} solicitó cerrar.")
                break
            
            else:
                conexion.sendall("Comando no reconocido. Use 'VOTE [OPCIÓN]' o 'EXIT'.".encode('utf-8'))

    except Exception as e:
        print(f"Error en la conexión con {identificador_cliente}: {e}")
    
    finally:
        conexion.close()
        print(f"Conexión con {identificador_cliente} cerrada.")

# esto se muestra al iniciar el servidor, se manejan hilos para más de un cliente a la vez
def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((DIRECCION_HOST, PUERTO))
        s.listen(5)
        
        try:
            ip_local = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            ip_local = "Dirección IP local desconocida"
            
        VERDE = '\033[92m'
        RESET = '\033[0m' 
        print(f"{VERDE}{'='*60}{RESET}")
        print(f"{VERDE}SERVIDOR DE VOTACIÓN CORRIENDO{RESET}")
        print(f"{VERDE}  IP Local de la red: {ip_local}{RESET}")
        print(f"{VERDE}  Escuchando en TODAS las IPs ({DIRECCION_HOST}) en el puerto: {PUERTO}{RESET}")
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