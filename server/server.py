import socket
import threading
import sys 
import os 

DIRECCION_HOST = '0.0.0.0' 
PUERTO = 65432 
BLOQUEO = threading.Lock() 

OPCIONES_PERMITIDAS = {
    "FRANCISCO": 0, "CAMILO LOVER": 0, "JUAN.PY": 0, "THOMAS PINTA": 0, "NULO": 0
}
CONTEO_VOTOS = OPCIONES_PERMITIDAS.copy()

MAPEO_VOTOS = {clave.upper(): clave for clave in OPCIONES_PERMITIDAS.keys()}

VOTANTES_REGISTRADOS = set()

def limpiar_pantalla():
    if 'TERM' not in os.environ: 
        os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_resumen():
    ROJO = '\033[91m'
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    RESET = '\033[0m'
    
    with BLOQUEO:
        total = sum(CONTEO_VOTOS.values())
        print(f"\n{VERDE}{'='*45}{RESET}") 
        print(f"{VERDE}         RESUMEN DEL CONTEO DE VOTOS  {RESET}") 
        print(f"{VERDE}{'='*45}{RESET}") 
        print(f"{AZUL}  TOTAL VOTOS EMITIDOS: {total}{RESET}")
        print(f"{VERDE}{'-'*45}{RESET}") 
        
        votos_ordenados = sorted(CONTEO_VOTOS.items(), key=lambda item: item[1], reverse=True)
        
        for i, (opcion, cuenta) in enumerate(votos_ordenados):
            color = AMARILLO if i == 0 and cuenta > 0 else RESET
            barra = "█" * cuenta 
            print(f"  {color}{opcion.ljust(15)}: {str(cuenta).ljust(4)} {barra}{RESET}") 
            
        print(f"{VERDE}{'='*45}{RESET}\n")


def manejar_cliente(conexion, direccion):
    ip_proxy = direccion[0] 
    puerto_cliente = direccion[1]
    ip_real_dispositivo = None
    
    try:
        datos_iniciales = conexion.recv(1024)
        if datos_iniciales:
            mensaje_inicial = datos_iniciales.decode('utf-8').strip()
            if mensaje_inicial.startswith("CLIENT_IP:"):
                ip_real_dispositivo = mensaje_inicial.split("CLIENT_IP:")[1].strip()
            else:
                ip_real_dispositivo = ip_proxy
        else:
            ip_real_dispositivo = ip_proxy
    except Exception as e:
        print(f"Error al recibir IP del cliente: {e}")
        ip_real_dispositivo = ip_proxy
    
    identificador_cliente = ip_real_dispositivo

    print(f"Cliente conectado desde {ip_proxy} (Puerto: {puerto_cliente})")
    print(f"  → IP real del dispositivo en la red: {ip_real_dispositivo}")
    
    ya_voto = identificador_cliente in VOTANTES_REGISTRADOS

    try:
        lista_opciones = ", ".join(OPCIONES_PERMITIDAS.keys())
        
        if ya_voto:
            msg = f"ERROR: Ya has votado (IP del dispositivo: {identificador_cliente}). Solo se permite un voto por dispositivo en la red."
            conexion.sendall(msg.encode('utf-8'))
            print(f"Dispositivo {identificador_cliente} intentó votar de nuevo.")
            return 
        else:
            bienvenida = f"Bienvenido desde dispositivo {ip_real_dispositivo}. Opciones: {lista_opciones}\nPor favor, vote usando 'VOTE [OPCIÓN]'"
            conexion.sendall(bienvenida.encode('utf-8'))
        
        while True:
            datos = conexion.recv(1024)
            if not datos:
                break
            
            mensaje = datos.decode('utf-8').strip().upper()
            
            if mensaje.startswith("CLIENT_IP:"):
                continue

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
                
                print(f"\n---- NUEVO VOTO EMITIDO ----")
                print(f"    IP del dispositivo en la red: {ip_real_dispositivo}")
                print(f"    Opción elegida: {clave_voto_original}")
                
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


def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((DIRECCION_HOST, PUERTO))
        server.listen(5)
    except socket.error as e:
        print(f"Error al iniciar el socket: {e}")
        return
        
    try:
        ip_local = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        ip_local = "Dirección IP local desconocida"
            
    VERDE = '\033[92m'
    RESET = '\033[0m' 
    print(f"{VERDE}{'='*60}{RESET}")
    print(f"{VERDE}SERVIDOR DE VOTACIÓN CORRIENDO{RESET}")
    print(f"{VERDE} IP Local de la red: {ip_local}{RESET}")
    print(f"{VERDE} Escuchando en TODAS las IPs ({DIRECCION_HOST}) en el puerto: {PUERTO}{RESET}")
    print(f"{VERDE}{'='*60}{RESET}")
    
    mostrar_resumen()

    while True:
        try:
            conexion, direccion = server.accept()
            hilo_cliente = threading.Thread(target=manejar_cliente, args=(conexion, direccion))
            hilo_cliente.daemon = True
            hilo_cliente.start()

        except KeyboardInterrupt:
            print("\n" + "="*50)
            print("         [SERVIDOR APAGADO POR EL USUARIO] ")
            print("         RESUMEN FINAL ANTES DE CERRAR")
            print("="*50)
            mostrar_resumen() 
            server.close()
            sys.exit(0)
        # ---------------------------------------------
            
        except Exception as e:
            print(f"Fallo al aceptar conexión: {e}")
            break

if __name__ == "__main__":
    iniciar_servidor()