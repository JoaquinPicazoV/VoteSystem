import socket
import threading

DIRECCION_HOST = '0.0.0.0' 
PUERTO = 65432 
BLOQUEO = threading.Lock() 

OPCIONES_PERMITIDAS = {
    "FRANCISCO": 0, "CAMILO LOVER": 0, "JUAN.PY": 0, "THOMAS PINTA": 0, "NULO": 0
}
CONTEO_VOTOS = OPCIONES_PERMITIDAS.copy()

VOTANTES_REGISTRADOS = set()

def mostrar_resumen():
    with BLOQUEO:
        print(f"\n{'='*20} RECUENTO {'='*20}") 
        votos_ordenados = sorted(CONTEO_VOTOS.items(), key=lambda item: item[1], reverse=True)
        for opcion, cuenta in votos_ordenados:
            print(f"  {opcion}: {cuenta}") 
        print(f"{'='*50}")

def manejar_cliente(conexion, direccion):
    ip_conexion_real = direccion[0] 
    identificador_usuario = ip_conexion_real 
    
    try:
        datos_iniciales = conexion.recv(1024).decode('utf-8').strip()
        
        if datos_iniciales.startswith("CLIENT_IP:"):
            ip_reportada = datos_iniciales.split(":")[1]
            identificador_usuario = ip_reportada
            print(f"[CONEXIÓN] Cliente reporta IP local: {identificador_usuario}")
        
        if identificador_usuario in VOTANTES_REGISTRADOS:
            msg = f"ERROR: La IP {identificador_usuario} ya ha votado previamente."
            conexion.sendall(msg.encode('utf-8'))
            print(f"[RECHAZADO] Intento de voto doble de {identificador_usuario}")
            return 

        opciones_str = ", ".join(OPCIONES_PERMITIDAS.keys())
        bienvenida = f"Bienvenido IP {identificador_usuario}. Vota con: VOTE [OPCION]\nOpciones: {opciones_str}"
        conexion.sendall(bienvenida.encode('utf-8'))

        while True:
            datos = conexion.recv(1024)
            if not datos: break
            
            mensaje = datos.decode('utf-8').strip().upper()
            
            if mensaje == "EXIT":
                break
                
            if mensaje.startswith("VOTE "):
                candidato = mensaje[5:].strip()
                
                with BLOQUEO:
                    if identificador_usuario in VOTANTES_REGISTRADOS:
                         conexion.sendall("Error: Ya registramos un voto tuyo.".encode('utf-8'))
                         break

                    if candidato in CONTEO_VOTOS:
                        CONTEO_VOTOS[candidato] += 1
                        VOTANTES_REGISTRADOS.add(identificador_usuario) 
                        conexion.sendall("Voto registrado exitosamente.".encode('utf-8'))
                        print(f"[VOTO] {identificador_usuario} votó por {candidato}")
                        mostrar_resumen()
                        break 
                    else:
                        conexion.sendall("Opción no válida. Revisa las opciones.".encode('utf-8'))
            else:
                conexion.sendall("Comando inválido. Usa 'VOTE [NOMBRE]'".encode('utf-8'))

    except Exception as e:
        print(f"Error con {identificador_usuario}: {e}")
    finally:
        conexion.close()

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((DIRECCION_HOST, PUERTO))
    server.listen()
    
    s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s_temp.connect(("8.8.8.8", 80))
        ip_servidor = s_temp.getsockname()[0]
    except:
        ip_servidor = "127.0.0.1"
    s_temp.close()

    print(f" SERVIDOR CORRIENDO EN {ip_servidor}:{PUERTO}")
    print(" Esperando votantes...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()